"""SQLite job queue (M8.2): idempotent enqueue, atomic claim with a lease, retry, dead-letter.

Many workers can share one SQLite file. Every state change that must not race (claim, reclaim,
complete, fail) runs inside ``BEGIN IMMEDIATE``, so SQLite's single writer lock is the mutex.

Lifecycle::

    queued --claim--> running --complete--> succeeded
                         |--fail (attempts left)--> queued   (run_after = backoff + jitter)
                         |--fail (out of attempts)--> dead   (quarantined; one alert)
                         |--lease expired (worker died)--> queued, or dead if out of attempts
    dead --retry_dead--> queued (attempts reset)             (the operator's decision)

``attempts`` counts claims, so a worker that dies mid-job spends an attempt: a job that kills its
worker every time cannot loop forever. A release on graceful shutdown refunds the attempt.

Idempotency key formats (decision D6; they end up in logs, so do not change them):
``outlines:{plan_id}``, ``author:{plan_id}:{option_id}``, ``reminder:{family_id}:{week_start}``,
``nudge:{family_id}:{week_start}``, ``lastcall:{family_id}:{week_start}``. After an outline
regeneration the scheduler appends ``:r{n}`` (n = regenerations so far) so a new round is new work.

Time is injectable (``now=``) on every function, so tests never sleep.
"""

from __future__ import annotations

import hashlib
import json
import os
import random
import sqlite3
from dataclasses import dataclass, fields
from datetime import UTC, datetime, timedelta
from typing import Any, Callable

STATES = ("queued", "running", "succeeded", "failed", "dead")
DEFAULT_MAX_ATTEMPTS = 5
BACKOFF_BASE_SECONDS = 30.0
BACKOFF_CAP_SECONDS = 3600.0
LAST_ERROR_MAX = 2000

# Called (job) after a job turns dead (the worker logs it; the email digest is job_alerts.send_digest).
DeadHook = Callable[["Job"], None]


def family_hash(family_id: str) -> str:
    """Short, salted hash used wherever a family must be referred to without its id."""
    salt = os.environ.get("JOB_ALERT_SALT", "")
    return hashlib.sha256((salt + family_id).encode()).hexdigest()[:8]


def utcnow() -> datetime:
    return datetime.now(UTC)


def iso(dt: datetime) -> str:
    """Fixed-width UTC text; compares correctly as a string."""
    if dt.tzinfo is None:
        raise ValueError("naive datetime: pass an aware datetime")
    return dt.astimezone(UTC).strftime("%Y-%m-%dT%H:%M:%S.%fZ")


def parse_iso(text: str) -> datetime:
    return datetime.strptime(text, "%Y-%m-%dT%H:%M:%S.%fZ").replace(tzinfo=UTC)


@dataclass(frozen=True)
class Job:
    id: int
    family_id: str
    kind: str
    payload: dict[str, Any]
    idempotency_key: str
    state: str
    attempts: int
    max_attempts: int
    run_after: str
    lease_owner: str | None
    lease_expires_at: str | None
    last_error: str | None
    alerted_at: str | None
    created_at: str
    updated_at: str
    finished_at: str | None


def _row_to_job(row: sqlite3.Row) -> Job:
    cols = {f.name: row[f.name] for f in fields(Job) if f.name != "payload"}
    return Job(payload=json.loads(row["payload_json"] or "{}"), **cols)


