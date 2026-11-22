"""The login flow: lockout gate, password check, session start."""

from __future__ import annotations

import os
import threading
from dataclasses import dataclass

from . import clock, lockout, passwords, store

# Each password check is a 32 MiB scrypt run, and anyone can ask for one without signing in. Only
# a few may run at once; the rest wait briefly and then get a calm "busy" answer. A refused attempt
# is turned away BEFORE the lockout gate, so it records nothing against anyone.
BUSY_WAIT_S = 3.0
BUSY_RETRY_AFTER_S = 3
# Waiting costs a worker thread, so only a few requests may wait for a slot; the rest are turned
# away at once instead of parking threads (a flood of sign-ins must not starve the whole app).
MAX_WAITERS = 4
_waiting = 0
_waiting_lock = threading.Lock()
_slots: threading.BoundedSemaphore | None = None
_slots_size = 0
_slots_lock = threading.Lock()


def _max_concurrent() -> int:
    try:
        return max(1, int(os.environ.get("AUTH_MAX_CONCURRENT_HASHES", "2")))
    except ValueError:
        return 2


def _slot_pool() -> threading.BoundedSemaphore:
    global _slots, _slots_size
    size = _max_concurrent()
    with _slots_lock:
        if _slots is None or _slots_size != size:
            _slots, _slots_size = threading.BoundedSemaphore(size), size
        return _slots


@dataclass(frozen=True)
class LoginResult:
    kind: str  # "ok" | "bad" | "locked" | "busy"
    token: str | None = None
    retry_after: int = 0
    user: store.User | None = None


def attempt_login(
    username: str, password: str, ip: str, user_agent: str | None = None
) -> LoginResult:
    pool = _slot_pool()
    if not pool.acquire(blocking=False):
        global _waiting
        with _waiting_lock:
            if _waiting >= MAX_WAITERS:
                return LoginResult("busy", retry_after=BUSY_RETRY_AFTER_S)
            _waiting += 1
        try:
            got = pool.acquire(timeout=BUSY_WAIT_S)
        finally:
            with _waiting_lock:
                _waiting -= 1
        if not got:
            return LoginResult("busy", retry_after=BUSY_RETRY_AFTER_S)
    try:
        return _attempt(username, password, ip, user_agent)
    finally:
        pool.release()


def _attempt(username: str, password: str, ip: str, user_agent: str | None) -> LoginResult:
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
