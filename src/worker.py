"""Background worker for the job queue: ``python -m worker`` (run from src/, or PYTHONPATH=src).

    python -m worker                 run a worker loop
    python -m worker --scheduler     also run the weekly-loop scheduler tick in this process
    python -m worker --once          drain what is runnable now, then exit (demos, cron-style)
    python -m worker --status        print queue depth, running and dead jobs, then exit
    python -m worker --retry JOB_ID  put a dead job back in the queue

Env: CURRICULUM_DB_PATH, WORKER_LEASE_SECONDS (300), WORKER_POLL_SECONDS (2),
WORKER_SHUTDOWN_GRACE_SECONDS (30), WORKER_HANDLER_MODULES (comma-separated modules that register
real handlers), LOOP_JOBS_ENABLED (the switch for the weekly loop: scheduler and web hooks),
ALERT_EMAIL_TO / SMTP_* (see job_alerts), SCHEDULER_* (see scheduler).

Safe to run several at once against one SQLite file. SIGTERM/SIGINT: stop claiming, give the
running job up to the grace period to finish, then release it back to the queue (a hard kill is
covered by lease expiry).
"""

from __future__ import annotations

import argparse
import importlib
import json
import logging
import os
import signal
import sys
import threading
import time
import uuid

try:
    from . import job_registry, jobs  # type: ignore
    from . import job_handlers_stub  # noqa: F401  # type: ignore
except ImportError:
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    import job_registry  # type: ignore
    import jobs  # type: ignore
    import job_handlers_stub  # noqa: F401  # type: ignore

DIGEST_SECONDS = 900  # at most one dead-job email per 15 minutes
logger = logging.getLogger("worker")


def _env_float(name: str, default: float, value: float | None = None) -> float:
    """``value`` when given, else the env var ``name`` (``default`` if unset or not a number)."""
    if value is not None:
        return value
    try:
        return float(os.environ.get(name, default))
    except ValueError:
        return default


def load_handler_modules(spec: str | None = None) -> list[str]:
    """Import the modules named in WORKER_HANDLER_MODULES so their @handler() calls run."""
    names = [
        m.strip()
        for m in (spec if spec is not None else os.environ.get("WORKER_HANDLER_MODULES", "")).split(
            ","
        )
        if m.strip()
    ]
    for name in names:
        importlib.import_module(name)
    return names


class Worker:
    def __init__(
        self,
        db_path: str,
        *,
        worker_id: str | None = None,
        lease_seconds: float | None = None,
        poll_seconds: float | None = None,
        shutdown_grace: float | None = None,
        backoff_base: float = jobs.BACKOFF_BASE_SECONDS,
        stop: threading.Event | None = None,
        kinds: list[str] | None = None,
    ):
        self.db_path = db_path
        self.worker_id = worker_id or f"w-{os.getpid()}-{uuid.uuid4().hex[:6]}"
        self.lease = lease_seconds or _env_float("WORKER_LEASE_SECONDS", 300)
        self.poll = _env_float("WORKER_POLL_SECONDS", 2, poll_seconds)
        self.grace = _env_float("WORKER_SHUTDOWN_GRACE_SECONDS", 30, shutdown_grace)
        self.backoff_base = backoff_base
        self.stop = stop or threading.Event()
        self.kinds = kinds
        self.conn = jobs.connect(db_path)
        self._last_digest = float("-inf")

    def _on_dead(self, job: jobs.Job) -> None:
        # The log line is the always-on alert. The email (job_alerts.send_digest) is batched.
        logger.error("job %s (%s) is DEAD after %s attempts", job.id, job.kind, job.attempts)

    def _digest(self) -> None:
        """Email newly dead jobs as one message, at most once per DIGEST_SECONDS."""
        now = time.monotonic()
        if now - self._last_digest < DIGEST_SECONDS:
            return
        self._last_digest = now
        try:
            try:
                from . import job_alerts  # type: ignore
            except ImportError:
                import job_alerts  # type: ignore
            job_alerts.send_digest(self.conn)
        except Exception:  # never let reporting stop the worker
            logger.exception("dead-job digest failed")

    def run_once(self) -> bool:
        """Claim and process one job. Returns False when nothing was runnable."""
        job = jobs.claim(
            self.conn,
            self.worker_id,
            lease_seconds=self.lease,
            kinds=self.kinds,
            on_dead=self._on_dead,
        )
        if job is None:
            return False
        self._process(job)
        return True

    def _process(self, job: jobs.Job) -> None:
        fn = job_registry.get_handler(job.kind)
        if fn is None:
            self._fail(job, f"NoHandler: no handler for {job.kind!r}")
            return
        lease_lost = threading.Event()
        ctx = job_registry.JobContext(
            job=job,
            db_path=self.db_path,
            heartbeat=lambda: self._heartbeat(job.id, lease_lost),
        )
        outcome: dict[str, BaseException | None] = {"error": None}
        done = threading.Event()

        def run() -> None:
            try:
                fn(ctx)
            except BaseException as exc:  # noqa: BLE001 - recorded, then retried
                outcome["error"] = exc
            finally:
                done.set()

        threading.Thread(target=run, name=f"job-{job.id}", daemon=True).start()
        waited_after_stop = 0.0
        tick = max(0.05, min(self.lease / 3, 5.0))
        while not done.wait(tick):
            if not self._heartbeat(job.id, lease_lost):
                break
            if self.stop.is_set():
                waited_after_stop += tick
                if waited_after_stop >= self.grace:
                    logger.warning("job %s outlived the shutdown grace; releasing it", job.id)
                    jobs.release(self.conn, job.id, self.worker_id)
                    return
        if lease_lost.is_set() and not done.is_set():
            logger.error(
                "job %s: lease lost while running; abandoning (another worker owns it)", job.id
            )
            return
        err = outcome["error"]
        if err is None:
            if not jobs.complete(self.conn, job.id, self.worker_id):
                logger.warning("job %s finished but its lease was lost", job.id)
        else:
            logger.warning("job %s failed: %s: %s", job.id, type(err).__name__, err)
            self._fail(job, f"{type(err).__name__}: {err}")

    def _fail(self, job: jobs.Job, error: str) -> None:
        jobs.fail(
            self.conn,
            job.id,
            self.worker_id,
            error,
            backoff_base=self.backoff_base,
            on_dead=self._on_dead,
        )

    def _heartbeat(self, job_id: int, lease_lost: threading.Event) -> bool:
        # The handler thread and this loop may both call it: use a private connection per call.
        conn = jobs.connect(self.db_path)
        try:
            ok = jobs.heartbeat(conn, job_id, self.worker_id, lease_seconds=self.lease)
        finally:
            conn.close()
        if not ok:
            lease_lost.set()
        return ok

    def run(self, *, drain: bool = False) -> int:
        """Loop until ``stop`` is set (or, with drain, until nothing is runnable)."""
        processed = 0
        while not self.stop.is_set():
            if self.run_once():
                processed += 1
                continue
            self._digest()
            if drain:
                break
            self.stop.wait(self.poll)
        self._last_digest = float("-inf")
        self._digest()  # report anything that died on the way out
        self.conn.close()
        return processed


