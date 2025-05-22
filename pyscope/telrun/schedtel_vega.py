from astroplan import Observer, FixedTarget
from astropy.time import Time
from astroplan.constraints import AirmassConstraint, AtNightConstraint, TimeConstraint
from astroplan import ObservingBlock
from astroplan.scheduling import Transitioner, PriorityScheduler, Schedule
from astropy import units as u


def viniii():
    """Test function"""
    pass


def setup_observer():
    """Create and return APO observer"""
    return Observer.at_site('apo')

def setup_target():
    """Create and return Vega target"""
    return FixedTarget.from_name('Vega')

def setup_time_constraints():
    """Setup observation time constraints"""
    noon_before = Time('2016-07-06 19:00:00', scale='utc')
    noon_after = Time('2016-07-07 19:00:00', scale='utc')
    half_night_start = Time('2016-07-07 02:00:00', scale='utc')
    half_night_end = Time('2016-07-07 08:00:00', scale='utc')
    
    return noon_before, noon_after, half_night_start, half_night_end

def create_blocks(target, time_constraint):
    """Create observation blocks for each filter"""
    read_out = 20 * u.second
    exp_time = 80 * u.second
    n_exposures = 12
    blocks = []
    
    for priority, band in enumerate(['B', 'V', 'R']):
        filter_name = band  # Explicitly set filter_name variable
        block = ObservingBlock.from_exposures(
            target=target,
            configuration={'filter': filter_name},
            time_per_exposure=exp_time,  # Changed from exposure_time to time_per_exposure
            number_exposures=1,  # Add this parameter
            priority=1,
            constraints=[time_constraint]
        )
        blocks.append(block)
    
    return blocks

def create_scheduler(constraints, observer):
    """Create and configure scheduler"""
    slew_rate = 0.8 * u.deg / u.second
    transitioner = Transitioner(
        slew_rate,
        {'filter': {('B','V'): 10*u.second,
                   ('V','R'): 10*u.second,
                   'default': 30*u.second}}
    )
    
    return PriorityScheduler(
        constraints=constraints,
        observer=observer,
        transitioner=transitioner
    )

def schedule_vega():
    """Main function to schedule Vega observations"""
    # Setup
    apo = setup_observer()
    vega = setup_target()
    noon_before, noon_after, half_night_start, half_night_end = setup_time_constraints()
    
    # Create constraints
    time_constraint = TimeConstraint(half_night_start, half_night_end)
    global_constraints = [
        AirmassConstraint(max=3, boolean_constraint=False),
        AtNightConstraint.twilight_astronomical()
    ]
    
    # Create blocks and scheduler
    blocks = create_blocks(vega, time_constraint)
    scheduler = create_scheduler(global_constraints, apo)
    schedule = Schedule(noon_before, noon_after)
    
    # Run scheduler
    scheduled = scheduler(blocks, schedule)
    
    # Return schedule's observing blocks if successful
    if scheduled:
        try:
            return schedule.observing_blocks  # Use correct attribute name
        except AttributeError:
            return schedule.scheduled_blocks  # Alternative attribute name
    return None

# ...existing code...

if __name__ == '__main__':
    from astropy.table import Table
    
    scheduled_blocks = schedule_vega()
    if scheduled_blocks:
        # Create table data
        data = {
            'Target': [],
            'Filter': [],
            'Start Time': [],
            'Duration': [],
            'Priority': []
        }
        
        # Populate table data from blocks
        for block in scheduled_blocks:
            data['Target'].append(block.target.name)
            data['Filter'].append(block.configuration['filter'])
            data['Start Time'].append(block.start_time.iso)
            data['Duration'].append(str(block.duration))
            data['Priority'].append(block.priority)
        
        # Create and display the table
        schedule_table = Table(data)
        print("\nScheduled Observations:")
        schedule_table.pprint_all()
    else:
        print("Scheduling failed!")