"""Job queue + worker tests (M8.2, M8.6): idempotency, retry/backoff/dead, alerts, concurrency,
crash recovery with a real killed subprocess, graceful shutdown."""

import os
import random
import subprocess
import sys
import threading
import time
from datetime import UTC, datetime, timedelta
from pathlib import Path

import pytest

import job_registry
import jobs
import worker as worker_mod
from migrations import apply_migrations

ROOT = Path(__file__).resolve().parents[1]
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


def test_migration_adds_jobs_and_family_timezone(conn):
    assert conn.execute("SELECT COUNT(*) FROM jobs").fetchone()[0] == 0
    cols = [r[1] for r in conn.execute("PRAGMA table_info(family_settings)")]
    assert "timezone" in cols


def test_enqueue_is_idempotent_by_key(conn):
    a, created_a = jobs.enqueue(conn, FAM, "outline", "outlines:p1", {"x": 1}, now=T0)
    b, created_b = jobs.enqueue(conn, FAM, "outline", "outlines:p1", {"x": 2}, now=T0)
    assert created_a and not created_b
    assert a.id == b.id and b.payload == {"x": 1}
    assert conn.execute("SELECT COUNT(*) FROM jobs").fetchone()[0] == 1
    # same key under another kind is a different job
    _, created_c = jobs.enqueue(conn, FAM, "author", "outlines:p1", now=T0)
    assert created_c


def test_claim_is_exclusive_and_ordered(conn):
    for i in range(3):
        jobs.enqueue(conn, FAM, "outline", f"k{i}", now=T0)
    first = jobs.claim(conn, "w1", lease_seconds=60, now=T0)
    second = jobs.claim(conn, "w2", lease_seconds=60, now=T0)
    assert first.idempotency_key == "k0" and second.idempotency_key == "k1"
    assert first.state == "running" and first.attempts == 1 and first.lease_owner == "w1"


def test_run_after_is_respected(conn):
    jobs.enqueue(conn, FAM, "outline", "later", run_after=T0 + timedelta(minutes=5), now=T0)
    assert jobs.claim(conn, "w", lease_seconds=60, now=T0) is None
    assert jobs.claim(conn, "w", lease_seconds=60, now=T0 + timedelta(minutes=5)) is not None


def test_expired_lease_is_reclaimed(conn):
    jobs.enqueue(conn, FAM, "outline", "k", now=T0)
    jobs.claim(conn, "dead-worker", lease_seconds=60, now=T0)
    assert jobs.claim(conn, "w2", lease_seconds=60, now=T0 + timedelta(seconds=30)) is None
    again = jobs.claim(conn, "w2", lease_seconds=60, now=T0 + timedelta(seconds=61))
    assert again.lease_owner == "w2" and again.attempts == 2


def test_old_owner_cannot_finish_a_reclaimed_job(conn):
    jobs.enqueue(conn, FAM, "outline", "k", now=T0)
    j = jobs.claim(conn, "old", lease_seconds=10, now=T0)
    jobs.claim(conn, "new", lease_seconds=10, now=T0 + timedelta(seconds=11))
    assert jobs.heartbeat(conn, j.id, "old", lease_seconds=10, now=T0) is False
    assert jobs.complete(conn, j.id, "old") is False
    assert jobs.complete(conn, j.id, "new") is True


def test_backoff_grows_and_is_jittered():
    rng = random.Random(1)
    d = [jobs.backoff_seconds(n, base=10, cap=1000, rng=rng) for n in (1, 2, 3, 4)]
    assert 5 <= d[0] <= 10 and 10 <= d[1] <= 20 and 20 <= d[2] <= 40 and 40 <= d[3] <= 80
    assert jobs.backoff_seconds(30, base=10, cap=1000, rng=rng) <= 1000
    assert len({jobs.backoff_seconds(3, base=10, cap=1000, rng=rng) for _ in range(20)}) > 1


