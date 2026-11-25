-- 0013 invites: single-use invite codes (only a SHA-256 is stored) and a verified-email flag.
-- Times in invite are unix seconds (REAL), like auth_session. Existing users count as verified.
CREATE TABLE invite (
    code_hash TEXT PRIMARY KEY,
    created_by TEXT REFERENCES app_user(id) ON DELETE SET NULL,
    created_at REAL NOT NULL,
    expires_at REAL NOT NULL,
    used_at REAL,
    used_by TEXT REFERENCES app_user(id) ON DELETE SET NULL
);

ALTER TABLE app_user ADD COLUMN email_verified_at TEXT;
UPDATE app_user SET email_verified_at = created_at;
