# API Reference Documentation

## REST API Endpoints

### 1. Main Interface

```python
@app.route('/')
def index():
    """
    Serves the main application interface

    Returns:
        HTML: Rendered index.html template with suggested targets

    Template Variables:
        - targets: List[str] - Suggested target names
    """
```

### 2. Target Management

#### Add Target

```python
@app.route('/add_target', methods=['POST'])
def add_target():
    """
    Add new observation target

    Request JSON:
    {
        "target": str,       # Target name or coordinates
        "exposure": float,   # Exposure time in minutes (1-120)
        "priority": int      # Priority level (1-10, 1 highest)
    }

    Returns JSON:
    {
        "status": "success" | "error",
        "message": str,
        "data": {
            "index": int,    # Target index in schedule
            "name": str,     # Target name
            "exposure": float,
            "priority": int
        }
    }

    Error Codes:
        400: Invalid input parameters
        404: Target not found
        500: Internal server error
    """
```

#### Remove Target

```python
@app.route('/remove_target', methods=['POST'])
def remove_target():
    """
    Remove target from schedule

    Request JSON:
    {
        "index": int    # Target index to remove
    }

    Returns JSON:
    {
        "status": "success" | "error",
        "message": str
    }

    Error Codes:
        400: Invalid index
        404: Target not found
        500: Internal server error
    """
```

#### List Blocks

```python
@app.route('/list_blocks')
def list_blocks():
    """
    Get list of all scheduled observation blocks

    Returns JSON:
    [
        {
            "index": int,
            "target": str,
            "exposure": float,
            "priority": int,
            "start_time": str,    # ISO format
            "end_time": str       # ISO format
        }
    ]

    Error Codes:
        500: Internal server error
    """
```

### 3. Visualization Endpoints

#### Generate Plots

```python
@app.route('/plot/<plot_type>')
def generate_plot(plot_type):
    """
    Generate visualization plots

    Parameters:
        plot_type: str - Type of plot to generate
            - 'schedule': Timeline visualization
            - 'sky': Sky position plot
            - 'airmass': Airmass plot

    Returns JSON:
    {
        "status": "success" | "error",
        "data": {
            "plot": str,    # Base64 encoded PNG
            "type": str,    # Plot type
            "time": str     # Generation timestamp
        }
    }

    Error Codes:
        400: Invalid plot type
        500: Plot generation error
    """
```

## Internal API

### 1. Schedule Generation

#### Build Schedule

```python
def build_schedule():
    """
    Generate complete observation schedule

    Process:
    1. Sort blocks by priority
    2. Apply constraints
    3. Optimize timing
    4. Validate schedule

    Returns:
        tuple: (scheduled_blocks, start_time)
            - scheduled_blocks: List[ObservingBlock]
            - start_time: astropy.time.Time

    Raises:
        ValueError: Invalid block configuration
        RuntimeError: Schedule generation failure
    """
```

#### Build Individual Schedule

```python
def build_individual_schedule(block):
    """
    Generate schedule for single target

    Parameters:
        block: ObservingBlock - Target observation block

    Returns:
        tuple: (scheduled_blocks, start_time)
            - scheduled_blocks: List[ObservingBlock]
            - start_time: astropy.time.Time

    Raises:
        ValueError: Invalid block parameters
        RuntimeError: Schedule generation failure
    """
```

### 2. Plot Generation

#### Schedule Plot

```python
def generate_schedule_plot():
    """
    Generate schedule visualization

    Features:
    - Individual timelines
    - Combined schedule
    - Priority indication
    - Time markers

    Returns:
        str: Base64 encoded PNG image

    Raises:
        RuntimeError: Plot generation error
    """
```

#### Sky Plot

```python
def generate_sky_plot():
    """
    Generate sky position visualization

    Features:
    - Dual view (with/without priority)
    - Target paths
    - Altitude indicators
    - Priority visualization

    Returns:
        str: Base64 encoded PNG image

    Raises:
        RuntimeError: Plot generation error
    """
```

#### Airmass Plot

```python
def generate_airmass_plot():
    """
    Generate airmass visualization

    Features:
    - Multiple target curves
    - Time indicators
    - Observable ranges
    - Priority indication

    Returns:
        str: Base64 encoded PNG image

    Raises:
        RuntimeError: Plot generation error
    """
```

## Data Structures

### 1. ObservingBlock

```python
class ObservingBlock:
    """
    Represents single observation target

    Attributes:
        target: FixedTarget - Target object
        duration: Quantity - Observation duration
        priority: int - Priority level (1-10)
        constraints: list - Observation constraints
    """
```

### 2. Schedule

```python
class Schedule:
    """
    Represents complete observation schedule

    Attributes:
        blocks: List[ObservingBlock] - Scheduled blocks
        start_time: Time - Schedule start time
        end_time: Time - Schedule end time
        observer: Observer - Observatory location
    """
```

## Error Handling

### 1. Error Responses

```python
def create_error_response(error, code=500):
    """
    Generate standardized error response

    Parameters:
        error: Exception - Error object
        code: int - HTTP status code

    Returns:
        tuple: (JSON response, status code)
    """
```

### 2. Input Validation

```python
def validate_target_input(data):
    """
    Validate target input data

    Parameters:
        data: dict - Target input data

    Returns:
        bool: Validation result

    Raises:
        ValueError: Invalid input parameters
    """
```

## Usage Examples

### 1. Adding Target

```python
# Example request
POST /add_target
{
    "target": "Deneb",
    "exposure": 30,
    "priority": 1
}

# Example response
{
    "status": "success",
    "message": "Target added successfully",
    "data": {
        "index": 0,
        "name": "Deneb",
        "exposure": 30,
        "priority": 1
    }
}
```

### 2. Generating Plot

```python
# Example request
GET /plot/schedule

# Example response
{
    "status": "success",
    "data": {
        "plot": "base64_encoded_image_data",
        "type": "schedule",
        "time": "2025-05-02T12:00:00Z"
    }
}
```
