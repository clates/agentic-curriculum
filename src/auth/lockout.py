"""Progressive lockout for logins. State lives in the ``login_attempt`` table (SQLite).

Three layers, so nobody can lock the real owner out from somewhere else:

* ``user_ip``  one username from one address. 3 free wrong tries; each wrong try after that locks
  that pair for 15 s, 30 s, 60 s ... doubling up to 1 hour. Reset by a correct password, or after
  a quiet period with no failures.
* ``ip``       one address across all usernames. 20 wrong tries inside 10 minutes lock that address
  for 10 minutes. Stops one address from walking through many usernames. A (username, address)
  pair the owner has signed in from in the last 30 days is exempt from this lock, so a stranger
  behind the same public address cannot stop the owner's own phone at home; the pair layer's own
  backoff still applies, so someone who shares that address can still trigger the pair lock
  (`python -m auth unlock` clears it, and the 30-day session cookie means the owner rarely needs
  to type the password). Code resends count here too (``reserve_ip``), with no pair to exempt.
* ``user``     one username across all addresses (a spread-out attack). 30 wrong tries inside an hour
  make addresses this user has never signed in from wait 30 s, doubling up to 5 minutes. An
  address the owner has signed in from in the last 30 days is never held by this layer, so the
  right address with the right password always gets through; it only slows strangers.

A try is counted BEFORE the password is checked and given back on success, so a burst of parallel
guesses cannot slip past a lock that has not been written yet. A locked try never has its
password checked and never says whether the username exists (unknown names get the same rows).

Every number is multiplied by ``AUTH_BACKOFF_SCALE`` (default 1; tests set a small fraction).
Times are unix seconds from ``auth.clock``.
"""

from __future__ import annotations

import math
import os
import sqlite3

FREE_FAILURES = 3
BASE_LOCK_S = 15
MAX_LOCK_S = 3600
QUIET_RESET_S = 2 * 3600  # no failures for 2 hours (and not locked): the slate is clean

IP_CEILING = 20
IP_WINDOW_S = 600
IP_LOCK_S = 600

USER_CEILING = 30
USER_WINDOW_S = 3600
USER_BASE_LOCK_S = 30
USER_MAX_LOCK_S = 300

KNOWN_ADDRESS_S = 30 * 86400

PRUNE_EVERY_S = 60
MAX_ROWS = 20000
_last_prune = float("-inf")


def scale() -> float:
    try:
        value = float(os.environ.get("AUTH_BACKOFF_SCALE", "1"))
    except ValueError:
        return 1.0
    return value if value > 0 else 1.0


def lock_seconds(failures: int) -> float:
    """Lock length after the ``failures``-th wrong try for one (username, address) pair."""
    if failures <= FREE_FAILURES:
        return 0.0
    exponent = min(failures - FREE_FAILURES - 1, 20)
    return float(min(BASE_LOCK_S * 2**exponent, MAX_LOCK_S)) * scale()


def _row(conn: sqlite3.Connection, scope: str, key: str):
    return conn.execute(
        "SELECT failures, window_start, last_failure_at, locked_until, lock_count, last_success_at "
        "FROM login_attempt WHERE scope=? AND key=?",
        (scope, key),
    ).fetchone()


def _save(conn, scope, key, **fields) -> None:
    cols = ["failures", "window_start", "last_failure_at", "locked_until", "lock_count"]
    existing = _row(conn, scope, key)
    if existing is None:
        conn.execute(
            "INSERT INTO login_attempt (scope, key, failures, window_start, last_failure_at,"
            " locked_until, lock_count) VALUES (?,?,0,?,NULL,0,0)",
            (scope, key, fields.get("window_start", 0)),
        )
    sets = ", ".join(f"{c}=?" for c in cols if c in fields)
    if sets:
        conn.execute(
            f"UPDATE login_attempt SET {sets} WHERE scope=? AND key=?",
            [fields[c] for c in cols if c in fields] + [scope, key],
        )


def _prune(conn: sqlite3.Connection, now: float) -> None:
    """Forget old rows, at most once a minute, and keep the table under MAX_ROWS."""
    global _last_prune
    if 0 <= now - _last_prune < PRUNE_EVERY_S * scale():
        return
    _last_prune = now  # also when the clock went backwards: the next call re-prunes
    conn.execute(
        "DELETE FROM login_attempt WHERE locked_until < ? AND COALESCE(last_failure_at, 0) < ? "
        "AND (last_success_at IS NULL OR last_success_at < ?)",
        (now, now - QUIET_RESET_S * scale(), now - KNOWN_ADDRESS_S),
    )
    (count,) = conn.execute("SELECT COUNT(*) FROM login_attempt").fetchone()
    if count > MAX_ROWS:  # a flood of made-up names: drop the oldest strangers first
        # Never a row that is holding an active lock: evicting it would let the attacker reset it.
        conn.execute(
            "DELETE FROM login_attempt WHERE rowid IN (SELECT rowid FROM login_attempt "
            "WHERE last_success_at IS NULL AND locked_until <= ? "
            "ORDER BY COALESCE(last_failure_at, 0) LIMIT ?)",
            (now, count - MAX_ROWS),
        )


