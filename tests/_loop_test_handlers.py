"""Handlers used by subprocess worker tests (loaded via WORKER_HANDLER_MODULES)."""

import os
import sqlite3
import time

from job_registry import handler


def _record(ctx, note=""):
    conn = sqlite3.connect(ctx.db_path, timeout=30)
    conn.execute("CREATE TABLE IF NOT EXISTS ran_log (job_id INTEGER, pid INTEGER, note TEXT)")
    conn.execute("INSERT INTO ran_log VALUES (?,?,?)", (ctx.job.id, os.getpid(), note))
    conn.commit()
    conn.close()


@handler("outline")
def record_run(ctx):
    _record(ctx)


@handler("author")
def hang_once_then_work(ctx):
    marker = os.environ["CRASH_MARKER"]
    if not os.path.exists(marker):
        open(marker, "w").write(str(os.getpid()))
        _record(ctx, "started")
        time.sleep(120)  # the test kill -9s this process while it sleeps
    _record(ctx, "finished")
