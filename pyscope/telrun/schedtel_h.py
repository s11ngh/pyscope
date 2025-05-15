import datetime
import logging

import astroplan
from astropy import coordinates as coord
from astropy import time as astrotime
from astropy import units as u
from astropy.table import Table
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

# Set up the observatory and targets
from astroplan import Observer, FixedTarget
from astroplan.constraints import TimeConstraint

observatory = Observer.at_site('apo')
deneb = FixedTarget.from_name('Deneb')
m13 = FixedTarget.from_name('M13')

# Define time boundaries
noon_before = astrotime.Time('2016-07-06 19:00')
noon_after = astrotime.Time('2016-07-07 19:00')

# Define 6-hour observation window
half_night_start = astrotime.Time('2016-07-07 02:00')
half_night_end = astrotime.Time('2016-07-07 08:00')  # Exactly 6 hours after start
first_half_night = TimeConstraint(half_night_start, half_night_end)

# Define observation parameters
read_out = 20 * u.second
deneb_exp = 60 * u.second
m13_exp = 100 * u.second
n = 16

# Define max_altitude for the scheduler
max_altitude = -12

# Create block_group in the format expected by basic_scheduler
block_group = []

# Create blocks for each filter and target
for priority, bandpass in enumerate(['B', 'G', 'R']):
    # Calculate total duration for each observation
    deneb_duration = deneb_exp * n + read_out * n
    m13_duration = m13_exp * n + read_out * n
    
    # Create Deneb block for this filter
    deneb_block = {
        "ID": astrotime.Time.now().mjd,
        "name": f"Deneb_{bandpass}",
        "target": deneb,
        "target_ra": deneb.ra.deg,
        "target_dec": deneb.dec.deg,
        "duration": deneb_duration,
        "filter": bandpass,
        "exposure": deneb_exp.to(u.second).value,
        "nexp": n,
        "priority": priority,
        "constraints": [first_half_night],
        "start_time": None,
        "end_time": None,
        "status": "U",
        "message": "Unscheduled",
        "observer": ["observer1"],
        "code": "test",
        "title": f"Deneb {bandpass}-band Observation",
        "filename": "",
        "pm_ra_cosdec": 0 * u.arcsec/u.hour,
        "pm_dec": 0 * u.arcsec/u.hour,
    }
    block_group.append(deneb_block)
    
    # Create M13 block for this filter
    m13_block = {
        "ID": astrotime.Time.now().mjd + 0.001 * (priority + 0.5),  # Ensure unique IDs
        "name": f"M13_{bandpass}",
        "target": m13,
        "target_ra": m13.ra.deg,
        "target_dec": m13.dec.deg,
        "duration": m13_duration,
        "filter": bandpass,
        "exposure": m13_exp.to(u.second).value,
        "nexp": n,
        "priority": priority,
        "constraints": [first_half_night],
        "start_time": None,
        "end_time": None,
        "status": "U",
        "message": "Unscheduled",
        "observer": ["observer1"],
        "code": "test",
        "title": f"M13 {bandpass}-band Observation",
        "filename": "",
        "pm_ra_cosdec": 0 * u.arcsec/u.hour,
        "pm_dec": 0 * u.arcsec/u.hour,
    }
    block_group.append(m13_block)
    



# Define the basic_scheduler function with hardcoded transition times
def basic_scheduler(block_group, schedule):
    # Set start time to half-night start
    start_time = half_night_start
    end_time = half_night_end
    
    # Hardcoded transition times based on filter changes
    TRANSITION_TIMES = {
        ('B', 'G'): 10 * u.second,
        ('G', 'R'): 10 * u.second,
        # Default transition time for target changes (slew)
        'default': 30 * u.second
    }
    
    # Function to get transition time between blocks
    def get_transition_time(block1, block2):
        filter_pair = (block1['filter'], block2['filter'])
        if filter_pair in TRANSITION_TIMES:
            return TRANSITION_TIMES[filter_pair]
        return TRANSITION_TIMES['default']
    
    for i in range(len(block_group)):
        if block_group[0]["start_time"] is None:
            try:
                if len(schedule) > 0:
                    print(f"Last end time: {schedule[-1]['end_time'].iso}")

                    # If there's a block group constraint, use it
                    if block_group[0]["constraints"] is not None:
                        if hasattr(block_group[0]["constraints"][0], 'min'):
                            block_group[0]["start_time"] = block_group[0]["constraints"][0].min
                        else:
                            # Otherwise, use the last end time
                            block_group[0]["start_time"] = schedule[-1]["end_time"]
                    else:
                        # If there's no block group constraint, use the last end time
                        block_group[0]["start_time"] = schedule[-1]["end_time"]

                    # Calculate transition time
                    transition_time = get_transition_time(block_group[0], schedule[-1])
                    
                    # If last end time + transition time is greater than start time, 
                    # use last end time + transition
                    if block_group[0]["start_time"] < schedule[-1]["end_time"] + transition_time:
                        block_group[0]["start_time"] = schedule[-1]["end_time"] + transition_time
                else:
                    # First block starts at the beginning of the half night
                    block_group[0]["start_time"] = start_time
            except Exception as e:
                print(f"Error in scheduler: {e}")
                # If there's a block group constraint, use it
                if block_group[0]["constraints"] is not None:
                    if hasattr(block_group[0]["constraints"][0], 'min'):
                        block_group[0]["start_time"] = block_group[0]["constraints"][0].min
                    else:
                        block_group[0]["start_time"] = start_time
                else:
                    block_group[0]["start_time"] = start_time

        # Calculate end time from transition times
        for i, block in enumerate(block_group):    
            print(f"Scheduling {block['name']} at {block['start_time'].iso if block['start_time'] else 'None'}")
            
            if i == len(block_group) - 1:
                block["end_time"] = block["start_time"] + block["duration"]
                block["status"] = "S"
                block["message"] = "Scheduled"
                schedule.append(block)
                return schedule
            else:
                next_block = block_group[i + 1]
            
            transition_time = get_transition_time(block, next_block)
            
            block["end_time"] = block["start_time"] + block["duration"]
            next_block["start_time"] = block["end_time"] + transition_time
            block["status"] = "S"
            block["message"] = "Scheduled"
            schedule.append(block)              
            
            if block["end_time"] > end_time:
                print(f"End time of {block['name']} is greater than half night end")
                # We continue anyway to see what would be scheduled

    return schedule

# Run the scheduler
schedule = []
scheduled_blocks = basic_scheduler(block_group, schedule)


from pyscope.telrun.sched_ecsv import save_schedule_to_ecsv

save_schedule_to_ecsv(scheduled_blocks, 'schedule.ecsv')

