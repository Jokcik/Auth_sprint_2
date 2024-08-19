#!/usr/bin/env bash

set -e

chmod +x entrypoint.sh
chown www-data:www-data /var/cache/pypoetry

echo "Collecting static files..."
poetry run python manage.py collectstatic --no-input --clear  # No input to avoid any prompts

echo "Applying database migrations..."
poetry run python manage.py migrate

exec poetry run gunicorn --config ./gunicorn.conf.py
