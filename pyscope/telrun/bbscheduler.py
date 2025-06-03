from astroplan.scheduling import PriorityScheduler


class BBScheduler(PriorityScheduler):
    """
    A scheduler that extends PriorityScheduler functionality.
    
    This scheduler maintains the core functionality of PriorityScheduler,
    which schedules observation blocks in order of priority, but is designed
    to be extended with additional features in the future. This enhanced 
    version tracks the original blocks passed to the scheduler and provides 
    methods to identify which blocks were not scheduled.
    
    Parameters
    ----------
    constraints : list or None, optional
        Constraints to apply to all observations.
    observer : astroplan.Observer
        The observer/site to do the scheduling for.
    transitioner : astroplan.Transitioner or None, optional
        The transitioner to use for computing transition times
        between observations.
    gap_time : astropy.units.Quantity
        The maximum length of time a transition between observations can take.
    time_resolution : astropy.units.Quantity
        The smallest time step to use when scheduling.
    
    Attributes
    ----------
    _original_blocks : list
        Storage for the original blocks passed to the scheduler.
    _last_schedule : Schedule or None
        The most recent schedule result from the scheduler.
    
    Methods
    -------
    get_observing_blocks()
        Get the successfully scheduled observation blocks.
    get_scheduled_blocks()
        Get all scheduled blocks including transitions.
    get_missing_blocks()
        Get blocks that couldn't be scheduled.
    get_original_blocks()
        Get all blocks originally submitted.
    get_scheduling_summary()
        Get summary of scheduling results.
    
    Examples
    --------
    >>> from astroplan import Observer
    >>> from astropy.coordinates import EarthLocation
    >>> import astropy.units as u
    >>> 
    >>> # Create observer
    >>> location = EarthLocation.of_site('Kitt Peak')
    >>> observer = Observer(location=location)
    >>> 
    >>> # Create scheduler
    >>> scheduler = BBScheduler(constraints=[], observer=observer)
    >>> 
    >>> # Schedule blocks (blocks and schedule objects needed)
    >>> # result_schedule = scheduler(blocks, schedule)
    >>> 
    >>> # Get scheduling results
    >>> summary = scheduler.get_scheduling_summary()
    >>> missing = scheduler.get_missing_blocks()
    
    Notes
    -----
    This scheduler extends astroplan.scheduling.PriorityScheduler and maintains
    backward compatibility while adding enhanced tracking capabilities. The 
    scheduler stores references to original blocks and provides convenience
    methods to analyze scheduling results.
    """

    def __init__(self, *args, **kwargs):
        super(BBScheduler, self).__init__(*args, **kwargs)
        self._original_blocks = []
        self._last_schedule = None

    def __call__(self, blocks, schedule):
        """
        Schedule a set of observing blocks.
        
        Parameters
        ----------
        blocks : list of ObservingBlock objects
            The observing blocks to schedule
        
        schedule : Schedule
            The schedule to add the blocks to
            
        Returns
        -------
        schedule : Schedule
            The updated schedule with new blocks added
        """
        # Store the original blocks for tracking
        self._original_blocks = blocks.copy()
        
        # Call the parent PriorityScheduler implementation
        result_schedule = super(BBScheduler, self).__call__(blocks, schedule)
        
        # Store the last schedule for missing blocks calculation
        self._last_schedule = result_schedule
        
        return result_schedule
    
    def get_original_blocks(self):
        """
        Get the original blocks that were passed to the scheduler.
        
        Returns
        -------
        list of ObservingBlock objects
            The original blocks passed to the last call of the scheduler
        """
        return self._original_blocks.copy()
    
    def get_observing_blocks(self):
        """
        Get the successfully scheduled observation blocks.
        
        This provides the same information as schedule.observing_blocks
        but accessible directly from the scheduler for convenience.
        
        Returns
        -------
        list of ObservingBlock objects
            The observation blocks that were successfully scheduled
        """
        if not self._last_schedule:
            return []
        return self._last_schedule.observing_blocks
    
    def get_scheduled_blocks(self):
        """
        Get all scheduled blocks including transitions.
        
        This provides the same information as schedule.scheduled_blocks
        but accessible directly from the scheduler for convenience.
        
        Returns
        -------
        list of Block objects
            All blocks (observation and transition) that were scheduled
        """
        if not self._last_schedule:
            return []
        return self._last_schedule.scheduled_blocks
    
    def get_missing_blocks(self):
        """
        Get the blocks that were not scheduled in the last scheduling run.
        
        Returns
        -------
        list of ObservingBlock objects
            The blocks that were passed to the scheduler but not scheduled
        """
        if not self._last_schedule or not self._original_blocks:
            return []
        
        # Get the scheduled observation blocks (not transition blocks)
        from astroplan.scheduling import TransitionBlock
        scheduled_obs_blocks = [
            block for block in self._last_schedule.scheduled_blocks 
            if not isinstance(block, TransitionBlock)
        ]
        
        # Use a more robust approach: if the number of scheduled blocks equals
        # the number of original blocks, then no blocks are missing
        if len(scheduled_obs_blocks) == len(self._original_blocks):
            return []
        
        # For cases where not all blocks were scheduled, we need to do detailed matching
        # Create a list of scheduled block signatures for comparison
        scheduled_signatures = []
        for block in scheduled_obs_blocks:
            signature = {
                'target_name': block.target.name,
                'duration_seconds': block.duration.to('second').value,
                'priority': getattr(block, 'priority', None),
                'configuration': str(block.configuration)  # Convert to string for comparison
            }
            scheduled_signatures.append(signature)
        
        # Find missing blocks by checking if each original block has a match
        missing = []
        for original_block in self._original_blocks:
            original_signature = {
                'target_name': original_block.target.name,
                'duration_seconds': original_block.duration.to('second').value,
                'priority': getattr(original_block, 'priority', None),
                'configuration': str(original_block.configuration)
            }
            
            # Look for a matching scheduled block
            found = False
            for i, scheduled_sig in enumerate(scheduled_signatures):
                if (scheduled_sig['target_name'] == original_signature['target_name'] and
                    abs(scheduled_sig['duration_seconds'] - original_signature['duration_seconds']) < 1.0 and
                    scheduled_sig['priority'] == original_signature['priority'] and
                    scheduled_sig['configuration'] == original_signature['configuration']):
                    # Mark this scheduled block as used (remove it to handle duplicates correctly)
                    scheduled_signatures.pop(i)
                    found = True
                    break
            
            if not found:
                missing.append(original_block)
        
        return missing
    
    def get_scheduling_summary(self):
        """
        Get a summary of the scheduling results.
        
        Returns
        -------
        dict
            A dictionary containing:
            - 'total_blocks': Total number of blocks submitted
            - 'scheduled_blocks': Number of blocks successfully scheduled
            - 'missing_blocks': Number of blocks that couldn't be scheduled
            - 'scheduling_efficiency': Percentage of blocks successfully scheduled
        """
        total = len(self._original_blocks)
        scheduled = len(self.get_observing_blocks())
        missing = len(self.get_missing_blocks())
        
        efficiency = (scheduled / total * 100) if total > 0 else 0
        
        return {
            'total_blocks': total,
            'scheduled_blocks': scheduled,
            'missing_blocks': missing,
            'scheduling_efficiency': efficiency
        }
    
    
    