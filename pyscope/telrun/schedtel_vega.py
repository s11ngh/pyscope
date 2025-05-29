from astroplan import Observer, FixedTarget
from astropy.time import Time
from astroplan.constraints import AirmassConstraint, AtNightConstraint, TimeConstraint
from astroplan import ObservingBlock
from astroplan.scheduling import Transitioner, PriorityScheduler, Schedule
from astropy import units as u


def setup_observer():
    """Create and return APO observer"""
    return Observer.at_site('apo')

def setup_targets():
    """Create and return multiple targets"""
    targets = [
        FixedTarget.from_name('Vega'),
        FixedTarget.from_name('Rigel'),
        FixedTarget.from_name('Aldebaran'),
        FixedTarget.from_name('Polaris'),
        FixedTarget.from_name('Altair')
    ]
    return targets

def setup_time_constraints():
    """Setup observation time constraints"""
    # 겨울철 관측 시간으로 변경
    noon_before = Time('2016-12-06 19:00:00', scale='utc')
    noon_after = Time('2016-12-07 19:00:00', scale='utc')
    half_night_start = Time('2016-12-07 02:00:00', scale='utc')
    half_night_end = Time('2016-12-07 08:00:00', scale='utc')
    
    return noon_before, noon_after, half_night_start, half_night_end

def create_blocks(targets, time_constraint):
    """Create observation blocks for multiple targets"""
    blocks = []
    exp_time = 80 * u.second
    
    # targets가 리스트가 아닌 경우 리스트로 변환
    if not isinstance(targets, list):
        targets = [targets]
    
    for target in targets:
        for priority, band in enumerate(['B', 'V', 'R']):
            block = ObservingBlock.from_exposures(
                target=target,
                configuration={'filter': band},
                time_per_exposure=exp_time,
                number_exposures=1,
                priority=1,  # 모든 타겟에 동일한 우선순위 부여
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

def schedule_stars():
    """Main function to schedule multiple star observations"""
    try:
        # Setup
        apo = setup_observer()
        targets = setup_targets()
        noon_before, noon_after, half_night_start, half_night_end = setup_time_constraints()
        
        # Create constraints with 더 완화된 조건
        time_constraint = TimeConstraint(half_night_start, half_night_end)
        global_constraints = [
            AirmassConstraint(max=5, boolean_constraint=False),  # max airmass 증가
            AtNightConstraint.twilight_civil()  # 더 관대한 twilight 조건
        ]
        
        # Create blocks and scheduler
        blocks = create_blocks(targets, time_constraint)
        scheduler = create_scheduler(global_constraints, apo)
        schedule = Schedule(noon_before, noon_after)
        
        # Run scheduler
        scheduled = scheduler(blocks, schedule)
        
        if scheduled:
            return schedule.observing_blocks
        return None
    except Exception as e:
        print(f"Error in scheduling: {e}")
        return None

if __name__ == '__main__':
    from astropy.table import Table
    
    print("Attempting to schedule observations...")
    scheduled_blocks = schedule_stars()
    if scheduled_blocks:
        data = {
            'Target': [],
            'Filter': [],
            'Start Time': [],
            'End Time': [],    # Added End Time
            'Duration': [],
            'Priority': []
        }
        
        print(f"\nTotal scheduled blocks: {len(scheduled_blocks)}")
        
        for block in scheduled_blocks:
            data['Target'].append(block.target.name)
            data['Filter'].append(block.configuration['filter'])
            data['Start Time'].append(block.start_time.iso)
            data['End Time'].append((block.start_time + block.duration).iso)  # Calculate end time
            data['Duration'].append(str(block.duration))
            data['Priority'].append(block.priority)
        
        schedule_table = Table(data)
        print("\nScheduled Observations:")
        schedule_table.pprint_all()
    else:
        print("Scheduling failed!")