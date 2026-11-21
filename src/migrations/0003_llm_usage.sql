-- M1.5: model-call ledger. Opaque family/student ids only; never prompt or response text.
-- No foreign keys: the ledger must keep working across tenancy changes and after a child is deleted.
CREATE TABLE IF NOT EXISTS llm_usage (
    usage_id TEXT PRIMARY KEY,
    family_id TEXT,
    student_id TEXT,
    task TEXT NOT NULL,
    model TEXT NOT NULL,
    prompt_tokens INTEGER NOT NULL DEFAULT 0,
    completion_tokens INTEGER NOT NULL DEFAULT 0,
    cost_usd REAL,
    latency_ms INTEGER,
    status TEXT NOT NULL,
    created_at TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_llm_usage_family_created ON llm_usage (family_id, created_at);
