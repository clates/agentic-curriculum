-- 0012 permissions: per-user permission grants ('admin' for now).
CREATE TABLE user_permission (
    user_id TEXT NOT NULL REFERENCES app_user(id) ON DELETE CASCADE,
    permission TEXT NOT NULL CHECK (permission IN ('admin')),
    granted_at TEXT NOT NULL,
    PRIMARY KEY (user_id, permission)
);
