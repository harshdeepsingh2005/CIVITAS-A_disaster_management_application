FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Install system deps needed for some Python packages (e.g. psycopg2)
RUN apt-get update \
    && apt-get install -y --no-install-recommends gcc libpq-dev build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first to leverage Docker cache
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project
COPY . .

# Create an unprivileged user and give ownership to it
RUN useradd -m civitas && chown -R civitas /app
USER civitas

# Railway injects PORT at runtime; default to 5000 for local Docker builds
ENV PORT=5000
EXPOSE ${PORT}

# Default to production flask env; override with Railway env or docker -e
ENV FLASK_ENV=production

# 2 workers to stay within Railway free-tier memory (~512 MB)
# Shell form so $PORT is expanded at runtime
CMD gunicorn --workers 2 --timeout 120 --bind 0.0.0.0:${PORT} app:app
