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

# Install Node.js for serving frontend
RUN apt-get update \
    && apt-get install --no-install-recommends -y build-essential curl \
    && curl -fsSL https://deb.nodesource.com/setup_20.x | bash - \
    && apt-get install -y nodejs \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt requirements.txt
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copy backend source
COPY standards_data ./standards_data
COPY src ./src
COPY docs ./docs
COPY README.md ./README.md

# Copy frontend build from builder stage
COPY --from=frontend-builder /app/frontend ./frontend

# Create a non-root user
RUN useradd -m -u 1000 appuser

# Ensure application files are owned by the non-root user
RUN chown -R appuser:appuser /app

# Expose only frontend port (backend is proxied through Next.js API routes)
EXPOSE 3000

USER appuser

# Create startup script to run both backend and frontend
COPY --chown=appuser:appuser <<'EOF' /app/start.sh
#!/bin/bash
set -e

# Seed the database only if it doesn't exist yet
DB_PATH="${CURRICULUM_DB_PATH:-/app/curriculum.db}"
if [ ! -f "$DB_PATH" ]; then
  echo "Database not found at $DB_PATH — seeding..."
  python src/ingest_standards.py
else
  echo "Database found at $DB_PATH — skipping seed."
fi

# Start backend in background
uvicorn src.main:app --host 0.0.0.0 --port 8000 &

# Start frontend (production mode)
cd /app/frontend
npm start -- --port 3000 &

# Wait for any process to exit
wait -n

# Exit with status of process that exited first
exit $?
EOF

RUN chmod +x /app/start.sh

CMD ["/bin/bash", "/app/start.sh"]
