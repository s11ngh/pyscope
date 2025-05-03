# Frontend Implementation Guide

## Overview

The frontend implementation uses modern web technologies to create an interactive interface for astronomical schedule management.

## Technology Stack

### Core Technologies

- HTML5
- CSS3 (Bootstrap 5.1.3)
- JavaScript (ES6+)
- jQuery 3.6.0

### Dependencies

```html
<!-- Required CSS -->
<link
  href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css"
  rel="stylesheet"
/>
<link href="/static/css/style.css" rel="stylesheet" />

<!-- Required JavaScript -->
<script src="https://code.jquery.com/jquery-3.6.0.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
<script src="/static/js/main.js"></script>
```

## Component Structure

### 1. Target Management Interface

```html
<div class="target-management">
  <!-- Add Target Form -->
  <form id="add-target-form">
    <div class="form-group">
      <label>Target Name</label>
      <input
        type="text"
        class="form-control"
        id="target-name"
        placeholder="Enter target name or coordinates"
      />
    </div>
    <div class="form-group">
      <label>Exposure Time (minutes)</label>
      <input
        type="number"
        class="form-control"
        id="exposure-time"
        min="1"
        max="120"
      />
    </div>
    <div class="form-group">
      <label>Priority (1-10)</label>
      <input
        type="number"
        class="form-control"
        id="priority"
        min="1"
        max="10"
      />
    </div>
    <button type="submit" class="btn btn-primary">Add Target</button>
  </form>

  <!-- Target List -->
  <div id="target-list" class="mt-4">
    <h3>Current Targets</h3>
    <div class="target-items"></div>
  </div>
</div>
```

### 2. Visualization Controls

```html
<div class="visualization-controls">
  <div class="btn-group" role="group">
    <button
      type="button"
      class="btn btn-secondary"
      onclick="showPlot('schedule')"
    >
      Schedule
    </button>
    <button type="button" class="btn btn-secondary" onclick="showPlot('sky')">
      Sky Position
    </button>
    <button
      type="button"
      class="btn btn-secondary"
      onclick="showPlot('airmass')"
    >
      Airmass
    </button>
  </div>
  <div id="plot-display" class="mt-3">
    <img id="current-plot" class="img-fluid" />
  </div>
</div>
```

## JavaScript Implementation

### 1. Target Management

```javascript
// Target addition handling
$("#add-target-form").submit(function (e) {
  e.preventDefault();
  const targetData = {
    target: $("#target-name").val(),
    exposure: parseFloat($("#exposure-time").val()),
    priority: parseInt($("#priority").val()),
  };

  $.ajax({
    url: "/add_target",
    method: "POST",
    contentType: "application/json",
    data: JSON.stringify(targetData),
    success: function (response) {
      updateTargetList();
      showAlert("success", "Target added successfully");
    },
    error: function (xhr) {
      showAlert("danger", "Error adding target: " + xhr.responseJSON.error);
    },
  });
});

// Target list update
function updateTargetList() {
  $.get("/list_blocks", function (data) {
    const targetList = $(".target-items");
    targetList.empty();

    data.forEach((target, index) => {
      targetList.append(`
                <div class="target-item card mb-2">
                    <div class="card-body">
                        <h5 class="card-title">${target.target}</h5>
                        <p class="card-text">
                            Exposure: ${target.exposure} min | 
                            Priority: ${target.priority}
                        </p>
                        <button class="btn btn-danger btn-sm" 
                                onclick="removeTarget(${index})">
                            Remove
                        </button>
                    </div>
                </div>
            `);
    });
  });
}
```

### 2. Visualization Handling

```javascript
// Plot display handling
function showPlot(plotType) {
  $("#plot-display").addClass("loading");

  $.get(`/plot/${plotType}`, function (response) {
    if (response.status === "success") {
      $("#current-plot")
        .attr("src", `data:image/png;base64,${response.data.plot}`)
        .on("load", function () {
          $("#plot-display").removeClass("loading");
        });
    } else {
      showAlert("danger", "Error generating plot");
    }
  });
}

// Error handling
function showAlert(type, message) {
  const alert = $(`
        <div class="alert alert-${type} alert-dismissible fade show">
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert">
            </button>
        </div>
    `);

  $(".alerts-container").append(alert);
  setTimeout(() => alert.alert("close"), 5000);
}
```

## CSS Styling

### 1. Custom Styles

```css
/* Loading state */
.loading {
  position: relative;
  min-height: 200px;
}

.loading::after {
  content: "Loading...";
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  background: rgba(255, 255, 255, 0.8);
  padding: 1rem;
  border-radius: 4px;
}

/* Target list styling */
.target-item {
  transition: all 0.3s ease;
}

.target-item:hover {
  box-shadow: 0 2px 5px rgba(0, 0, 0, 0.2);
}

/* Plot display */
#plot-display {
  background: #f8f9fa;
  padding: 1rem;
  border-radius: 4px;
  min-height: 400px;
}
```

## Event Handling

### 1. Form Validation

```javascript
function validateTargetInput() {
  const name = $("#target-name").val();
  const exposure = parseFloat($("#exposure-time").val());
  const priority = parseInt($("#priority").val());

  if (!name) {
    showAlert("danger", "Target name is required");
    return false;
  }

  if (exposure < 1 || exposure > 120) {
    showAlert("danger", "Exposure time must be between 1 and 120 minutes");
    return false;
  }

  if (priority < 1 || priority > 10) {
    showAlert("danger", "Priority must be between 1 and 10");
    return false;
  }

  return true;
}
```

### 2. Real-time Updates

```javascript
// Automatic updates
setInterval(updateTargetList, 30000); // Update every 30 seconds

// WebSocket connection (if implemented)
const ws = new WebSocket("ws://localhost:5000/ws");
ws.onmessage = function (event) {
  const data = JSON.parse(event.data);
  if (data.type === "target_update") {
    updateTargetList();
  }
};
```

## Responsive Design

### 1. Mobile Optimization

```css
@media (max-width: 768px) {
  .visualization-controls {
    flex-direction: column;
  }

  .btn-group {
    flex-direction: column;
    width: 100%;
  }

  .target-item {
    margin-bottom: 1rem;
  }
}
```

## Error Handling

### 1. Network Errors

```javascript
$(document).ajaxError(function (event, jqXHR, settings, error) {
  showAlert("danger", `Network error: ${error}`);
});
```

### 2. Input Validation

```javascript
// Real-time validation
$("#exposure-time").on("input", function () {
  const value = parseFloat($(this).val());
  if (value < 1 || value > 120) {
    $(this).addClass("is-invalid");
  } else {
    $(this).removeClass("is-invalid");
  }
});
```

## Performance Optimization

### 1. Image Loading

```javascript
// Lazy loading for plots
$("#current-plot").attr("loading", "lazy");

// Plot caching
const plotCache = {};
function cachePlot(type, data) {
  plotCache[type] = {
    data: data,
    timestamp: Date.now(),
  };
}
```

### 2. DOM Updates

```javascript
// Batch DOM updates
function updateUI(updates) {
  requestAnimationFrame(() => {
    updates.forEach((update) => {
      const { element, content } = update;
      $(element).html(content);
    });
  });
}
```
