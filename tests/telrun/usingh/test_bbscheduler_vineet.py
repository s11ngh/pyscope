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
    return Observer.at_site("haleakala")


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


class TestBBSchedulerVineet:
    """Test suite for BBScheduler - Vineet's assignments."""

    def test_constraint_violation_tracking(self, observer, time_constants, standard_transitioner):
        """
        Test that missing blocks correctly identifies constraint violations.
        
        Verify that blocks failing different types of constraints (altitude,
        time, airmass) are properly identified as missing and that the
        constraint violation reason can be determined.
        """
        # TODO: Implement test for constraint violation tracking
        # - Create blocks with various constraint violations (altitude, time, airmass)
        # - Schedule the blocks
        # - Verify that constraint-violating blocks appear in get_missing_blocks()
        # - Verify that schedulable blocks don't appear in missing blocks
        # - Test with multiple constraint types simultaneously

        # Create test target
        target = FixedTarget.from_name('Vega')
        
        # Create blocks with different constraint violations
        blocks = [
            # Block 1: Impossible altitude constraint
            ObservingBlock(
                target,
                30*u.minute,
                priority=1,
                configuration={'filter': 'V'},
                constraints=[AltitudeConstraint(min=89*u.deg)]
            ),
            
            # Block 2: Time constraint violation
            ObservingBlock(
                target,
                30*u.minute,
                priority=1,
                configuration={'filter': 'R'}, 
                constraints=[TimeConstraint(
                    Time('2025-07-08 00:00:00'), # Outside of the time window
                    Time('2025-07-08 02:00:00')   
                )]
            ),
            

            # NOTE: airmass constraints does not give error if max is less than 1
            # and does not give error if max < min

            # Block 3: Comment out using regular # instead of triple quotes
            # ObservingBlock(
            #     target,
            #     30*u.minute,
            #     priority=1,
            #     configuration={'filter': 'B'},
            #     constraints=[AirmassConstraint(min=0.1, max=0.9)]
            # ),

            # Block 3a: Definitely should fail (impossible airmass)
            ObservingBlock(
                FixedTarget.from_name('Polaris'),
                30*u.minute,
                priority=1,
                configuration={'filter': 'B1'},
                constraints=[AirmassConstraint(min=0.1, max=0.9)]
            ),

            # Block 3b: Definitely should fail (airmass too low for Polaris)
            ObservingBlock(
                FixedTarget.from_name('Polaris'),
                30*u.minute,
                priority=1,
                configuration={'filter': 'B2'},
                constraints=[AirmassConstraint(min=1.0, max=1.5)]  # Impossible - Polaris always at ~2.9
            ),

            # Block 3c: Should succeed (includes Polaris's actual airmass)
            ObservingBlock(
                FixedTarget.from_name('Polaris'),
                30*u.minute,
                priority=1,
                configuration={'filter': 'B3'},
                constraints=[AirmassConstraint(min=2.0, max=3.5)]  # Should work for Polaris
            ),
            
            # Block 4: Multiple constraints but all satisfiable
            ObservingBlock(
                target,
                30*u.minute,
                priority=1,
                configuration={'filter': 'I'},
                constraints=[
                    AltitudeConstraint(min=20*u.deg),
                    AtNightConstraint(),
                    AirmassConstraint(max=2.0)
                ]
            ),
            
            # Block 5: Multiple conflicting constraints
            ObservingBlock(
                target,
                30*u.minute,
                priority=1,
                configuration={'filter': 'G'},
                constraints=[
                    AltitudeConstraint(min=89*u.deg),  # Make it definitely impossible
                    AirmassConstraint(max=1.01),       # Even stricter airmass
                    TimeConstraint(
                        Time('2025-07-07 02:00:00'),
                        Time('2025-07-07 02:01:00')    # Very narrow time window
                    )
                ]
            ),
            
            # Block 6: Multiple targets with same constraints
            ObservingBlock(
                FixedTarget.from_name('Deneb'),  # Different target
                30*u.minute,
                priority=1,
                configuration={'filter': 'U'},
                constraints=[
                    AltitudeConstraint(min=20*u.deg),
                    AtNightConstraint(),
                    AirmassConstraint(max=2.0)
                ]
            ),
            
            # Block 7: Edge case constraint values
            ObservingBlock(
                target,
                30*u.minute,
                priority=1,
                configuration={'filter': 'H'},
                constraints=[
                    AltitudeConstraint(min=0*u.deg, max=90*u.deg),  # Full range
                    AirmassConstraint(min=1.0, max=1.0001)  # Nearly impossible
                ]
            )
        ]
        
        # Create schedule and scheduler
        schedule = Schedule(time_constants['start_time'], time_constants['end_time'])
        scheduler = BBScheduler(
            constraints=[AtNightConstraint()],
            observer=observer,
            transitioner=standard_transitioner
        )
        
        # Run scheduler
        result_schedule = scheduler(blocks, schedule)
        
        # Get missing and scheduled blocks
        missing_blocks = scheduler.get_missing_blocks()
        scheduled_blocks = scheduler.get_observing_blocks()
        
        # Add this before the assertions for debugging
        print("Missing blocks:", [b.configuration['filter'] for b in missing_blocks])
        print("Scheduled blocks:", [b.configuration['filter'] for b in scheduled_blocks])
        
        # Verify basic counts
        assert len(missing_blocks) == 6, "Expected 6 blocks to be missing due to constraint violations"
        assert len(scheduled_blocks) == 3, "Expected 3 blocks to be successfully scheduled"  # Changed from 2 to 3
        
        # Verify specific blocks by their filter configurations
        scheduled_configs = [block.configuration['filter'] for block in scheduled_blocks]
        missing_configs = [block.configuration['filter'] for block in missing_blocks]
        
        # Blocks that should be scheduled
        assert 'I' in scheduled_configs, "Block I (satisfiable constraints) should be scheduled"
        assert 'U' in scheduled_configs, "Block U (Deneb with satisfiable constraints) should be scheduled"
        assert 'B3' in scheduled_configs, "Block B3 (Polaris with correct airmass) should be scheduled"
        
        # Blocks that should be missing
        assert 'V' in missing_configs, "Block V (impossible altitude) should be missing"
        assert 'R' in missing_configs, "Block R (time constraint violation) should be missing"
        assert 'B1' in missing_configs, "Block B1 (impossible airmass < 1) should be missing"
        assert 'B2' in missing_configs, "Block B2 (impossible airmass for Polaris) should be missing"
        assert 'G' in missing_configs, "Block G (multiple strict constraints) should be missing"
        assert 'H' in missing_configs, "Block H (nearly impossible airmass) should be missing"
        
        # Verify scheduling summary
        summary = scheduler.get_scheduling_summary()
        assert summary['total_blocks'] == 9  # Correct - we have 9 total blocks
        assert summary['scheduled_blocks'] == 3
        assert summary['missing_blocks'] == 6
        assert summary['scheduling_efficiency'] == pytest.approx(33.33, rel=0.01)  # 3/9 * 100

        # Add debug prints after scheduling:
        print("\nAirmass test details:")
        for block in missing_blocks + scheduled_blocks:
            if block.configuration['filter'].startswith('B'):
                status = "scheduled" if block in scheduled_blocks else "missing"
                print(f"Block {block.configuration['filter']} ({status})")
                print(f"Target: {block.target.name}")
                print(f"Constraints: {block.constraints[0].min} <= airmass <= {block.constraints[0].max}\n")


    def test_scheduling_summary_accuracy(self, observer, time_constants, standard_transitioner):
        """
        Test that get_scheduling_summary() provides accurate statistics.
        
        Verify that the scheduling summary correctly calculates efficiency
        percentages, block counts, and handles edge cases like 100% efficiency
        and 0% efficiency scenarios.
        """
        # TODO: Implement test for scheduling summary accuracy
        # - Test scenario with 100% scheduling efficiency (all blocks scheduled)
        # - Test scenario with 0% scheduling efficiency (no blocks scheduled)
        # - Test scenario with partial scheduling (some blocks scheduled)
        # - Verify efficiency calculation: (scheduled/total) * 100
        # - Verify all summary fields are present and accurate
        pass

    def test_complex_constraint_combinations(self, observer, time_constants, standard_transitioner):
        """
        Test scheduler with complex combinations of constraints.
        
        Verify that the scheduler correctly handles blocks with multiple
        overlapping constraints and properly determines which blocks can
        be scheduled when constraints interact in complex ways.
        """
        # TODO: Implement test for complex constraint combinations
        # - Create blocks with multiple constraints (altitude + time + airmass)
        # - Create blocks where constraints conflict with each other
        # - Schedule the blocks
        # - Verify that only blocks satisfying ALL constraints are scheduled
        # - Verify that blocks violating ANY constraint appear in missing blocks
        pass

    def test_priority_vs_constraint_interaction(self, observer, time_constants, standard_transitioner):
        """
        Test interaction between priority ordering and constraint satisfaction.
        
        Verify that high-priority blocks that violate constraints are not
        scheduled, while lower-priority blocks that satisfy constraints are
        scheduled, demonstrating proper constraint enforcement.
        """
        # TODO: Implement test for priority vs constraint interaction
        # - Create high-priority block with impossible constraints
        # - Create low-priority block with satisfiable constraints
        # - Schedule the blocks
        # - Verify low-priority block is scheduled, high-priority is missing
        # - Verify that constraints take precedence over priority
        pass

    def test_edge_case_time_windows(self, observer, time_constants, standard_transitioner):
        """
        Test scheduler behavior with edge case time windows.
        
        Verify that the scheduler handles very short time windows, overlapping
        time constraints, and blocks that barely fit within available time
        slots correctly.
        """
        # TODO: Implement test for edge case time windows
        # - Create very short scheduling window (e.g., 30 minutes)
        # - Create blocks that barely fit within the window
        # - Create blocks with overlapping time constraints
        # - Schedule the blocks
        # - Verify that only blocks fitting within time constraints are scheduled
        # - Verify proper handling of edge cases (block duration = window duration)
        pass