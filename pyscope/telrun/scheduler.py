import argparse
from textwrap import dedent
import warnings

from astropy.coordinates import SkyCoord, EarthLocation
from astropy.time import Time
import astropy.units as u

from astroplan import Observer, FixedTarget, ObservingBlock, Schedule
from astroplan.scheduling import PriorityScheduler, Transitioner, TransitionBlock
from astroplan.constraints import AltitudeConstraint, AirmassConstraint

# Suppress unnecessary warnings from astroplan/astropy
warnings.filterwarnings('ignore', module='astropy.time.core')
warnings.filterwarnings('ignore', module='astroplan.scheduling')

def create_schedule(observer, targets, start_time, end_time, duration_per_target):
    """
    Creates a simple observation schedule using astroplan.

    Args:
        observer (astroplan.Observer): The observer object.
        targets (list): A list of astroplan.FixedTarget objects.
        start_time (astropy.time.Time): The start time of the observing window.
        end_time (astropy.time.Time): The end time of the observing window.
        duration_per_target (astropy.units.Quantity): The duration for each observation block.

    Returns:
        astropy.table.Table or None: The generated schedule table, or None if scheduling fails.
    """
    # Define basic constraints (optional, but good practice)
    constraints = [
        AltitudeConstraint(min=20*u.deg),
        AirmassConstraint(max=3)
    ]

    # Create observing blocks for each target
    blocks = []
    for i, target in enumerate(targets):
        # Assigning a simple priority (can be customized later)
        priority = len(targets) - i 
        blocks.append(ObservingBlock(target, duration_per_target, priority=priority, constraints=constraints))

    # Initialize the scheduler
    # PriorityScheduler attempts to observe higher priority targets first
    # We need a transitioner to account for slew time, etc.
    # Instantiate the base Transitioner with a plausible slew rate.
    # This object is callable, fulfilling the Scheduler's requirement.
    transitioner = Transitioner(slew_rate=1*u.deg/u.second) # Adjust slew rate as needed
    scheduler = PriorityScheduler(constraints=constraints, observer=observer, transitioner=transitioner)

    # Create an empty Schedule object for the desired time window
    schedule_to_fill = Schedule(start_time, end_time)

    # Generate the schedule
    print("\nAttempting to schedule observations...")
    print(f"Observer: {observer.name} at {observer.location.lat}, {observer.location.lon}")
    print(f"Time range: {start_time} to {end_time}")
    print(f"Targets: {[t.name for t in targets]}")
    print(f"Duration per target: {duration_per_target}")

    try:
        # Call the scheduler with the blocks and the empty schedule object
        schedule = scheduler(blocks, schedule_to_fill)
        print("\nSchedule generated successfully!")
        return schedule
    except Exception as e:
        print(f"\nError generating schedule: {e}")
        print("This might happen if no targets are observable within the constraints and time range.")
        return None

def main():
    parser = argparse.ArgumentParser(
        description="Create a simple astronomical observation schedule using astroplan.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=dedent("""
        Example Usage:
        python scheduler.py --lat 34.0 --lon -118.0 --elevation 300 \
                          --targets "M31,M42,M13" \
                          --start "2025-05-02 01:00:00" \
                          --end "2025-05-02 05:00:00" \
                          --duration 30
        """)
    )

    # Observer arguments
    parser.add_argument("--name", type=str, default="Observatory", help="Name of the observer/observatory.")
    parser.add_argument("--lat", type=float, required=True, help="Latitude of the observer (degrees).")
    parser.add_argument("--lon", type=float, required=True, help="Longitude of the observer (degrees).")
    parser.add_argument("--elevation", type=float, default=0, help="Elevation of the observer (meters).")

    # Target arguments
    parser.add_argument("--targets", type=str, required=True, 
                        help="Comma-separated list of target names (resolvable by SkyCoord, e.g., 'M31,M42').")

    # Time arguments
    parser.add_argument("--start", type=str, required=True, help="Start time for scheduling (YYYY-MM-DD HH:MM:SS).")
    parser.add_argument("--end", type=str, required=True, help="End time for scheduling (YYYY-MM-DD HH:MM:SS).")

    # Observation arguments
    parser.add_argument("--duration", type=float, default=30, help="Duration of each observation block (minutes).")

    args = parser.parse_args()

    # --- Process arguments --- 

    # Create Observer
    location = EarthLocation.from_geodetic(args.lon*u.deg, args.lat*u.deg, args.elevation*u.m)
    observer = Observer(name=args.name, location=location)

    # Create Targets
    target_names = [name.strip() for name in args.targets.split(',')]
    try:
        targets = [FixedTarget(coord=SkyCoord.from_name(name), name=name) for name in target_names]
    except Exception as e:
        print(f"Error resolving target names: {e}. Make sure names are valid (e.g., 'M31', 'Sirius').")
        return

    # Create Time range
    try:
        start_time = Time(args.start)
        end_time = Time(args.end)
    except ValueError as e:
        print(f"Error parsing time strings: {e}. Use 'YYYY-MM-DD HH:MM:SS' format.")
        return
        
    if start_time >= end_time:
        print("Error: Start time must be before end time.")
        return

    # Observation duration
    duration_per_target = args.duration * u.minute

    # --- Create and Print Schedule --- 
    schedule = create_schedule(observer, targets, start_time, end_time, duration_per_target)

    # Check if the schedule object exists and if it contains any observing blocks
    if schedule is not None and len(schedule.observing_blocks) > 0:
        print("\n--- Generated Schedule ---")
        # Use the to_table() method to get a printable Astropy Table
        schedule_table = schedule.to_table(show_transitions=True) # Set show_transitions=False to hide them
        print(schedule_table)
    elif schedule is not None: # Handles the case where schedule exists but is empty
        print("\n--- No observations scheduled --- ")
        print("No targets could be scheduled within the specified time and constraints.")

if __name__ == "__main__":
    main()
