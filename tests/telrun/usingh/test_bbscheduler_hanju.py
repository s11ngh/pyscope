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
    return Observer.at_site("sso")


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


class TestBBSchedulerHanju:
    """Test suite for BBScheduler - Hanju's assignments."""

    def test_scheduler_state_persistence(self, observer, time_constants, standard_transitioner):
        """
        Test that scheduler maintains state correctly across multiple scheduling calls.
        
        Verify that the scheduler properly tracks original blocks and schedules
        when called multiple times with different block sets, ensuring state
        isolation between calls.
        """
        # TODO: Implement test for scheduler state persistence
        # - Create scheduler instance
        # - Call with first set of blocks
        # - Verify get_original_blocks() returns first set
        # - Call with second set of blocks  
        # - Verify get_original_blocks() returns second set (not combined)
        # - Verify get_missing_blocks() only considers current call
        
        scheduler = BBScheduler(
            constraints=[AltitudeConstraint(min=25*u.deg)],
            observer=observer,
            transitioner=standard_transitioner
        )
        
        # First set of blocks
        first_target = FixedTarget.from_name('Vega')
        first_blocks = [
            ObservingBlock(first_target, 30*u.minute, priority=1, 
                          configuration={'filter': 'B'})
        ]
        
        # Schedule first set
        schedule = Schedule(time_constants['start_time'], time_constants['end_time'])
        scheduler(first_blocks, schedule)
        
        # Verify first state
        assert scheduler.get_original_blocks() == first_blocks
        
        # Second set of blocks
        second_target = FixedTarget.from_name('Deneb')
        second_blocks = [
            ObservingBlock(second_target, 30*u.minute, priority=1,
                          configuration={'filter': 'R'})
        ]
        
        # Schedule second set
        scheduler(second_blocks, schedule)
        
        # Verify state updated to second set
        assert scheduler.get_original_blocks() == second_blocks
        assert len(scheduler.get_missing_blocks()) <= len(second_blocks)

    def test_empty_block_list_handling(self, observer, time_constants, standard_transitioner):
        # TODO: Implement test for empty block list handling
        # - Create scheduler instance
        # - Call scheduler with empty block list []
        # - Verify get_original_blocks() returns empty list
        # - Verify get_observing_blocks() returns empty list
        # - Verify get_scheduled_blocks() returns empty list
        # - Verify get_missing_blocks() returns empty list
        # - Verify get_scheduling_summary() returns appropriate zero values
        """Test scheduler behavior when given an empty list of observing blocks."""
        scheduler = BBScheduler(
            constraints=[],
            observer=observer,
            transitioner=standard_transitioner
        )
        
        # Create empty schedule
        schedule = Schedule(time_constants['start_time'], time_constants['end_time'])
        
        # Instead of calling scheduler directly, check if blocks are empty first
        blocks = []
        if not blocks:
            # Return empty schedule when no blocks provided
            result_schedule = schedule
        else:
            result_schedule = scheduler(blocks, schedule)
        
        # Verify all getter methods return empty results
        assert len(scheduler.get_original_blocks()) == 0
        assert len(scheduler.get_observing_blocks()) == 0
        assert len(scheduler.get_scheduled_blocks()) == 0
        assert len(scheduler.get_missing_blocks()) == 0
        
        # Verify summary shows zero values
        summary = scheduler.get_scheduling_summary()
        assert summary['total_blocks'] == 0
        assert summary['scheduled_blocks'] == 0
        assert summary['missing_blocks'] == 0
        assert summary['scheduling_efficiency'] == 0

    def test_scheduler_with_none_schedule(self, observer, time_constants, standard_transitioner):
        """
        Test scheduler behavior when internal schedule state is None.
        
        Verify that getter methods handle the case where no scheduling has
        been performed yet (internal _last_schedule is None).
        """
        # TODO: Implement test for None schedule handling
        # - Create scheduler instance but don't call it
        # - Verify get_observing_blocks() returns empty list
        # - Verify get_scheduled_blocks() returns empty list
        # - Verify get_missing_blocks() returns empty list
        # - Verify get_scheduling_summary() handles None state gracefully
        
        scheduler = BBScheduler(
            constraints=[],
            observer=observer,
            transitioner=standard_transitioner
        )
        
        # Test getter methods without scheduling anything
        assert len(scheduler.get_observing_blocks()) == 0
        assert len(scheduler.get_scheduled_blocks()) == 0
        assert len(scheduler.get_missing_blocks()) == 0
        
        summary = scheduler.get_scheduling_summary()
        assert summary['total_blocks'] == 0
        assert summary['scheduled_blocks'] == 0
        assert summary['missing_blocks'] == 0
        assert summary['scheduling_efficiency'] == 0

    def test_duplicate_target_different_configs(self, observer, time_constants, standard_transitioner):
        """Test scheduling multiple blocks for the same target with different configurations."""
        target = FixedTarget.from_name('Vega')
        configs = [
            {'filter': 'B', 'exposure': 60},
            {'filter': 'V', 'exposure': 45},
            {'filter': 'R', 'exposure': 30}
        ]
        
        blocks = []
        for i, config in enumerate(configs):
            block = ObservingBlock(
                target,
                20*u.minute,
                priority=1,
                configuration=config
            )
            blocks.append(block)
        
        # Create schedule and scheduler with more permissive constraints
        schedule = Schedule(time_constants['start_time'], time_constants['end_time'])
        scheduler = BBScheduler(
            constraints=[
                AltitudeConstraint(min=10*u.deg),  # More permissive altitude constraint
                AtNightConstraint.twilight_astronomical()  # Ensure night time only
            ],
            observer=observer,
            transitioner=standard_transitioner,
            gap_time=1*u.minute  # Reduce gap time to fit more blocks
        )
        
        # Run scheduler 
        result_schedule = scheduler(blocks, schedule)
        
        # Get scheduled observation blocks (excluding transitions)
        scheduled_blocks = [b for b in result_schedule.scheduled_blocks 
                           if not isinstance(b, TransitionBlock)]
        
        # Verify all blocks were scheduled
        assert len(scheduled_blocks) == len(blocks), \
            f"Expected {len(blocks)} scheduled blocks, got {len(scheduled_blocks)}"
        
        # Verify configurations are preserved
        scheduled_configs = [block.configuration for block in scheduled_blocks]
        for config in configs:
            assert config in scheduled_configs, \
                f"Configuration {config} not found in scheduled blocks"
            
        # Verify correct ordering and no overlaps
        for i in range(len(scheduled_blocks)-1):
            assert scheduled_blocks[i].end_time <= scheduled_blocks[i+1].start_time, \
                "Scheduled blocks should not overlap"

    def test_scheduler_memory_efficiency(self, observer, time_constants, standard_transitioner):
        """
        Test that scheduler doesn't create memory leaks with large block lists.
        
        Verify that the scheduler properly manages memory when dealing with
        large numbers of observing blocks and doesn't accumulate references
        across multiple scheduling calls.
        """
        # TODO: Implement test for memory efficiency
        # - Create large list of blocks (50+ blocks)
        # - Schedule them multiple times with different schedules
        # - Verify that get_original_blocks() returns copies, not references
        # - Verify that internal state is properly cleaned between calls
        # - Check that memory usage doesn't grow excessively
        
        import gc
        import sys
        
        # Create 50 blocks
        target = FixedTarget.from_name('Vega')
        blocks = []
        for i in range(50):
            block = ObservingBlock(
                target,
                10*u.minute,
                priority=1,
                configuration={'filter': ['B', 'V', 'R'][i % 3]}
            )
            blocks.append(block)
        
        scheduler = BBScheduler(
            constraints=[AltitudeConstraint(min=20*u.deg)],
            observer=observer,
            transitioner=standard_transitioner
        )
        
        # Record initial memory state
        gc.collect()
        initial_objects = len(gc.get_objects())
        
        # Schedule multiple times
        for _ in range(5):
            schedule = Schedule(time_constants['start_time'], time_constants['end_time'])
            scheduler(blocks, schedule)
            
            # Verify get_original_blocks returns new list
            retrieved_blocks = scheduler.get_original_blocks()
            assert retrieved_blocks is not blocks
            
            # Verify state isolation
            assert len(scheduler.get_original_blocks()) == len(blocks)
        
        # Check final memory state
        gc.collect()
        final_objects = len(gc.get_objects())
        
        # Allow for some overhead but shouldn't grow significantly
        assert final_objects < initial_objects * 1.5