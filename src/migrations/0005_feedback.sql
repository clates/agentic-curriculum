-- 0005 feedback: raw check results become the source of truth (D4). Additive columns only; the
-- mastery blob on the student stays derived data that can be rebuilt from these rows.
--   check_results_json   {check_id: 'got_it'|'shaky'|'missed'} exactly as the parent ticked them
--   quick_rating         'smooth'|'mixed'|'rough' when no per-check results were given
--   derived_mastery_json {standard_id: MASTERED|DEVELOPING|STRUGGLING} that was applied
--   version              1 on first save, +1 on every edit
--   updated_at           last save time (completed_at keeps its existing meaning)
ALTER TABLE packet_feedback ADD COLUMN check_results_json TEXT;
ALTER TABLE packet_feedback ADD COLUMN quick_rating TEXT;
ALTER TABLE packet_feedback ADD COLUMN derived_mastery_json TEXT;
ALTER TABLE packet_feedback ADD COLUMN version INTEGER NOT NULL DEFAULT 1;
ALTER TABLE packet_feedback ADD COLUMN updated_at TEXT;

-- One feedback row per packet so saves can be a real upsert. The old code did select-then-update,
-- so duplicates should not exist; if any do, keep the newest.
DELETE FROM packet_feedback
WHERE feedback_id NOT IN (
    SELECT MAX(feedback_id) FROM packet_feedback GROUP BY family_id, packet_id
);
CREATE UNIQUE INDEX idx_packet_feedback_packet ON packet_feedback(family_id, packet_id);
