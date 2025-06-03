# BBScheduler: Enhanced Observation Block Scheduler for Pyscope

**BBScheduler** is an advanced astronomical observation scheduler that extends the functionality of astroplan's `PriorityScheduler` by providing additional capabilities for tracking scheduling efficiency and identifying unscheduled observation blocks. It is designed for use within the `pyscope` ecosystem for robotic telescope operations.

---

## Overview and Features

BBScheduler offers significant enhancements over the standard astroplan scheduler:

- **Comprehensive Block Tracking:** Maintains references to all original observation blocks, those successfully scheduled, and those that could not be scheduled.
- **Scheduling Efficiency Metrics:** Tracks and reports the percentage of scheduled versus unscheduled blocks.
- **Duplicate Block Handling:** Uses robust block-matching algorithms to accurately identify unscheduled blocks, even with duplicate observations.
- **Detailed Reporting:** Exposes API methods for retrieving original, scheduled, and missing blocks, plus summary statistics.
- **Seamless Astroplan Integration:** Supports all astroplan constraints (airmass, altitude, moon separation, time windows, custom constraints), so it can replace `PriorityScheduler` transparently.

---

## Installation and Dependencies

### Prerequisites

- `astroplan` (for scheduling and constraints)
- `astropy` (for coordinates and time handling)
- `numpy` (for numerical operations)
- `pyscope` (for telescope control and integration)

### Installation Steps

1. **Install pyscope and dependencies:**

   ```bash
   pip install pyscope
   ```

2. **Clone the repository and install in development mode:**

   ```bash
   git clone https://github.com/s11ngh/pyscope
   cd pyscope
   pip install -e ".[dev]"
   ```

3. **(Optional) Use a virtual environment for development:**
   ```bash
   python -m venv pyscope-dev
   source pyscope-dev/bin/activate  # On Windows: pyscope-dev\Scripts\activate
   pip install astroplan astropy numpy
   ```

---

## API Reference

### Class Definition

```python
from pyscope.telrun.bbscheduler import BBScheduler
```

#### Constructor

```python
BBScheduler(constraints=None, observer=None, transitioner=None, gap_time=None, time_resolution=None)
```

#### Parameters

    '''
    constraints : list or None
        Constraints to apply to all observations

    observer : astroplan.Observer
        The observer/site to do the scheduling for

    transitioner : astroplan.Transitioner or None
        The transitioner to use for computing transition times
        between observations

    gap_time : astropy.units.Quantity
        The maximum length of time a transition between observations can take

    time_resolution : astropy.units.Quantity
        The smallest time step to use when scheduling
    '''

#### Core Methods

- `__call__(blocks, schedule)`: Schedule given blocks, with enhanced tracking.
- `get_original_blocks()`: Returns a copy of the original observation blocks submitted for scheduling.
- `get_observing_blocks()`: Returns successfully scheduled observation blocks.
- `get_scheduled_blocks()`: Returns all scheduled blocks (including transitions).
- `get_missing_blocks()`: Returns blocks that could not be scheduled, using a robust matching algorithm.
- `get_scheduling_summary()`: Returns a dictionary with keys: `total_blocks`, `scheduled_blocks`, `missing_blocks`, and `scheduling_efficiency` (percent scheduled).

---

## Example Usage

### Basic Scheduling

```python
from pyscope.telrun.bbscheduler import BBScheduler
from astroplan import Observer, FixedTarget, ObservingBlock
from astropy.time import Time
from astropy import units as u
from astroplan.constraints import AirmassConstraint, AtNightConstraint, TimeConstraint, AltitudeConstraint
from astroplan.scheduling import TransitionBlock, Schedule, Transitioner
from astroplan.scheduling import PriorityScheduler

observer = Observer.at_site('subaru')
targets = [
    FixedTarget.from_name('Deneb'),
    FixedTarget.from_name('M13'),
    FixedTarget.from_name('Vega')
]

configurations = [{'filter': 'B'}, {'filter': 'C'}, {'filter': 'R'}]
blocks = []
transitioner = Transitioner(slew_rate=1*u.deg/u.second)

# Create blocks for each target
for i, target in enumerate(targets):
    block = ObservingBlock(
        target,
        5*u.minute,
        priority=i+1,  # Different priorities
        configuration=configurations[i],
        constraints=None
    )
    blocks.append(block)

# Create schedule and scheduler
schedule = Schedule(Time('2024-08-15 02:00:00'), Time('2024-08-15 10:00:00'))

scheduler = BBScheduler(
    constraints=[],
    observer=observer,
    transitioner=transitioner,
    gap_time=5*u.minute,
    time_resolution=1*u.minute
)

# Run the scheduler
schedule = scheduler(blocks, schedule)
```

### Scheduling Analysis

```python
summary = scheduler.get_scheduling_summary()
print("Scheduling efficiency:", summary["scheduling_efficiency"], "%")
print("Unscheduled blocks:", scheduler.get_missing_blocks())
```
