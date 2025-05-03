# Installation Guide

## Prerequisites

### System Requirements

### Software Dependencies

1. **Base Requirements:**

```bash
# Core software
Python 3.7+
Git
Cairo graphics library
Web browser (Chrome/Firefox/Safari)
```

2. **Python Packages:**

```txt
Flask>=2.0.1
astroplan>=0.9
astropy>=5.3.1
matplotlib>=3.5.1
numpy>=1.24.4
flask-cors>=4.0.0
gunicorn>=21.2.0  # For production deployment
```

## Installation Steps

### 1. Getting the Code

```bash
# Clone the pyscope repository, and use the VINIDND branch
git clone https://github.com/s11ngh/pyscope.git
```

### 2. Virtual Environment Setup

```bash
# Create virtual conda environment as given in the pyscope documentation

# Activate virtual environment
```

### 3. Installing Dependencies

```bash
# Now set the DND folder as directory and install required packages
conda install -r requirements.txt
```

### 4. Configuration

## Development Setup

### Running Development Server

```bash
# Start Flask development server making DND folder as direcorty
python app.py
```

### Testing Installation or running the flask server

1. Access http://localhost:5000

## Troubleshooting

### Common Issues

1. **Package Installation Failures**

```bash

# Installing with pip insted
pip install -r requirements.txt

# Upgrade pip
python -m pip install --upgrade pip

# Install wheel
pip install wheel

# Try installation again
pip install -r requirements.txt
```

2. **Matplotlib Backend Issues**

```python
# Add to app.py
import matplotlib
matplotlib.use('Agg')
```

3. **Permission Issues**

```bash
# Fix directory permissions
chmod -R 755 .
```

### Verification Steps

1. **Check Dependencies**

```bash
pip freeze | grep -E "flask|astro|matplotlib|numpy"
```

2. **Test Core Functions**

```python
# Test astronomical calculations
from astropy.time import Time
Time.now()
```

3. **Verify File Access**

```python
# Check log file creation
touch app.log
```
