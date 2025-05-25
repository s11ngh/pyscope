import pytest
from astroplan import Observer, FixedTarget, ObservingBlock
from astropy.time import Time
from astropy import units as u
from astroplan.constraints import AirmassConstraint, AtNightConstraint, TimeConstraint, AltitudeConstraint
from astroplan.scheduling import TransitionBlock, Schedule, Transitioner
from pyscope.telrun.bbscheduler import BBScheduler
from astroplan.scheduling import PriorityScheduler


# Constants for all tests
def get_test_constants():
    """Return common constants used across all tests."""
    observer = Observer.at_site('apo')
    start_time = Time('2025-07-06 19:00')  # UT
    end_time = Time('2025-07-07 19:00')  # UT
    half_night_start = Time('2025-07-07 02:00')  # UT
    half_night_end = Time('2025-07-07 08:00')  # UT
    return {
        'observer': observer,
        'start_time': start_time,
        'end_time': end_time,
        'half_night_start': half_night_start,
        'half_night_end': half_night_end
    }

class TestBBScheduler:


    def test_bbscheduler_with_priority(self):
        """Test that the BBScheduler can schedule blocks with priority."""
        constants = get_test_constants()
        
        # Create targets and blocks
        targets = [
            FixedTarget.from_name('Deneb'),
            FixedTarget.from_name('M13'),
            FixedTarget.from_name('Vega')
        ]
        
        configurations = [{'filter': 'B'}, {'filter': 'C'}, {'filter': 'R'}]
        blocks = []
        
        # Create blocks for each target
        for i, target in enumerate(targets):
            block = ObservingBlock(
                target, 
                5*u.minute, 
                priority=i+1,  # Different priorities
                configuration=configurations[i],
                constraints=None
            )
            blocks.append(block)
        
        # Create schedule and transitioner
        schedule = Schedule(constants['start_time'], constants['end_time'])
        transitioner = Transitioner(slew_rate=1*u.deg/u.second)
        
        scheduler_bbscheduler = BBScheduler(
            constraints=[],
            observer=constants['observer'],
            transitioner=transitioner,
            gap_time=5*u.minute,
            time_resolution=1*u.minute
        )

        scheduler_priority = PriorityScheduler(
            constraints=[],
            observer=constants['observer'],
            transitioner=transitioner,
            gap_time=5*u.minute,
            time_resolution=1*u.minute
        )

        # Schedule all blocks, not just one
        schedule_bbscheduler = scheduler_bbscheduler(blocks, schedule)
        schedule_priority = scheduler_priority(blocks, schedule)

        # Verify both schedules are the same
        assert schedule_bbscheduler == schedule_priority, "BBScheduler and PriorityScheduler should schedule the same blocks"
    
    """Test suite for the BBScheduler class."""
    def test_single_target_no_transitions(self):
        """Test that a schedule with a single target has no transition blocks."""
        constants = get_test_constants()
        
        # Create target and block
        target = FixedTarget.from_name('Deneb')
        duration = 5*u.minute
        priority = 1
        block = ObservingBlock(target, duration, priority, configuration={'filter': 'B'})
        
        # Create schedule and transitioner
        schedule = Schedule(constants['start_time'], constants['end_time'])
        transitioner = Transitioner(slew_rate=1*u.deg/u.second)
        
        # Create scheduler and run
        scheduler = BBScheduler(
            constraints=[],
            observer=constants['observer'],
            transitioner=transitioner,
            gap_time=5*u.minute,
            time_resolution=1*u.minute
        )
        
        # Run the scheduler
        schedule = scheduler([block], schedule)
        
        # Assert no transition blocks in schedule
        for block in schedule.scheduled_blocks:
            assert not isinstance(block, TransitionBlock), "Schedule should not contain transition blocks"
        assert len(schedule.scheduled_blocks) == 1, "Schedule should contain exactly one block for one target"
    
    def test_transition_insertion(self):
        """Test that correct transition blocks are inserted when necessary."""
        constants = get_test_constants()
        
        # Create targets and blocks
        targets = [
            FixedTarget.from_name('Deneb'),
            FixedTarget.from_name('M13'),
            FixedTarget.from_name('Vega')
        ]
        
        configurations = [{'filter': 'B'}, {'filter': 'C'}, {'filter': 'R'}]
        blocks = []
        
        # Create blocks for each target
        for i, target in enumerate(targets):
            block = ObservingBlock(
                target, 
                5*u.minute, 
                priority=i+1,  # Different priorities
                configuration=configurations[i],
                constraints=None
            )
            blocks.append(block)
        
        # Create schedule and transitioner
        schedule = Schedule(constants['start_time'], constants['end_time'])
        transitioner = Transitioner(slew_rate=1*u.deg/u.second)
        
        # Create scheduler and run
        scheduler = BBScheduler(
            constraints=[],
            observer=constants['observer'],
            transitioner=transitioner,
            gap_time=5*u.minute,
            time_resolution=1*u.minute
        )
        
        # Run the scheduler
        schedule = scheduler(blocks, schedule)
        
        # Create mapping from target name to configuration
        target_to_config = {targets[i].name: configurations[i] for i in range(len(targets))}
        
        # Check for transition blocks between observations
        has_transition = False
        for block in schedule.scheduled_blocks:
            if isinstance(block, TransitionBlock):
                has_transition = True
                
        assert has_transition, "Schedule should contain transition blocks between different targets"
        
        # Verify observation blocks have correct configurations
        for block in schedule.scheduled_blocks:
            if not isinstance(block, TransitionBlock):
                target_name = block.target.name
                expected_config = target_to_config[target_name]
                assert block.configuration == expected_config, f"Block for {target_name} has incorrect configuration"
    
    def test_unobservable_target(self):
        """Test scheduling an unobservable target."""
        constants = get_test_constants()
        
        # Create target and block with impossible constraint
        target = FixedTarget.from_name('Deneb')
        duration = 5*u.minute
        priority = 1
        
        constraints = [AltitudeConstraint(max=0*u.deg)]  # Impossible constraint
        
        block = ObservingBlock(
            target, 
            duration, 
            priority,
            configuration={'filter': 'B'},
            constraints=constraints
        )
        
        # Create schedule and transitioner
        schedule = Schedule(constants['start_time'], constants['end_time'])
        transitioner = Transitioner(slew_rate=1*u.deg/u.second)
        
        # Create scheduler and run
        scheduler = BBScheduler(
            constraints=constraints,
            observer=constants['observer'],
            transitioner=transitioner,
            gap_time=5*u.minute,
            time_resolution=1*u.minute
        )
        
        # Run the scheduler
        schedule = scheduler([block], schedule)
        
        # Assert no blocks were scheduled
        assert len(schedule.scheduled_blocks) == 0, "Schedule should contain no blocks for unobservable target"
        
    def test_half_night_schedule(self):
        """Test scheduling within a limited time window."""
        constants = get_test_constants()
        
        # Create targets and blocks
        targets = [
            FixedTarget.from_name('Deneb'),
            FixedTarget.from_name('M13'),
            FixedTarget.from_name('Vega')
        ]
        
        configurations = [{'filter': 'B'}, {'filter': 'C'}, {'filter': 'R'}]
        blocks = []
        
        # Create blocks for each target
        for i, target in enumerate(targets):
            block = ObservingBlock(
                target, 
                5*u.minute, 
                priority=i+1,
                configuration=configurations[i],
                constraints=None
            )
            blocks.append(block)
        
        # Create schedule with the half-night window
        schedule = Schedule(constants['half_night_start'], constants['half_night_end'])
        transitioner = Transitioner(slew_rate=1*u.deg/u.second)
        
        # Create scheduler with time constraint
        time_constraint = TimeConstraint(constants['half_night_start'], constants['half_night_end'])
        scheduler = BBScheduler(
            constraints=[time_constraint],
            observer=constants['observer'],
            transitioner=transitioner,
            gap_time=5*u.minute,
            time_resolution=1*u.minute
        )
        
        # Run the scheduler
        schedule = scheduler(blocks, schedule)
        
        # Verify blocks are within time window
        for block in schedule.scheduled_blocks:
            if not isinstance(block, TransitionBlock):
                assert block.start_time >= constants['half_night_start'], "Block starts before half night window"
                assert block.end_time <= constants['half_night_end'], "Block ends after half night window"
                
    def test_priority_ordering(self):
        """Test that blocks are scheduled in priority order."""
        constants = get_test_constants()
        
        # Create targets and blocks with different priorities
        targets = [
            FixedTarget.from_name('Deneb'),
            FixedTarget.from_name('M13'),
            FixedTarget.from_name('Vega')
        ]
        
        # Priorities (1 is highest)
        priorities = [3, 1, 2]  # M13 highest, then Vega, then Deneb
        blocks = []
        
        # Create blocks for each target with assigned priorities
        for i, target in enumerate(targets):
            block = ObservingBlock(
                target, 
                5*u.minute, 
                priority=priorities[i],
                configuration={'filter': 'B'}
            )
            blocks.append(block)
        
        # Create schedule and transitioner
        schedule = Schedule(constants['start_time'], constants['end_time'])
        transitioner = Transitioner(slew_rate=1*u.deg/u.second)
        
        # Create scheduler and run
        scheduler = BBScheduler(
            constraints=[],
            observer=constants['observer'],
            transitioner=transitioner,
            gap_time=5*u.minute,
            time_resolution=1*u.minute
        )
        
        # Run the scheduler
        schedule = scheduler(blocks, schedule)
        
        # Get scheduled observing blocks (not transition blocks)
        observation_blocks = [block for block in schedule.scheduled_blocks 
                             if not isinstance(block, TransitionBlock)]
        
        # First observation block should be M13 (priority 1)
        assert observation_blocks[0].target.name == 'M13', "First scheduled block should be the highest priority (M13)"
    
    def test_single_target_with_transitions(self):
        """
        Test that a schedule with a single target and multiple filters has no transition blocks.
        
        This test verifies that scheduling a single target with multiple filter configurations
        results in a schedule without transition blocks between exposures.
        """
        constants = get_test_constants()
        
        # Create target and blocks with different filters
        target = FixedTarget.from_name('Deneb')
        blocks = []
        
        # Create blocks with different filter configurations but the same target
        configurations = [{'filter': 'B'}, {'filter': 'C'}, {'filter': 'R'}]
        for i, config in enumerate(configurations):
            block = ObservingBlock(
                target, 
                5*u.minute, 
                priority=1,  # Same priority for all
                configuration=config
            )
            blocks.append(block)
        
        # Create schedule and transitioner
        schedule = Schedule(constants['start_time'], constants['end_time'])
        transitioner = Transitioner(slew_rate=1*u.deg/u.second)
        
        # Create scheduler and run
        scheduler = BBScheduler(
            constraints=[],
            observer=constants['observer'],
            transitioner=transitioner,
            gap_time=5*u.minute,
            time_resolution=1*u.minute
        )
        
        # Run the scheduler
        schedule = scheduler(blocks, schedule)
        
        # Assert no transition blocks in schedule
        for block in schedule.scheduled_blocks:
            assert not isinstance(block, TransitionBlock), "Schedule should not contain transition blocks"
            
        # Verify that all blocks were scheduled
        observation_blocks = [block for block in schedule.scheduled_blocks 
                             if not isinstance(block, TransitionBlock)]
        assert len(observation_blocks) == len(configurations), f"Expected {len(configurations)} blocks, got {len(observation_blocks)}"
    
    def test_single_target_with_exposure(self):
        """
        Test scheduling a single star with one filter for one exposure.
        
        This test verifies that scheduling a single target with one filter for one exposure
        results in exactly one observation block with no transition blocks.
        """
        constants = get_test_constants()
        
        # Create target and block
        target = FixedTarget.from_name('M31')
        block = ObservingBlock(
            target,
            5*u.minute,  # Duration for a single exposure
            priority=1,
            configuration={'filter': 'B'}  # Single filter
        )
        
        # Create schedule and transitioner
        schedule = Schedule(constants['start_time'], constants['end_time'])
        transitioner = Transitioner(slew_rate=1*u.deg/u.second)
        
        # Create scheduler and run
        scheduler = BBScheduler(
            constraints=[],
            observer=constants['observer'],
            transitioner=transitioner,
            gap_time=5*u.minute,
            time_resolution=1*u.minute
        )
        
        # Run the scheduler
        schedule = scheduler([block], schedule)
        
        # Assert no transition blocks in schedule
        for block in schedule.scheduled_blocks:
            assert not isinstance(block, TransitionBlock), "Schedule should not contain transition blocks"
            
        # Verify we have exactly one scheduled block (one exposure)
        assert len(schedule.scheduled_blocks) == 1, "Schedule should contain exactly one block for one exposure"
        
        # Verify the scheduled block has the correct configuration
        assert schedule.scheduled_blocks[0].configuration['filter'] == 'B', "Scheduled block should use filter B"
        assert schedule.scheduled_blocks[0].target.name == 'M31', "Scheduled block should target M31"


    def test_targets_rise_and_set(self):
        """
        Test behavior with targets that rise/set during the observation window.
        
        Verifies the scheduler can handle targets that become observable only during 
        part of the night - one rising midway, one setting midway.
        """
        constants = get_test_constants()
        
        # Create schedule for a full night
        schedule = Schedule(constants['start_time'], constants['end_time'])
        transitioner = Transitioner(slew_rate=1*u.deg/u.second)
        
        # Create targets - we'll use real astronomical objects that would have 
        # different rise/set times during the test night
        rising_target = FixedTarget.from_name('Antares')  # Rises later in night
        setting_target = FixedTarget.from_name('Arcturus')  # Sets earlier in night
        
        # Create blocks for the targets
        rising_block = ObservingBlock(
            rising_target,
            30*u.minute,
            priority=1,
            configuration={'filter': 'R'}
        )
        
        setting_block = ObservingBlock(
            setting_target,
            30*u.minute,
            priority=1,
            configuration={'filter': 'B'}
        )
        
        # Create scheduler with altitude constraints to ensure proper observability
        constraints = [AltitudeConstraint(min=30*u.deg)]
        scheduler = BBScheduler(
            constraints=constraints,
            observer=constants['observer'],
            transitioner=transitioner,
            gap_time=5*u.minute,
            time_resolution=1*u.minute
        )
        
        # Run the scheduler
        schedule = scheduler([rising_block, setting_block], schedule)
        
        # Get observation blocks (not transitions)
        observation_blocks = [block for block in schedule.scheduled_blocks 
                             if not isinstance(block, TransitionBlock)]
        
        # Verify both targets were scheduled
        target_names = [block.target.name for block in observation_blocks]
        assert 'Antares' in target_names, "Rising target (Antares) should be scheduled"
        assert 'Arcturus' in target_names, "Setting target (Arcturus) should be scheduled"
        
        # Get the scheduled times for each target
        rising_scheduled = None
        setting_scheduled = None
        
        for block in observation_blocks:
            if block.target.name == 'Antares':
                rising_scheduled = block
            elif block.target.name == 'Arcturus':
                setting_scheduled = block
        
        # Verify rising star is scheduled later in the night
        rising_time = constants['observer'].target_rise_time(
            constants['start_time'], rising_target, horizon=30*u.deg)
        assert rising_scheduled.start_time >= rising_time, "Rising target should be scheduled after its rise time"
        
        # Verify setting star is scheduled earlier in the night  
        setting_time = constants['observer'].target_set_time(
            constants['start_time'], setting_target, horizon=30*u.deg)
        assert setting_scheduled.end_time <= setting_time, "Setting target should be scheduled before its set time"
        
        # Verify the order of observations (setting star before rising star)
        if len(observation_blocks) >= 2:
            setting_index = target_names.index('Arcturus')
            rising_index = target_names.index('Antares')
            assert setting_index < rising_index, "Setting target should be scheduled before rising target"
            
    

    def test_targets_rise_and_set(self):
        """
        Test behavior with targets that rise/set during the observation window.
        
        Verifies the scheduler can handle targets that become observable only during 
        part of the night - one rising midway, one setting midway.
        """
        constants = get_test_constants()
        
        # Create schedule for a full night
        schedule = Schedule(constants['start_time'], constants['end_time'])
        transitioner = Transitioner(slew_rate=1*u.deg/u.second)
        
        # Create targets - we'll use real astronomical objects that would have 
        # different rise/set times during the test night
        rising_target = FixedTarget.from_name('Antares')  # Rises later in night
        setting_target = FixedTarget.from_name('Arcturus')  # Sets earlier in night
        
        # Create blocks for the targets
        rising_block = ObservingBlock(
            rising_target,
            30*u.minute,
            priority=1,
            configuration={'filter': 'R'}
        )
        
        setting_block = ObservingBlock(
            setting_target,
            30*u.minute,
            priority=1,
            configuration={'filter': 'B'}
        )
        
        # Create scheduler with altitude constraints to ensure proper observability
        constraints = [AltitudeConstraint(min=30*u.deg)]
        scheduler = BBScheduler(
            constraints=constraints,
            observer=constants['observer'],
            transitioner=transitioner,
            gap_time=5*u.minute,
            time_resolution=1*u.minute
        )
        
        # Run the scheduler
        schedule = scheduler([rising_block, setting_block], schedule)
        
        # Get observation blocks (not transitions)
        observation_blocks = [block for block in schedule.scheduled_blocks 
                             if not isinstance(block, TransitionBlock)]
        
        # Verify both targets were scheduled
        target_names = [block.target.name for block in observation_blocks]
        assert 'Antares' in target_names, "Rising target (Antares) should be scheduled"
        assert 'Arcturus' in target_names, "Setting target (Arcturus) should be scheduled"
        
        # Get the scheduled times for each target
        rising_scheduled = None
        setting_scheduled = None
        
        for block in observation_blocks:
            if block.target.name == 'Antares':
                rising_scheduled = block
            elif block.target.name == 'Arcturus':
                setting_scheduled = block
        
        # Verify rising star is scheduled later in the night
        rising_time = constants['observer'].target_rise_time(
            constants['start_time'], rising_target, horizon=30*u.deg)
        assert rising_scheduled.start_time >= rising_time, "Rising target should be scheduled after its rise time"
        
        # Verify setting star is scheduled earlier in the night  
        setting_time = constants['observer'].target_set_time(
            constants['start_time'], setting_target, horizon=30*u.deg)
        assert setting_scheduled.end_time <= setting_time, "Setting target should be scheduled before its set time"
        
        # Verify the order of observations (setting star before rising star)
        if len(observation_blocks) >= 2:
            setting_index = target_names.index('Arcturus')
            rising_index = target_names.index('Antares')
            assert setting_index < rising_index, "Setting target should be scheduled before rising target"
    
    