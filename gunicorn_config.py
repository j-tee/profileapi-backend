"""Gunicorn configuration file for Portfolio API"""

import multiprocessing

# Server socket
bind = "127.0.0.1:8001"
backlog = 2048

# Worker processes
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = 'sync'
worker_connections = 1000
timeout = 30
keepalive = 2

# Logging
accesslog = '/var/www/portfolio/backend/logs/gunicorn_access.log'
errorlog = '/var/www/portfolio/backend/logs/gunicorn_error.log'
loglevel = 'info'
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s"'

# Process naming
proc_name = 'portfolio_api'

# Server mechanics
daemon = False
pidfile = '/var/www/portfolio/backend/gunicorn.pid'
user = None
group = None
tmp_upload_dir = None

# SSL (handled by nginx)
# No SSL configuration needed here as nginx handles it
