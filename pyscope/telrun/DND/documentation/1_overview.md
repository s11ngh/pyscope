# PyScope DND Observatory Scheduler - Overview

## Introduction

The PyScope DND (Drag and Drop) Observatory Scheduler is a sophisticated web-based application designed for astronomical observation planning and scheduling. It provides an intuitive interface for managing multiple observation targets while optimizing observation schedules based on various astronomical constraints.

## Core Features

### 1. Target Management

- **Adding Targets**

  - Support for named celestial objects
  - Custom coordinate input (RA/Dec)
  - Exposure time configuration (1-120 minutes)
  - Priority assignment (1-10 scale)
  - Validation of target visibility

- **Target List Management**
  - Dynamic updates
  - Real-time validation
  - Priority-based sorting
  - Bulk operations support

### 2. Scheduling System

- **Automated Scheduling**

  - Priority-based scheduling algorithm
  - Night-time constraint handling
  - Altitude constraints
  - Weather condition integration
  - Telescope slew time optimization

- **Schedule Optimization**
  - Minimal transition time
  - Maximum observation efficiency
  - Priority weighting
  - Constraint satisfaction

### 3. Visualization Tools

- **Schedule Visualization**

  - Timeline views
  - Individual target schedules
  - Combined observation plan
  - Interactive time selection

- **Sky Position Plots**
  - Dual view system
  - Priority visualization
  - Altitude tracking
  - Airmass plotting

### 4. Real-time Updates

- **Dynamic Interface**
  - Instant feedback
  - Live schedule updates
  - Real-time constraint checking
  - Interactive plot generation

## Use Cases

### 1. Single Night Planning

```python
# Example: Basic night planning
observer = Observer.at_site('apo')
night_schedule = Schedule(
    time_range=Time([sunset, sunrise]),
    observer=observer,
    constraints=[AtNightConstraint()]
)
```

### 2. Multiple Target Optimization

```python
# Example: Multiple target scheduling
targets = [
    ("Deneb", 20*u.minute, 1),  # (name, exposure, priority)
    ("M13", 15*u.minute, 2),
    ("Vega", 30*u.minute, 3)
]

scheduler = SimpleScheduler(
    observer=observer,
    constraints=constraints,
    time_resolution=5*u.minute
)
```

### 3. Priority-based Scheduling

```python
# Example: Priority handling
def handle_priorities(blocks):
    return sorted(blocks, key=lambda x: x.priority)
```

## System Requirements

### Hardware Requirements

- **Minimum:**

  - CPU: Dual-core processor
  - RAM: 4GB
  - Storage: 1GB free space
  - Network: Basic internet connection

- **Recommended:**
  - CPU: Quad-core processor
  - RAM: 8GB
  - Storage: 5GB free space
  - Network: High-speed internet connection

### Software Requirements

- **Required Software:**

  - Python 3.7+
  - Web browser (Chrome/Firefox/Safari)
  - Cairo graphics library
  - Git (for installation)

- **Python Dependencies:**
  ```text
  Flask>=2.0.1
  astroplan>=0.9
  astropy>=5.3.1
  matplotlib>=3.5.1
  numpy>=1.24.4
  ```

## Getting Started

### Quick Start

```bash
# Clone repository
git clone https://github.com/yourusername/pyscope.git

# Setup virtual environment
cd pyscope/DND
python -m venv venv
.\venv\Scripts\activate  # Windows
source venv/bin/activate # Linux/Mac

# Install dependencies
pip install -r requirements.txt

# Run application
python app.py
```

### First Steps

1. Access the web interface (http://localhost:5000)
2. Add your first target
3. Set exposure time and priority
4. Generate schedule visualization
5. Export or save your schedule

## Additional Resources

- [Astroplan Documentation](https://astroplan.readthedocs.io/)
- [Astropy Documentation](https://docs.astropy.org/)
- [Flask Documentation](https://flask.palletsprojects.com/)
