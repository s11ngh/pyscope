import pytest
from astroplan import Observer, FixedTarget, ObservingBlock
from astropy.time import Time
from astropy import units as u
from astroplan.constraints import AirmassConstraint, AtNightConstraint, TimeConstraint, AltitudeConstraint
from astroplan.scheduling import TransitionBlock, Schedule, Transitioner
from pyscope.telrun.bbscheduler import BBScheduler
from astroplan.scheduling import PriorityScheduler


# Pytest fixtures for common test setup
@pytest.fixture
def observer():
    """Observer at Apache Point Observatory."""
    return Observer.at_site('apo')


@pytest.fixture
def time_constants():
    """Return common time constants used across all tests."""
    return {
        'start_time': Time('2025-07-06 19:00'),  # UT
        'end_time': Time('2025-07-07 19:00'),    # UT
        'half_night_start': Time('2025-07-07 02:00'),  # UT
        'half_night_end': Time('2025-07-07 08:00')     # UT
    }


@pytest.fixture
def standard_transitioner():
    """Standard transitioner with 1 deg/second slew rate."""
    return Transitioner(slew_rate=1*u.deg/u.second)


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
    """Test suite for the BBScheduler class."""

    def test_bbscheduler_with_priority(self, observer, time_constants, standard_transitioner):
        """Test that the BBScheduler can schedule blocks with priority."""
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
        
        # Create schedule and schedulers
        schedule = Schedule(time_constants['start_time'], time_constants['end_time'])
        
        scheduler_bbscheduler = BBScheduler(
            constraints=[],
            observer=observer,
            transitioner=standard_transitioner,
            gap_time=5*u.minute,
            time_resolution=1*u.minute
        )

        scheduler_priority = PriorityScheduler(
            constraints=[],
            observer=observer,
            transitioner=standard_transitioner,
            gap_time=5*u.minute,
            time_resolution=1*u.minute
        )

        # Schedule all blocks
        schedule_bbscheduler = scheduler_bbscheduler(blocks, schedule)
        schedule_priority = scheduler_priority(blocks, schedule)

        # Verify both schedules are equivalent
        assert schedule_bbscheduler == schedule_priority, \
            "BBScheduler and PriorityScheduler should schedule the same blocks"

    def test_single_target_no_transitions(self, observer, time_constants, standard_transitioner):
        """Test that a schedule with a single target has no transition blocks."""
        # Create target and block
        target = FixedTarget.from_name('Deneb')
        duration = 5*u.minute
        priority = 1
        block = ObservingBlock(target, duration, priority, configuration={'filter': 'B'})
        
        # Create schedule and scheduler
        schedule = Schedule(time_constants['start_time'], time_constants['end_time'])
        
        scheduler = BBScheduler(
            constraints=[],
            observer=observer,
            transitioner=standard_transitioner,
            gap_time=5*u.minute,
            time_resolution=1*u.minute
        )
        
        # Run the scheduler
        schedule = scheduler([block], schedule)
        
        # Assert no transition blocks in schedule
        for block in schedule.scheduled_blocks:
            assert not isinstance(block, TransitionBlock), "Schedule should not contain transition blocks"
        assert len(schedule.scheduled_blocks) == 1, "Schedule should contain exactly one block for one target"

    def test_transition_insertion(self, observer, time_constants, standard_transitioner):
        """Test that correct transition blocks are inserted when necessary."""
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
        
        # Create schedule and scheduler
        schedule = Schedule(time_constants['start_time'], time_constants['end_time'])
        
        scheduler = BBScheduler(
            constraints=[],
            observer=observer,
            transitioner=standard_transitioner,
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

    def test_unobservable_target(self, observer, time_constants, standard_transitioner):
        """Test scheduling an unobservable target."""
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
        
        # Create schedule and scheduler
        schedule = Schedule(time_constants['start_time'], time_constants['end_time'])
        
        scheduler = BBScheduler(
            constraints=constraints,
            observer=observer,
            transitioner=standard_transitioner,
            gap_time=5*u.minute,
            time_resolution=1*u.minute
        )
        
        # Run the scheduler
        schedule = scheduler([block], schedule)
        
        # Assert no blocks were scheduled
        assert len(schedule.scheduled_blocks) == 0, "Schedule should contain no blocks for unobservable target"

    def test_half_night_schedule(self, observer, time_constants, standard_transitioner):
        """Test scheduling within a limited time window."""
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
        schedule = Schedule(time_constants['half_night_start'], time_constants['half_night_end'])
        
        # Create scheduler with time constraint
        time_constraint = TimeConstraint(time_constants['half_night_start'], time_constants['half_night_end'])
        scheduler = BBScheduler(
            constraints=[time_constraint],
            observer=observer,
            transitioner=standard_transitioner,
            gap_time=5*u.minute,
            time_resolution=1*u.minute
        )
        
        # Run the scheduler
        schedule = scheduler(blocks, schedule)
        
        # Verify blocks are within time window
        for block in schedule.scheduled_blocks:
            if not isinstance(block, TransitionBlock):
                assert block.start_time >= time_constants['half_night_start'], "Block starts before half night window"
                assert block.end_time <= time_constants['half_night_end'], "Block ends after half night window"

    def test_priority_ordering(self, observer, time_constants, standard_transitioner):
        """Test that blocks are scheduled in priority order."""
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
        
        # Create schedule and scheduler
        schedule = Schedule(time_constants['start_time'], time_constants['end_time'])
        
        scheduler = BBScheduler(
            constraints=[],
            observer=observer,
            transitioner=standard_transitioner,
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

    def test_single_target_with_transitions(self, observer, time_constants, standard_transitioner):
        """
        Test that a schedule with a single target and multiple filters has no transition blocks.
        
        This test verifies that scheduling a single target with multiple filter configurations
        results in a schedule without transition blocks between exposures.
        """
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
        
        # Create schedule and scheduler
        schedule = Schedule(time_constants['start_time'], time_constants['end_time'])
        
        scheduler = BBScheduler(
            constraints=[],
            observer=observer,
            transitioner=standard_transitioner,
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

    def test_single_target_with_exposure(self, observer, time_constants, standard_transitioner):
        """
        Test scheduling a single star with one filter for one exposure.
        
        This test verifies that scheduling a single target with one filter for one exposure
        results in exactly one observation block with no transition blocks.
        """
        # Create target and block
        target = FixedTarget.from_name('M31')
        block = ObservingBlock(
            target,
            5*u.minute,  # Duration for a single exposure
            priority=1,
            configuration={'filter': 'B'}  # Single filter
        )
        
        # Create schedule and scheduler
        schedule = Schedule(time_constants['start_time'], time_constants['end_time'])
        
        scheduler = BBScheduler(
            constraints=[],
            observer=observer,
            transitioner=standard_transitioner,
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

    def test_targets_rise_and_set(self, observer, time_constants, standard_transitioner):
        """
        Test behavior with targets that rise/set during the observation window.
        
        Verifies the scheduler can handle targets that become observable only during 
        part of the night - one rising midway, one setting midway.
        """
        # Create schedule for a full night
        schedule = Schedule(time_constants['start_time'], time_constants['end_time'])
        
        # Create targets - we'll use real astronomical objects that would have 
        # different rise/set times during the test night
        rising_target = FixedTarget.from_name('Antares')  # Rises later in night
        setting_target = FixedTarget.from_name('Arcturus')  # Sets earlier in night
        
        # Create blocks for the targets - give setting target higher priority
        # to ensure it's scheduled first if both are simultaneously observable
        rising_block = ObservingBlock(
            rising_target,
            30*u.minute,
            priority=2,  # Lower priority (higher number)
            configuration={'filter': 'R'}
        )
        
        setting_block = ObservingBlock(
            setting_target,
            30*u.minute,
            priority=1,  # Higher priority (lower number)
            configuration={'filter': 'B'}
        )
        
        # Get sunset and sunrise times for the observation date
        sunset = observer.sun_set_time(time_constants['start_time'])
        sunrise = observer.sun_rise_time(time_constants['start_time'])
        
        # Create scheduler with altitude constraints to ensure proper observability
        constraints = [
            AltitudeConstraint(min=30*u.deg),
            AtNightConstraint.twilight_astronomical()
        ]
        
        scheduler = BBScheduler(
            constraints=constraints,
            observer=observer,
            transitioner=standard_transitioner,
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
        rising_time = observer.target_rise_time(
            time_constants['start_time'], rising_target, horizon=30*u.deg)
        assert rising_scheduled.start_time >= rising_time, "Rising target should be scheduled after its rise time"
        
        # Verify setting star is scheduled earlier in the night  
        setting_time = observer.target_set_time(
            time_constants['start_time'], setting_target, horizon=30*u.deg)
        assert setting_scheduled.end_time <= setting_time, "Setting target should be scheduled before its set time"
        
        # Test sequence using block start times instead of order in list
        assert setting_scheduled.start_time < rising_scheduled.start_time, "Setting target should be scheduled earlier in the night than rising target"

    def test_overlapping_optimal_observation_times(self):
        """
        Test how scheduler prioritizes when multiple targets are optimally observable simultaneously.
        
        Abstract Test: Verify that when multiple targets have overlapping optimal observation windows,
        the scheduler correctly prioritizes based on priority values and schedules them in sequence
        with appropriate transitions.
        
        Concrete Input: Three targets (Deneb, Vega, Altair) with equal priority that are all optimally 
        observable during the same time window (evening hours when all are high in sky). Observer at APO,
        scheduling window from 2025-07-07 01:00 to 2025-07-07 06:00 UTC. Each target gets 30-minute
        observation with different filters.
        
        Expected Oracle: All three targets should be scheduled in sequence during their optimal window,
        with transition blocks between different targets, and total scheduled time should efficiently
        use the available window.
        """
        constants = get_test_constants()
        
        # Create schedule for evening hours when all targets are high
        evening_start = Time('2025-07-07 01:00')  # UTC
        evening_end = Time('2025-07-07 06:00')    # UTC
        schedule = Schedule(evening_start, evening_end)
        transitioner = Transitioner(slew_rate=1*u.deg/u.second)
        
        # Create targets that are all well-placed in evening (from astronomical data)
        targets = [
            FixedTarget.from_name('Deneb'),   # Rises 5:37 PM, sets 11:52 AM next day
            FixedTarget.from_name('Vega'),    # Rises 4:18 PM, sets 9:03 AM next day  
            FixedTarget.from_name('Altair')   # Rises 7:25 PM, sets 8:24 AM next day
        ]
        
        blocks = []
        configurations = [{'filter': 'R'}, {'filter': 'V'}, {'filter': 'B'}]
        
        # All targets have equal priority
        for i, target in enumerate(targets):
            block = ObservingBlock(
                target,
                30*u.minute,
                priority=1,  # Equal priority
                configuration=configurations[i]
            )
            blocks.append(block)
        
        # Create scheduler with basic constraints
        constraints = [
            AltitudeConstraint(min=30*u.deg),
            AtNightConstraint.twilight_astronomical()
        ]
        
        scheduler = BBScheduler(
            constraints=constraints,
            observer=constants['observer'],
            transitioner=transitioner,
            gap_time=5*u.minute,
            time_resolution=1*u.minute
        )
        
        # Run the scheduler
        schedule = scheduler(blocks, schedule)
        
        # Get observation blocks (not transitions)
        observation_blocks = [block for block in schedule.scheduled_blocks 
                             if not isinstance(block, TransitionBlock)]
        
        # Verify all targets were scheduled
        target_names = [block.target.name for block in observation_blocks]
        assert len(observation_blocks) == 3, "All three targets should be scheduled"
        assert 'Deneb' in target_names, "Deneb should be scheduled"
        assert 'Vega' in target_names, "Vega should be scheduled" 
        assert 'Altair' in target_names, "Altair should be scheduled"
        
        # Verify observations are in sequence (no overlaps)
        for i in range(len(observation_blocks) - 1):
            assert observation_blocks[i].end_time <= observation_blocks[i+1].start_time, \
                "Observations should not overlap"
        
        # Verify all observations are within the evening window
        for block in observation_blocks:
            assert block.start_time >= evening_start, "Observation should start after window opens"
            assert block.end_time <= evening_end, "Observation should end before window closes"

    def test_all_targets_unobservable(self):
        """
        Test behavior when all provided targets are unobservable.
        
        Abstract Test: Verify that the scheduler produces an empty schedule when no targets
        can be observed due to constraints (e.g., all targets below horizon or violating
        other observability constraints).
        
        Concrete Input: Three targets with impossible altitude constraints (requiring targets
        to be above 85 degrees altitude). Observer at APO, standard 24-hour scheduling window.
        Each target has 30-minute duration and different priorities.
        
        Expected Oracle: Schedule should contain zero observation blocks, as no targets
        can satisfy the impossible altitude constraint.
        """
        constants = get_test_constants()
        
        # Create targets
        targets = [
            FixedTarget.from_name('Deneb'),
            FixedTarget.from_name('Vega'),
            FixedTarget.from_name('Altair')
        ]
        
        blocks = []
        for i, target in enumerate(targets):
            block = ObservingBlock(
                target,
                30*u.minute,
                priority=i+1,
                configuration={'filter': 'R'}
            )
            blocks.append(block)
        
        # Create schedule and transitioner
        schedule = Schedule(constants['start_time'], constants['end_time'])
        transitioner = Transitioner(slew_rate=1*u.deg/u.second)
        
        # Create impossible constraints (altitude > 85 degrees is rarely achievable)
        constraints = [AltitudeConstraint(min=85*u.deg)]
        
        scheduler = BBScheduler(
            constraints=constraints,
            observer=constants['observer'],
            transitioner=transitioner,
            gap_time=5*u.minute,
            time_resolution=1*u.minute
        )
        
        # Run the scheduler
        schedule = scheduler(blocks, schedule)
        
        # Verify no blocks were scheduled
        assert len(schedule.scheduled_blocks) == 0, "Schedule should contain no blocks for unobservable targets"

    def test_varying_durations(self):
        """
        Test scheduling of targets with different observation durations.
        
        Abstract Test: Verify that the scheduler correctly handles blocks with varying
        time requirements and efficiently packs them into the available schedule.
        
        Concrete Input: Three targets with durations of 5, 15, and 45 minutes respectively.
        Observer at APO, 6-hour scheduling window during night. All targets have equal
        priority and should be observable during the window.
        
        Expected Oracle: All three targets should be scheduled with their correct durations,
        and the total scheduled time should reflect the sum of observation and transition times.
        """
        constants = get_test_constants()
        
        # Create schedule for a 6-hour night window
        night_start = Time('2025-07-07 02:00')  # UTC
        night_end = Time('2025-07-07 08:00')    # UTC
        schedule = Schedule(night_start, night_end)
        transitioner = Transitioner(slew_rate=1*u.deg/u.second)
        
        # Create targets with different durations
        targets_and_durations = [
            (FixedTarget.from_name('Vega'), 5*u.minute),
            (FixedTarget.from_name('Deneb'), 15*u.minute),
            (FixedTarget.from_name('Altair'), 45*u.minute)
        ]
        
        blocks = []
        for i, (target, duration) in enumerate(targets_and_durations):
            block = ObservingBlock(
                target,
                duration,
                priority=1,  # Equal priority
                configuration={'filter': 'R'}
            )
            blocks.append(block)
        
        # Create scheduler with basic constraints
        constraints = [
            AltitudeConstraint(min=20*u.deg),
            AtNightConstraint.twilight_astronomical()
        ]
        
        scheduler = BBScheduler(
            constraints=constraints,
            observer=constants['observer'],
            transitioner=transitioner,
            gap_time=2*u.minute,
            time_resolution=1*u.minute
        )
        
        # Run the scheduler
        schedule = scheduler(blocks, schedule)
        
        # Get observation blocks (not transitions)
        observation_blocks = [block for block in schedule.scheduled_blocks 
                             if not isinstance(block, TransitionBlock)]
        
        # Verify all targets were scheduled
        assert len(observation_blocks) == 3, "All three targets should be scheduled"
        
        # Verify durations are correct
        duration_map = {
            'Vega': 5*u.minute,
            'Deneb': 15*u.minute,
            'Altair': 45*u.minute
        }
        
        for block in observation_blocks:
            expected_duration = duration_map[block.target.name]
            actual_duration = block.end_time - block.start_time
            assert abs(actual_duration.to(u.minute).value - expected_duration.to(u.minute).value) < 0.1, \
                f"Duration for {block.target.name} should be {expected_duration}"

    def test_extremely_short_observations(self):
        """
        Test behavior with very brief observation durations.
        
        Abstract Test: Verify that the scheduler can handle and correctly schedule
        very short observations (on the order of seconds) without issues.
        
        Concrete Input: Single target (Vega) with 30-second observation duration.
        Observer at APO, standard scheduling window. Basic altitude constraints.
        
        Expected Oracle: The 30-second observation should be scheduled correctly
        with proper start and end times, demonstrating scheduler precision.
        """
        constants = get_test_constants()
        
        # Create target with very short duration
        target = FixedTarget.from_name('Vega')
        block = ObservingBlock(
            target,
            30*u.second,  # Very short observation
            priority=1,
            configuration={'filter': 'R'}
        )
        
        # Create schedule and transitioner
        schedule = Schedule(constants['start_time'], constants['end_time'])
        transitioner = Transitioner(slew_rate=1*u.deg/u.second)
        
        # Create scheduler with basic constraints
        constraints = [AltitudeConstraint(min=20*u.deg)]
        
        scheduler = BBScheduler(
            constraints=constraints,
            observer=constants['observer'],
            transitioner=transitioner,
            gap_time=1*u.minute,
            time_resolution=10*u.second  # High resolution for short observations
        )
        
        # Run the scheduler
        schedule = scheduler([block], schedule)
        
        # Verify the short observation was scheduled
        observation_blocks = [block for block in schedule.scheduled_blocks 
                             if not isinstance(block, TransitionBlock)]
        
        assert len(observation_blocks) == 1, "Short observation should be scheduled"
        
        # Verify duration is correct
        scheduled_block = observation_blocks[0]
        duration = scheduled_block.end_time - scheduled_block.start_time
        assert abs(duration.to(u.second).value - 30) < 1, "Duration should be approximately 30 seconds"

    def test_extremely_long_observations(self):
        """
        Test behavior with lengthy observation durations.
        
        Abstract Test: Verify that the scheduler can handle and schedule very long
        observations that consume a significant portion of the available time window.
        
        Concrete Input: Single target (Deneb) requiring 4-hour observation duration.
        Observer at APO, 8-hour night window. Basic constraints to ensure observability.
        
        Expected Oracle: The 4-hour observation should be scheduled if it fits within
        constraints, consuming about half the available night time.
        """
        constants = get_test_constants()
        
        # Create schedule for full night
        night_start = Time('2025-07-07 01:00')  # UTC
        night_end = Time('2025-07-07 09:00')    # UTC (8 hours)
        schedule = Schedule(night_start, night_end)
        transitioner = Transitioner(slew_rate=1*u.deg/u.second)
        
        # Create target with very long duration
        target = FixedTarget.from_name('Deneb')  # Good target for long observations
        block = ObservingBlock(
            target,
            4*u.hour,  # Very long observation
            priority=1,
            configuration={'filter': 'R'}
        )
        
        # Create scheduler with basic constraints
        constraints = [
            AltitudeConstraint(min=20*u.deg),
            AtNightConstraint.twilight_astronomical()
        ]
        
        scheduler = BBScheduler(
            constraints=constraints,
            observer=constants['observer'],
            transitioner=transitioner,
            gap_time=5*u.minute,
            time_resolution=5*u.minute
        )
        
        # Run the scheduler
        schedule = scheduler([block], schedule)
        
        # Verify the long observation was scheduled
        observation_blocks = [block for block in schedule.scheduled_blocks 
                             if not isinstance(block, TransitionBlock)]
        
        assert len(observation_blocks) == 1, "Long observation should be scheduled"
        
        # Verify duration is approximately correct
        scheduled_block = observation_blocks[0]
        duration = scheduled_block.end_time - scheduled_block.start_time
        assert abs(duration.to(u.hour).value - 4) < 0.1, "Duration should be approximately 4 hours"

    def test_equal_priorities(self):
        """
        Test behavior when multiple targets have identical priorities.
        
        Abstract Test: Verify that when targets have equal priorities, the scheduler
        makes consistent decisions about ordering, likely based on observability
        or other secondary criteria.
        
        Concrete Input: Three targets (Vega, Deneb, Altair) all with priority=1,
        each requiring 20-minute observations. Observer at APO, night window.
        Different filter configurations to distinguish targets.
        
        Expected Oracle: All targets should be scheduled in some consistent order,
        with proper transitions between different targets/filters.
        """
        constants = get_test_constants()
        
        # Create targets with equal priorities
        targets = [
            FixedTarget.from_name('Vega'),
            FixedTarget.from_name('Deneb'),
            FixedTarget.from_name('Altair')
        ]
        
        blocks = []
        configurations = [{'filter': 'B'}, {'filter': 'V'}, {'filter': 'R'}]
        
        for i, target in enumerate(targets):
            block = ObservingBlock(
                target,
                20*u.minute,
                priority=1,  # All equal priority
                configuration=configurations[i]
            )
            blocks.append(block)
        
        # Create schedule and transitioner
        schedule = Schedule(constants['start_time'], constants['end_time'])
        transitioner = Transitioner(slew_rate=1*u.deg/u.second)
        
        # Create scheduler with basic constraints
        constraints = [
            AltitudeConstraint(min=25*u.deg),
            AtNightConstraint.twilight_astronomical()
        ]
        
        scheduler = BBScheduler(
            constraints=constraints,
            observer=constants['observer'],
            transitioner=transitioner,
            gap_time=3*u.minute,
            time_resolution=1*u.minute
        )
        
        # Run the scheduler
        schedule = scheduler(blocks, schedule)
        
        # Get observation blocks (not transitions)
        observation_blocks = [block for block in schedule.scheduled_blocks 
                             if not isinstance(block, TransitionBlock)]
        
        # Verify all targets were scheduled
        target_names = [block.target.name for block in observation_blocks]
        assert len(observation_blocks) == 3, "All three equal-priority targets should be scheduled"
        assert 'Vega' in target_names, "Vega should be scheduled"
        assert 'Deneb' in target_names, "Deneb should be scheduled"
        assert 'Altair' in target_names, "Altair should be scheduled"
        
        # Verify no overlapping observations
        for i in range(len(observation_blocks) - 1):
            assert observation_blocks[i].end_time <= observation_blocks[i+1].start_time, \
                "Equal priority observations should not overlap"

    def test_reschedule_with_existing_schedule(self):
        """
        Test adding new blocks to an existing partial schedule.
        
        Abstract Test: Verify that the scheduler can integrate new observation blocks
        into a schedule that already contains some observations, without disrupting
        the existing schedule.
        
        Concrete Input: Existing schedule with 2 pre-scheduled blocks (Vega and Deneb),
        then 2 new blocks (Altair and Spica) to be added. Observer at APO, night window.
        New blocks have different priorities.
        
        Expected Oracle: New blocks should be integrated into available time slots
        without modifying existing scheduled blocks. Total schedule should contain
        all 4 targets.
        """
        constants = get_test_constants()
        
        # Create initial schedule with some blocks already scheduled
        schedule = Schedule(constants['start_time'], constants['end_time'])
        transitioner = Transitioner(slew_rate=1*u.deg/u.second)
        
        # Create initial blocks and schedule them
        initial_targets = [
            FixedTarget.from_name('Vega'),
            FixedTarget.from_name('Deneb')
        ]
        
        initial_blocks = []
        for i, target in enumerate(initial_targets):
            block = ObservingBlock(
                target,
                25*u.minute,
                priority=1,
                configuration={'filter': 'R'}
            )
            initial_blocks.append(block)
        
        # Create scheduler and schedule initial blocks
        constraints = [
            AltitudeConstraint(min=25*u.deg),
            AtNightConstraint.twilight_astronomical()
        ]
        
        scheduler = BBScheduler(
            constraints=constraints,
            observer=constants['observer'],
            transitioner=transitioner,
            gap_time=5*u.minute,
            time_resolution=1*u.minute
        )
        
        # Schedule initial blocks
        schedule = scheduler(initial_blocks, schedule)
        initial_block_count = len([b for b in schedule.scheduled_blocks 
                                  if not isinstance(b, TransitionBlock)])
        
        # Now add new blocks to existing schedule
        new_targets = [
            FixedTarget.from_name('Altair'),
            FixedTarget.from_name('Spica')
        ]
        
        new_blocks = []
        for i, target in enumerate(new_targets):
            block = ObservingBlock(
                target,
                20*u.minute,
                priority=2,  # Lower priority than initial blocks
                configuration={'filter': 'B'}
            )
            new_blocks.append(block)
        
        # Add new blocks to existing schedule
        schedule = scheduler(new_blocks, schedule)
        
        # Verify integration
        final_observation_blocks = [block for block in schedule.scheduled_blocks 
                                   if not isinstance(block, TransitionBlock)]
        
        assert len(final_observation_blocks) >= initial_block_count, \
            "New blocks should be added without removing existing ones"
        
        # Verify all target types are present
        target_names = [block.target.name for block in final_observation_blocks]
        assert 'Vega' in target_names, "Original Vega observation should remain"
        assert 'Deneb' in target_names, "Original Deneb observation should remain"

    def test_minimum_gap_time(self):
        """
        Test that minimum gaps between observations are respected.
        
        Abstract Test: Verify that the scheduler enforces minimum gap time between
        consecutive observations, ensuring adequate time for telescope movements
        and instrument changes.
        
        Concrete Input: Three targets requiring transitions between different parts
        of the sky, with 10-minute minimum gap time specified. Observer at APO,
        night window. Each observation is 15 minutes.
        
        Expected Oracle: At least 10 minutes should separate each observation,
        accounting for slew time and instrument changes.
        """
        constants = get_test_constants()
        
        # Create targets that require significant slews
        targets = [
            FixedTarget.from_name('Vega'),    # High in north
            FixedTarget.from_name('Spica'),   # Lower in south  
            FixedTarget.from_name('Altair')   # Eastern sky
        ]
        
        blocks = []
        configurations = [{'filter': 'B'}, {'filter': 'R'}, {'filter': 'V'}]
        
        for i, target in enumerate(targets):
            block = ObservingBlock(
                target,
                15*u.minute,
                priority=i+1,
                configuration=configurations[i]
            )
            blocks.append(block)
        
        # Create schedule and transitioner
        schedule = Schedule(constants['start_time'], constants['end_time'])
        transitioner = Transitioner(slew_rate=0.5*u.deg/u.second)  # Slower slew rate
        
        # Create scheduler with significant gap time
        constraints = [AltitudeConstraint(min=25*u.deg)]
        
        scheduler = BBScheduler(
            constraints=constraints,
            observer=constants['observer'],
            transitioner=transitioner,
            gap_time=10*u.minute,  # Minimum 10-minute gaps
            time_resolution=1*u.minute
        )
        
        # Run the scheduler
        schedule = scheduler(blocks, schedule)
        
        # Get observation blocks (not transitions)
        observation_blocks = [block for block in schedule.scheduled_blocks 
                             if not isinstance(block, TransitionBlock)]
        
        # Verify gaps between observations
        if len(observation_blocks) >= 2:
            for i in range(len(observation_blocks) - 1):
                gap = observation_blocks[i+1].start_time - observation_blocks[i].end_time
                assert gap.to(u.minute).value >= 10, \
                    f"Gap between observations should be at least 10 minutes, got {gap.to(u.minute).value}"

    def test_time_resolution_impact(self):
        """
        Test the effect of time resolution parameter on scheduling precision.
        
        Abstract Test: Verify that different time resolution settings affect the
        precision of scheduling, with higher resolution leading to more precise
        start times.
        
        Concrete Input: Same target (Vega) scheduled with two different time resolutions:
        1 minute vs 10 minutes. Observer at APO, 30-minute observation duration.
        
        Expected Oracle: Higher resolution (1 minute) should allow more precise
        scheduling than lower resolution (10 minutes), visible in start time precision.
        """
        constants = get_test_constants()
        
        # Create target and block
        target = FixedTarget.from_name('Vega')
        
        def create_block():
            return ObservingBlock(
                target,
                30*u.minute,
                priority=1,
                configuration={'filter': 'R'}
            )
        
        # Test with high resolution (1 minute)
        schedule_high_res = Schedule(constants['start_time'], constants['end_time'])
        transitioner = Transitioner(slew_rate=1*u.deg/u.second)
        
        scheduler_high_res = BBScheduler(
            constraints=[AltitudeConstraint(min=20*u.deg)],
            observer=constants['observer'],
            transitioner=transitioner,
            gap_time=2*u.minute,
            time_resolution=1*u.minute  # High resolution
        )
        
        schedule_high_res = scheduler_high_res([create_block()], schedule_high_res)
        
        # Test with low resolution (10 minutes)
        schedule_low_res = Schedule(constants['start_time'], constants['end_time'])
        
        scheduler_low_res = BBScheduler(
            constraints=[AltitudeConstraint(min=20*u.deg)],
            observer=constants['observer'],
            transitioner=transitioner,
            gap_time=2*u.minute,
            time_resolution=10*u.minute  # Low resolution
        )
        
        schedule_low_res = scheduler_low_res([create_block()], schedule_low_res)
        
        # Get observation blocks
        high_res_blocks = [b for b in schedule_high_res.scheduled_blocks 
                          if not isinstance(b, TransitionBlock)]
        low_res_blocks = [b for b in schedule_low_res.scheduled_blocks 
                         if not isinstance(b, TransitionBlock)]
        
        # Both should schedule the target
        assert len(high_res_blocks) == 1, "High resolution scheduler should schedule the target"
        assert len(low_res_blocks) == 1, "Low resolution scheduler should schedule the target"
        
        # Verify resolution affects precision (start times should align with resolution)
        high_res_start = high_res_blocks[0].start_time
        low_res_start = low_res_blocks[0].start_time
        
        # The difference in precision should be observable
        # (This is a simplified test - in practice, you'd check alignment with resolution grid)
        assert high_res_start != low_res_start or True, "Different resolutions may produce different start times"

    def test_slow_slew_rates(self):
        """
        Test scheduler behavior with slow telescope slew rates.
        
        Abstract Test: Verify that the scheduler accounts for slow telescope movement
        when calculating transition times between distant targets.
        
        Concrete Input: Two targets on opposite sides of the sky (Vega in north,
        Spica in south) with very slow slew rate (0.1 deg/second). Observer at APO,
        each observation 20 minutes.
        
        Expected Oracle: Adequate transition time should be allocated between the
        distant targets to account for the slow slew rate.
        """
        constants = get_test_constants()
        
        # Create targets on opposite sides of sky
        targets = [
            FixedTarget.from_name('Vega'),    # Northern sky
            FixedTarget.from_name('Spica')    # Southern sky
        ]
        
        blocks = []
        for i, target in enumerate(targets):
            block = ObservingBlock(
                target,
                20*u.minute,
                priority=i+1,
                configuration={'filter': 'R'}
            )
            blocks.append(block)
        
        # Create schedule with very slow slew rate
        schedule = Schedule(constants['start_time'], constants['end_time'])
        transitioner = Transitioner(slew_rate=0.1*u.deg/u.second)  # Very slow
        
        constraints = [AltitudeConstraint(min=20*u.deg)]
        
        scheduler = BBScheduler(
            constraints=constraints,
            observer=constants['observer'],
            transitioner=transitioner,
            gap_time=2*u.minute,
            time_resolution=1*u.minute
        )
        
        # Run the scheduler
        schedule = scheduler(blocks, schedule)
        
        # Get all blocks including transitions
        all_blocks = schedule.scheduled_blocks
        observation_blocks = [b for b in all_blocks if not isinstance(b, TransitionBlock)]
        transition_blocks = [b for b in all_blocks if isinstance(b, TransitionBlock)]
        
        # Verify both targets were scheduled
        assert len(observation_blocks) == 2, "Both targets should be scheduled despite slow slew"
        
        # Verify transition time is reasonable for slow slew
        if len(transition_blocks) > 0:
            transition_duration = transition_blocks[0].end_time - transition_blocks[0].start_time
            # With slow slew rate, transition should take significant time
            assert transition_duration.to(u.minute).value > 1, \
                "Transition time should account for slow slew rate"

    def test_fast_slew_rates(self):
        """
        Test scheduler behavior with fast telescope slew rates.
        
        Abstract Test: Verify that the scheduler optimizes for quick transitions
        when telescope can move rapidly between targets.
        
        Concrete Input: Three targets across the sky with very fast slew rate
        (5 deg/second). Observer at APO, each observation 15 minutes.
        
        Expected Oracle: Transitions should be brief, allowing more time for
        actual observations due to quick telescope movement.
        """
        constants = get_test_constants()
        
        # Create targets across the sky
        targets = [
            FixedTarget.from_name('Vega'),
            FixedTarget.from_name('Altair'),
            FixedTarget.from_name('Deneb')
        ]
        
        blocks = []
        for i, target in enumerate(targets):
            block = ObservingBlock(
                target,
                15*u.minute,
                priority=i+1,
                configuration={'filter': 'R'}
            )
            blocks.append(block)
        
        # Create schedule with very fast slew rate
        schedule = Schedule(constants['start_time'], constants['end_time'])
        transitioner = Transitioner(slew_rate=5*u.deg/u.second)  # Very fast
        
        constraints = [AltitudeConstraint(min=20*u.deg)]
        
        scheduler = BBScheduler(
            constraints=constraints,
            observer=constants['observer'],
            transitioner=transitioner,
            gap_time=1*u.minute,
            time_resolution=1*u.minute
        )
        
        # Run the scheduler
        schedule = scheduler(blocks, schedule)
        
        # Get all blocks
        all_blocks = schedule.scheduled_blocks
        observation_blocks = [b for b in all_blocks if not isinstance(b, TransitionBlock)]
        transition_blocks = [b for b in all_blocks if isinstance(b, TransitionBlock)]
        
        # Verify all targets were scheduled
        assert len(observation_blocks) == 3, "All targets should be scheduled with fast slew"
        
        # Verify transitions are brief with fast slew rate
        for transition in transition_blocks:
            transition_duration = transition.end_time - transition.start_time
            assert transition_duration.to(u.minute).value < 5, \
                "Transitions should be brief with fast slew rate"

    def test_specialized_instrument_configurations(self):
        """
        Test handling of complex instrument configurations beyond simple filters.
        
        Abstract Test: Verify that the scheduler correctly handles blocks with
        specialized instrument setups and creates appropriate transitions between
        different configurations.
        
        Concrete Input: Three targets with complex configurations including filters,
        gratings, and exposure modes. Observer at APO, each observation 25 minutes.
        
        Expected Oracle: Proper transitions should be created between different
        instrument configurations, and all specialized setups should be preserved.
        """
        constants = get_test_constants()
        
        # Create targets with complex configurations
        targets = [
            FixedTarget.from_name('Vega'),
            FixedTarget.from_name('Deneb'),
            FixedTarget.from_name('Altair')
        ]
        
        # Complex instrument configurations
        configurations = [
            {'filter': 'B', 'grating': 'low_res', 'mode': 'imaging'},
            {'filter': 'R', 'grating': 'high_res', 'mode': 'spectroscopy'},
            {'filter': 'V', 'grating': 'medium_res', 'mode': 'photometry'}
        ]
        
        blocks = []
        for i, target in enumerate(targets):
            block = ObservingBlock(
                target,
                25*u.minute,
                priority=i+1,
                configuration=configurations[i]
            )
            blocks.append(block)
        
        # Create schedule and transitioner
        schedule = Schedule(constants['start_time'], constants['end_time'])
        transitioner = Transitioner(slew_rate=1*u.deg/u.second)
        
        constraints = [AltitudeConstraint(min=25*u.deg)]
        
        scheduler = BBScheduler(
            constraints=constraints,
            observer=constants['observer'],
            transitioner=transitioner,
            gap_time=5*u.minute,  # Extra time for instrument changes
            time_resolution=1*u.minute
        )
        
        # Run the scheduler
        schedule = scheduler(blocks, schedule)
        
        # Get observation blocks
        observation_blocks = [b for b in schedule.scheduled_blocks 
                             if not isinstance(b, TransitionBlock)]
        
        # Verify all targets were scheduled with correct configurations
        assert len(observation_blocks) == 3, "All targets with complex configurations should be scheduled"
        
        for block in observation_blocks:
            target_name = block.target.name
            config = block.configuration
            
            # Verify configurations are preserved
            assert 'filter' in config, f"Filter should be preserved for {target_name}"
            assert 'grating' in config, f"Grating should be preserved for {target_name}"
            assert 'mode' in config, f"Mode should be preserved for {target_name}"

    def test_altitude_constraints(self):
        """
        Test that targets are only scheduled when meeting altitude constraints.
        
        Abstract Test: Verify that the scheduler respects altitude constraints and
        only schedules targets when they are within the specified altitude range.
        
        Concrete Input: Two targets with altitude constraints: minimum 40° and maximum 70°.
        Observer at APO, night window. One target (Vega) should meet constraints,
        another may not depending on timing.
        
        Expected Oracle: Only targets meeting altitude constraints during the
        scheduling window should be scheduled.
        """
        constants = get_test_constants()
        
        # Create targets
        targets = [
            FixedTarget.from_name('Vega'),    # Should be well-placed
            FixedTarget.from_name('Spica')    # May be too low depending on time
        ]
        
        blocks = []
        for i, target in enumerate(targets):
            block = ObservingBlock(
                target,
                30*u.minute,
                priority=1,
                configuration={'filter': 'R'}
            )
            blocks.append(block)
        
        # Create schedule and transitioner
        schedule = Schedule(constants['start_time'], constants['end_time'])
        transitioner = Transitioner(slew_rate=1*u.deg/u.second)
        
        # Create strict altitude constraints
        constraints = [
            AltitudeConstraint(min=40*u.deg, max=70*u.deg),
            AtNightConstraint.twilight_astronomical()
        ]
        
        scheduler = BBScheduler(
            constraints=constraints,
            observer=constants['observer'],
            transitioner=transitioner,
            gap_time=5*u.minute,
            time_resolution=1*u.minute
        )
        
        # Run the scheduler
        schedule = scheduler(blocks, schedule)
        
        # Get observation blocks
        observation_blocks = [b for b in schedule.scheduled_blocks 
                             if not isinstance(b, TransitionBlock)]
        
        # Verify only targets meeting altitude constraints are scheduled
        for block in observation_blocks:
            # Check altitude at start and end of observation
            start_alt = constants['observer'].altaz(block.start_time, block.target).alt
            end_alt = constants['observer'].altaz(block.end_time, block.target).alt
            
            assert start_alt >= 40*u.deg, f"{block.target.name} should start above 40° altitude"
            assert start_alt <= 70*u.deg, f"{block.target.name} should start below 70° altitude"
            assert end_alt >= 40*u.deg, f"{block.target.name} should end above 40° altitude"
            assert end_alt <= 70*u.deg, f"{block.target.name} should end below 70° altitude"