def _print_status(db_path: str, as_json: bool) -> None:
    conn = jobs.connect(db_path)
    try:
        st = jobs.status(conn)
    finally:
        conn.close()
    if as_json:
        print(json.dumps(st, indent=2, sort_keys=True))
        return
    c = st["counts"]
    print(f"queue depth: {st['queue_depth']} (runnable now: {st['ready_now']})")
    print(f"running:     {st['running']} (expired leases: {st['expired_leases']})")
    print(f"succeeded:   {c['succeeded']}   failed: {c['failed']}   dead: {c['dead']}")
    for d in st["dead"]:
        fam = jobs.family_hash(d["family_id"])
        print(
            f"  DEAD job={d['id']} kind={d['kind']} family={fam} attempts={d['attempts']} "
            f"error={d['last_error']!r}"
        )
    if st["dead"]:
        print("Retry one with: python -m worker --retry <job id>")


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="worker", description=__doc__.split("\n")[0])
    p.add_argument("--db", default=None, help="SQLite path (default: CURRICULUM_DB_PATH)")
    p.add_argument("--status", action="store_true")
    p.add_argument("--json", action="store_true", help="with --status: machine-readable")
    p.add_argument("--retry", type=int, metavar="JOB_ID")
    p.add_argument("--once", action="store_true", help="drain runnable jobs, then exit")
    p.add_argument("--scheduler", action="store_true", help="also run the scheduler tick loop")
    args = p.parse_args(argv)
    logging.basicConfig(
        level=os.environ.get("LOG_LEVEL", "INFO"),
        format="%(asctime)s %(levelname)s %(name)s %(message)s",
    )
    try:
        from .db_utils import get_db_path  # type: ignore
    except ImportError:
        from db_utils import get_db_path  # type: ignore
    db_path = args.db or get_db_path()

    if args.status:
        _print_status(db_path, args.json)
        return 0
    if args.retry is not None:
        conn = jobs.connect(db_path)
        ok = jobs.retry_dead(conn, args.retry)
        conn.close()
        print("requeued" if ok else f"job {args.retry} is not dead (nothing changed)")
        return 0 if ok else 1

    try:
        from .migrations import apply_migrations  # type: ignore
    except ImportError:
        from migrations import apply_migrations  # type: ignore
    apply_migrations(db_path)
    loaded = load_handler_modules()
    stop = threading.Event()
    for sig in (signal.SIGTERM, signal.SIGINT):
        signal.signal(sig, lambda *_: stop.set())
    for kind in job_registry.kinds():
        logger.info("handler %-12s %s", kind, "STUB" if job_registry.is_stub(kind) else "real")
    logger.info("worker up: db=%s extra handler modules=%s", db_path, loaded)

    if args.scheduler:
        try:
            from . import loop_integration, scheduler  # type: ignore
        except ImportError:
            import loop_integration  # type: ignore
            import scheduler  # type: ignore
        if not loop_integration.enabled():
            # The one switch for the weekly loop (also read by the web app). Off, the worker idles
            # and nothing is planned, queued or paid for.
            logger.warning("LOOP_JOBS_ENABLED is not set: the scheduler is OFF, the loop is idle")
            args.scheduler = False
    if args.scheduler:
        threading.Thread(
            target=scheduler.run_forever, args=(db_path, stop), name="scheduler", daemon=True
        ).start()

    n = Worker(db_path, stop=stop).run(drain=args.once)
    logger.info("worker stopped after %d job(s)", n)
    return 0


if __name__ == "__main__":
    sys.exit(main())
