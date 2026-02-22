#!/bin/sh
set -e
echo "Collecting static files..."
python manage.py collectstatic --noinput --settings=config.settings.production

echo "Running migrations..."
python manage.py migrate --settings=config.settings.production

echo "Starting server..."
exec gunicorn config.wsgi:application \
    --bind 0.0.0.0:8000 \
    --workers 4 \
    --timeout 120 \
    --access-logfile - \
    --error-logfile -
