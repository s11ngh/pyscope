# Astronomical Scheduler Documentation

## Overview

The scheduler component handles astronomical observation scheduling through Flask-based web interface, integrating with astroplan for astronomical calculations and schedule optimization.

## Core Components

### 1. Global Variables

```python
blocks = []  # Stores observation blocks
SUGGESTED_TARGETS = ["Deneb", "M13", "Sirius", "algol", "vega"]  # Default targets
```

### 2. Block Management

```python
@app.route('/add_target', methods=['POST'])
def add_target():
    """
    Add new observation target

    Parameters:
        target: str - Target name
        exposure: float - Exposure time (1-120 minutes)
        priority: int - Priority level (1-10)

    Validation:
    - Exposure time: 1-120 minutes
    - Priority: 1-10 (1 highest)
    """

@app.route('/remove_target', methods=['POST'])
def remove_target():
    """
    Remove target from schedule by index
    """
```

## Schedule Generation

### 1. Main Schedule Builder

```python
def build_schedule():
    """
    Build complete observation schedule

    Process:
    1. Create Observer at APO site
    2. Set night-time constraints
    3. Calculate sunset to sunrise window
    4. Sort blocks by priority
    5. Apply scheduling algorithm

    Components:
    - Observer: APO site location
    - Constraints: AtNightConstraint
    - Transitioner: 2 deg/second slew rate
    - Time Resolution: 5 minutes
    """
```

### 2. Individual Schedule Builder

```python
def build_individual_schedule(single_block):
    """
    Build schedule for single target

    Features:
    - 24-hour schedule window
    - Same constraints as main schedule
    - Individual target optimization
    """
```

## Visualization System

### 1. Schedule Visualization

```python
def generate_schedule_plot():
    """
    Generate schedule visualizations

    Outputs:
    1. Individual target timelines
    2. Combined schedule view
    3. Detailed schedule table with:
       - Target name
       - Priority
       - Individual start/end times
       - Combined start/end times
       - Duration
    """
```

### 2. Sky Position Plot

```python
def generate_sky_plot():
    """
    Generate sky position plots

    Features:
    1. Dual view system:
       - Basic plot without priority
       - Enhanced plot with priority
    2. Color-coded targets
    3. Date-based titling
    4. Legend with priority levels
    """
```

### 3. Airmass Plot

```python
def generate_airmass_plot():
    """
    Generate airmass visualization

    Features:
    1. Sunset to sunrise coverage
    2. Priority-labeled targets
    3. Time-based x-axis (UTC)
    4. Grid overlay
    """
```

## Technical Implementation

### 1. Dependencies

```python
from astroplan import FixedTarget, Observer, Transitioner
from astroplan.scheduling import Schedule, ObservingBlock
from astroplan.plots import plot_schedule_airmass, plot_sky
from astroplan.constraints import AtNightConstraint
from astropy.time import Time, TimeDelta
from astropy import units as u
```

### 2. Error Handling

```python
try:
    # Schedule generation/plot creation
    ...
except Exception as e:
    current_app.logger.error(f"Error: {str(e)}")
    return jsonify({'error': str(e)})
```

### 3. Plot Generation

```python
def convert_plot_to_base64():
    """
    Convert matplotlib plots to web-friendly format

    Process:
    1. Save plot to BytesIO buffer
    2. Convert to base64 string
    3. Clean up resources
    """
```

## API Endpoints

### 1. Plot Generation

```python
@app.route('/plot/<plot_type>')
def generate_plot(plot_type):
    """
    Generate visualization plots

    Types:
    - schedule: Timeline visualization
    - sky: Sky position plots
    - airmass: Airmass curves

    Returns:
    - Base64 encoded PNG image
    - Error message if generation fails
    """
```

### 2. Block Management

```python
@app.route('/list_blocks')
def list_blocks():
    """
    List all scheduled blocks

    Returns:
    JSON array of blocks with:
    - index: Block position
    - target: Target name
    - exposure: Duration in minutes
    - priority: Priority level
    """
```

## Configuration

### 1. Environment Setup

```python
matplotlib.use('Agg')  # Non-interactive backend
plt.switch_backend('Agg')
```

### 2. CORS Configuration

```python
CORS(app)
@app.after_request
def after_request(response):
    """Configure CORS headers"""
```

### 3. Logging

```python
logging.basicConfig(level=logging.DEBUG)
```
