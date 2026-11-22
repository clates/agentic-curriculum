"""The login flow: lockout gate, password check, session start."""

from __future__ import annotations

from dataclasses import dataclass

from . import clock, lockout, passwords, store


@dataclass(frozen=True)
class LoginResult:
    kind: str  # "ok" | "bad" | "locked"
    token: str | None = None
    retry_after: int = 0
    user: store.User | None = None


def attempt_login(
    username: str, password: str, ip: str, user_agent: str | None = None
) -> LoginResult:
    name = store.normalize_username(username)
    conn = store.connect()
    try:
        wait = lockout.reserve(conn, name, ip, clock.now())
        if wait > 0:
            return LoginResult("locked", retry_after=int(wait))  # password never evaluated
        user = store.get_user(conn, name)
        if user is None or user.disabled:
            passwords.verify_dummy(password)  # same cost as a real check
            return LoginResult("bad")
        if not passwords.verify_password(password, user.password_hash):
            return LoginResult("bad")
        lockout.record_success(conn, name, ip, clock.now())
        if passwords.needs_rehash(user.password_hash):
            store.replace_hash(conn, user.id, passwords.hash_password(password))
        token = store.create_session(conn, user.id, user_agent)
        return LoginResult("ok", token=token, user=user)
    finally:
        conn.close()