def _is_known_address(row, now: float) -> bool:
    return bool(row and row[5] and now - row[5] < KNOWN_ADDRESS_S)


def reserve(conn: sqlite3.Connection, username: str, ip: str, now: float) -> float:
    """Gate one attempt. Returns seconds to wait (> 0 means locked and nothing was recorded).

    Otherwise counts the attempt as a failure up front and returns 0; call ``record_success``
    when the password turns out right. ``conn`` must be in autocommit mode.
    """
    s = scale()
    conn.execute("BEGIN IMMEDIATE")
    try:
        _prune(conn, now)
        pair_key, ip_key, user_key = f"{username}|{ip}", ip, username
        pair, ip_row, user = (
            _row(conn, "user_ip", pair_key),
            _row(conn, "ip", ip_key),
            _row(conn, "user", user_key),
        )
        locked_until = 0.0
        if ip_row and not _is_known_address(pair, now):
            locked_until = max(locked_until, ip_row[3])
        if pair:
            locked_until = max(locked_until, pair[3])
        if user and not _is_known_address(pair, now):
            locked_until = max(locked_until, user[3])
        if locked_until > now:
            conn.execute("COMMIT")
            return math.ceil(locked_until - now)

        # -- pair: progressive backoff, with a quiet-period reset
        failures, last, lock_until, count = 0, None, 0.0, 0
        if pair:
            failures, last = pair[0], pair[2]
            if last is not None and now - last > QUIET_RESET_S * s:
                failures = 0
        failures += 1
        _save(
            conn,
            "user_ip",
            pair_key,
            failures=failures,
            window_start=now,
            last_failure_at=now,
            locked_until=now + lock_seconds(failures),
            lock_count=0,
        )

        _count_ip(conn, ip_key, ip_row, now)

        # -- username ceiling across addresses: slows strangers, never the known address
        failures, window, count = (user[0], user[1], user[4]) if user else (0, now, 0)
        if user and user[2] is not None and now - user[2] > QUIET_RESET_S * s:
            failures, window, count = 0, now, 0
        if now - window > USER_WINDOW_S * s:
            failures, window = 0, now
        failures += 1
        lock_until = user[3] if user else 0.0
        if failures >= USER_CEILING:
            count += 1
            lock_until = now + min(USER_BASE_LOCK_S * 2 ** (count - 1), USER_MAX_LOCK_S) * s
            failures, window = 0, now
        _save(
            conn, "user", user_key, failures=failures, window_start=window, last_failure_at=now,
            locked_until=lock_until, lock_count=count,
        )  # fmt: skip
        conn.execute("COMMIT")
        return 0.0
    except BaseException:
        conn.execute("ROLLBACK")
        raise


def _count_ip(conn, ip_key: str, ip_row, now: float) -> None:
    """The address ceiling over a rolling window."""
    s = scale()
    failures, window = (ip_row[0], ip_row[1]) if ip_row else (0, now)
    if now - window > IP_WINDOW_S * s:
        failures, window = 0, now
    failures += 1
    lock_until = ip_row[3] if ip_row else 0.0  # a known pair passing through keeps the lock
    if failures >= IP_CEILING:
        lock_until, failures, window = now + IP_LOCK_S * s, 0, now
    _save(
        conn, "ip", ip_key, failures=failures, window_start=window, last_failure_at=now,
        locked_until=lock_until,
    )  # fmt: skip


def reserve_ip(conn: sqlite3.Connection, ip: str, now: float) -> float:
    """Gate and count one request against the address layer alone (no username, no password).
    Returns seconds to wait (> 0 means locked and nothing was recorded)."""
    conn.execute("BEGIN IMMEDIATE")
    try:
        _prune(conn, now)
        row = _row(conn, "ip", ip)
        if row and row[3] > now:
            conn.execute("COMMIT")
            return math.ceil(row[3] - now)
        _count_ip(conn, ip, row, now)
        conn.execute("COMMIT")
        return 0.0
    except BaseException:
        conn.execute("ROLLBACK")
        raise


def record_success(conn: sqlite3.Connection, username: str, ip: str, now: float) -> None:
    """The password was right: give the tentative failure back and remember this address."""
    conn.execute("BEGIN IMMEDIATE")
    try:
        pair_key = f"{username}|{ip}"
        _save(conn, "user_ip", pair_key, failures=0, locked_until=0, lock_count=0)
        conn.execute(
            "UPDATE login_attempt SET last_success_at=? WHERE scope='user_ip' AND key=?",
            (now, pair_key),
        )
        conn.execute(
            "UPDATE login_attempt SET failures = MAX(failures - 1, 0) WHERE scope='ip' AND key=?",
            (ip,),
        )
        conn.execute(
            "UPDATE login_attempt SET failures = 0 WHERE scope='user' AND key=?", (username,)
        )
        conn.execute("COMMIT")
    except BaseException:
        conn.execute("ROLLBACK")
        raise