def test_retry_dead_requeues_with_fresh_budget(conn):
    jobs.enqueue(conn, FAM, "outline", "k", max_attempts=1, now=T0)
    j = jobs.claim(conn, "w", lease_seconds=10, now=T0)
    jobs.fail(conn, j.id, "w", "X: y", now=T0)
    assert jobs.retry_dead(conn, j.id, now=T0) and not jobs.retry_dead(conn, j.id, now=T0)
    again = jobs.claim(conn, "w", lease_seconds=10, now=T0)
    assert again.attempts == 1


def test_status_counts(conn):
    for i in range(3):
        jobs.enqueue(conn, FAM, "outline", f"k{i}", now=T0)
    jobs.claim(conn, "w", lease_seconds=10, now=T0)
    st = jobs.status(conn, now=T0)
    assert st["queue_depth"] == 2 and st["running"] == 1 and st["dead"] == []


def test_stub_handlers_exist_and_real_ones_replace_them(registry):
    for kind in ("outline", "author", "send_notice"):
        assert job_registry.is_stub(kind)

    @job_registry.handler("outline")
    def real(ctx):
        pass

    assert job_registry.get_handler("outline") is real and not job_registry.is_stub("outline")
    with pytest.raises(job_registry.DuplicateHandler):

        @job_registry.handler("outline")
        def another(ctx):
            pass

    @job_registry.handler("outline", stub=True)
    def late_stub(ctx):
        pass

    assert job_registry.get_handler("outline") is real


def test_worker_runs_stub_and_unknown_kind_fails(db, conn):
    jobs.enqueue(conn, FAM, "send_notice", "n1")
    jobs.enqueue(conn, FAM, "mystery", "m1", max_attempts=1)
    w = worker_mod.Worker(db, poll_seconds=0.01)
    assert w.run(drain=True) == 2
    c = jobs.connect(db)
    st = {r["kind"]: r["state"] for r in c.execute("SELECT kind, state FROM jobs")}
    assert st == {"send_notice": "succeeded", "mystery": "dead"}


def test_worker_handler_failure_then_success(db, conn, registry):
    calls = []

    @job_registry.handler("outline")
    def flaky(ctx):
        calls.append(ctx.job.attempts)
        if len(calls) == 1:
            raise RuntimeError("first try fails")

    jobs.enqueue(conn, FAM, "outline", "k")
    w = worker_mod.Worker(db, poll_seconds=0.01, backoff_base=0.01)
    deadline = time.time() + 5
    while time.time() < deadline and jobs.status(conn)["counts"]["succeeded"] == 0:
        w.run_once()
        time.sleep(0.02)
    assert calls == [1, 2]
    assert conn.execute("SELECT state, last_error FROM jobs").fetchone()[0] == "succeeded"


def test_graceful_stop_releases_a_job_that_outlives_the_grace(db, conn, registry):
    release = threading.Event()

    @job_registry.handler("outline")
    def slow(ctx):
        release.wait(10)

    jobs.enqueue(conn, FAM, "outline", "k")
    stop = threading.Event()
    w = worker_mod.Worker(db, stop=stop, lease_seconds=0.3, shutdown_grace=0.2, poll_seconds=0.01)
    t = threading.Thread(target=w.run_once)
    t.start()
    time.sleep(0.2)
    stop.set()
    t.join(5)
    release.set()
    row = conn.execute("SELECT state, attempts FROM jobs").fetchone()
    assert (row[0], row[1]) == ("queued", 0)  # released, attempt refunded


def test_graceful_stop_lets_a_short_job_finish(db, conn, registry):
    @job_registry.handler("outline")
    def short(ctx):
        time.sleep(0.3)

    jobs.enqueue(conn, FAM, "outline", "k")
    stop = threading.Event()
    w = worker_mod.Worker(db, stop=stop, lease_seconds=3, shutdown_grace=5, poll_seconds=0.01)
    t = threading.Thread(target=w.run_once)
    t.start()
    time.sleep(0.1)
    stop.set()
    t.join(5)
    assert conn.execute("SELECT state FROM jobs").fetchone()[0] == "succeeded"


