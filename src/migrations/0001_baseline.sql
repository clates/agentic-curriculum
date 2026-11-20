-- 0001 baseline: the schema that used to be created by ingest_standards.create_database()
-- and packet_store.ensure_schema(). Every statement is IF NOT EXISTS, so applying this to an
-- existing database changes nothing.

CREATE TABLE IF NOT EXISTS standards (
    standard_id TEXT PRIMARY KEY,
    source TEXT,
    subject TEXT,
    grade_level INTEGER,
    description TEXT,
    json_blob TEXT
);

CREATE TABLE IF NOT EXISTS student_profiles (
    student_id TEXT PRIMARY KEY,
    progress_blob TEXT,
    plan_rules_blob TEXT,
    metadata_blob TEXT
);

CREATE TABLE IF NOT EXISTS weekly_packets (
    packet_id TEXT PRIMARY KEY,
    student_id TEXT NOT NULL,
    grade_level INTEGER NOT NULL,
    subject TEXT NOT NULL,
    week_of TEXT NOT NULL,
    status TEXT NOT NULL,
    weekly_overview TEXT,
    summary_json TEXT,
    payload_json TEXT NOT NULL,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_weekly_packets_student_week
    ON weekly_packets(student_id, week_of);

CREATE INDEX IF NOT EXISTS idx_weekly_packets_status
    ON weekly_packets(status);

CREATE TABLE IF NOT EXISTS daily_lessons (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    packet_id TEXT NOT NULL,
    day_label TEXT NOT NULL,
    focus TEXT,
    standards_json TEXT,
    lesson_plan_json TEXT NOT NULL,
    resources_json TEXT,
    worksheet_plans_json TEXT,
    resource_errors_json TEXT,
    created_at TEXT NOT NULL,
    FOREIGN KEY(packet_id) REFERENCES weekly_packets(packet_id) ON DELETE CASCADE,
    UNIQUE(packet_id, day_label)
);

CREATE TABLE IF NOT EXISTS worksheet_artifacts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    packet_id TEXT NOT NULL,
    daily_lesson_id INTEGER NOT NULL,
    day_label TEXT NOT NULL,
    kind TEXT NOT NULL,
    file_format TEXT NOT NULL,
    file_path TEXT NOT NULL,
    checksum TEXT,
    file_size_bytes INTEGER,
    metadata_json TEXT,
    created_at TEXT NOT NULL,
    FOREIGN KEY(packet_id) REFERENCES weekly_packets(packet_id) ON DELETE CASCADE,
    FOREIGN KEY(daily_lesson_id) REFERENCES daily_lessons(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_artifacts_packet_kind
    ON worksheet_artifacts(packet_id, kind);

CREATE INDEX IF NOT EXISTS idx_daily_lessons_packet
    ON daily_lessons(packet_id);

CREATE TABLE IF NOT EXISTS packet_feedback (
    feedback_id INTEGER PRIMARY KEY AUTOINCREMENT,
    packet_id TEXT NOT NULL,
    student_id TEXT NOT NULL,
    completed_at TEXT NOT NULL,
    mastery_feedback_blob TEXT,
    quantity_feedback INTEGER,
    FOREIGN KEY(packet_id) REFERENCES weekly_packets(packet_id) ON DELETE CASCADE
);
