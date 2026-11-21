-- 0008 student FK (decision D2): packets and feedback now carry a real composite foreign key
-- (family_id, student_id) -> student_profiles(family_id, student_id).
--
-- DESTRUCTIVE ON PURPOSE: the development database is disposable (user decision), so rows that
-- cannot satisfy the new constraint are DROPPED, not repaired: every weekly_packets row whose
-- (family_id, student_id) has no student_profiles row, plus everything hanging off those
-- packets (daily_lessons, worksheet_artifacts, packet_feedback, week_documents, prep_checks),
-- and any packet_feedback row whose own student has no profile. A production database must
-- not hold such rows; the app now creates a minimal profile (db_utils.ensure_student) before
-- it first saves a packet for an unseen student.
--
-- student_profiles already holds family_id (0002) with the unique (family_id, student_id) key
-- that a composite FK needs (idx_student_profiles_family_student); nothing to rebuild there.
-- week_plan (0006) already has this FK. week_documents and prep_checks have no student column:
-- they reach the student through their (family_id, packet_id) FK to weekly_packets, so the
-- packet's FK covers them. llm_usage keeps a nullable, FK-free student_id on purpose: it is a
-- spend ledger that must outlive the student.
--
-- weekly_packets and packet_feedback are rebuilt with the 12-step recipe (the runner has foreign
-- keys off and runs foreign_key_check before commit). Children of weekly_packets reference it by
-- name, so drop + rename keeps them pointing at the new table.

-- 1. Drop the rows that violate the new constraint (children first; FKs are off, no cascade).
DELETE FROM weekly_packets
WHERE NOT EXISTS (
    SELECT 1 FROM student_profiles s
    WHERE s.family_id = weekly_packets.family_id AND s.student_id = weekly_packets.student_id
);
DELETE FROM prep_checks WHERE NOT EXISTS (
    SELECT 1 FROM weekly_packets p
    WHERE p.family_id = prep_checks.family_id AND p.packet_id = prep_checks.packet_id
);
DELETE FROM week_documents WHERE NOT EXISTS (
    SELECT 1 FROM weekly_packets p
    WHERE p.family_id = week_documents.family_id AND p.packet_id = week_documents.packet_id
);
DELETE FROM worksheet_artifacts
WHERE packet_id NOT IN (SELECT packet_id FROM weekly_packets);
DELETE FROM daily_lessons
WHERE packet_id NOT IN (SELECT packet_id FROM weekly_packets);
DELETE FROM packet_feedback WHERE NOT EXISTS (
    SELECT 1 FROM student_profiles s
    WHERE s.family_id = packet_feedback.family_id AND s.student_id = packet_feedback.student_id
) OR packet_id NOT IN (SELECT packet_id FROM weekly_packets);

-- 2. weekly_packets with the student FK.
CREATE TABLE weekly_packets_new (
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
    updated_at TEXT NOT NULL,
    family_id TEXT NOT NULL DEFAULT 'fam_local' REFERENCES family(family_id),
    FOREIGN KEY (family_id, student_id) REFERENCES student_profiles(family_id, student_id)
        ON DELETE CASCADE
);
INSERT INTO weekly_packets_new (packet_id, student_id, grade_level, subject, week_of, status,
    weekly_overview, summary_json, payload_json, created_at, updated_at, family_id)
SELECT packet_id, student_id, grade_level, subject, week_of, status,
    weekly_overview, summary_json, payload_json, created_at, updated_at, family_id
FROM weekly_packets;
DROP TABLE weekly_packets;
ALTER TABLE weekly_packets_new RENAME TO weekly_packets;
CREATE INDEX idx_weekly_packets_student_week ON weekly_packets(student_id, week_of);
CREATE INDEX idx_weekly_packets_status ON weekly_packets(status);
CREATE UNIQUE INDEX idx_weekly_packets_family_packet ON weekly_packets(family_id, packet_id);
CREATE INDEX idx_weekly_packets_family ON weekly_packets(family_id);

-- 3. packet_feedback with the student FK (keeps the 0002/0005 packet FKs and indexes).
CREATE TABLE packet_feedback_new (
    feedback_id INTEGER PRIMARY KEY AUTOINCREMENT,
    packet_id TEXT NOT NULL,
    student_id TEXT NOT NULL,
    completed_at TEXT NOT NULL,
    mastery_feedback_blob TEXT,
    quantity_feedback INTEGER,
    family_id TEXT NOT NULL DEFAULT 'fam_local',
    check_results_json TEXT,
    quick_rating TEXT,
    derived_mastery_json TEXT,
    version INTEGER NOT NULL DEFAULT 1,
    updated_at TEXT,
    FOREIGN KEY (packet_id) REFERENCES weekly_packets(packet_id) ON DELETE CASCADE,
    FOREIGN KEY (family_id, packet_id) REFERENCES weekly_packets(family_id, packet_id),
    FOREIGN KEY (family_id, student_id) REFERENCES student_profiles(family_id, student_id)
        ON DELETE CASCADE
);
INSERT INTO packet_feedback_new (feedback_id, packet_id, student_id, completed_at,
    mastery_feedback_blob, quantity_feedback, family_id, check_results_json, quick_rating,
    derived_mastery_json, version, updated_at)
SELECT feedback_id, packet_id, student_id, completed_at, mastery_feedback_blob,
    quantity_feedback, family_id, check_results_json, quick_rating, derived_mastery_json,
    version, updated_at
FROM packet_feedback;
DROP TABLE packet_feedback;
ALTER TABLE packet_feedback_new RENAME TO packet_feedback;
CREATE UNIQUE INDEX idx_packet_feedback_packet ON packet_feedback(family_id, packet_id);
