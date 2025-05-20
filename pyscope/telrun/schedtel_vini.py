"""
This file implements a basic astronomical observation scheduler for telescope operations.
It handles scheduling observation blocks during nighttime, specifically for the Palomar Observatory.
The scheduler:
1. Creates an observation block for the Andromeda Galaxy (M31)
2. Determines appropriate observation times based on sunset and sunrise
3. Handles transitions between observations
4. Saves the schedule to a file
The code is designed to ensure observations occur during dark time and handles 
timing constraints and transition times between observations.
"""

from astropy import time as astrotime
from astropy import units as u
from astropy import coordinates as coord
from astroplan import Observer, FixedTarget, ObservingBlock
import datetime
from astropy.coordinates import SkyCoord, EarthLocation
from pyscope.telrun.sched_ecsv import save_schedule_to_ecsv
import os
from astropy.table import Table
from astropy.io import ascii


#-------------------------------------------------------------------------------------


# Define the geographical coordinates of Palomar Observatory
# lat: 33.356 degrees North
# lon: -116.863 degrees West (negative for western longitude)
# height: 1712 meters above sea level
location = EarthLocation(lat=33.356*u.deg, lon=-116.863*u.deg, height=1712*u.m)
# Create an Observer object representing Palomar Observatory for astronomical calculations
observatory = Observer(location=location)



# Get current date and time for schedule planning
date = datetime.datetime.now()



# Create a target object for M31 (Andromeda Galaxy)
# SkyCoord.from_name looks up the coordinates of M31 from astronomical databases
# FixedTarget creates an object suitable for scheduling observations
target = FixedTarget(SkyCoord.from_name('M31'))




# Define an observation block dictionary containing all necessary parameters
block = {
    "ID": astrotime.Time.now().mjd,          # Unique identifier using Modified Julian Date
    "name": "M31_observation",               # Name of the observation
    "target": target,                        # Target object (M31)
    "target_ra": target.ra.deg,             # Right Ascension in degrees
    "target_dec": target.dec.deg,           # Declination in degrees
    "duration": 30 * u.minute,              # Total duration of observation
    "filter": 'R',                          # Red filter for observation
    "exposure": 300,                        # Individual exposure time (5 minutes)
    "nexp": 6,                              # Number of exposures
    "priority": 1,                          # Priority level of observation
    "constraints": None,                     # No timing constraints
    "start_time": None,                     # Start time (to be set by scheduler)
    "end_time": None,                       # End time (to be set by scheduler)
    "status": "U",                          # Status (U = Unscheduled)
    "message": "Unscheduled",               # Status message
    "observer": ["observer1"],              # Observer name(s)
    "code": "test",                         # Project code
    "title": "M31 R-band Observation",      # Descriptive title
    "filename": "",                         # Output filename
    "pm_ra_cosdec": 0 * u.arcsec/u.hour,   # Proper motion in RA (0 for fixed target)
    "pm_dec": 0 * u.arcsec/u.hour,         # Proper motion in Dec (0 for fixed target)
}

# Mock class to simulate telescope reconfiguration time calculations
class DummyReconfig:
    def calc_reconfig_time_blocks(self, block1, block2, location, verbose=False):
        # Returns a fixed transition time of 30 seconds between observations
        return 30 * u.second

# Create an instance of the DummyReconfig class
reconfig_file = DummyReconfig()

