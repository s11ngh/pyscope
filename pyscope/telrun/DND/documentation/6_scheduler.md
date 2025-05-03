# Astronomical Scheduler Documentation

## Overview

The scheduler component is responsible for creating optimized observation schedules based on target priorities, constraints, and astronomical conditions.

## Core Components

### 1. SimpleScheduler Class

```python
class SimpleScheduler(Scheduler):
    """
    Custom scheduler implementation for astronomical observations

    Features:
    - Priority-based scheduling
    - Night-time constraint handling
    - Slew time optimization
    - Multiple target coordination
    """

    def __init__(self, observer, constraints=None, time_resolution=5*u.minute):
        self.observer = observer
        self.constraints = constraints or []
        self.time_resolution = time_resolution
```

### 2. ObservingBlock Class

```python
class ObservingBlock:
    """
    Represents a single observation target with its requirements

    Attributes:
        target (FixedTarget): Astronomical target
        duration (Quantity): Observation duration
        priority (int): Priority level (1-10)
        constraints (list): List of observing constraints
    """
```

## Scheduling Algorithm

### 1. Priority Handling

```python
def sort_by_priority(blocks):
    """
    Sort blocks by priority (1 highest, 10 lowest)

    Parameters:
        blocks (list): List of ObservingBlocks

    Returns:
        list: Priority-sorted blocks
    """
    return sorted(blocks, key=lambda x: x.priority)
```

### 2. Time Allocation

```python
def allocate_time(blocks, start_time, end_time):
    """
    Allocate observation times for blocks

    Parameters:
        blocks (list): Priority-sorted observation blocks
        start_time (Time): Schedule start time
        end_time (Time): Schedule end time

    Returns:
        dict: Allocated time slots for each block
    """
```

### 3. Constraint Management

```python
def apply_constraints(block, time_slot):
    """
    Apply observing constraints to time slot

    Constraints:
    1. Night time requirement
    2. Minimum altitude
    3. Weather conditions
    4. Target visibility
    """
```

## Schedule Generation Process

### 1. Initialization

```python
def initialize_schedule(observer, time_range):
    """
    Create new schedule instance

    Parameters:
        observer (Observer): Observatory location
        time_range (tuple): Start and end times

    Returns:
        Schedule: New schedule instance
    """
```

### 2. Block Processing

```python
def process_blocks(blocks):
    """
    Process observation blocks

    Steps:
    1. Sort by priority
    2. Calculate visibility windows
    3. Optimize transitions
    4. Allocate time slots
    """
```

### 3. Schedule Optimization

```python
def optimize_schedule(schedule):
    """
    Optimize observation schedule

    Optimization criteria:
    1. Minimize slew time
    2. Maximize observation time
    3. Maintain priority order
    4. Handle timing constraints
    """
```

## Time Management

### 1. Time Windows

```python
def calculate_time_windows(observer, target, constraints):
    """
    Calculate observable time windows

    Parameters:
        observer (Observer): Observatory location
        target (FixedTarget): Target object
        constraints (list): Observing constraints

    Returns:
        list: Observable time windows
    """
```

### 2. Transition Times

```python
def calculate_transition_time(current_target, next_target, slew_rate):
    """
    Calculate telescope transition time

    Parameters:
        current_target (FixedTarget): Current target
        next_target (FixedTarget): Next target
        slew_rate (Quantity): Telescope slew rate

    Returns:
        Quantity: Required transition time
    """
```

## Constraint Types

### 1. Time Constraints

```python
class TimeConstraint:
    """
    Time-based observation constraints

    Types:
    1. Night time requirement
    2. Specific time ranges
    3. Maximum duration
    """
```

### 2. Altitude Constraints

```python
class AltitudeConstraint:
    """
    Target altitude constraints

    Parameters:
    - min_altitude (Angle): Minimum observable altitude
    - max_altitude (Angle): Maximum observable altitude
    """
```

## Schedule Output

### 1. Schedule Format

```python
class Schedule:
    """
    Final schedule representation

    Attributes:
        blocks (list): Scheduled observation blocks
        start_time (Time): Schedule start time
        end_time (Time): Schedule end time
        transitions (list): Block transition times
    """
```

### 2. Block Details

```python
class ScheduledBlock:
    """
    Scheduled block information

    Attributes:
        target (str): Target name
        start_time (Time): Observation start time
        duration (Quantity): Observation duration
        priority (int): Target priority
    """
```

## Error Handling

### 1. Validation

```python
def validate_schedule(schedule):
    """
    Validate generated schedule

    Checks:
    1. Time slot conflicts
    2. Constraint violations
    3. Priority ordering
    4. Transition feasibility
    """
```

### 2. Error Types

```python
class SchedulingError(Exception):
    """Base class for scheduling errors"""
    pass

class ConstraintViolationError(SchedulingError):
    """Raised when constraints cannot be satisfied"""
    pass

class TimingError(SchedulingError):
    """Raised for timing-related issues"""
    pass
```

## Usage Examples

### 1. Basic Schedule Creation

```python
def create_basic_schedule():
    """
    Example: Create basic observation schedule
    """
    observer = Observer.at_site('apo')
    constraints = [AtNightConstraint()]

    # Create blocks
    blocks = [
        ObservingBlock(target, duration, priority)
        for target, duration, priority in targets
    ]

    # Generate schedule
    scheduler = SimpleScheduler(observer, constraints)
    schedule = scheduler(blocks)
    return schedule
```

### 2. Advanced Scheduling

```python
def create_advanced_schedule():
    """
    Example: Advanced schedule with multiple constraints
    """
    # Add custom constraints
    constraints = [
        AtNightConstraint(),
        AltitudeConstraint(min=30*u.deg),
        WeatherConstraint()
    ]

    # Generate optimized schedule
    scheduler = SimpleScheduler(
        observer=observer,
        constraints=constraints,
        time_resolution=1*u.minute
    )
    return scheduler(blocks)
```