def test_four_threads_drain_200_jobs_exactly_once(db, conn, registry):
    ran, lock = [], threading.Lock()

    @job_registry.handler("outline")
    def record(ctx):
        with lock:
            ran.append(ctx.job.id)

    for i in range(200):
        jobs.enqueue(conn, FAM, "outline", f"k{i}")
    workers = [worker_mod.Worker(db, poll_seconds=0.01) for _ in range(4)]
    threads = [threading.Thread(target=w.run, kwargs={"drain": True}) for w in workers]
    [t.start() for t in threads]
    [t.join(120) for t in threads]
    assert len(ran) == 200 and len(set(ran)) == 200
    st = jobs.status(conn)["counts"]
    assert st["succeeded"] == 200 and st["queued"] == 0 and st["dead"] == 0


def _env(db, **extra):
    env = dict(
        os.environ,
        PYTHONPATH=f"{ROOT / 'src'}{os.pathsep}{ROOT / 'tests'}",
        CURRICULUM_DB_PATH=db,
        WORKER_HANDLER_MODULES="_loop_test_handlers",
        ALERT_EMAIL_TO="",
    )
    env.update(extra)
    return env


def test_four_processes_drain_jobs_exactly_once(db, conn):
    for i in range(60):
        jobs.enqueue(conn, FAM, "outline", f"k{i}")
    procs = [
        subprocess.Popen(
            [sys.executable, "-m", "worker", "--once"],
            cwd=ROOT / "src",
            env=_env(db),
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        for _ in range(4)
    ]
    for p in procs:
        assert p.wait(120) == 0
    rows = conn.execute("SELECT job_id, COUNT(*) FROM ran_log GROUP BY job_id").fetchall()
    assert len(rows) == 60 and all(r[1] == 1 for r in rows)
    assert jobs.status(conn)["counts"]["succeeded"] == 60


def test_kill9_mid_job_is_reclaimed_and_finished_by_another_worker(db, conn, tmp_path):
    jobs.enqueue(conn, FAM, "author", "author:p1:a")
    env = _env(
        db,
        CRASH_MARKER=str(tmp_path / "marker"),
        WORKER_LEASE_SECONDS="2",
        WORKER_POLL_SECONDS="0.2",
    )
    victim = subprocess.Popen(
        [sys.executable, "-m", "worker"],
        cwd=ROOT / "src",
        env=env,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    try:
        deadline = time.time() + 30
        while time.time() < deadline and not (tmp_path / "marker").exists():
            time.sleep(0.1)
        assert (tmp_path / "marker").exists(), "victim never started the job"
        assert conn.execute("SELECT state FROM jobs").fetchone()[0] == "running"
        victim.kill()  # SIGKILL: no cleanup, no release
        victim.wait(10)
    finally:
        victim.kill()
    assert conn.execute("SELECT state FROM jobs").fetchone()[0] == "running"  # orphaned
    rescuer = subprocess.Popen(
        [sys.executable, "-m", "worker"],
        cwd=ROOT / "src",
        env=env,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    try:
        deadline = time.time() + 30
        while time.time() < deadline:
            if conn.execute("SELECT state FROM jobs").fetchone()[0] == "succeeded":
                break
            time.sleep(0.2)
    finally:
        rescuer.terminate()
        rescuer.wait(15)
    row = conn.execute("SELECT state, attempts FROM jobs").fetchone()
    assert (row[0], row[1]) == ("succeeded", 2)
    notes = [r[0] for r in conn.execute("SELECT note FROM ran_log ORDER BY rowid")]
    assert notes == ["started", "finished"]


def test_sigterm_exits_cleanly_when_idle(db):
    p = subprocess.Popen(
        [sys.executable, "-m", "worker"],
        cwd=ROOT / "src",
        env=_env(db),
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    time.sleep(1.5)
    p.terminate()
    assert p.wait(15) == 0


def test_status_cli(db, conn):
    jobs.enqueue(conn, FAM, "outline", "k1")
    out = subprocess.run(
        [sys.executable, "-m", "worker", "--status", "--db", db],
        cwd=ROOT / "src",
        env=_env(db),
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert out.returncode == 0 and "queue depth: 1" in out.stdout and "dead:" in out.stdout


# --- permanent failures go dead at once; transient ones keep retrying -------------------------


def _llm_errors():
    import llm.errors as e

    return e


@pytest.mark.parametrize(
    "name,permanent",
    [
        ("LLMAuthError", True),
        ("LLMBadRequest", True),
        ("LLMConfigError", True),
        ("CostCapExceeded", True),
        ("LLMRateLimit", False),
        ("LLMTimeout", False),
        ("LLMServerError", False),
        ("LLMConnectionError", False),
        ("LLMEmptyResponse", False),
        ("StructuredOutputError", False),
    ],
)
def test_the_model_errors_that_retrying_cannot_fix_are_permanent(name, permanent):
    e = _llm_errors()
    cls = getattr(e, name)
    kw = {"family_id": "f", "spent": 1.0, "cap": 1.0} if name == "CostCapExceeded" else {}
    assert jobs.is_permanent(cls("boom", **kw)) is permanent
    assert jobs.is_permanent(RuntimeError("boom")) is False
    assert jobs.is_permanent(jobs.PermanentJobError("boom")) is True


def test_fail_permanent_goes_dead_on_the_first_attempt(conn):
    jobs.enqueue(conn, FAM, "outline", "k", now=T0)  # 5 attempts allowed
    j = jobs.claim(conn, "w", lease_seconds=10, now=T0)
    dead = []
    state = jobs.fail(
        conn, j.id, "w", "LLMAuthError: HTTP 401", now=T0, permanent=True, on_dead=dead.append
    )
    after = jobs.get_job(conn, j.id)
    assert state == "dead" and after.state == "dead" and after.attempts == 1
    assert after.last_error == "LLMAuthError: HTTP 401" and after.finished_at
    assert [d.id for d in dead] == [j.id]


def test_fail_not_permanent_still_backs_off(conn):
    jobs.enqueue(conn, FAM, "outline", "k", now=T0)
    j = jobs.claim(conn, "w", lease_seconds=10, now=T0)
    assert jobs.fail(conn, j.id, "w", "LLMRateLimit: 429", now=T0, rng=random.Random(1)) == "queued"
    after = jobs.get_job(conn, j.id)
    assert after.state == "queued" and jobs.parse_iso(after.run_after) > T0


def _run_failing_job(db, conn, registry, exc):
    @job_registry.handler("outline")
    def boom(ctx):
        raise exc

    jobs.enqueue(conn, FAM, "outline", "k")
    w = worker_mod.Worker(db, poll_seconds=0.01, backoff_base=60)
    w.run_once()
    row = conn.execute("SELECT state, attempts, last_error, run_after FROM jobs").fetchone()
    w.conn.close()
    return row


def test_a_rejected_key_is_dead_after_one_attempt_with_the_class_recorded(db, conn, registry):
    e = _llm_errors()
    row = _run_failing_job(db, conn, registry, e.LLMAuthError("HTTP 401: User not found"))
    assert (row["state"], row["attempts"]) == ("dead", 1)
    assert row["last_error"].startswith("LLMAuthError: ")


def test_a_bad_request_is_dead_after_one_attempt(db, conn, registry):
    row = _run_failing_job(db, conn, registry, _llm_errors().LLMBadRequest("HTTP 400"))
    assert (row["state"], row["attempts"]) == ("dead", 1)


def test_an_explicit_permanent_error_is_dead_after_one_attempt(db, conn, registry):
    row = _run_failing_job(db, conn, registry, jobs.PermanentJobError("nope"))
    assert (row["state"], row["attempts"]) == ("dead", 1)
    assert row["last_error"] == "PermanentJobError: nope"


@pytest.mark.parametrize(
    "name", ["LLMRateLimit", "LLMTimeout", "LLMServerError", "LLMConnectionError"]
)
def test_transient_model_errors_still_retry_with_backoff(db, conn, registry, name):
    e = _llm_errors()
    before = datetime.now(UTC)
    row = _run_failing_job(db, conn, registry, getattr(e, name)("HTTP 429 slow down"))
    assert (row["state"], row["attempts"]) == ("queued", 1)
    assert row["last_error"].startswith(f"{name}: ")
    assert jobs.parse_iso(row["run_after"]) > before + timedelta(seconds=25)  # backed off
