-- 0007 loop state: an append-only log of the events that moved a week_plan (M8.1). The unique
-- (plan_id, event_key) index is what makes a replayed event a no-op, even across processes.

CREATE TABLE loop_event (
    event_id INTEGER PRIMARY KEY AUTOINCREMENT,
    family_id TEXT NOT NULL REFERENCES family(family_id) ON DELETE CASCADE,
    plan_id TEXT NOT NULL REFERENCES week_plan(plan_id) ON DELETE CASCADE,
    event_key TEXT,                    -- caller's idempotency key; NULL = not deduplicated by key
    event_type TEXT NOT NULL,
    from_status TEXT NOT NULL,
    to_status TEXT NOT NULL,
    payload_json TEXT,
    created_at TEXT NOT NULL
);
CREATE UNIQUE INDEX idx_loop_event_key ON loop_event(plan_id, event_key)
    WHERE event_key IS NOT NULL;
CREATE INDEX idx_loop_event_plan ON loop_event(plan_id, event_id);
