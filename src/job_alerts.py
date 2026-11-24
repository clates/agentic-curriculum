"""Maintainer alerts for dead jobs (M8.6): the log, plus one email digest. No push, no per-job mail.

A job that ran out of retries is ``dead``. The worker logs an ERROR line for each one the moment it
dies (always on). ``send_digest`` then emails the maintainer ONE message listing every dead job
not yet reported, so a bad night is one email, not one per family. The email is off until
``ALERT_EMAIL_TO`` and ``SMTP_HOST`` are both set.

Each dead job is reported once: ``jobs.alerted_at`` is claimed with a compare-and-set before the
send, and handed back if the send fails so the next digest retries it. A line carries the job id,
kind, a short hash of the family id, attempts and the exception class name. Never child data and
never the error text (handler errors can quote prompts).

Env: ALERT_EMAIL_TO (comma-separated), SMTP_HOST, SMTP_PORT (587; 465 uses implicit TLS),
SMTP_USER, SMTP_PASSWORD, SMTP_FROM (default SMTP_USER). The password is never logged.
"""

from __future__ import annotations

import logging
import os
import re
import smtplib
import sqlite3
import ssl
from email.message import EmailMessage

try:
    from .jobs import Job, family_hash, iso, utcnow  # type: ignore
except ImportError:
    from jobs import Job, family_hash, iso, utcnow  # type: ignore

logger = logging.getLogger(__name__)
_CLASS_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_.]{0,80}")
MAX_PER_DIGEST = 50


def recipients() -> list[str]:
    return [a.strip() for a in os.environ.get("ALERT_EMAIL_TO", "").split(",") if a.strip()]


def enabled() -> bool:
    return bool(recipients() and os.environ.get("SMTP_HOST", "").strip())


def error_class(last_error: str | None) -> str:
    """The exception class name only (text before the first colon), or 'unknown'."""
    if not last_error:
        return "unknown"
    m = _CLASS_RE.match(last_error.split(":", 1)[0].strip())
    return m.group(0) if m else "unknown"


def build_line(job: Job) -> str:
    return (
        f"job={job.id} kind={job.kind} family={family_hash(job.family_id)} "
        f"attempts={job.attempts}/{job.max_attempts} error={error_class(job.last_error)}"
    )


def build_message(dead: list[Job]) -> tuple[str, str]:
    n = len(dead)
    subject = f"[curriculum] {n} job{'s' if n != 1 else ''} gave up"
    body = (
        "These jobs failed every retry and were set aside (nothing is deleted):\n\n"
        + "\n".join(build_line(j) for j in dead)
        + "\n\nInspect: python -m worker --status\nRetry one: python -m worker --retry <job id>\n"
    )
    return subject, body


def _send_email(subject: str, body: str) -> None:  # the transport; faked in tests
    host = os.environ["SMTP_HOST"].strip()
    port = int(os.environ.get("SMTP_PORT", "587") or 587)
    user = os.environ.get("SMTP_USER", "").strip()
    password = os.environ.get("SMTP_PASSWORD", "")
    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = os.environ.get("SMTP_FROM", "").strip() or user or recipients()[0]
    msg["To"] = ", ".join(recipients())
    msg.set_content(body)
    context = ssl.create_default_context()
    if port == 465:
        server: smtplib.SMTP = smtplib.SMTP_SSL(host, port, timeout=15, context=context)
    else:
        server = smtplib.SMTP(host, port, timeout=15)
    with server:
        if port != 465:
            server.starttls(context=context)
        if user:
            server.login(user, password)
        server.send_message(msg)


def send_digest(conn: sqlite3.Connection) -> int:
    """Email every dead job not yet reported, as one message. Returns how many were reported."""
    if not enabled():
        return 0
    ids = [
        r[0]
        for r in conn.execute(
            "SELECT id FROM jobs WHERE state='dead' AND alerted_at IS NULL ORDER BY id LIMIT ?",
            (MAX_PER_DIGEST,),
        )
    ]
    claimed: list[int] = []
    for job_id in ids:  # compare-and-set each, so two workers never report the same job
        cur = conn.execute(
            "UPDATE jobs SET alerted_at=? WHERE id=? AND state='dead' AND alerted_at IS NULL",
            (iso(utcnow()), job_id),
        )
        if cur.rowcount == 1:
            claimed.append(job_id)
    conn.commit()
    if not claimed:
        return 0
    try:
        from .jobs import get_job  # type: ignore
    except ImportError:
        from jobs import get_job  # type: ignore
    dead = [j for j in (get_job(conn, i) for i in claimed) if j is not None]
    try:
        _send_email(*build_message(dead))
    except Exception as exc:  # an alert must never break the worker; the next digest retries
        logger.warning("dead-job email failed (%s); will retry: %s", type(exc).__name__, exc)
        conn.executemany("UPDATE jobs SET alerted_at=NULL WHERE id=?", [(i,) for i in claimed])
        conn.commit()
        return 0
    return len(claimed)
