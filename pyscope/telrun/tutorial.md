# Pyscope Scheduler Tutorial

This tutorial explains how to run the astronomical scheduler script located at `pyscope/telrun/scheduler.py` and understand its output.

## Running the Scheduler

The scheduler is designed to generate an observation schedule for a list of astronomical targets based on various constraints like location, time window, and observing conditions.

You can run the scheduler from your terminal using a command similar to this:

```bash
python pyscope/telrun/scheduler.py --lat 34.0 --lon -118.0 --elevation 300 --targets "M31,M42,M13" --start "2025-05-02 01:00:00" --end "2025-05-02 05:00:00" --duration 30
```

**Explanation of the command:**

1.  `python`: This specifies the Python interpreter to use. Make sure this path points to the Python environment where `pyscope` and its dependencies (like `astroplan`) are installed to either your conda environment or virtual environment.
2.  `pyscope/telrun/scheduler.py`: This is the path to the scheduler script itself, relative to the root of the `pyscope` project directory.
3.  `--lat 34.0`: Specifies the latitude of the observatory in degrees.
4.  `--lon -118.0`: Specifies the longitude of the observatory in degrees (West is negative).
5.  `--elevation 300`: Specifies the elevation of the observatory in meters.
6.  `--targets "M31,M42,M13"`: A comma-separated list of target names (e.g., Messier objects, NGC objects, or specific coordinates if the script is adapted for them). The scheduler will try to observe these targets.
7.  `--start "2025-05-02 01:00:00"`: The start date and time for the observation window in UTC (YYYY-MM-DD HH:MM:SS format).
8.  `--end "2025-05-02 05:00:00"`: The end date and time for the observation window in UTC (YYYY-MM-DD HH:MM:SS format).
9.  `--duration 30`: The desired observation duration for *each* target in minutes.

## Understanding the Output

When you run the command, the scheduler will:

1.  Define the observer's location based on the provided latitude, longitude, and elevation.
2.  Define the time window for observations.
3.  Resolve the target names into coordinates.
4.  Create `ObservingBlock` objects for each target, including the desired duration and constraints (like minimum altitude and maximum airmass, which are defined within the script).
5.  Use the `astroplan.PriorityScheduler` to attempt to schedule the observations within the given time window, considering the constraints and the time it takes to slew the telescope between targets (defined by the `Transitioner`).
6.  Print the resulting schedule as a table.

The output table will typically show:

*   The start and end times for each scheduled observation block.
*   The target being observed during that block.
*   The duration of the observation.
*   Information about transitions (slew time) between targets.
*   Whether the block was successfully scheduled (`scheduled=True`) or not.

If a target cannot be scheduled (e.g., it's below the horizon or doesn't meet the airmass constraints during the specified window), it might not appear in the final schedule or might be marked accordingly, depending on the script's specific output formatting.

If the script encounters issues (like targets not being resolvable or no targets being schedulable), it might print error messages instead of a schedule table.

## Constructing Your Own CLI Commands

The example command provides a template. Here's a breakdown of how to build your own command based on your specific needs:

**Base Command:**

```bash
<path_to_python_interpreter> pyscope/telrun/scheduler.py [options]
```

*   `<path_to_python_interpreter>`: As mentioned before, this needs to point to the correct Python executable within the environment where `pyscope` and `astroplan` are installed.
*   `pyscope/telrun/scheduler.py`: The relative path to the script from your current working directory (usually the root of the `pyscope` project).

**Required Arguments:**

You *must* provide values for these arguments:

*   `--lat <latitude>`: Your observatory's latitude in decimal degrees (e.g., `34.0`, `-22.9`).
*   `--lon <longitude>`: Your observatory's longitude in decimal degrees (e.g., `-118.0`, `-43.2`). Remember West longitudes are negative.
*   `--targets "<target1>,<target2>,..."`: A comma-separated string of target names. These names must be recognizable by `astropy.coordinates.SkyCoord.from_name` (e.g., "M31", "Sirius", "NGC 253"). Enclose the list in quotes if it contains spaces or special characters, although simple comma separation usually works.
*   `--start "<YYYY-MM-DD HH:MM:SS>"`: The desired start time for your observing run in UTC. Use the exact format shown.
*   `--end "<YYYY-MM-DD HH:MM:SS>"`: The desired end time for your observing run in UTC. Must be later than the start time.

**Optional Arguments:**

These arguments have default values if you don't specify them:

*   `--elevation <meters>`: Your observatory's elevation in meters above sea level. Defaults to `0` if omitted.
*   `--duration <minutes>`: The time to spend observing *each* target in minutes. Defaults to `30` if omitted.
*   `--name "<observatory_name>"`: A name for your observatory site. Defaults to `"Observatory"` if omitted.

**Putting It Together:**

1.  **Identify your location:** Find your latitude, longitude, and elevation.
2.  **Choose your targets:** List the celestial objects you want to observe.
3.  **Define your time window:** Decide on the start and end UTC times for the schedule.
4.  **Decide on observation duration:** How long do you want to spend on each target?
5.  **Assemble the command:** Start with the base command, then add each required argument with its value, followed by any optional arguments you want to customize.

**Example Modification:**

Let's say you are at Kitt Peak (Lat ~31.96, Lon ~-111.6, Elev ~2096m), want to observe the Pleiades (M45) and the Orion Nebula (M42) for 45 minutes each, starting tonight at 10 PM local time (which might be 2025-05-03 05:00:00 UTC depending on timezone) and ending at 2 AM (2025-05-03 09:00:00 UTC):

```bash
/path/to/your/python pyscope/telrun/scheduler.py --lat 31.96 --lon -111.6 --elevation 2096 --targets "M45,M42" --start "2025-05-03 05:00:00" --end "2025-05-03 09:00:00" --duration 45 --name "Kitt Peak"
```

Remember to replace `/path/to/your/python` with the actual path to your Python interpreter.

# --- Supported Features ---
# - Takes observer location (latitude, longitude, elevation) via command-line arguments.
# - Accepts a comma-separated list of target names (resolvable by SkyCoord).
# - Defines an observing window with start and end times.
# - Specifies a fixed observation duration per target.
# - Applies basic observing constraints:
#   - Minimum Altitude (currently 20 degrees).
#   - Maximum Airmass (currently 3).
# - Uses a PriorityScheduler, giving higher priority to targets listed earlier.
# - Accounts for telescope slew time between targets using a Transitioner (1 deg/sec).
# - Provides a command-line interface for easy execution.
# - Outputs the generated schedule as a table or indicates if scheduling failed.
# --------------------------