-- 0002 tenancy: accounts, sign-in and audit tables, and family_id on every tenant table.
-- Existing rows are backfilled to the single local family 'fam_local'. Nothing in the app reads
-- family_id yet (tenant guards arrive in a later wave), so every family_id has a default.
-- NOTE: packets do not yet carry a composite FK to the student: existing flows (and tests) save
-- packets for students that have no profile row. Packets hold a family FK and a (family_id,
-- packet_id) key that feedback references; the student link is enforced in a later wave.
-- packet_feedback is rebuilt (SQLite cannot add a composite FK in place); the runner has foreign
-- keys off and checks foreign_key_check before commit.

CREATE TABLE family (
    family_id TEXT PRIMARY KEY,
    name TEXT,
    created_at TEXT NOT NULL
);

INSERT INTO family (family_id, name, created_at)
VALUES ('fam_local', 'Local family', strftime('%Y-%m-%dT%H:%M:%SZ', 'now'));

CREATE TABLE parent_user (
    user_id TEXT PRIMARY KEY,
    family_id TEXT NOT NULL REFERENCES family(family_id) ON DELETE CASCADE,
    email TEXT,
    display_name TEXT,
    role TEXT NOT NULL DEFAULT 'member' CHECK (role IN ('owner', 'member')),
    created_at TEXT NOT NULL,
    disabled_at TEXT
);
CREATE INDEX idx_parent_user_family ON parent_user(family_id);
CREATE UNIQUE INDEX idx_parent_user_email ON parent_user(email) WHERE email IS NOT NULL;

CREATE TABLE auth_identity (
    identity_id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL REFERENCES parent_user(user_id) ON DELETE CASCADE,
    provider TEXT NOT NULL,            -- 'email_code' | 'password' | 'google' ...
    subject TEXT NOT NULL,             -- provider's stable id (email, google sub, ...)
    secret_hash TEXT,                  -- password hash when provider = 'password'
    created_at TEXT NOT NULL,
    UNIQUE (provider, subject)
);
CREATE INDEX idx_auth_identity_user ON auth_identity(user_id);

CREATE TABLE session (
    session_id TEXT PRIMARY KEY,       -- store a hash of the cookie token, never the token
    user_id TEXT NOT NULL REFERENCES parent_user(user_id) ON DELETE CASCADE,
    family_id TEXT NOT NULL REFERENCES family(family_id) ON DELETE CASCADE,
    created_at TEXT NOT NULL,
    expires_at TEXT NOT NULL,
    revoked_at TEXT
);
CREATE INDEX idx_session_user ON session(user_id);

CREATE TABLE auth_challenge (
    challenge_id TEXT PRIMARY KEY,
    purpose TEXT NOT NULL,             -- 'login' | 'invite' | 'verify_email'
    subject TEXT NOT NULL,             -- e.g. the email the code was sent to
    code_hash TEXT NOT NULL,
    attempts INTEGER NOT NULL DEFAULT 0,
    created_at TEXT NOT NULL,
    expires_at TEXT NOT NULL,
    consumed_at TEXT
);
CREATE INDEX idx_auth_challenge_subject ON auth_challenge(subject);

CREATE TABLE audit_log (
    audit_id INTEGER PRIMARY KEY AUTOINCREMENT,
    family_id TEXT REFERENCES family(family_id) ON DELETE SET NULL,
    user_id TEXT,
    action TEXT NOT NULL,
    target TEXT,
    detail_json TEXT,
    created_at TEXT NOT NULL
);
CREATE INDEX idx_audit_log_family ON audit_log(family_id, created_at);

-- family_id on the tenant tables. ALTER ... ADD COLUMN (rather than a rebuild) keeps every
-- existing column and row as is; the runner runs with foreign keys off, so a REFERENCES column
-- with a non-null default is allowed, and the constraint is enforced on later writes.
ALTER TABLE student_profiles
    ADD COLUMN family_id TEXT NOT NULL DEFAULT 'fam_local' REFERENCES family(family_id);
CREATE UNIQUE INDEX idx_student_profiles_family_student
    ON student_profiles(family_id, student_id);

ALTER TABLE weekly_packets
    ADD COLUMN family_id TEXT NOT NULL DEFAULT 'fam_local' REFERENCES family(family_id);
CREATE UNIQUE INDEX idx_weekly_packets_family_packet ON weekly_packets(family_id, packet_id);
CREATE INDEX idx_weekly_packets_family ON weekly_packets(family_id);

ALTER TABLE daily_lessons
    ADD COLUMN family_id TEXT NOT NULL DEFAULT 'fam_local' REFERENCES family(family_id);

ALTER TABLE worksheet_artifacts
    ADD COLUMN family_id TEXT NOT NULL DEFAULT 'fam_local' REFERENCES family(family_id);

-- packet_feedback (canonical shape: cascade from the packet)
CREATE TABLE packet_feedback_new (
    feedback_id INTEGER PRIMARY KEY AUTOINCREMENT,
    packet_id TEXT NOT NULL,
    student_id TEXT NOT NULL,
    completed_at TEXT NOT NULL,
    mastery_feedback_blob TEXT,
    quantity_feedback INTEGER,
    family_id TEXT NOT NULL DEFAULT 'fam_local',
    FOREIGN KEY (packet_id) REFERENCES weekly_packets(packet_id) ON DELETE CASCADE,
    FOREIGN KEY (family_id, packet_id) REFERENCES weekly_packets(family_id, packet_id)
);
INSERT INTO packet_feedback_new (feedback_id, packet_id, student_id, completed_at,
    mastery_feedback_blob, quantity_feedback)
SELECT feedback_id, packet_id, student_id, completed_at,
    mastery_feedback_blob, quantity_feedback FROM packet_feedback;
DROP TABLE packet_feedback;
ALTER TABLE packet_feedback_new RENAME TO packet_feedback;
