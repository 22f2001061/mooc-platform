FROM python:3.12-slim

# Prevents Python from writing .pyc files and buffers stdout/stderr
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Install system dependencies for psycopg2
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev gcc \
    && rm -rf /var/lib/apt/lists/*

COPY requirements/production.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# # Collect static files at build time
# RUN python manage.py collectstatic --noinput \
#     --settings=config.settings.production \
#     || true   # allow failure if DB not connected yet (static doesn't need DB)

EXPOSE 8000

# Entrypoint: migrate then start gunicorn
COPY docker-entrypoint.sh /docker-entrypoint.sh
RUN chmod +x /docker-entrypoint.sh
ENTRYPOINT ["/docker-entrypoint.sh"]
