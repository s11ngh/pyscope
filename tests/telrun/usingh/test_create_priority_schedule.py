import pytest
from astroplan import Observer, FixedTarget
from astropy.time import Time
from astropy import units as u
from astroplan.constraints import AirmassConstraint, AtNightConstraint
from astroplan.scheduling import TransitionBlock
from pyscope.telrun.create_priority_schedule import create_priority_schedule, print_schedule

# Constants for all tests
def get_test_constants():
    """Return common constants used across all tests."""
    observer = Observer.at_site('apo')
    start_time = Time('2025-07-10 19:00')   # UT
    end_time = Time('2025-07-11 05:00')   # UT
    
    return {
        'observer': observer,
        'start_time': start_time,
        'end_time': end_time,
    }


class TestPriorityScheduler:
    """Test suite for the create_priority_schedule function."""
    
    def test_single_target_no_transitions(self):
        """Test that a schedule with a single target has no transition blocks."""
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
    
    def test_single_target_with_transitions(self):
        """Test that a schedule with a single target has no transition blocks."""
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
    
    
        
    
    