# Error Handling Documentation

## Overview

The DND system implements comprehensive error handling across all components to ensure robust operation and meaningful error reporting.

## Error Types

### 1. Input Validation Errors

```python
class InputValidationError(Exception):
    """
    Raised when input validation fails

    Examples:
    - Invalid target name
    - Exposure time out of range (1-120 minutes)
    - Invalid priority level (1-10)
    - Missing required fields
    """
```

### 2. Scheduling Errors

```python
class SchedulingError(Exception):
    """
    Raised during schedule generation

    Types:
    - Constraint violations
    - Timing conflicts
    - Resource allocation failures
    - Priority conflicts
    """
```

### 3. Astronomical Errors

```python
class AstronomicalError(Exception):
    """
    Raised during astronomical calculations

    Cases:
    - Target not visible
    - Invalid coordinates
    - Time range errors
    - Observatory location issues
    """
```

## Logging Configuration

```python
import logging

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('dnd.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)
```

## Log Error Function

```python
def log_error(error, context=None):
    """
    Log error with context

    Parameters:
        error: Exception object
        context: Additional context dictionary
    """
    logger.error(f"Error: {str(error)}")
    if context:
        logger.error(f"Context: {context}")
```

## Error Messages

```python
ERROR_MESSAGES = {
    'validation_error': 'Please check your input: {detail}',
    'scheduling_error': 'Unable to schedule observation: {detail}',
    'system_error': 'System error occurred: {detail}',
    'network_error': 'Network connection issue: {detail}'
}

def get_user_message(error_type, detail):
    """Generate user-friendly error message"""
    template = ERROR_MESSAGES.get(error_type, 'An error occurred: {detail}')
    return template.format(detail=detail)
```

## Global AJAX Error Handling

```javascript
// Global AJAX error handler
$(document).ajaxError(function (event, xhr, settings, error) {
  const errorMessage = xhr.responseJSON?.error || "An unknown error occurred";
  showErrorAlert(errorMessage);
});

function showErrorAlert(message) {
  const alert = $(`
        <div class="alert alert-danger alert-dismissible fade show">
            <strong>Error:</strong> ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        </div>
    `);
  $("#alerts-container").append(alert);

  // Auto-dismiss after 5 seconds
  setTimeout(() => alert.alert("close"), 5000);
}

function updateStatus(status, message) {
  const statusBar = $("#status-bar");
  statusBar.removeClass().addClass(`alert alert-${status}`);
  statusBar.text(message);
}
```

## Flask Global Error Handler

```python
def error_handler(error):
    """
    Global error handler for Flask application

    Parameters:
        error: Exception object

    Returns:
        JSON response with error details
    """
    if isinstance(error, InputValidationError):
        return jsonify({
            'error': str(error),
            'type': 'validation_error',
            'status_code': 400
        }), 400

    if isinstance(error, SchedulingError):
        return jsonify({
            'error': str(error),
            'type': 'scheduling_error',
            'status_code': 500
        }), 500

    # Default error response
    return jsonify({
        'error': 'An unexpected error occurred',
        'type': 'internal_error',
        'status_code': 500
    }), 500
```

## Target Validation

```python
def validate_target(target_name):
    """
    Validate target name or coordinates

    Checks:
    1. Name resolution via astropy
    2. Coordinate format
    3. Target visibility
    4. Database existence
    """
    try:
        target = FixedTarget.from_name(target_name)
        return True, target
    except Exception as e:
        return False, str(e)
```

## Parameter Validation

```python
def validate_parameters(exposure_time, priority):
    """
    Validate numerical parameters

    Rules:
    - Exposure time: 1-120 minutes
    - Priority: 1-10 (integer)
    """
    errors = []

    if not 1 <= exposure_time <= 120:
        errors.append("Exposure time must be between 1 and 120 minutes")

    if not 1 <= priority <= 10:
        errors.append("Priority must be between 1 and 10")

    return len(errors) == 0, errors
```

## Recovery Mechanism

```python
def attempt_recovery(operation, max_retries=3):
    """
    Attempt operation with automatic recovery

    Features:
    - Multiple retry attempts
    - Exponential backoff
    - State cleanup
    - Error logging
    """
    for attempt in range(max_retries):
        try:
            return operation()
        except Exception as e:
            if attempt == max_retries - 1:
                raise
            cleanup_state()
            time.sleep(2 ** attempt)
```

```python
def restore_last_valid_state():
    """
    Restore system to last known good state

    Steps:
    1. Load backup data
    2. Reset connections
    3. Clear caches
    4. Reinitialize components
    """
```

## Test Error Handling

```python
def test_error_handling():
    """
    Test error handling mechanisms

    Cases:
    1. Invalid input validation
    2. Schedule generation failures
    3. Network timeouts
    4. Resource exhaustion
    """
```

```python
def test_error_propagation():
    """
    Test error propagation through system

    Scenarios:
    1. Frontend to backend
    2. Between components
    3. Recovery mechanisms
    4. User feedback
    """
```