def connect(db_path: str) -> sqlite3.Connection:
    """A connection tuned for many writers on one file (WAL, long busy timeout)."""
    conn = sqlite3.connect(db_path, timeout=30, isolation_level=None, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA busy_timeout = 30000")
    conn.execute("PRAGMA journal_mode = WAL")
    conn.execute("PRAGMA synchronous = NORMAL")
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def _begin(conn: sqlite3.Connection) -> None:
    """Take the write lock now (works whether the connection autocommits or not)."""
    if conn.in_transaction:
        conn.commit()
    conn.row_factory = sqlite3.Row
    conn.execute("BEGIN IMMEDIATE")


def get_job(conn: sqlite3.Connection, job_id: int) -> Job | None:
    conn.row_factory = sqlite3.Row
    row = conn.execute("SELECT * FROM jobs WHERE id=?", (job_id,)).fetchone()
    return _row_to_job(row) if row else None


def enqueue(
    conn: sqlite3.Connection,
    family_id: str,
    kind: str,
    idempotency_key: str,
    payload: dict[str, Any] | None = None,
    *,
    run_after: datetime | None = None,
    max_attempts: int = DEFAULT_MAX_ATTEMPTS,
    now: datetime | None = None,
) -> tuple[Job, bool]:
    """Add a job, or return the one that already has this (family, kind, key).

    Returns ``(job, created)``. A second call with the same key never creates a second job and
    never changes the first one (not its payload, not its state).
    """
    now = now or utcnow()
    conn.row_factory = sqlite3.Row
    cur = conn.execute(
        "INSERT OR IGNORE INTO jobs (family_id, kind, payload_json, idempotency_key, "
        "max_attempts, run_after, created_at, updated_at) VALUES (?,?,?,?,?,?,?,?)",
        (
            family_id,
            kind,
            json.dumps(payload or {}, sort_keys=True),
            idempotency_key,
            max_attempts,
            iso(run_after or now),
            iso(now),
            iso(now),
        ),
    )
    created = cur.rowcount == 1
    conn.commit()
    row = conn.execute(
        "SELECT * FROM jobs WHERE family_id=? AND kind=? AND idempotency_key=?",
        (family_id, kind, idempotency_key),
    ).fetchone()
    return _row_to_job(row), created


def backoff_seconds(
    attempts: int,
    *,
    base: float = BACKOFF_BASE_SECONDS,
    cap: float = BACKOFF_CAP_SECONDS,
    rng: random.Random | None = None,
) -> float:
    """Exponential backoff after the ``attempts``-th failure, with 'equal jitter':
    half fixed, half random, so a burst of failures does not retry in lockstep."""
    ceiling = min(cap, base * (2 ** max(0, attempts - 1)))
    r = rng.random() if rng else random.random()
    return ceiling / 2 + (ceiling / 2) * r


def _mark_dead(conn: sqlite3.Connection, job_id: int, error: str, now: datetime) -> None:
    conn.execute(
        "UPDATE jobs SET state='dead', lease_owner=NULL, lease_expires_at=NULL, last_error=?, "
        "finished_at=?, updated_at=? WHERE id=?",
        (error[:LAST_ERROR_MAX], iso(now), iso(now), job_id),
    )


def claim(
    conn: sqlite3.Connection,
    worker_id: str,
    *,
    lease_seconds: float,
    kinds: list[str] | None = None,
    now: datetime | None = None,
    on_dead: DeadHook | None = None,
) -> Job | None:
    """Atomically take the oldest runnable job, or None. Reclaims expired leases first."""
    now = now or utcnow()
    dead_ids: list[int] = []
    _begin(conn)
    try:
        expired = conn.execute(
            "SELECT id, attempts, max_attempts FROM jobs "
            "WHERE state='running' AND lease_expires_at <= ?",
            (iso(now),),
        ).fetchall()
        for row in expired:
            if row["attempts"] >= row["max_attempts"]:
                _mark_dead(conn, row["id"], "LeaseExpired: worker died or hung", now)
                dead_ids.append(row["id"])
            else:
                conn.execute(
                    "UPDATE jobs SET state='queued', lease_owner=NULL, lease_expires_at=NULL, "
                    "last_error='LeaseExpired: worker died or hung', run_after=?, updated_at=? "
                    "WHERE id=?",
                    (iso(now), iso(now), row["id"]),
                )
        sql = "SELECT id FROM jobs WHERE state='queued' AND run_after <= ?"
        args: list[Any] = [iso(now)]
        if kinds:
            sql += f" AND kind IN ({','.join('?' * len(kinds))})"
            args += kinds
        sql += " ORDER BY run_after, id LIMIT 1"
        picked = conn.execute(sql, args).fetchone()
        if picked:
            conn.execute(
                "UPDATE jobs SET state='running', attempts=attempts+1, lease_owner=?, "
                "lease_expires_at=?, updated_at=? WHERE id=?",
                (worker_id, iso(now + timedelta(seconds=lease_seconds)), iso(now), picked["id"]),
            )
        conn.commit()
    except BaseException:
        if conn.in_transaction:
            conn.rollback()
        raise
    if on_dead:
        for job_id in dead_ids:
            job = get_job(conn, job_id)
            if job:
                on_dead(job)
    return get_job(conn, picked["id"]) if picked else None


def heartbeat(
    conn: sqlite3.Connection,
    job_id: int,
    worker_id: str,
    *,
    lease_seconds: float,
    now: datetime | None = None,
) -> bool:
    """Extend the lease. False means we no longer own the job (it was reclaimed)."""
    now = now or utcnow()
    cur = conn.execute(
        "UPDATE jobs SET lease_expires_at=?, updated_at=? "
        "WHERE id=? AND state='running' AND lease_owner=?",
        (iso(now + timedelta(seconds=lease_seconds)), iso(now), job_id, worker_id),
    )
    conn.commit()
    return cur.rowcount == 1


def complete(
    conn: sqlite3.Connection, job_id: int, worker_id: str, *, now: datetime | None = None
) -> bool:
    """Mark succeeded. False if the lease was lost (someone else owns the job now)."""
    now = now or utcnow()
    cur = conn.execute(
        "UPDATE jobs SET state='succeeded', lease_owner=NULL, lease_expires_at=NULL, "
        "finished_at=?, updated_at=? WHERE id=? AND state='running' AND lease_owner=?",
        (iso(now), iso(now), job_id, worker_id),
    )
    conn.commit()
    return cur.rowcount == 1


def fail(
    conn: sqlite3.Connection,
    job_id: int,
    worker_id: str,
    error: str,
    *,
    now: datetime | None = None,
    rng: random.Random | None = None,
    backoff_base: float = BACKOFF_BASE_SECONDS,
    backoff_cap: float = BACKOFF_CAP_SECONDS,
    on_dead: DeadHook | None = None,
) -> str | None:
    """Record a failed attempt. Returns the new state ('queued' or 'dead'), None if lease lost."""
    now = now or utcnow()
    _begin(conn)
    try:
        row = conn.execute(
            "SELECT attempts, max_attempts FROM jobs "
            "WHERE id=? AND state='running' AND lease_owner=?",
            (job_id, worker_id),
        ).fetchone()
        if row is None:
            conn.rollback()
            return None
        if row["attempts"] >= row["max_attempts"]:
            _mark_dead(conn, job_id, error, now)
            new_state = "dead"
        else:
            delay = backoff_seconds(row["attempts"], base=backoff_base, cap=backoff_cap, rng=rng)
            conn.execute(
                "UPDATE jobs SET state='queued', lease_owner=NULL, lease_expires_at=NULL, "
                "last_error=?, run_after=?, updated_at=? WHERE id=?",
                (error[:LAST_ERROR_MAX], iso(now + timedelta(seconds=delay)), iso(now), job_id),
            )
            new_state = "queued"
        conn.commit()
    except BaseException:
        if conn.in_transaction:
            conn.rollback()
        raise
    if new_state == "dead" and on_dead:
        job = get_job(conn, job_id)
        if job:
            on_dead(job)
    return new_state


def release(
    conn: sqlite3.Connection, job_id: int, worker_id: str, *, now: datetime | None = None
) -> bool:
    """Give an unfinished job back (graceful shutdown). The attempt is refunded."""
    now = now or utcnow()
    cur = conn.execute(
        "UPDATE jobs SET state='queued', lease_owner=NULL, lease_expires_at=NULL, "
        "attempts=MAX(attempts-1, 0), run_after=?, updated_at=? "
        "WHERE id=? AND state='running' AND lease_owner=?",
        (iso(now), iso(now), job_id, worker_id),
    )
    conn.commit()
    return cur.rowcount == 1


def retry_dead(conn: sqlite3.Connection, job_id: int, *, now: datetime | None = None) -> bool:
    """Operator action: put a dead job back in the queue with a fresh attempt budget."""
    now = now or utcnow()
    cur = conn.execute(
        "UPDATE jobs SET state='queued', attempts=0, run_after=?, alerted_at=NULL, "
        "finished_at=NULL, updated_at=? WHERE id=? AND state='dead'",
        (iso(now), iso(now), job_id),
    )
    conn.commit()
    return cur.rowcount == 1


def status(
    conn: sqlite3.Connection, *, now: datetime | None = None, family_id: str | None = None
) -> dict[str, Any]:
    """Counts for ``worker --status``: queue depth, running, dead, plus the oldest wait. With
    ``family_id``, only that family's jobs (the loop console shows a family its own queue)."""
    now = now or utcnow()
    conn.row_factory = sqlite3.Row
    mine, fam = ("AND family_id=?", (family_id,)) if family_id is not None else ("", ())
    counts = {s: 0 for s in STATES}
    for row in conn.execute(
        f"SELECT state, COUNT(*) AS n FROM jobs WHERE 1=1 {mine} GROUP BY state", fam  # noqa: S608
    ):
        counts[row["state"]] = row["n"]
    ready = conn.execute(
        "SELECT COUNT(*) AS n, MIN(run_after) AS oldest FROM jobs "
        f"WHERE state='queued' AND run_after <= ? {mine}",  # noqa: S608
        (iso(now), *fam),
    ).fetchone()
    stale = conn.execute(
        f"SELECT COUNT(*) AS n FROM jobs WHERE state='running' AND lease_expires_at <= ? {mine}",  # noqa: S608
        (iso(now), *fam),
    ).fetchone()
    dead = [
        dict(r)
        for r in conn.execute(
            "SELECT id, kind, family_id, attempts, last_error, finished_at FROM jobs "
            f"WHERE state='dead' {mine} ORDER BY id",  # noqa: S608
            fam,
        )
    ]
    return {
        "counts": counts,
        "queue_depth": counts["queued"],
        "ready_now": ready["n"],
        "oldest_ready_run_after": ready["oldest"],
        "running": counts["running"],
        "expired_leases": stale["n"],
        "dead": dead,
    }
