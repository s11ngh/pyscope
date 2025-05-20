from astroplan import Observer
from astroplan import FixedTarget
from astropy.time import Time
from astroplan.constraints import AtNightConstraint, AirmassConstraint
from astroplan import ObservingBlock
from astroplan.constraints import TimeConstraint
from astropy import units as u
from astroplan.scheduling import Transitioner
from astroplan.scheduling import SequentialScheduler
from astroplan.scheduling import Schedule
from astroplan.scheduling import PriorityScheduler
from typing import List, Dict, Union, Optional, Tuple


def create_schedule(
    observer_site: str = 'apo',
    targets: List[str] = ['Deneb', 'M13'],
    start_time: str = '2016-07-06 19:00',
    end_time: str = '2016-07-07 19:00',
    constraint_window: Optional[Tuple[str, str]] = ('2016-07-07 02:00', '2016-07-07 08:00'),
    exposure_times: Optional[Dict[str, float]] = None,
    num_exposures: int = 16,
    read_out_time: float = 20,
    filters: List[str] = ['B', 'G', 'R'],
    max_airmass: float = 3,
    slew_rate: float = 0.8,
    filter_change_times: Optional[Dict] = None,
    scheduler_type: str = 'both'  # 'priority', 'sequential', or 'both'
):
    """
    Create an observation schedule using astroplan.
    
    Parameters
    ----------
    observer_site : str
        Name of the observatory site
    targets : List[str]
        List of target names to observe
    start_time : str
        Start time of the observation window in 'YYYY-MM-DD HH:MM' format
    end_time : str
        End time of the observation window in 'YYYY-MM-DD HH:MM' format
    constraint_window : Optional[Tuple[str, str]]
        Time constraint window in ('YYYY-MM-DD HH:MM', 'YYYY-MM-DD HH:MM') format
        Set to None to not use a time constraint
    exposure_times : Optional[Dict[str, float]]
        Dictionary mapping target names to exposure times in seconds
        If None, defaults to 60s for first target and 100s for second target
    num_exposures : int
        Number of exposures to take per target and filter
    read_out_time : float
        Read out time in seconds
    filters : List[str]
        List of filters to use
    max_airmass : float
        Maximum airmass constraint
    slew_rate : float
        Telescope slew rate in degrees per second
    filter_change_times : Optional[Dict]
        Dictionary specifying filter change times
        If None, uses default values
    scheduler_type : str
        Type of scheduler to use ('priority', 'sequential', or 'both')
        
    Returns
    -------
    Tuple[Schedule, Schedule]
        A tuple containing (priority_schedule, sequential_schedule)
        If scheduler_type is 'priority', only priority_schedule will be populated
        If scheduler_type is 'sequential', only sequential_schedule will be populated
        If scheduler_type is 'both', both schedules will be populated
    """
    # Set up observer
    observer = Observer.at_site(observer_site)
    
    # Set up targets
    target_objects = {}
    for target in targets:
        target_objects[target] = FixedTarget.from_name(target)
    
    # Set up times
    noon_before = Time(start_time)
    noon_after = Time(end_time)
    
    # Set up global constraints
    global_constraints = [
        AirmassConstraint(max=max_airmass, boolean_constraint=False),
        AtNightConstraint.twilight_civil()
    ]
    
    # Set up time constraint if provided
    time_constraint = None
    if constraint_window:
        half_night_start = Time(constraint_window[0])
        half_night_end = Time(constraint_window[1])
        time_constraint = TimeConstraint(half_night_start, half_night_end)
    
    # Set up exposure times
    if exposure_times is None:
        if len(targets) >= 2:
            exposure_times = {targets[0]: 60, targets[1]: 100}
            # Set default exposure time for any additional targets
            for target in targets[2:]:
                exposure_times[target] = 80
        else:
            exposure_times = {targets[0]: 60}
    
    # Convert to astropy units
    read_out = read_out_time * u.second
    
    # Create observing blocks
    blocks = []
    for priority, bandpass in enumerate(filters):
        for target_name, target_obj in target_objects.items():
            target_exp = exposure_times[target_name] * u.second
            constraints = [time_constraint] if time_constraint else []
            
            b = ObservingBlock.from_exposures(
                target_obj, priority, target_exp, num_exposures, read_out,
                configuration={'filter': bandpass},
                constraints=constraints
            )
            blocks.append(b)
    
    # Set up transitioner
    if filter_change_times is None:
        filter_change_times = {
            'filter': {
                ('B', 'G'): 10 * u.second,
                ('G', 'R'): 10 * u.second,
                'default': 30 * u.second
            }
        }
    
    slew_rate_with_units = slew_rate * u.deg / u.second
    transitioner = Transitioner(slew_rate_with_units, filter_change_times)
    
    # Set up schedulers
    seq_scheduler = SequentialScheduler(
        constraints=global_constraints,
        observer=observer,
        transitioner=transitioner
    )
    
    pri_scheduler = PriorityScheduler(
        constraints=global_constraints,
        observer=observer,
        transitioner=transitioner
    )
    
    # Create schedules
    sequential_schedule = Schedule(noon_before, noon_after)
    priority_schedule = Schedule(noon_before, noon_after)
    
    # Run the appropriate scheduler
    if scheduler_type.lower() == 'priority' or scheduler_type.lower() == 'both':
        pri_scheduler(blocks, priority_schedule)
        
    if scheduler_type.lower() == 'sequential' or scheduler_type.lower() == 'both':
        seq_scheduler(blocks, sequential_schedule)
    
    return priority_schedule, sequential_schedule


def print_schedule(schedule):
    """
    Convert a schedule to a table and return it
    
    Parameters
    ----------
    schedule : Schedule
        The schedule to print
        
    Returns
    -------
    Table
        The schedule as a table
    """
    return schedule.to_table()


# Example usage of the function with default parameters
if __name__ == "__main__":
    # This recreates the original script behavior
    priority_schedule, sequential_schedule = create_schedule()
    
    print(type(priority_schedule))
    print(type(sequential_schedule))
    
    priority_table = print_schedule(priority_schedule)
    sequential_table = print_schedule(sequential_schedule)
    
    print(priority_table)
    print(sequential_table)