def basic_scheduler(block_group, schedule):
    """
    Main scheduling function that determines observation times based on astronomical constraints
    Parameters:
    - block_group: List of observation blocks to be scheduled
    - schedule: Existing schedule (empty list for new schedule)
    """
    # Convert current date to astronomical time format
    current_time = astrotime.Time(
        date,
        format="datetime",
    )
    
    # Calculate next sunset and sunrise times using observatory location
    # horizon=max_altitude sets the sun's position below horizon (-12 degrees) for dark time
    sun_set = observatory.sun_set_time(current_time, which="next", horizon=max_altitude * u.deg)
    sun_rise = observatory.sun_rise_time(current_time, which="next", horizon=max_altitude * u.deg)
    
    # Convert sunset/sunrise times to Modified Julian Date (MJD) format
    start_time = sun_set.mjd
    start_time = astrotime.Time(start_time, format="mjd")
    end_time = sun_rise.mjd
    end_time = astrotime.Time(end_time, format="mjd")
    
    # Process each block in the block group
    for i in range(len(block_group)):
        # Check if the first block needs a start time
        if block_group[0]["start_time"] is None:
            try:
                # If there are previous observations in schedule
                if len(schedule) > 0:
                    print(f"Last end time: {schedule[-1]['end_time']}")

                    # Check for timing constraints
                    if block_group[0]["constraints"] is not None:
                        block_group[0]["start_time"] = block_group[0]["constraints"][0].min 
                    else:
                        # Use end time of previous observation
                        block_group[0]["start_time"] = schedule[-1]["end_time"]

                    # Add transition time between observations
                    transition_time = reconfig_file.calc_reconfig_time_blocks(
                        block_group[0], schedule[-1], location, verbose=False)
                    block_group[0]["start_time"] = block_group[0]["start_time"] + transition_time
                else:
                    # For first observation, use sunset time
                    block_group[0]["start_time"] = start_time

            except Exception as e:
                # If any error occurs, default to starting at sunset
                print(f"Notice: Starting new schedule at sunset ({e})")
                block_group[0]["start_time"] = start_time

        # Calculate end times and handle transitions between blocks
        for i, block in enumerate(block_group):    
            current_obj = block["target"]

            # Handle last block in group
            if i == len(block_group) - 1:
                block["end_time"] = block["start_time"] + block["duration"]
                block["status"] = "S"  # Mark as scheduled
                block["message"] = "Scheduled successfully"
                schedule.append(block)
                return schedule
            else:
                # Handle transitions between blocks
                next_block = block_group[i + 1]
                next_obj = next_block["target"]
                
                # Calculate transition time and total time needed
                transition_time = reconfig_file.calc_reconfig_time_blocks(
                    block, next_block, location, verbose=False)
                total_time = transition_time + block["duration"]
                
                # Set end time for current block and start time for next block
                block["end_time"] = block["start_time"] + total_time
                next_block["start_time"] = block["end_time"]
                schedule.append(block)              
                
                # Check if observation extends past sunrise
                if block["end_time"] > end_time:
                    print("End time is greater than sunrise")

    return schedule

# Define maximum solar altitude for night observations
# -12 degrees below horizon is astronomical twilight
max_altitude = -12  

# Initialize empty schedule and create block group with single M31 observation
schedule = []
block_group = [block]

# Execute the scheduler
scheduled_blocks = basic_scheduler(block_group, schedule)

# Process and display results
if len(scheduled_blocks) > 0:
    # Print details of scheduled observations
    print("\nScheduled observation:")
    for block in scheduled_blocks:
        print(f"Target: {block['name']}")
        print(f"Start time: {block['start_time'].iso}")
        print(f"End time: {block['end_time'].iso}")
        print(f"Status: {block['status']}")
        print(f"Message: {block['message']}")
    
    # Generate unique filename based on start time
    first_time = scheduled_blocks[0]["start_time"].strftime("%Y-%m-%dT%H-%M-%S")
    base_filename = f"schedule_vini_{first_time}.ecsv"
    
    # Handle file naming conflicts
    counter = 1
    filename = base_filename
    while True:
        try:
            # Attempt to save schedule to ECSV file
            save_schedule_to_ecsv(scheduled_blocks, filename)
            full_path = os.path.abspath(os.path.join('tests', 'bin', filename))
            print(f"\nSchedule saved to {filename}")
            print(f"Full path: {full_path}")
            break
        except FileExistsError:
            # If file exists, append counter to filename and try again
            filename = f"schedule_vini_{first_time}_{counter}.ecsv"
            counter += 1
else:
    # Notify if no blocks were successfully scheduled
    print("No blocks were scheduled")