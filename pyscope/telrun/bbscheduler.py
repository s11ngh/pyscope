from astroplan.scheduling import Scheduler, PriorityScheduler





class BBScheduler(PriorityScheduler):
    """
    A scheduler that extends PriorityScheduler functionality.
    
    This scheduler maintains the core functionality of PriorityScheduler,
    which schedules observation blocks in order of priority, but is designed
    to be extended with additional features in the future.
    
    Parameters
    ----------
    constraints : list or None
        Constraints to apply to all observations
    
    observer : astroplan.Observer
        The observer/site to do the scheduling for
    
    transitioner : astroplan.Transitioner or None
        The transitioner to use for computing transition times
        between observations
    
    gap_time : astropy.units.Quantity
        The maximum length of time a transition between observations can take
    
    time_resolution : astropy.units.Quantity
        The smallest time step to use when scheduling
    """

    def __init__(self, *args, **kwargs):
        super(BBScheduler, self).__init__(*args, **kwargs)

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
        # Call the parent PriorityScheduler implementation
        return super(BBScheduler, self).__call__(blocks, schedule)


