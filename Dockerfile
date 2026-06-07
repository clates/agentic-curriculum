# syntax=docker/dockerfile:1.6

# Stage 1: Build frontend
FROM node:20-alpine AS frontend-builder

WORKDIR /app/frontend

# Copy frontend package files
COPY frontend/package*.json ./

# Install dependencies
RUN npm ci

# Copy frontend source
COPY frontend ./

# Build the Next.js app
RUN npm run build

# Stage 2: Python backend with frontend
FROM python:3.11-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    POETRY_VIRTUALENVS_CREATE=false \
    PYTHONPATH=/app/src

WORKDIR /app

# Install Node.js, cron, and build tools
RUN apt-get update \
    && apt-get install --no-install-recommends -y build-essential curl cron \
    && curl -fsSL https://deb.nodesource.com/setup_20.x | bash - \
    && apt-get install -y nodejs \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt requirements.txt
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copy backend source
COPY standards_data ./standards_data
COPY src ./src
COPY scripts ./scripts
COPY docs ./docs
COPY README.md ./README.md

# Install crontab (must be root-owned, mode 0644 for cron.d)
COPY docker/crontab /etc/cron.d/curriculum
RUN chmod 0644 /etc/cron.d/curriculum

# Copy frontend build from builder stage
COPY --from=frontend-builder /app/frontend ./frontend

# Create a non-root user
RUN useradd -m -u 1000 appuser

# Ensure application files are owned by the non-root user
RUN chown -R appuser:appuser /app

# Expose only frontend port (backend is proxied through Next.js API routes)
EXPOSE 3000

# start.sh runs as root so it can start the cron daemon, then drops to appuser
# for the backend and frontend processes via su.
COPY <<'EOF' /app/start.sh
#!/bin/bash
set -e

# Start cron daemon (reads /etc/cron.d/curriculum, jobs run as appuser)
cron

# Seed the database only if it doesn't exist yet
DB_PATH="${CURRICULUM_DB_PATH:-/app/curriculum.db}"
if [ ! -f "$DB_PATH" ]; then
  echo "Database not found at $DB_PATH — seeding..."
  su -s /bin/bash appuser -c "PYTHONPATH=/app/src python /app/src/ingest_standards.py"
else
  echo "Database found at $DB_PATH — skipping seed."
fi

# Start backend in background (as appuser)
su -s /bin/bash appuser -c "uvicorn src.main:app --host 0.0.0.0 --port 8181" &

# Start frontend in background (as appuser)
su -s /bin/bash appuser -c "cd /app/frontend && npm start -- --port 3000" &

# Wait for any process to exit
wait -n

# Exit with status of process that exited first
exit $?
EOF

RUN chmod +x /app/start.sh

CMD ["/bin/bash", "/app/start.sh"]
