-- 0006 week_plan: one row per (family, student, school week) holding the weekly loop's state,
-- the three outlines offered, the pick, and the deadlines. M3, M6, M8 and M10 all read this
-- shape. Status values are the loop states (M8.1 owns the transitions; see src/loop_state.py).
-- needs_attention is a flag, not a state. state_version is the compare-and-set counter.
-- Timestamps are ISO-8601 UTC text; outlines_json is the OutlineSet (src/outline_models.py).

CREATE TABLE week_plan (
    plan_id TEXT PRIMARY KEY,
    family_id TEXT NOT NULL REFERENCES family(family_id) ON DELETE CASCADE,
    student_id TEXT NOT NULL,
    week_start TEXT NOT NULL,          -- Monday of the school week the plan is FOR (YYYY-MM-DD)
    status TEXT NOT NULL DEFAULT 'awaiting_feedback' CHECK (status IN (
        'awaiting_feedback', 'outlining', 'awaiting_pick', 'authoring',
        'ready', 'printed', 'expired'
    )),
    state_version INTEGER NOT NULL DEFAULT 0,
    needs_attention INTEGER NOT NULL DEFAULT 0 CHECK (needs_attention IN (0, 1)),
    attention_reason TEXT,
    outlines_json TEXT,                -- OutlineSet, set when outlines are ready
    outlines_ready_at TEXT,
    picked_option TEXT,                -- option_id of the chosen outline
    packet_id TEXT,                    -- the authored week once it exists
    feedback_due_at TEXT,              -- soft: when the Friday check-in is nudged
    pick_deadline TEXT,                -- outlines expire here if not picked
    print_deadline TEXT,               -- the week must be ready to print by here (Sunday)
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    FOREIGN KEY (family_id, student_id) REFERENCES student_profiles(family_id, student_id)
        ON DELETE CASCADE,
    UNIQUE (family_id, student_id, week_start)
);
CREATE INDEX idx_week_plan_family_status ON week_plan(family_id, status);
CREATE INDEX idx_week_plan_deadlines ON week_plan(status, pick_deadline);
