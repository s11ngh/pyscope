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
    return Observer.at_site("Subaru", timezone="US/Hawaii")


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


class TestBBSchedulerGukgi:
    """Test suite for BBScheduler - Gukgi's assignments."""

    def test_transitioner_configuration_impact(self, observer, time_constants, standard_transitioner):
        """
        Test how different transitioner configurations affect scheduling results.
        
        Verify that changes in slew rates, instrument reconfiguration times,
        and gap times properly influence which blocks get scheduled and
        the overall scheduling efficiency.
        """
        # TODO: Implement test for transitioner configuration impact
        # - Create identical block sets
        # - Schedule with fast transitioner (high slew rate, short gaps)
        # - Schedule with slow transitioner (low slew rate, long gaps)
        # - Compare scheduling results and efficiency
        # - Verify that faster transitioner allows more blocks to be scheduled
        targets = [
            FixedTarget.from_name('Vega'),
            FixedTarget.from_name('Altair'),
            FixedTarget.from_name('Deneb')
        ]

        blocks = []
        for i, target in enumerate(targets):
            block = ObservingBlock(
                target,
                20 * u.minute,
                priority=1,
                configuration={'filter': f'F{i}'}
            )
            blocks.append(block)

        # Fast transitioner setup
        fast_transitioner = Transitioner(slew_rate=5 * u.deg / u.second)
        schedule_fast = Schedule(time_constants['start_time'], time_constants['end_time'])
        scheduler_fast = BBScheduler(
            constraints=[AltitudeConstraint(min=20 * u.deg)],
            observer=observer,
            transitioner=fast_transitioner,
            gap_time=1 * u.minute,
            time_resolution=1 * u.minute
        )
        schedule_fast = scheduler_fast(blocks, schedule_fast)

        # Slow transitioner setup
        slow_transitioner = Transitioner(slew_rate=0.2 * u.deg / u.second)
        schedule_slow = Schedule(time_constants['start_time'], time_constants['end_time'])
        scheduler_slow = BBScheduler(
            constraints=[AltitudeConstraint(min=20 * u.deg)],
            observer=observer,
            transitioner=slow_transitioner,
            gap_time=5 * u.minute,
            time_resolution=1 * u.minute
        )
        schedule_slow = scheduler_slow(blocks, schedule_slow)

        # Get scheduled blocks only (excluding transitions)
        fast_blocks = [b for b in schedule_fast.scheduled_blocks if not isinstance(b, TransitionBlock)]
        slow_blocks = [b for b in schedule_slow.scheduled_blocks if not isinstance(b, TransitionBlock)]

        # Check that fast scheduler results in more scheduled blocks or equal
        assert len(fast_blocks) >= len(slow_blocks), \
            "Fast transitioner should allow at least as many scheduled blocks as slow transitioner"
        

    def test_block_duration_edge_cases(self, observer, time_constants, standard_transitioner):
        """
        Test scheduler behavior with extreme block durations.
        
        Verify that the scheduler correctly handles very short blocks (seconds),
        very long blocks (hours), and blocks with durations that exactly match
        available time slots.
        """
        # TODO: Implement test for block duration edge cases
        # - Create blocks with very short durations (10 seconds)
        # - Create blocks with very long durations (8+ hours)
        # - Create blocks that exactly fit available time slots
        # - Schedule the blocks
        # - Verify proper handling of all duration extremes
        # - Verify that duration constraints are respected
         # Setup
        schedule = Schedule(time_constants['start_time'], time_constants['end_time'])

        # Very short duration block
        short_block = ObservingBlock(
            FixedTarget.from_name('Vega'),
            10 * u.second,
            priority=1,
            configuration={'filter': 'B'}
        )

        # Very long duration block (almost entire night)
        time_diff = (time_constants['end_time'] - time_constants['start_time']).to(u.hour)
        # Convert both durations to the same unit before subtraction
        short_duration = 10 * u.minute
        long_duration = time_diff - short_duration.to(u.hour)
        long_block = ObservingBlock(
            FixedTarget.from_name('Altair'),
            long_duration,
            priority=1,
            configuration={'filter': 'R'}
        )

        # Block that exactly fits a 30-minute slot
        exact_block = ObservingBlock(
            FixedTarget.from_name('Deneb'),
            30 * u.minute,
            priority=1,
            configuration={'filter': 'V'}
        )

        blocks = [short_block, long_block, exact_block]

        scheduler = BBScheduler(
            constraints=[AltitudeConstraint(min=20 * u.deg)],
            observer=observer,
            transitioner=standard_transitioner,
            gap_time=2 * u.minute,
            time_resolution=10 * u.second  # high precision
        )

        result_schedule = scheduler(blocks, schedule)
        scheduled_blocks = [b for b in result_schedule.scheduled_blocks if not isinstance(b, TransitionBlock)]

        # Check durations
        for block in scheduled_blocks:
            duration = block.end_time - block.start_time
            if block.target.name == 'Vega':
                assert abs(duration.to(u.second).value - 10) < 1, "Short block duration should be ~10 seconds"
            elif block.target.name == 'Altair':
                assert abs(duration.to(u.minute).value - long_duration.to(u.minute).value) < 1, "Long block duration should be ~all night minus 10 min"
            elif block.target.name == 'Deneb':
                assert abs(duration.to(u.minute).value - 30) < 1, "Exact block duration should be 30 minutes"


    def test_observer_location_impact(self, time_constants, standard_transitioner):
        """
        Test how different observer locations affect target visibility and scheduling.
        
        Verify that the same targets scheduled from different observatory
        locations (different latitudes) produce different scheduling results
        due to varying target visibility.
        """
        # TODO: Implement test for observer location impact
        # - Create observers at different locations (e.g., APO, Keck, CTIO)
        # - Use same target list and time window for all observers
        # - Schedule blocks for each observer location
        # - Compare scheduling results between locations
        # - Verify that target visibility differences affect scheduling

        # Observers at different locations
        observers = {
            'Subaru': Observer.at_site("Subaru", timezone="US/Hawaii"),
            'CTIO': Observer.at_site("ctio"),
            'APO': Observer.at_site("apo")
        }

        # Common targets and blocks
        targets = [
            FixedTarget.from_name('Spica'),     # Southern sky
            FixedTarget.from_name('Vega'),      # Northern sky
            FixedTarget.from_name('Canopus')    # Far southern sky, hard for APO
        ]

        blocks = []
        for i, target in enumerate(targets):
            blocks.append(ObservingBlock(
                target,
                30 * u.minute,
                priority=1,
                configuration={'filter': f'F{i}'}
            ))

        scheduled_by_site = {}

        for site_name, observer in observers.items():
            schedule = Schedule(time_constants['start_time'], time_constants['end_time'])
            scheduler = BBScheduler(
                constraints=[AltitudeConstraint(min=20 * u.deg), AtNightConstraint.twilight_astronomical()],
                observer=observer,
                transitioner=standard_transitioner,
                gap_time=2 * u.minute,
                time_resolution=1 * u.minute
            )
            result = scheduler(blocks, schedule)

            # Record scheduled targets
            scheduled_targets = [b.target.name for b in result.scheduled_blocks if not isinstance(b, TransitionBlock)]
            scheduled_by_site[site_name] = set(scheduled_targets)

        # Assert at least one observer sees a different subset
        scheduled_sets = list(scheduled_by_site.values())
        assert any(scheduled_sets[0] != scheduled_sets[i] for i in range(1, len(scheduled_sets))), \
            f"Scheduling results should differ between observatories: {scheduled_by_site}"
        

    def test_seasonal_target_visibility(self, observer, standard_transitioner):
        """
        Test scheduler behavior with targets across different seasons.
        
        Verify that the scheduler correctly handles seasonal target visibility
        by testing the same targets during different times of year (summer vs winter).
        """
        # TODO: Implement test for seasonal target visibility
        # - Create summer observation window (July)
        # - Create winter observation window (December)
        # - Use same target list for both seasons
        # - Schedule blocks for both time periods
        # - Compare which targets are schedulable in each season
        # - Verify seasonal visibility effects on missing blocks
        
        summer_start = Time('2025-07-07 01:00')
        summer_end = Time('2025-07-07 09:00')
        winter_start = Time('2025-12-15 01:00')
        winter_end = Time('2025-12-15 09:00')

        targets = [
            FixedTarget.from_name('Vega'),
            FixedTarget.from_name('Betelgeuse'),
            FixedTarget.from_name('Canopus')  # Better seasonal contrast
        ]

        blocks = []
        for i, target in enumerate(targets):
            blocks.append(ObservingBlock(
                target,
                30 * u.minute,
                priority=1,
                configuration={'filter': f'F{i}'}
            ))

        constraints = [AltitudeConstraint(min=20 * u.deg), AtNightConstraint.twilight_astronomical()]

        # Summer
        scheduler_summer = BBScheduler(
            constraints=constraints,
            observer=observer,
            transitioner=standard_transitioner,
            gap_time=2 * u.minute,
            time_resolution=1 * u.minute
        )
        schedule_summer = Schedule(summer_start, summer_end)
        schedule_summer = scheduler_summer(blocks, schedule_summer)

        summer_targets = {
            block.target.name for block in schedule_summer.scheduled_blocks
            if hasattr(block, 'target') and not isinstance(block, TransitionBlock)
        }

        # Winter
        scheduler_winter = BBScheduler(
            constraints=constraints,
            observer=observer,
            transitioner=standard_transitioner,
            gap_time=2 * u.minute,
            time_resolution=1 * u.minute
        )
        schedule_winter = Schedule(winter_start, winter_end)
        schedule_winter = scheduler_winter(blocks, schedule_winter)

        winter_targets = {
            block.target.name for block in schedule_winter.scheduled_blocks
            if hasattr(block, 'target') and not isinstance(block, TransitionBlock)
        }

        # Compare visibility
        difference = summer_targets.symmetric_difference(winter_targets)

        assert len(difference) > 0, (
            f"Expected seasonal visibility difference but got:\n"
            f"Summer: {summer_targets}\nWinter: {winter_targets}"
        )
        
    def test_concurrent_scheduling_consistency(self, observer, time_constants, standard_transitioner):
        """
        Test that multiple scheduler instances produce consistent results.
        
        Verify that creating multiple BBScheduler instances with identical
        parameters and scheduling identical block sets produces the same
        results, ensuring deterministic behavior.
        """
        # TODO: Implement test for concurrent scheduling consistency
        # - Create multiple BBScheduler instances with identical parameters
        # - Schedule identical block sets with each scheduler
        # - Compare all scheduling results (scheduled, missing, summary)
        # - Verify that results are identical across all instances
        # - Test with different random seeds if applicable
        
        targets = [
            FixedTarget.from_name('Vega'),
            FixedTarget.from_name('Altair'),
            FixedTarget.from_name('Deneb')
        ]

        blocks = []
        for i, target in enumerate(targets):
            blocks.append(ObservingBlock(
                target,
                30 * u.minute,
                priority=1,
                configuration={'filter': f'F{i}'}
            ))

        constraints = [AltitudeConstraint(min=20 * u.deg), AtNightConstraint.twilight_astronomical()]

        def run_scheduler():
            schedule = Schedule(time_constants['start_time'], time_constants['end_time'])
            scheduler = BBScheduler(
                constraints=constraints,
                observer=observer,
                transitioner=standard_transitioner,
                gap_time=3 * u.minute,
                time_resolution=1 * u.minute
            )
            return scheduler(blocks, schedule)

        schedule1 = run_scheduler()
        schedule2 = run_scheduler()

        obs1 = [b for b in schedule1.scheduled_blocks if not isinstance(b, TransitionBlock)]
        obs2 = [b for b in schedule2.scheduled_blocks if not isinstance(b, TransitionBlock)]

        assert len(obs1) == len(obs2), "Mismatch in number of scheduled blocks"

        for b1, b2 in zip(obs1, obs2):
            assert b1.target.name == b2.target.name, "Target mismatch"
            assert abs((b1.start_time - b2.start_time).to(u.second).value) < 1, "Start time mismatch"
            assert abs((b1.end_time - b2.end_time).to(u.second).value) < 1, "End time mismatch"
            assert b1.configuration == b2.configuration, "Configuration mismatch"