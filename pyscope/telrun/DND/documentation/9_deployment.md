# Deployment Guide

## Overview

This guide covers the deployment process for the PyScope DND system in both development and production environments.

## Development Environment Setup

### 1. Local Environment Setup

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment (Windows)
.\venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment variables
set FLASK_ENV=development
set FLASK_DEBUG=1
set FLASK_APP=app.py
```

### 2. Development Configuration

```python
# config.py
class DevelopmentConfig:
    """Development configuration"""
    DEBUG = True
    TESTING = False
    DATABASE_URI = 'sqlite:///dev.db'
    LOG_LEVEL = 'DEBUG'
    CORS_ENABLED = True
```

## Production Deployment

### 1. Server Requirements

```text
Hardware Requirements:
- CPU: 4+ cores recommended
- RAM: 8GB minimum
- Storage: 20GB+ SSD
- Network: 100Mbps+

Software Requirements:
- Python 3.7+
- Nginx 1.18+
- Gunicorn 21.2+
- Supervisor 4.2+
```

### 2. Production Configuration

```python
# config.py
class ProductionConfig:
    """Production configuration"""
    DEBUG = False
    TESTING = False
    DATABASE_URI = 'postgresql://user:pass@localhost/dbname'
    LOG_LEVEL = 'INFO'
    CORS_ENABLED = False

    # Security settings
    SESSION_COOKIE_SECURE = True
    REMEMBER_COOKIE_SECURE = True
    PERMANENT_SESSION_LIFETIME = timedelta(days=7)
```

### 3. Nginx Configuration

```nginx
# /etc/nginx/sites-available/pyscope
server {
    listen 80;
    server_name example.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location /static/ {
        alias /path/to/pyscope/static/;
        expires 30d;
    }
}
```

### 4. Gunicorn Configuration

```python
# gunicorn.conf.py
bind = '127.0.0.1:8000'
workers = 4
worker_class = 'sync'
worker_connections = 1000
timeout = 30
keepalive = 2

# Logging
accesslog = '/var/log/pyscope/access.log'
errorlog = '/var/log/pyscope/error.log'
loglevel = 'info'
```

### 5. Supervisor Configuration

```ini
# /etc/supervisor/conf.d/pyscope.conf
[program:pyscope]
directory=/path/to/pyscope
command=/path/to/venv/bin/gunicorn -c gunicorn.conf.py app:app
user=www-data
autostart=true
autorestart=true
stderr_logfile=/var/log/pyscope/supervisor.err.log
stdout_logfile=/var/log/pyscope/supervisor.out.log
```

## Deployment Process

### 1. Initial Server Setup

```bash
# Update system
sudo apt update && sudo apt upgrade

# Install required packages
sudo apt install python3-venv nginx supervisor postgresql

# Create application directory
sudo mkdir -p /opt/pyscope
sudo chown -R www-data:www-data /opt/pyscope
```

### 2. Application Deployment

```bash
# Clone repository
git clone https://github.com/yourusername/pyscope.git /opt/pyscope

# Setup virtual environment
cd /opt/pyscope
python3 -m venv venv
source venv/bin/activate

# Install production dependencies
pip install -r requirements.txt
pip install gunicorn psycopg2-binary
```

### 3. Database Setup

```sql
-- Create database and user
CREATE DATABASE pyscope;
CREATE USER pyscope_user WITH PASSWORD 'secure_password';
GRANT ALL PRIVILEGES ON DATABASE pyscope TO pyscope_user;
```

### 4. Environment Configuration

```bash
# Create environment file
cat << EOF > .env
FLASK_ENV=production
DATABASE_URL=postgresql://pyscope_user:secure_password@localhost/pyscope
SECRET_KEY=your_secure_key_here
EOF
```

## Monitoring and Maintenance

### 1. Log Management

```python
# logging_config.py
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': '/var/log/pyscope/app.log',
            'maxBytes': 10485760,  # 10MB
            'backupCount': 5
        }
    }
}
```

### 2. Backup Strategy

```bash
#!/bin/bash
# backup_script.sh

# Backup database
pg_dump pyscope > /backup/pyscope_$(date +%Y%m%d).sql

# Backup application files
tar -czf /backup/pyscope_$(date +%Y%m%d).tar.gz /opt/pyscope

# Rotate backups (keep last 7 days)
find /backup -type f -mtime +7 -delete
```

### 3. Update Process

```bash
#!/bin/bash
# update_script.sh

# Stop application
sudo supervisorctl stop pyscope

# Backup current version
tar -czf /backup/pyscope_pre_update_$(date +%Y%m%d).tar.gz /opt/pyscope

# Update from repository
cd /opt/pyscope
git pull origin main

# Update dependencies
source venv/bin/activate
pip install -r requirements.txt

# Restart application
sudo supervisorctl start pyscope
```

## Security Considerations

### 1. SSL Configuration

```nginx
# SSL configuration in Nginx
server {
    listen 443 ssl;
    server_name example.com;

    ssl_certificate /etc/letsencrypt/live/example.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/example.com/privkey.pem;

    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
}
```

### 2. Firewall Configuration

```bash
# UFW firewall setup
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow ssh
sudo ufw allow http
sudo ufw allow https
sudo ufw enable
```

## Troubleshooting

### 1. Common Issues

```python
def check_system_health():
    """
    System health check script

    Checks:
    1. Database connectivity
    2. File permissions
    3. Service status
    4. Resource usage
    """
```

### 2. Recovery Procedures

```bash
# Service recovery
sudo supervisorctl restart pyscope

# Log inspection
tail -f /var/log/pyscope/app.log

# Database repair
pg_repair -d pyscope
```
