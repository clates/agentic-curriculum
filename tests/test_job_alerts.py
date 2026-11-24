"""Dead jobs (M8.6): an ERROR log line each, and one batched, redacted email digest."""

import logging
import random
import time
from datetime import UTC, datetime, timedelta

import pytest

import job_alerts
import job_registry
import jobs
import worker as worker_mod
from migrations import apply_migrations

FAM = "fam_local"
T0 = datetime(2026, 1, 1, 12, 0, tzinfo=UTC)


@pytest.fixture
def db(tmp_path):
    path = str(tmp_path / "q.db")
    apply_migrations(path)
    return path


@pytest.fixture
def conn(db):
    c = jobs.connect(db)
    yield c
    c.close()


@pytest.fixture
def registry():
    saved = dict(job_registry._HANDLERS)
    yield job_registry
    job_registry._HANDLERS.clear()
    job_registry._HANDLERS.update(saved)


@pytest.fixture
def mail(monkeypatch):
    sent = []
    monkeypatch.setenv("ALERT_EMAIL_TO", "me@example.com")
    monkeypatch.setenv("SMTP_HOST", "smtp.example.com")
    monkeypatch.setattr(
        job_alerts, "_send_email", lambda subject, body: sent.append((subject, body))
    )
    return sent


def kill(conn, key, kind="outline", child="Ava"):
    """Enqueue a job that fails its only attempt, and return it dead."""
    jobs.enqueue(conn, FAM, kind, key, {"child": child}, max_attempts=1, now=T0)
    j = jobs.claim(conn, "w", lease_seconds=60, now=T0)
    jobs.fail(conn, j.id, "w", f"RuntimeError: boom {child} Smith", now=T0)
    return jobs.get_job(conn, j.id)


def test_retry_backoff_then_dead_then_one_redacted_email(conn, mail):
    jobs.enqueue(conn, FAM, "outline", "k", {"child": "Ava"}, max_attempts=3, now=T0)
    now = T0
    states = []
    for _ in range(3):
        j = jobs.claim(conn, "w", lease_seconds=60, now=now)
        assert j is not None
        states.append(
            jobs.fail(
                conn,
                j.id,
                "w",
                "RuntimeError: boom Ava Smith",
                now=now,
                rng=random.Random(0),
                backoff_base=10,
            )
        )
        row = jobs.get_job(conn, j.id)
        if states[-1] == "queued":  # not runnable until the backoff has elapsed
            assert jobs.claim(conn, "w", lease_seconds=60, now=now) is None
            now = jobs.parse_iso(row.run_after)
    assert states == ["queued", "queued", "dead"]
    assert job_alerts.send_digest(conn) == 1
    ((subject, body),) = mail
    assert "1 job gave up" in subject
    assert "Ava" not in subject + body and FAM not in body and "boom" not in body
    assert job_alerts.family_hash(FAM) in body and "RuntimeError" in body


def test_a_bad_night_is_one_email_not_one_per_job(conn, mail):
    for i in range(4):
        kill(conn, f"k{i}", child=f"Kid{i}")
    assert job_alerts.send_digest(conn) == 4
    assert len(mail) == 1 and "4 jobs gave up" in mail[0][0]
    assert all(f"Kid{i}" not in mail[0][1] for i in range(4))
    assert mail[0][1].count("job=") == 4


def test_each_dead_job_is_reported_once_and_email_is_off_by_default(conn, mail, monkeypatch):
    kill(conn, "k")
    assert job_alerts.send_digest(conn) == 1
    assert job_alerts.send_digest(conn) == 0
    assert len(mail) == 1
    kill(conn, "k2")
    monkeypatch.delenv("ALERT_EMAIL_TO")
    assert job_alerts.send_digest(conn) == 0 and len(mail) == 1  # off: nothing sent, not marked
    monkeypatch.setenv("ALERT_EMAIL_TO", "me@example.com")
    assert job_alerts.send_digest(conn) == 1  # turned on later: still reported


def test_a_failed_send_is_retried_next_digest(conn, monkeypatch):
    monkeypatch.setenv("ALERT_EMAIL_TO", "me@example.com")
    monkeypatch.setenv("SMTP_HOST", "smtp.example.com")
    calls = []

    def flaky(subject, body):
        calls.append(subject)
        if len(calls) == 1:
            raise OSError("smtp down")

    monkeypatch.setattr(job_alerts, "_send_email", flaky)
    kill(conn, "k")
    assert job_alerts.send_digest(conn) == 0  # failed: the job is handed back, nothing lost
    assert job_alerts.send_digest(conn) == 1
    assert len(calls) == 2 and job_alerts.send_digest(conn) == 0


def test_retried_job_that_dies_again_is_reported_again(conn, mail):
    dead = kill(conn, "k")
    assert job_alerts.send_digest(conn) == 1
    assert jobs.retry_dead(conn, dead.id, now=T0)
    j = jobs.claim(conn, "w", lease_seconds=60, now=T0)
    jobs.fail(conn, j.id, "w", "RuntimeError: again", now=T0)
    assert job_alerts.send_digest(conn) == 1 and len(mail) == 2


def test_lease_expiry_out_of_attempts_goes_dead_and_is_reported(conn, mail):
    jobs.enqueue(conn, FAM, "outline", "k", max_attempts=1, now=T0)
    jobs.claim(conn, "w", lease_seconds=10, now=T0)
    assert jobs.claim(conn, "w2", lease_seconds=10, now=T0 + timedelta(seconds=11)) is None
    assert jobs.status(conn, now=T0)["counts"]["dead"] == 1
    assert job_alerts.send_digest(conn) == 1


def test_worker_logs_each_death_and_emails_one_digest(db, conn, registry, mail, caplog):
    @job_registry.handler("outline")
    def always_fails(ctx):
        raise ValueError("kaboom with child name Ava")

    jobs.enqueue(conn, FAM, "outline", "k", max_attempts=3)
    w = worker_mod.Worker(db, poll_seconds=0.01, backoff_base=0.001)
    with caplog.at_level(logging.ERROR, logger="worker"):
        for _ in range(200):
            w.run_once()
            if jobs.status(conn)["counts"]["dead"]:
                break
            time.sleep(0.01)
        for _ in range(5):
            w.run_once()
    row = conn.execute("SELECT state, attempts FROM jobs").fetchone()
    assert (row[0], row[1]) == ("dead", 3)
    assert sum("is DEAD" in r.getMessage() for r in caplog.records) == 1
    assert not mail  # the email waits for the digest, it does not fire per job
    w._digest()
    assert len(mail) == 1 and "Ava" not in mail[0][1]
    w._last_digest = float("-inf")
    w._digest()
    assert len(mail) == 1  # already reported


def test_digest_is_rate_limited_in_the_worker(db, conn, registry, mail):
    w = worker_mod.Worker(db, poll_seconds=0.01)
    kill(conn, "k1")
    w._digest()
    kill(conn, "k2")
    w._digest()  # inside the 15 minute window: held back
    assert len(mail) == 1
