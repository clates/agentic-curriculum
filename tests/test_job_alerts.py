"""Maintainer alerts for dead jobs (M8.6): one alert per dead job, redacted, env-guarded."""

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
def alerts(monkeypatch):
    sent = []
    monkeypatch.setenv("JOB_ALERTS_ENABLED", "1")
    monkeypatch.setattr(job_alerts, "_send", lambda title, msg: sent.append((title, msg)))
    return sent


def test_retry_backoff_then_dead_with_one_alert(conn, alerts):
    jobs.enqueue(conn, FAM, "outline", "k", {"child": "Ava"}, max_attempts=3, now=T0)
    now = T0
    states = []
    for _ in range(3):
        j = jobs.claim(conn, "w", lease_seconds=60, now=now)
        assert j is not None
        st = jobs.fail(
            conn,
            j.id,
            "w",
            "RuntimeError: boom Ava Smith",
            now=now,
            rng=random.Random(0),
            backoff_base=10,
            on_dead=lambda job: job_alerts.alert_dead_job(conn, job),
        )
        states.append(st)
        row = jobs.get_job(conn, j.id)
        if st == "queued":  # not runnable until the backoff has elapsed
            assert jobs.claim(conn, "w", lease_seconds=60, now=now) is None
            assert jobs.parse_iso(row.run_after) > now
            now = jobs.parse_iso(row.run_after)
    assert states == ["queued", "queued", "dead"]
    assert jobs.get_job(conn, j.id).state == "dead"
    assert jobs.claim(conn, "w", lease_seconds=60, now=now + timedelta(days=9)) is None
    assert len(alerts) == 1
    title, msg = alerts[0]
    assert "Ava" not in title + msg and FAM not in msg and "boom" not in msg
    assert job_alerts.family_hash(FAM) in msg and "RuntimeError" in msg


def test_alert_not_repeated_and_off_by_default(conn, alerts, monkeypatch):
    jobs.enqueue(conn, FAM, "outline", "k", max_attempts=1, now=T0)
    j = jobs.claim(conn, "w", lease_seconds=60, now=T0)
    jobs.fail(conn, j.id, "w", "X: y", now=T0)
    dead = jobs.get_job(conn, j.id)
    assert job_alerts.alert_dead_job(conn, dead) is True
    assert job_alerts.alert_dead_job(conn, dead) is False
    assert len(alerts) == 1
    monkeypatch.delenv("JOB_ALERTS_ENABLED")
    assert job_alerts.alert_dead_job(conn, dead) is False


def test_lease_expiry_out_of_attempts_goes_dead_and_alerts_once(conn, alerts):
    jobs.enqueue(conn, FAM, "outline", "k", max_attempts=1, now=T0)
    jobs.claim(conn, "w", lease_seconds=10, now=T0)
    hook = lambda job: job_alerts.alert_dead_job(conn, job)  # noqa: E731
    assert (
        jobs.claim(conn, "w2", lease_seconds=10, now=T0 + timedelta(seconds=11), on_dead=hook)
        is None
    )
    jobs.claim(conn, "w2", lease_seconds=10, now=T0 + timedelta(seconds=12), on_dead=hook)
    assert jobs.status(conn, now=T0)["counts"]["dead"] == 1 and len(alerts) == 1


def test_worker_dead_path_fires_alert_exactly_once(db, conn, registry, alerts):
    @job_registry.handler("outline")
    def always_fails(ctx):
        raise ValueError("kaboom with child name Ava")

    jobs.enqueue(conn, FAM, "outline", "k", max_attempts=3)
    w = worker_mod.Worker(db, poll_seconds=0.01, backoff_base=0.001)
    for _ in range(200):
        w.run_once()
        if jobs.status(conn)["counts"]["dead"]:
            break
        time.sleep(0.01)
    for _ in range(5):
        w.run_once()
    row = conn.execute("SELECT state, attempts FROM jobs").fetchone()
    assert (row[0], row[1]) == ("dead", 3)
    assert len(alerts) == 1 and "Ava" not in alerts[0][1]
