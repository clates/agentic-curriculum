"""Maintainer alerts for dead jobs (M8.6). ntfy is the maintainer channel only.

One alert per dead job: ``jobs.alerted_at`` is claimed with a compare-and-set before sending, so
two workers (or a reclaim plus a failure) cannot alert twice. The message carries the job kind,
a short hash of the family id, the job id and the exception class name. Never child data, never
the error text (handler errors can quote prompts).

Guarded by env: nothing is sent unless ``JOB_ALERTS_ENABLED`` is truthy. Tests swap ``_send``.
"""

from __future__ import annotations

import logging
import os
import re
import sqlite3

try:
    from .jobs import Job, family_hash, iso, utcnow  # type: ignore
    from . import ntfy  # type: ignore
except ImportError:
    from jobs import Job, family_hash, iso, utcnow  # type: ignore
    import ntfy  # type: ignore

logger = logging.getLogger(__name__)
_CLASS_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_.]{0,80}")


def enabled() -> bool:
    return os.environ.get("JOB_ALERTS_ENABLED", "").strip().lower() in ("1", "true", "yes", "on")


def error_class(last_error: str | None) -> str:
    """The exception class name only (text before the first colon), or 'unknown'."""
    if not last_error:
        return "unknown"
    m = _CLASS_RE.match(last_error.split(":", 1)[0].strip())
    return m.group(0) if m else "unknown"


def build_message(job: Job) -> tuple[str, str]:
    title = f"Job dead: {job.kind}"
    body = (
        f"job={job.id} kind={job.kind} family={family_hash(job.family_id)} "
        f"attempts={job.attempts}/{job.max_attempts} error={error_class(job.last_error)}. "
        "Inspect: python -m worker --status"
    )
    return title, body


def _send(title: str, message: str) -> None:  # the transport; faked in tests
    ntfy.notify(title, message, priority="high")


def alert_dead_job(conn: sqlite3.Connection, job: Job) -> bool:
    """Send the alert for a dead job once. Returns True if this call sent it."""
    if not enabled():
        return False
    cur = conn.execute(
        "UPDATE jobs SET alerted_at=? WHERE id=? AND state='dead' AND alerted_at IS NULL",
        (iso(utcnow()), job.id),
    )
    conn.commit()
    if cur.rowcount != 1:
        return False
    try:
        _send(*build_message(job))
    except Exception as exc:  # an alert must never break the worker
        logger.warning("dead-job alert failed for job %s: %s", job.id, exc)
    return True
