from astroplan import Observer, FixedTarget, ObservingBlock
from astropy.time import Time
from astroplan.constraints import AtNightConstraint, AirmassConstraint, TimeConstraint
from astroplan.scheduling import Transitioner, SequentialScheduler, PriorityScheduler, Schedule
from astropy import units as u

apo = Observer.at_site('apo')

deneb = FixedTarget.from_name('Deneb')
m13 = FixedTarget.from_name('M13')
sirius = FixedTarget.from_name('Sirius')  # New target

noon_before = Time('2016-07-06 19:00')
noon_after = Time('2016-07-07 19:00')

global_constraints = [
    AirmassConstraint(max=3, boolean_constraint=False),
    AtNightConstraint.twilight_civil()
]

read_out = 20 * u.second
deneb_exp = 60 * u.second
m13_exp = 100 * u.second
sirius_exp = 80 * u.second

n = 16

half_night_start = Time('2016-07-07 02:00')
half_night_end = Time('2016-07-07 08:00')
first_half_night = TimeConstraint(half_night_start, half_night_end)

blocks = []
for priority, bandpass in enumerate(['B', 'G', 'R']):
    b = ObservingBlock.from_exposures(
        deneb, priority, deneb_exp, n, read_out,
        configuration={'filter': bandpass},
        constraints=[first_half_night]
    )
    blocks.append(b)

    b = ObservingBlock.from_exposures(
        m13, priority, m13_exp, n, read_out,
        configuration={'filter': bandpass},
        constraints=[first_half_night]
    )
    blocks.append(b)

    b = ObservingBlock.from_exposures(
        sirius, priority, sirius_exp, n, read_out,
        configuration={'filter': bandpass},
        constraints=[first_half_night]
    )
    blocks.append(b)

slew_rate = 0.8 * u.deg / u.second
transitioner = Transitioner(
    slew_rate,
    {'filter': {('B', 'G'): 10 * u.second, ('G', 'R'): 10 * u.second, 'default': 30 * u.second}}
)

seq_scheduler = SequentialScheduler(
    constraints=global_constraints,
    observer=apo,
    transitioner=transitioner
)
sequential_schedule = Schedule(noon_before, noon_after)
seq_scheduler(blocks, sequential_schedule)

pri_scheduler = PriorityScheduler(
    constraints=global_constraints,
    observer=apo,
    transitioner=transitioner
)
priority_schedule = Schedule(noon_before, noon_after)
pri_scheduler(blocks, priority_schedule)

schedule_table = sequential_schedule.to_table()
priority_table = priority_schedule.to_table()

def print_priority_schedule():
    return priority_table

def print_sequential_schedule():
    return schedule_table

print("=== PRIORITY SCHEDULE ===")
print(print_priority_schedule())

print("\n=== SEQUENTIAL SCHEDULE ===")
print(print_sequential_schedule())
