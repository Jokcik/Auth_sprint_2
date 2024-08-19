# Gunicorn configuration file: gunicorn.conf.py

import os

# Server socket
bind = '0.0.0.0:8000'
backlog = 2048

# Worker processes
workers = int(os.getenv('GUNICORN_PROCESSES', '2'))  # Default to 2 workers if environment variable is not set
threads = int(os.getenv('GUNICORN_THREADS', '4'))  # Default to 4 threads if environment variable is not set
worker_class = 'gthread'  # Use gthread worker class to enable threads
max_requests = 5000
max_requests_jitter = 100

# Security
user = 'www-data'
group = 'www-data'

# Server mechanics
preload_app = True  # Corresponds to uWSGI's lazy-apps
reload = True  # Enable automatic reloading on code changes
timeout = int(os.getenv('GUNICORN_HARAKIRI', '30'))  # Set timeout; default to 30 seconds if not set
graceful_timeout = 10  # Corresponds to uWSGI's reload-mercy
keepalive = 2

# Logging
loglevel = 'info'
accesslog = '-'  # Log to stdout
errorlog = '-'  # Log to stderr

# Working directory and Python path
chdir = '/opt/app'

# WSGI application path
wsgi_app = 'config.wsgi:application'
