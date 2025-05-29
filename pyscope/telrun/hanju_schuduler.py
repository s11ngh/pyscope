# -*- coding: utf-8 -*-
from astroplan import Observer, FixedTarget
from astropy.time import Time
from astroplan.constraints import AirmassConstraint, AtNightConstraint, TimeConstraint
from astroplan import ObservingBlock
from astroplan.scheduling import Transitioner, PriorityScheduler, Schedule
from astropy import units as u
import astrotime

# Create observatory instance
observatory = Observer.at_site("apo")  # Example: Apache Point Observatory
location = observatory.location

# Define current date
date = astrotime.Time.now()

# Set maximum altitude for sun (for determining night time)
max_altitude = -12

# Create a single observation block
single_block = {
    "target": SkyCoord("12h00m00s +30d00m00s"),  # Example coordinates for a star
    "start_time": None,
    "end_time": None,
    "duration": 300 * u.second,  # 5 minutes observation
    "constraints": None,
}

def basic_scheduler(block_group, schedule):
    # Set start time based on sun set angle
    current_time = astrotime.Time(
        date,
        format="datetime",
    )
    sun_set = observatory.sun_set_time(current_time, which="next", horizon=max_altitude * u.deg)
    sun_rise = observatory.sun_rise_time(current_time, which="next", horizon=max_altitude * u.deg)
    start_time = sun_set.mjd
    start_time = astrotime.Time(start_time, format="mjd")
    end_time = sun_rise.mjd
    end_time = astrotime.Time(end_time, format="mjd")

    for i in range(len(block_group)):
        if block_group[0]["start_time"] is None:
            try:
                print(f"Last end time: {schedule[-1]['end_time']}")

                # If there's a block group constraint, use it as
                # that should be the scheduled utstart time
                if block_group[0]["constraints"] is not None:
                    if block_group[0]["constraints"][0].min is not None:
                        block_group[0]["start_time"] = block_group[0]["constraints"][0].min
                    else:
                        # Otherwise, use the last end time
                        block_group[0]["start_time"] = schedule[-1]["end_time"]
                else:
                    # If there's no block group constraint, use the last end time
                    block_group[0]["start_time"] = schedule[-1]["end_time"]

                # Calculate transition time
                transition_time = reconfig_file.calc_reconfig_time_blocks(
                    block_group[0], schedule[-1], location, verbose=False
                )

                # If last end time + transition time is greater than start time,
                # use last end time
                if block_group[0]["start_time"] < schedule[-1]["end_time"] + transition_time:
                    block_group[0]["start_time"] = schedule[-1]["end_time"] + transition_time

# total_time = transition_time + block_group[0]["duration"] 
                    # # total_time /= 86400
                    # block_group[0]["start_time"] = schedule[-1]["end_time"] + total_time 
            except Exception as e:
                print(f"Error in scheduler: {e}")
                # If there's a block group constraint, use it
                if block_group[0]["constraints"] is not None:
                    block_group[0]["start_time"] = block_group[0]["constraints"][0].min
                else:
                    block_group[0]["start_time"] = start_time

        # Calculate end time from transition times
        for i, block in enumerate(block_group):
            current_obj = block["target"]

            if i == len(block_group) - 1:
                block["end_time"] = block["start_time"] + block["duration"]
                return schedule
            else:
                next_block = block_group[i + 1]
            next_obj = next_block["target"]

            transition_time = reconfig_file.calc_reconfig_time_blocks(
                block, next_block, location, verbose=False
            )
            total_time = transition_time + block["duration"]
            block["end_time"] = block["start_time"] + total_time
            next_block["start_time"] = block["end_time"]
            schedule.append(block)

            if block["end_time"] > end_time:
                print("End time is greater than sunrise")

    return schedule



# Example usage
a = []
b=[]
basic_scheduler(a, b)