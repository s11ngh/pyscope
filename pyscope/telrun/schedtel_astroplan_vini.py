#schuduling with with astroplan
#We want to observe Deneb and M13 in the B, V and R 
#filters. We are scheduled for the first half-night
# on July 6 2016 and want to know the order we should
# schedule the targets in.





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



# obsever
apo = Observer.at_site('apo')



# Initialize the targets
deneb = FixedTarget.from_name('Deneb')
m13 = FixedTarget.from_name('M13')


# print the targets
print(deneb)
print("\n")
print(m13)



# Define time boundaries
noon_before = Time('2016-07-06 19:00')
noon_after = Time('2016-07-07 19:00')



# create the list of constraints that all targets must satisfy
global_constraints = [AirmassConstraint(max = 3, boolean_constraint = False),
                      AtNightConstraint.twilight_civil()]






# Define the read-out time, exposure duration and number of exposures
read_out = 20 * u.second
deneb_exp = 60*u.second
m13_exp = 100*u.second
n = 16
blocks = []


# half night start and end times
# Define the time constraint for the first half-night
# on July 6, 2016
half_night_start = Time('2016-07-07 02:00')
half_night_end = Time('2016-07-07 08:00')
first_half_night = TimeConstraint(half_night_start, half_night_end)


# Create ObservingBlocks for each filter and target with our time
# constraint, and durations determined by the exposures needed
for priority, bandpass in enumerate(['B', 'G', 'R']):
    # We want each filter to have separate priority (so that target
    # and reference are both scheduled)
    b = ObservingBlock.from_exposures(deneb, priority, deneb_exp, n, read_out,
                                        configuration = {'filter': bandpass},
                                        constraints = [first_half_night])
    blocks.append(b)
    b = ObservingBlock.from_exposures(m13, priority, m13_exp, n, read_out,
                                        configuration = {'filter': bandpass},
                                        constraints = [first_half_night])
    blocks.append(b)






# Initialize a transitioner object with the slew rate and/or the
# duration of other transitions (e.g. filter changes)
slew_rate = .8*u.deg/u.second
transitioner = Transitioner(slew_rate,
                            {'filter':{('B','G'): 10*u.second,
                                       ('G','R'): 10*u.second,
                                       'default': 30*u.second}})









# Initialize the sequential scheduler with the constraints and transitioner
seq_scheduler = SequentialScheduler(constraints = global_constraints,
                                    observer = apo,
                                    transitioner = transitioner)
# Initialize a Schedule object, to contain the new schedule
sequential_schedule = Schedule(noon_before, noon_after)

# Call the schedule with the observing blocks and schedule to schedule the blocks
seq_scheduler(blocks, sequential_schedule)




# Initialize the priority scheduler with the constraints and transitioner
prior_scheduler = PriorityScheduler(constraints = global_constraints,
                                    observer = apo,
                                    transitioner = transitioner)
# Initialize a Schedule object, to contain the new schedule
priority_schedule = Schedule(noon_before, noon_after)

# Call the schedule with the observing blocks and schedule to schedule the blocks
prior_scheduler(blocks, priority_schedule)


print("nigros")
print(priority_schedule.to_table())