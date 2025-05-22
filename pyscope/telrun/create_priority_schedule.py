from astroplan import Observer, Constraint
from astroplan import FixedTarget
from astropy.time import Time
from astroplan.constraints import AtNightConstraint, AirmassConstraint, AltitudeConstraint
from astroplan import ObservingBlock
from astroplan.constraints import TimeConstraint
from astropy import units as u
from astroplan.scheduling import Transitioner
from astroplan.scheduling import SequentialScheduler
from astroplan.scheduling import Schedule
from astroplan.scheduling import PriorityScheduler
from typing import List, Dict, Union, Optional, Tuple, Any
from astroplan.scheduling import Scheduler
from astropy.coordinates import EarthLocation

def create_priority_schedule(
    targets: List[FixedTarget],
    observer: Observer,
    start_time: Time,
    end_time: Time,
    priorities: Optional[List[int]] = None,
    durations: Optional[Union[List[u.Quantity], u.Quantity]] = None,
    constraints: Optional[List[Constraint]] = None,
    slew_rate: u.Quantity = 1 * u.deg / u.second,
    time_resolution: u.Quantity = 1 * u.minute,
    gap_time: u.Quantity = 5 * u.minute,
    instrument_reconfig_times: Optional[Dict[str, Dict[Tuple[str, str], u.Quantity]]] = None,
    configuration: Optional[Union[List[Dict[str, Any]], Dict[str, Any]]] = None,
    exposure_time: Optional[u.Quantity] = None,
    num_exposures: Optional[Union[List[int], int]] = None,
    read_out_time: u.Quantity = 20 * u.second,
    names: Optional[List[str]] = None,
) -> Tuple[Schedule, PriorityScheduler]:
    """
    Create a priority schedule for astronomical observations.
    
    This is a convenience function that wraps the PriorityScheduler to make it
    easier to create and use a schedule based on target priorities. It's designed
    to be a robust test harness for scheduling scenarios.
    
    Parameters
    ----------
    targets : List[FixedTarget]
        The targets to be scheduled for observation.
    
    observer : Observer
        The observer/site to do the scheduling for.
    
    start_time : Time
        The starting time of the schedule.
    
    end_time : Time
        The ending time of the schedule.
    
    priorities : List[int], optional
        The priority of each target (1 is highest priority, no maximum).
        If None, targets will be prioritized in the order they are provided.
    
    durations : List[u.Quantity] or u.Quantity, optional
        The exposure/observation time for each target. If a single value is provided,
        it will be applied to all targets. If None, durations will be calculated from
        exposure_time and num_exposures.
    
    constraints : List[Constraint], optional
        The constraints to apply to all observations. If None, only an AltitudeConstraint
        with min=0 degrees will be applied.
    
    slew_rate : u.Quantity, optional
        The slew rate of the telescope. Default is 1 deg/s.
    
    time_resolution : u.Quantity, optional
        The smallest factor of time used in scheduling. Default is 1 minute.
    
    gap_time : u.Quantity, optional
        The maximum length of time a transition between ObservingBlocks could take.
        Default is 5 minutes.
    
    instrument_reconfig_times : Dict, optional
        If not None, gives a mapping from property names to another dictionary.
        The second dictionary maps 2-tuples of states to the time it takes to
        transition between those states, can also take a 'default' key mapped
        to a default transition time.
    
    configuration : List[Dict] or Dict, optional
        Configuration metadata for each observation. If a single dict is provided,
        it will be applied to all targets.
    
    exposure_time : u.Quantity, optional
        The exposure time for each target. Used with num_exposures to calculate
        durations if durations is None.
    
    num_exposures : List[int] or int, optional
        Number of exposures for each target. Used with exposure_time to calculate
        durations if durations is None.
    
    read_out_time : u.Quantity, optional
        The readout time between exposures. Default is 20 seconds.
    
    names : List[str], optional
        User-defined name or ID for each observing block. If None, targets will
        use their own names.
    
    Returns
    -------
    schedule : Schedule
        A schedule object with the observing blocks scheduled according to priority.
    
    scheduler : PriorityScheduler
        The scheduler object used to create the schedule.
    """
    # Input validation and standardization
    n_targets = len(targets)
    
    # Handle priorities
    if priorities is None:
        priorities = list(range(1, n_targets + 1))
    elif len(priorities) != n_targets:
        raise ValueError("Number of priorities must match number of targets")
    priorities =[1] * n_targets
    # Handle durations
    if durations is None:
        if exposure_time is None or num_exposures is None:
            raise ValueError("Either durations or both exposure_time and num_exposures must be provided")
        
        if not isinstance(num_exposures, list):
            num_exposures = [num_exposures] * n_targets
        elif len(num_exposures) != n_targets:
            raise ValueError("Number of exposures must match number of targets")
        
        durations = [(exposure_time + read_out_time) * n_exp for n_exp in num_exposures]
    elif not isinstance(durations, list):
        durations = [durations] * n_targets
    elif len(durations) != n_targets:
        raise ValueError("Number of durations must match number of targets")
    
    # Ensure all durations are Quantity objects
    for i, duration in enumerate(durations):
        if not isinstance(duration, u.Quantity):
            durations[i] = duration * u.minute  # Default to minutes if no unit specified
    
    # Handle configuration
    if configuration is None:
        configuration = [{}] * n_targets
    elif not isinstance(configuration, list):
        configuration = [configuration] * n_targets
    elif len(configuration) != n_targets:
        raise ValueError("Number of configurations must match number of targets")
    
    # Handle names
    if names is None:
        names = [target.name for target in targets]
    elif len(names) != n_targets:
        raise ValueError("Number of names must match number of targets")
    
    # Create the observing blocks
    blocks = []
    for i in range(n_targets):
        block = ObservingBlock(targets[i], durations[i], priorities[i], 
                              configuration=configuration[i], 
                              constraints=None, name=names[i])
        blocks.append(block)
    
    # Create the schedule
    schedule = Schedule(start_time, end_time)
    
    # Create the transitioner
    transitioner = Transitioner(slew_rate=slew_rate, 
                               instrument_reconfig_times=instrument_reconfig_times)
    
    # Create the scheduler
    scheduler = PriorityScheduler(constraints=constraints, 
                                 observer=observer,
                                 transitioner=transitioner,
                                 gap_time=gap_time,
                                 time_resolution=time_resolution)
    
    # Run the scheduler
    scheduler(blocks, schedule)
    
    return schedule, scheduler


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