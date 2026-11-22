"""Users and sessions in SQLite. Tokens are never stored: only their SHA-256."""

from __future__ import annotations

import hashlib
import secrets
import sqlite3
import unicodedata
import uuid
from dataclasses import dataclass
from datetime import UTC, datetime

from db_utils import get_db_path

from . import clock
from .passwords import hash_password, validate_new_password

DEFAULT_FAMILY = "fam_local"
SESSION_LIFETIME_S = 30 * 86400
# A sliding session is only rewritten (and its cookie re-issued) this often, not on every request.
SESSION_REFRESH_S = 3600
USERNAME_MAX = 64
USER_AGENT_MAX = 200


def connect() -> sqlite3.Connection:
    conn = sqlite3.connect(get_db_path(), isolation_level=None, timeout=30)
    conn.execute("PRAGMA busy_timeout = 30000")
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def normalize_username(raw: str) -> str:
    return unicodedata.normalize("NFKC", raw).strip().lower()[:USERNAME_MAX]


def token_hash(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


@dataclass(frozen=True)
class User:
    id: str
    username: str
    password_hash: str
    family_id: str
    disabled: bool


def _user(row) -> User | None:
    return User(row[0], row[1], row[2], row[3], bool(row[4])) if row else None


_COLS = "id, username, password_hash, family_id, disabled"


def get_user(conn: sqlite3.Connection, username: str) -> User | None:
    return _user(
        conn.execute(
            f"SELECT {_COLS} FROM app_user WHERE lower(username)=?", (normalize_username(username),)
        ).fetchone()
    )


class UserError(ValueError):
    pass


def create_user(
    conn: sqlite3.Connection, username: str, password: str, family_id: str = DEFAULT_FAMILY
) -> User | None:
    """Create a user. Returns None (and changes nothing) when the username already exists."""
    name = normalize_username(username)
    if not name or any(ch.isspace() for ch in name):
        raise UserError("Username must be a single word with no spaces.")
    validate_new_password(password)
    if get_user(conn, name):
        return None
    if not conn.execute("SELECT 1 FROM family WHERE family_id=?", (family_id,)).fetchone():
        raise UserError(f"No such family: {family_id}")
    user_id = f"usr_{uuid.uuid4().hex[:16]}"
    conn.execute(
        "INSERT INTO app_user (id, username, password_hash, family_id, created_at) "
        "VALUES (?,?,?,?,?)",
        (user_id, name, hash_password(password), family_id,
         datetime.now(UTC).isoformat(timespec="seconds")),
    )  # fmt: skip
    return get_user(conn, name)


def set_password(conn: sqlite3.Connection, username: str, password: str) -> bool:
    validate_new_password(password)
    user = get_user(conn, username)
    if not user:
        return False
    conn.execute(
        "UPDATE app_user SET password_hash=? WHERE id=?", (hash_password(password), user.id)
    )
    conn.execute("DELETE FROM auth_session WHERE user_id=?", (user.id,))  # sign out everywhere
    return True


def set_disabled(conn: sqlite3.Connection, username: str, disabled: bool) -> bool:
    user = get_user(conn, username)
    if not user:
        return False
    conn.execute("UPDATE app_user SET disabled=? WHERE id=?", (int(disabled), user.id))
    if disabled:
        conn.execute("DELETE FROM auth_session WHERE user_id=?", (user.id,))
    return True


def replace_hash(conn: sqlite3.Connection, user_id: str, new_hash: str) -> None:
    conn.execute("UPDATE app_user SET password_hash=? WHERE id=?", (new_hash, user_id))


def create_session(conn: sqlite3.Connection, user_id: str, user_agent: str | None) -> str:
    """Start a session; returns the raw token (the only copy that will ever exist)."""
    now = clock.now()
    token = secrets.token_urlsafe(32)  # 32 random bytes
    conn.execute("DELETE FROM auth_session WHERE expires_at < ?", (now,))
    conn.execute(
        "INSERT INTO auth_session (token_hash, user_id, created_at, expires_at, last_seen_at, "
        "user_agent) VALUES (?,?,?,?,?,?)",
        (token_hash(token), user_id, now, now + SESSION_LIFETIME_S, now,
         (user_agent or "")[:USER_AGENT_MAX] or None),
    )  # fmt: skip
    return token


def resolve_session(conn: sqlite3.Connection, token: str | None) -> tuple[User, bool] | None:
    """The user a token belongs to, and whether the cookie should be re-issued (sliding expiry)."""
    if not token or len(token) > 200:
        return None
    now = clock.now()
    row = conn.execute(
        "SELECT s.id, s.expires_at, s.last_seen_at, u.id, u.username, u.password_hash, "
        "u.family_id, u.disabled FROM auth_session s JOIN app_user u ON u.id = s.user_id "
        "WHERE s.token_hash=?",
        (token_hash(token),),
    ).fetchone()
    if not row or row[1] <= now or row[7]:
        return None
    refreshed = now - row[2] >= SESSION_REFRESH_S
    if refreshed:
        conn.execute(
            "UPDATE auth_session SET last_seen_at=?, expires_at=? WHERE id=?",
            (now, now + SESSION_LIFETIME_S, row[0]),
        )
    return User(row[3], row[4], row[5], row[6], bool(row[7])), refreshed


def delete_session(conn: sqlite3.Connection, token: str | None) -> None:
    if token:
        conn.execute("DELETE FROM auth_session WHERE token_hash=?", (token_hash(token),))
