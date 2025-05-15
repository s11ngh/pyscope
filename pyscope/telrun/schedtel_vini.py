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

# Define observatory location (example: Palomar Observatory)
location = EarthLocation(lat=33.356*u.deg, lon=-116.863*u.deg, height=1712*u.m)
observatory = Observer(location=location)

# Set the date for tonight
date = datetime.datetime.now()

# Create a target (example: observing M31 - Andromeda Galaxy)
target = FixedTarget(SkyCoord.from_name('M31'))

# Create a single observation block
block = {
    "ID": astrotime.Time.now().mjd,
    "name": "M31_observation",
    "target": target,
    "target_ra": target.ra.deg,
    "target_dec": target.dec.deg,
    "duration": 30 * u.minute,  # 30 minute observation
    "filter": 'R',  # Red filter
    "exposure": 300,  # 5 minutes per exposure
    "nexp": 6,  # 6 exposures
    "priority": 1,
    "constraints": None,  # No specific timing constraints
    "start_time": None,  # Will be set by scheduler
    "end_time": None,  # Will be set by scheduler
    "status": "U",  # Unscheduled
    "message": "Unscheduled",
    "observer": ["observer1"],
    "code": "test",
    "title": "M31 R-band Observation",
    "filename": "",
    "pm_ra_cosdec": 0 * u.arcsec/u.hour,
    "pm_dec": 0 * u.arcsec/u.hour,
}

# Mock reconfig file with a simple transition time calculator
class DummyReconfig:
    def calc_reconfig_time_blocks(self, block1, block2, location, verbose=False):
        return 30 * u.second  # Fixed 30-second transition time

reconfig_file = DummyReconfig()

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
                # Only try to access previous schedule if it exists
                if len(schedule) > 0:
                    print(f"Last end time: {schedule[-1]['end_time']}")

                    # If there's a block group constraint, use it
                    if block_group[0]["constraints"] is not None:
                        block_group[0]["start_time"] = block_group[0]["constraints"][0].min 
                    else:
                        # Use the last end time if schedule exists
                        block_group[0]["start_time"] = schedule[-1]["end_time"]

                    # Calculate transition time
                    transition_time = reconfig_file.calc_reconfig_time_blocks(
                        block_group[0], schedule[-1], location, verbose=False)
                    
                    # Add transition time to start time
                    block_group[0]["start_time"] = block_group[0]["start_time"] + transition_time
                else:
                    # If schedule is empty, use sunset time
                    block_group[0]["start_time"] = start_time

            except Exception as e:
                print(f"Notice: Starting new schedule at sunset ({e})")
                block_group[0]["start_time"] = start_time

        # Calculate end time from transition times
        for i, block in enumerate(block_group):    
            current_obj = block["target"]

            if i == len(block_group) - 1:
                block["end_time"] = block["start_time"] + block["duration"]
                block["status"] = "S"  # Mark as scheduled
                block["message"] = "Scheduled successfully"
                schedule.append(block)
                return schedule
            else:
                next_block = block_group[i + 1]
                next_obj = next_block["target"]
                
                transition_time = reconfig_file.calc_reconfig_time_blocks(
                    block, next_block, location, verbose=False)
                total_time = transition_time + block["duration"]
                block["end_time"] = block["start_time"] + total_time
                next_block["start_time"] = block["end_time"]
                schedule.append(block)              
                
                if block["end_time"] > end_time:
                    print("End time is greater than sunrise")

    return schedule

# Constants
max_altitude = -12  # Maximum solar altitude for night time in degrees

# Create empty schedule and block group
schedule = []
block_group = [block]  # Single block for now

# Run the scheduler
scheduled_blocks = basic_scheduler(block_group, schedule)

# Print results
if len(scheduled_blocks) > 0:
    print("\nScheduled observation:")
    for block in scheduled_blocks:
        print(f"Target: {block['name']}")
        print(f"Start time: {block['start_time'].iso}")
        print(f"End time: {block['end_time'].iso}")
        print(f"Status: {block['status']}")
        print(f"Message: {block['message']}")
    
    # Save schedule to ECSV file with unique name
    first_time = scheduled_blocks[0]["start_time"].strftime("%Y-%m-%dT%H-%M-%S")
    base_filename = f"schedule_vini_{first_time}.ecsv"
    
    # Find a unique filename by adding a counter if needed
    counter = 1
    filename = base_filename
    while True:
        try:
            save_schedule_to_ecsv(scheduled_blocks, filename)
            # Get the full path to the saved file
            full_path = os.path.abspath(os.path.join('tests', 'bin', filename))
            print(f"\nSchedule saved to {filename}")
            print(f"Full path: {full_path}")
            
            # Read and display the ECSV file in tabular format using the full path
            table = Table.read(full_path, format='ascii.ecsv')
            print("\nSchedule in tabular format:")
            print(table)
            break
        except FileExistsError:
            filename = f"schedule_vini_{first_time}_{counter}.ecsv"
            counter += 1
else:
    print("No blocks were scheduled")