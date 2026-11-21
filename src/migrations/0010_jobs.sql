-- 0010 job queue (M8.2) and family timezone (M8.4).
-- jobs: a durable SQLite-backed queue. One row per unit of background work. (family_id, kind,
-- idempotency_key) is unique, so enqueueing the same work twice is one job. A worker claims a
-- job inside BEGIN IMMEDIATE and holds a lease; an expired lease is reclaimed. A job that keeps
-- failing ends 'dead' (quarantined, never deleted) and raises one maintainer alert (alerted_at).
-- Timestamps are fixed-width ISO-8601 UTC text (YYYY-MM-DDTHH:MM:SS.ffffffZ) so they compare as
-- strings. payload_json must hold no child data beyond ids.
-- family_settings.timezone: IANA name for the scheduler's family-local windows. It is a side table,
-- not a column on family: existing code and tests insert into family positionally. No row, or a
-- NULL timezone, means the deployment default (SCHEDULER_DEFAULT_TZ).

CREATE TABLE jobs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    family_id TEXT NOT NULL REFERENCES family(family_id) ON DELETE CASCADE,
    kind TEXT NOT NULL,
    payload_json TEXT NOT NULL DEFAULT '{}',
    idempotency_key TEXT NOT NULL,
    state TEXT NOT NULL DEFAULT 'queued'
        CHECK (state IN ('queued', 'running', 'succeeded', 'failed', 'dead')),
    attempts INTEGER NOT NULL DEFAULT 0,
    max_attempts INTEGER NOT NULL DEFAULT 5 CHECK (max_attempts >= 1),
    run_after TEXT NOT NULL,
    lease_owner TEXT,
    lease_expires_at TEXT,
    last_error TEXT,
    alerted_at TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    finished_at TEXT,
    UNIQUE (family_id, kind, idempotency_key)
);
CREATE INDEX idx_jobs_ready ON jobs(state, run_after);
CREATE INDEX idx_jobs_lease ON jobs(lease_expires_at) WHERE state = 'running';

CREATE TABLE family_settings (
    family_id TEXT PRIMARY KEY REFERENCES family(family_id) ON DELETE CASCADE,
    timezone TEXT,
    updated_at TEXT NOT NULL
);
