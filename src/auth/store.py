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
PERMISSIONS = frozenset({"admin"})
INVITE_ALPHABET = "ABCDEFGHJKMNPQRSTVWXYZ23456789"  # no 0 O 1 I L U
INVITE_LENGTH = 10
INVITE_DAYS = 14


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
    verified: bool = True  # False until a self-registered account confirms its email


def _user(row) -> User | None:
    return User(row[0], row[1], row[2], row[3], bool(row[4]), bool(row[5])) if row else None


_COLS = "id, username, password_hash, family_id, disabled, email_verified_at IS NOT NULL"


def get_user(conn: sqlite3.Connection, username: str) -> User | None:
    return _user(
        conn.execute(
            f"SELECT {_COLS} FROM app_user WHERE lower(username)=?", (normalize_username(username),)
        ).fetchone()
    )


class UserError(ValueError):
    pass


def create_family(conn: sqlite3.Connection, name: str) -> str:
    """Make a family and return its id (fam_ + 12 hex)."""
    family_id = f"fam_{uuid.uuid4().hex[:12]}"
    conn.execute(
        "INSERT INTO family (family_id, name, created_at) VALUES (?,?,?)",
        (family_id, name, datetime.now(UTC).isoformat(timespec="seconds")),
    )
    return family_id


def create_user(
    conn: sqlite3.Connection, username: str, password: str, family_id: str = DEFAULT_FAMILY
) -> User | None:
    """Create a user (operator-made, so verified). Returns None (and changes nothing) when the
    username already exists."""
    name = normalize_username(username)
    if not name or any(ch.isspace() for ch in name):
        raise UserError("Username must be a single word with no spaces.")
    validate_new_password(password)
    if get_user(conn, name):
        return None
    if not conn.execute("SELECT 1 FROM family WHERE family_id=?", (family_id,)).fetchone():
        raise UserError(f"No such family: {family_id}")
    insert_user(conn, name, hash_password(password), family_id, verified=True)
    return get_user(conn, name)


def insert_user(
    conn: sqlite3.Connection, name: str, password_hash: str, family_id: str, verified: bool
) -> str:
    """Insert an already-validated user row; returns its id."""
    user_id = f"usr_{uuid.uuid4().hex[:16]}"
    stamp = datetime.now(UTC).isoformat(timespec="seconds")
    conn.execute(
        "INSERT INTO app_user (id, username, password_hash, family_id, created_at, "
        "email_verified_at) VALUES (?,?,?,?,?,?)",
        (user_id, name, password_hash, family_id, stamp, stamp if verified else None),
    )
    return user_id


def create_invite(conn: sqlite3.Connection, created_by: str | None, days: int = INVITE_DAYS) -> str:
    """Make a single-use invite code. Returns the plain code: only its hash is stored."""
    code = "".join(secrets.choice(INVITE_ALPHABET) for _ in range(INVITE_LENGTH))
    now = clock.now()
    conn.execute(
        "INSERT INTO invite (code_hash, created_by, created_at, expires_at) VALUES (?,?,?,?)",
        (token_hash(code), created_by, now, now + days * 86400),
    )
    return code


def consume_invite(conn: sqlite3.Connection, code: str, user_id: str | None) -> bool:
    """Spend a code. True only for an unused, unexpired one (atomic: the UPDATE decides)."""
    now = clock.now()
    return (
        conn.execute(
            "UPDATE invite SET used_at=?, used_by=? "
            "WHERE code_hash=? AND used_at IS NULL AND expires_at > ?",
            (now, user_id, token_hash(code.strip().upper()), now),
        ).rowcount
        == 1
    )


def permissions(conn: sqlite3.Connection, user_id: str) -> frozenset[str]:
    rows = conn.execute(
        "SELECT permission FROM user_permission WHERE user_id=?", (user_id,)
    ).fetchall()
    return frozenset(r[0] for r in rows)


def grant(conn: sqlite3.Connection, username: str, permission: str) -> bool:
    """Give a user a permission (idempotent). False when the user does not exist."""
    if permission not in PERMISSIONS:
        raise UserError(
            f"Unknown permission: {permission} (known: {', '.join(sorted(PERMISSIONS))})"
        )
    user = get_user(conn, username)
    if not user:
        return False
    conn.execute(
        "INSERT OR IGNORE INTO user_permission (user_id, permission, granted_at) VALUES (?,?,?)",
        (user.id, permission, datetime.now(UTC).isoformat(timespec="seconds")),
    )
    return True


def revoke(conn: sqlite3.Connection, username: str, permission: str) -> bool:
    """Take a permission away. False when the user does not exist."""
    user = get_user(conn, username)
    if not user:
        return False
    conn.execute(
        "DELETE FROM user_permission WHERE user_id=? AND permission=?", (user.id, permission)
    )
    return True


def set_password(conn: sqlite3.Connection, username: str, password: str) -> bool:
    validate_new_password(password)
    user = get_user(conn, username)
    if not user:
        return False
    conn.execute(
        "UPDATE app_user SET password_hash=? WHERE id=?", (hash_password(password), user.id)
    )
    conn.execute("DELETE FROM auth_session WHERE user_id=?", (user.id,))  # sign out everywhere
    clear_attempts(conn, user.username)  # a new password starts with a clean slate
    return True


def set_disabled(conn: sqlite3.Connection, username: str, disabled: bool) -> bool:
    user = get_user(conn, username)
    if not user:
        return False
    conn.execute("UPDATE app_user SET disabled=? WHERE id=?", (int(disabled), user.id))
    if disabled:
        conn.execute("DELETE FROM auth_session WHERE user_id=?", (user.id,))
    else:
        clear_attempts(conn, user.username)
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


def clear_attempts(conn: sqlite3.Connection, username: str | None = None) -> int:
    """Forget lockout state: one user's rows (their 'user' row and every 'user_ip' row, for the
    sign-in name and for the registration keys 'register:<name>' and 'verify:<name>'), or all
    rows, address locks included, when no username is given. Returns the rows removed."""
    if username is None:
        return conn.execute("DELETE FROM login_attempt").rowcount
    name = normalize_username(username)
    removed = 0
    for key in (name, f"register:{name}", f"verify:{name}"):
        prefix = key + "|"
        removed += conn.execute(
            "DELETE FROM login_attempt WHERE (scope='user' AND key=?) "
            "OR (scope='user_ip' AND substr(key, 1, ?) = ?)",
            (key, len(prefix), prefix),
        ).rowcount
    return removed
