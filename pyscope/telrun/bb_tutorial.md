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
- `pytest` (for running tests)
- `pytest-cov` (for test coverage reporting)

### Installation Steps

1. **Install pyscope and dependencies:**

   ```bash
   pip install pyscope pytest pytest-cov
   ```

2. **Clone the repository and install in development mode:**

   ```bash
   git clone https://github.com/s11ngh/pyscope
   cd pyscope
   pip install -e ".[dev]"
   ```

3. **Verify installation:**
   ```bash
   python -c "from pyscope.telrun.bbscheduler import BBScheduler"
   ```

---

## Testing Framework

### Running Tests

The BBScheduler has comprehensive test coverage using pytest. To run the test suite:

```bash
# Run all BBScheduler tests
pytest tests/telrun/test_bbscheduler.py

# Run with coverage report
pytest --cov=pyscope.telrun.bbscheduler tests/telrun/test_bbscheduler.py

# Run specific test class
pytest tests/telrun/test_bbscheduler.py::TestBBScheduler

# Run specific test
pytest tests/telrun/test_bbscheduler.py::TestBBScheduler::test_priority_ordering
```

### Test Categories

The test suite is organized into three main classes:

1. **Core Functionality (`TestBBScheduler`)**

   - Basic scheduling operations
   - Priority handling
   - Block transitions
   - Time constraints
   - Target observability

2. **Interface Testing (`TestBBSchedulerUnifiedInterface`)**

   - API consistency
   - Block tracking
   - Results reporting
   - Statistical summaries

3. **Real Data Testing (`TestBBSchedulerRealData`)**
   - Integration with .sch files
   - XPG1 schedule validation
   - Time window handling
   - Error conditions

### Testing Assumptions

1. **Time Resolution**

   - Minimum: 1 minute
   - Maximum schedule window: 24 hours
   - Time zones: All calculations in UTC

2. **Coordinate Systems**

   - Uses ICRS coordinates
   - Altitude constraints in degrees
   - Slew rates in degrees/second

3. **Priority Handling**

   - Lower numbers = higher priority (1 is highest)
   - Equal priorities scheduled in submission order
   - Valid priority range: 1-999

4. **Block Duration**
   - Minimum: 30 seconds
   - Maximum: 4 hours
   - Resolution: 1 second

### Input Partitioning

The test suite validates these input categories:

1. **Time Windows**

   - Very short (<15 minutes)
   - Standard (15 minutes - 12 hours)
   - Long (12-24 hours)
   - Invalid (>24 hours)

2. **Block Counts**

   - Single block
   - Small set (2-10 blocks)
   - Medium set (11-50 blocks)
   - Large set (51-200 blocks)

3. **Target Types**

   - Fixed stars
   - Deep sky objects
   - Solar system objects
   - Custom coordinates

4. **Constraint Combinations**
   - No constraints
   - Single constraint
   - Multiple constraints
   - Conflicting constraints

---

## Usage Guidelines

### Basic Usage

```python
from pyscope.telrun.bbscheduler import BBScheduler
from astroplan import Observer, FixedTarget
from astropy.time import Time
import astropy.units as u

# Create scheduler
observer = Observer.at_site('apo')
scheduler = BBScheduler(
    constraints=[],
    observer=observer,
    time_resolution=1*u.minute
)

# Define observation window
start_time = Time('2024-08-15 02:00:00')
end_time = Time('2024-08-15 10:00:00')
schedule = Schedule(start_time, end_time)

# Schedule observations
schedule = scheduler(blocks, schedule)

# Get results
summary = scheduler.get_scheduling_summary()
print(f"Scheduled {summary['scheduling_efficiency']}% of blocks")
```

### Advanced Features

1. **Block Tracking**

   ```python
   # Get blocks that couldn't be scheduled
   missing = scheduler.get_missing_blocks()

   # Get original blocks
   original = scheduler.get_original_blocks()

   # Get successfully scheduled blocks
   scheduled = scheduler.get_observing_blocks()
   ```

2. **Custom Constraints**

   ```python
   from astroplan import Constraint

   class CustomAltitudeConstraint(Constraint):
       def __init__(self, min_alt):
           self.min_alt = min_alt

       def compute_constraint(self, times, observer, targets):
           return [compute_altitude(time, observer, target) >= self.min_alt
                  for time, target in zip(times, targets)]
   ```

### Performance Considerations

1. **Memory Usage**

   - Keep block count under 200 per scheduling run
   - Clear scheduler between multiple runs
   - Use appropriate time resolution

2. **Speed Optimization**
   - Minimize constraint complexity
   - Use reasonable time resolutions (≥1 minute)
   - Group similar targets together

### Error Handling

Common errors and their resolutions:

1. **ValueError: Schedule window too short**

   - Ensure window > 15 minutes
   - Check time zone handling

2. **RuntimeError: No blocks scheduled**
   - Verify target observability
   - Check constraint conflicts
   - Validate priorities

---

## Integration with MACRO

### Configuration

Create observatory settings in `config.yaml`:

```yaml
observatory:
  name: "APO"
  latitude: 32.78
  longitude: -105.82
  elevation: 2788
  timezone: "US/Mountain"
```

### Execution

```python
from pyscope.observatory import Observatory
from pyscope.telrun.bbscheduler import BBScheduler

# Setup
obs = Observatory.from_config('config.yaml')
scheduler = BBScheduler(observer=obs.observer)

# Schedule
result = scheduler(blocks, schedule)
```

### Logging

The scheduler integrates with pyscope's logging:

```python
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('pyscope.telrun.bbscheduler')
```

---

## Contributing

### Development Setup

1. Create development environment:

```bash
python -m venv bbscheduler-dev
source bbscheduler-dev/bin/activate  # Windows: bbscheduler-dev\Scripts\activate
```

2. Install development dependencies:

```bash
pip install -e ".[dev]"
pip install pytest pytest-cov black isort
```

3. Run tests before submitting changes:

```bash
pytest tests/telrun/test_bbscheduler.py --cov
```

### Code Style

- Follow PEP 8
- Use type hints
- Document all functions
- Include tests for new features

---

## License

This project is part of pyscope and is licensed under the GPL-3.0 License.
