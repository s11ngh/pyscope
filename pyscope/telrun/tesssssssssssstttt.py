'''

THIS FILE IS JUST A TEST FILE TO TEACH GUK GI AND HAN JU ABOUT PYTHON, BASIC SKILLS, AND BASIC PYTHON

'''



#import
#from MODULE import PERTICULAR FUNCTION as ALIAS

from astropy import time as astrotime
from astropy import units as u
from astroplan import Observer
import datetime
from astropy.coordinates import SkyCoord, EarthLocation


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
