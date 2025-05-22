import pytest
from astroplan import Observer, FixedTarget
from astropy.time import Time
from astropy import units as u
from astroplan.constraints import AirmassConstraint, AtNightConstraint, TimeConstraint, AltitudeConstraint
from astroplan.scheduling import TransitionBlock
from pyscope.telrun.create_priority_schedule import create_priority_schedule, print_schedule

# Constants for all tests
def get_test_constants():
    """Return common constants used across all tests."""
    observer = Observer.at_site('apo')
    # Full 24 h window
    start_time      = Time('2025-07-06 19:00')  # UT
    end_time        = Time('2025-07-07 19:00')  # UT

# 6 h half‑night sub‑window
    half_night_start = Time('2025-07-07 02:00')  # UT
    half_night_end   = Time('2025-07-07 08:00')  # UT
    return {
        'observer': observer,
        'start_time': start_time,
        'end_time': end_time,
        'half_night_start': half_night_start,
        'half_night_end': half_night_end
    }


class TestPriorityScheduler:
    """Test suite for the create_priority_schedule function."""
    
    def test_single_target_no_transitions(self):
        """
        Test that a schedule with a single target has no transition blocks.
        
        Abstract Test:
            Verify that scheduling a single target with a single configuration
            results in a schedule without any transition blocks.
        
        Concrete Input:
            - One target (Deneb)
            - One filter configuration ('B')
            - 5-minute observation duration
            - No additional constraints
        
        Expected Oracle:
            - Schedule contains no TransitionBlock instances
            - Schedule contains exactly one block
        """
        # Get constants
        constants = get_test_constants()
        
        # Setup test-specific parameters
        targets = [FixedTarget.from_name('Deneb')]
        durations = [5*u.minute]
        constraints = []
        configuration = [{'filter': 'B'}]
        
        # Create schedule
        schedule, scheduler = create_priority_schedule(
            targets=targets,
            observer=constants['observer'],
            start_time=constants['start_time'],
            end_time=constants['end_time'],
            durations=durations,
            constraints=constraints,
            configuration=configuration,
        )
        
        # Assert no transition blocks in schedule
        for block in schedule.scheduled_blocks:
            assert not isinstance(block, TransitionBlock), "Schedule should not contain transition blocks"
        assert len(schedule.scheduled_blocks) == 1, "Schedule should contain exactly one block for one target"
    
    def test_single_target_with_transitions(self):
        """
        Test that a schedule with a single target and multiple filters has no transition blocks.
        
        Abstract Test:
            Verify that scheduling a single target with multiple filter configurations
            results in a schedule without transition blocks between exposures.
        
        Concrete Input:
            - One target (Deneb)
            - Three filter configurations ('B', 'C', 'R')
            - 5-minute observation duration
            - No additional constraints
        
        Expected Oracle:
            - Schedule contains no TransitionBlock instances
        """
        # Get constants
        constants = get_test_constants()
        
        # Setup test-specific parameters
        targets = [FixedTarget.from_name('Deneb')]
        durations = [5*u.minute]
        constraints = []
        configuration = [{'filter': 'B'}, {'filter': 'C'}, {'filter': 'R'}]
        
        # Create schedule
        schedule, scheduler = create_priority_schedule(
            targets=targets,
            observer=constants['observer'],
            start_time=constants['start_time'],
            end_time=constants['end_time'],
            durations=durations,
            constraints=constraints,
            configuration=configuration,
        )
        
        # Assert no transition blocks in schedule
        for block in schedule.scheduled_blocks:
            assert not isinstance(block, TransitionBlock), "Schedule should not contain transition blocks"
    
    def test_single_target_with_exposure(self):
        """
        Test scheduling a single star with one filter for one exposure.
        
        Abstract Test:
            Verify that scheduling a single target with one filter for one exposure
            results in exactly one observation block with no transition blocks.
        
        Concrete Input:
            - One target (M31)
            - One filter configuration ('B')
            - 5-minute observation duration
            - No additional constraints
        
        Expected Oracle:
            - Schedule contains no TransitionBlock instances
            - Schedule contains exactly one block
            - The scheduled block targets M31 with filter 'B'
        """
        # Get constants
        constants = get_test_constants()
        
        # Setup test-specific parameters
        targets = [FixedTarget.from_name('M31')]
        durations = [5*u.minute]  # Duration for a single exposure
        constraints = []
        configuration = [{'filter': 'B'}]  # Single filter
        
        # Create schedule
        schedule, scheduler = create_priority_schedule(
            targets=targets,
            observer=constants['observer'],
            start_time=constants['start_time'],
            end_time=constants['end_time'],
            durations=durations,
            constraints=constraints,
            configuration=configuration,
        )
        
        # Assert no transition blocks in schedule
        for block in schedule.scheduled_blocks:
            assert not isinstance(block, TransitionBlock), "Schedule should not contain transition blocks"
            
        # Verify we have exactly one scheduled block (one exposure)
        assert len(schedule.scheduled_blocks) == 1, "Schedule should contain exactly one block for one exposure"
        
        # Verify the scheduled block has the correct configuration
        assert schedule.scheduled_blocks[0].configuration['filter'] == 'B', "Scheduled block should use filter B"
        assert schedule.scheduled_blocks[0].target.name == 'M31', "Scheduled block should target M31"

    
        
    
    def test_unobservable_target(self):
        """Test scheduling an unobservable target. At 0 degrees altitude, the target is not observable. We expect no blocks in the schedule given a full night and 1 filter and 1 target"""
        # Get constants
        constants = get_test_constants()
        
        # Setup test-specific parameters
        targets = [FixedTarget.from_name('Deneb')]
        durations = [5*u.minute]
        constraints = [AltitudeConstraint(max=0*u.deg)]
        configuration = [{'filter': 'B'}]
        
        # Create schedule
        schedule, scheduler = create_priority_schedule(
            targets=targets,
            observer=constants['observer'],
            start_time=constants['start_time'],
            end_time=constants['end_time'],
            durations=durations,
            constraints=constraints,
            configuration=configuration,
        )
        
        # Assert no transition blocks in schedule
        assert len(schedule.scheduled_blocks) == 0, "Schedule should contain no blocks for unobservable target"

    def test_multiple_targets_no_filter(self):
        """
        Test scheduling multiple targets with no specific filter configuration.
        
        Abstract Test:
            Verify that scheduling multiple targets with default configuration
            results in a schedule with observable targets.
        
        Concrete Input:
            - Two targets (Deneb and M13)
            - 5-minute observation duration for each target
            - No constraints
            - Empty configuration (should default to empty dict per target)
        
        Expected Oracle:
            - Schedule contains at least one block
            - Schedule contains M31
            - Schedule contains Deneb
            - Schedule contains a transition block between Deneb and M31
        """
        # Get constants
        constants = get_test_constants()
        
        # Setup test-specific parameters
        targets = [FixedTarget.from_name('Deneb'), FixedTarget.from_name('M13')]
        durations = [5*u.minute, 5*u.minute]
        constraints = []
        # Fix: provide a configuration for each target instead of an empty list
        configuration = []  # Empty dict for each target
        
        # Create schedule
        schedule, scheduler = create_priority_schedule(
            targets=targets,
            observer=constants['observer'],
            start_time=constants['start_time'],
            end_time=constants['end_time'],
            durations=durations,
            constraints=constraints,
            configuration=configuration,
        )
        
        # Assert schedule has at least one block
        assert len(schedule.scheduled_blocks) > 0, "Schedule should contain at least one block"
        assert schedule.scheduled_blocks[0].target.name == 'Deneb' or schedule.scheduled_blocks[0].target.name == 'M13', "Scheduled block should target Deneb or M13"
        assert schedule.scheduled_blocks[2].target.name == 'Deneb' or schedule.scheduled_blocks[1].target.name == 'M13', "Scheduled block should target Deneb or M13"
        assert isinstance(schedule.scheduled_blocks[1], TransitionBlock), "Scheduled blocks should be TransitionBlocks"

    def test_half_night_schedule(self):
        """Test scheduling a single target with one filter for one exposure.
        
        Abstract Test:
            Verify that scheduling a single target with one filter for one exposure
            results in exactly one observation block with no transition blocks.
        
        Concrete Input:
            - One target (Deneb)
            - One filter configuration ('B')
            - 5-minute observation duration
            - No additional constraints 
            - Half night window
            
        Expected Oracle:
            - Schedule contains no TransitionBlock instances
            - Schedule contains exactly one block
            - The scheduled block targets Deneb with filter 'B'"""
        
        constants = get_test_constants()
        
        # Setup test-specific parameters
        targets = [FixedTarget.from_name('Deneb'), FixedTarget.from_name('M13'), 
                   FixedTarget.from_name('Vega'), 
                   FixedTarget.from_name('Polaris'), 
                   FixedTarget.from_name('Altair'), 
                   FixedTarget.from_name('Albireo'),
                   FixedTarget.from_name('Arcturus'),FixedTarget.from_name('Capella')]
        durations = [5*u.minute, 5*u.minute, 5*u.minute, 5*u.minute, 5*u.minute, 5*u.minute, 5*u.minute, 5*u.minute]
        constraints = [TimeConstraint(constants['half_night_start'],constants['half_night_end'])]
        configuration = [{'filter': 'B'}, {'filter': 'C'}, {'filter': 'R'}, {'filter': 'G'}, {'filter': 'I'}, {'filter': 'Y'}, {'filter': 'V'}, {'filter': 'B'}]
        
        # Create schedule
        schedule, scheduler = create_priority_schedule(
            targets=targets,
            observer=constants['observer'],
            start_time=constants['start_time'],
            end_time=constants['end_time'],
            durations=durations,
            constraints=constraints,
            configuration=configuration,
        )
        
        assert len(schedule.scheduled_blocks) >=1, "Schedule should schedule at least one block"
        assert Time(schedule.scheduled_blocks[0].start_time.iso) >= constants['half_night_start'] and Time(schedule.scheduled_blocks[0].end_time.iso) <= constants['half_night_end'], "First block should be within the half night window"
        assert Time(schedule.scheduled_blocks[-1].start_time.iso) >= constants['half_night_start'] and Time(schedule.scheduled_blocks[-1].end_time.iso) <= constants['half_night_end'], "Last block should be within the half night window"

    def test_transition_insertion(self):
        """Test that correct transition blocks are inserted when necessary.
        
        Abstract Test:
            Verify that transition blocks are inserted between observable targets
        
        Concrete Input:
            - Two targets (Deneb and M13)
            - 5-minute observation duration for each target
            - No constraints
            - Empty configuration (should default to empty dict per target)
            """
        constants = get_test_constants()
        
        # Setup test-specific parameters
        targets = [FixedTarget.from_name('Deneb'), FixedTarget.from_name('M13'), 
                   FixedTarget.from_name('Vega'), 
                   FixedTarget.from_name('Polaris'), 
                   FixedTarget.from_name('Altair'), 
                   FixedTarget.from_name('Albireo'),
                   FixedTarget.from_name('Arcturus'),FixedTarget.from_name('Capella')]
        durations = [5*u.minute, 5*u.minute, 5*u.minute, 5*u.minute, 5*u.minute, 5*u.minute, 5*u.minute, 5*u.minute]
        constraints = []
        configuration = [{'filter': 'B'}, {'filter': 'C'}, {'filter': 'R'}, {'filter': 'G'}, {'filter': 'I'}, {'filter': 'Y'}, {'filter': 'V'}, {'filter': 'B'}]
        

        # Create schedule
        schedule, scheduler = create_priority_schedule(
            targets=targets,
            observer=constants['observer'],
            start_time=constants['start_time'],
            end_time=constants['end_time'],
            durations=durations,
            constraints=constraints,
            configuration=configuration,
        )
        # TODO: Need to finish this later
    
    def test_transition_repeat(self):
        """Test “no transitions for repeated exposures same filter”
Abstract Test: multiple exposures of same target+filter require no TransitionBlock.
Concrete Input: one star, one filter, durations list >1.
Expected: no TransitionBlock in schedule"""
        constants = get_test_constants()
        
        # Setup test-specific parameters
        targets = [FixedTarget.from_name('Deneb'), FixedTarget.from_name('M13'), 
                   FixedTarget.from_name('Vega'), 
                   FixedTarget.from_name('Polaris'), 
                   FixedTarget.from_name('Altair'), 
                   FixedTarget.from_name('Albireo'),
                   FixedTarget.from_name('Arcturus'),FixedTarget.from_name('Capella')]
        durations = [5*u.minute, 5*u.minute, 5*u.minute, 5*u.minute, 5*u.minute, 5*u.minute, 5*u.minute, 5*u.minute]
        constraints = []
        configuration = [{'filter': 'B'}, {'filter': 'B'}, {'filter': 'B'}, {'filter': 'B'}, {'filter': 'B'}, {'filter': 'B'}, {'filter': 'B'}, {'filter': 'B'}]
        
        #TODO assert that no scheduled_blocks are TransitionBlocks
        schedule, scheduler = create_priority_schedule(
            targets=targets,
            observer=constants['observer'],
            start_time=constants['start_time'],
            end_time=constants['end_time'],
            durations=durations,
            constraints=constraints,
            configuration=configuration,
        )
        for block in schedule.scheduled_blocks:
            assert not isinstance(block, TransitionBlock), "Schedule should not contain transition blocks"
        
