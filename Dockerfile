# syntax=docker/dockerfile:1.6

# Node and Python versions: the newest LTS Node and the newest Python, both inside their security
# support windows (see "Dependency and runtime policy" in CONTRIBUTING.md). One Node image is used for
# the build AND copied into the runtime stage, so the frontend is built and run with the same Node and
# the same C library (glibc); no third-party install script is piped into a shell.
ARG NODE_IMAGE=node:26-slim
ARG PYTHON_IMAGE=python:3.15-slim

FROM ${NODE_IMAGE} AS node-runtime

# Stage 1: Build frontend
FROM ${NODE_IMAGE} AS frontend-builder

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
FROM ${PYTHON_IMAGE} AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    POETRY_VIRTUALENVS_CREATE=false \
    PYTHONPATH=/app/src

WORKDIR /app

# cron and build tools (some Python wheels may need compiling)
RUN apt-get update \
    && apt-get install --no-install-recommends -y build-essential curl cron \
    && rm -rf /var/lib/apt/lists/*

# Node.js from the official image (same version the frontend was built with): node, npm and npx.
COPY --from=node-runtime /usr/local/bin/node /usr/local/bin/node
COPY --from=node-runtime /usr/local/lib/node_modules /usr/local/lib/node_modules
RUN ln -s ../lib/node_modules/npm/bin/npm-cli.js /usr/local/bin/npm \
    && ln -s ../lib/node_modules/npm/bin/npx-cli.js /usr/local/bin/npx \
    && node --version && npm --version

# Install Python dependencies: runtime only (dev and test tools live in requirements-dev.txt)
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

# Build metadata, surfaced by GET /version (pass via --build-arg)
ARG GIT_SHA=unknown
ARG BUILD_TIME=unknown
ARG RELEASE_TAG=unknown
ENV GIT_SHA=${GIT_SHA} \
    BUILD_TIME=${BUILD_TIME} \
    RELEASE_TAG=${RELEASE_TAG}
LABEL org.opencontainers.image.revision=${GIT_SHA} \
      org.opencontainers.image.created=${BUILD_TIME} \
      org.opencontainers.image.source="https://github.com/clates/agentic-curriculum"

# Expose only frontend port (backend is proxied through Next.js API routes)
EXPOSE 3000

# start.sh runs as root so it can start the cron daemon, then drops to appuser
# for the backend and frontend processes via su.
COPY <<'EOF' /app/start.sh
#!/bin/bash
set -e

# Start cron daemon (reads /etc/cron.d/curriculum, jobs run as appuser)
cron

# Always seed/update standards on startup (idempotent — INSERT OR REPLACE).
# Add or update JSON files in standards_data/ and redeploy to pick up changes.
DB_PATH="${CURRICULUM_DB_PATH:-/app/curriculum.db}"
echo "Seeding curriculum database at $DB_PATH..."
su -s /bin/bash appuser -c "PYTHONPATH=/app/src python /app/src/ingest_standards.py"

# Run standards migration if present (for ID renames, splits, etc.)
if [ -f /app/src/migrate_standards.py ]; then
  echo "Running standards migration..."
  su -s /bin/bash appuser -c "PYTHONPATH=/app/src python /app/src/migrate_standards.py"
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
