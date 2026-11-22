-- 0011 auth: username + password login (stopgap that grows into M7 accounts).
-- 0009 is reserved for week authoring and 0010 for the job queue; the runner applies by version,
-- so gaps are fine (it only skips versions already recorded in schema_version).
-- app_user.family_id points at the family the user belongs to. The first user maps to the
-- existing default family 'fam_local' so existing data stays visible. Routes still use the local
-- tenant; per-family isolation is M7.
-- Times in auth_session and login_attempt are unix seconds (REAL) so the clock is easy to inject.

CREATE TABLE app_user (
    id TEXT PRIMARY KEY,
    username TEXT NOT NULL,            -- stored lower-cased; unique ignoring case
    password_hash TEXT NOT NULL,       -- scrypt$N$r$p$salt$hash (see auth/passwords.py)
    family_id TEXT NOT NULL REFERENCES family(family_id),
    created_at TEXT NOT NULL,
    disabled INTEGER NOT NULL DEFAULT 0 CHECK (disabled IN (0, 1))
);
CREATE UNIQUE INDEX idx_app_user_username ON app_user(lower(username));
CREATE INDEX idx_app_user_family ON app_user(family_id);

CREATE TABLE auth_session (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    token_hash TEXT NOT NULL UNIQUE,   -- SHA-256 hex of the cookie token; the token is never stored
    user_id TEXT NOT NULL REFERENCES app_user(id) ON DELETE CASCADE,
    created_at REAL NOT NULL,
    expires_at REAL NOT NULL,
    last_seen_at REAL NOT NULL,
    user_agent TEXT
);
CREATE INDEX idx_auth_session_user ON auth_session(user_id);
CREATE INDEX idx_auth_session_expires ON auth_session(expires_at);

-- Lockout state. scope is 'user_ip' (one username from one address), 'ip' (one address, all
-- usernames) or 'user' (one username, all addresses). key is lower(username)|ip, ip or
-- lower(username). last_success_at on a 'user_ip' row marks an address the owner has used.
CREATE TABLE login_attempt (
    scope TEXT NOT NULL CHECK (scope IN ('user_ip', 'ip', 'user')),
    key TEXT NOT NULL,
    failures INTEGER NOT NULL DEFAULT 0,
    window_start REAL NOT NULL,
    last_failure_at REAL,
    locked_until REAL NOT NULL DEFAULT 0,
    lock_count INTEGER NOT NULL DEFAULT 0,
    last_success_at REAL,
    PRIMARY KEY (scope, key)
);
-- The prune DELETE filters on locked_until first (rows with no active lock).
CREATE INDEX idx_login_attempt_locked ON login_attempt(locked_until);
