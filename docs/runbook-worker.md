# Runbook: job worker and scheduler

The weekly loop runs in the background: a **worker** executes queued jobs (outline generation,
week authoring, notices) and a **scheduler** tick decides, per family and in the family's own
timezone, which jobs are due. Both are plain Python processes over the same SQLite file as the
app. Code: `src/jobs.py` (queue), `src/worker.py`, `src/scheduler.py`, `src/job_registry.py`,
`src/job_alerts.py`. Schema: migration `0010_jobs.sql`.

## Run it

From the repo root with the venv (the container already sets `PYTHONPATH=/app/src`):

```bash
cd src
../venv/bin/python -m worker                # worker loop
../venv/bin/python -m worker --scheduler    # worker + scheduler tick (once a minute) in one process
../venv/bin/python -m scheduler             # scheduler only
../venv/bin/python -m worker --once         # drain what is runnable now, then exit
../venv/bin/python -m worker --status       # queue depth, running, dead jobs (add --json)
../venv/bin/python -m worker --retry 42     # put dead job 42 back in the queue
../venv/bin/python ../scripts/demo_weekly_loop.py   # simulated week on a temp DB
```

Running several workers on one DB is safe (claims take SQLite's write lock). Run exactly one
scheduler if you can, but two is harmless: every tick effect is idempotent.

## Environment

| Variable | Default | Meaning |
|----------|---------|---------|
| `CURRICULUM_DB_PATH` | `<repo>/curriculum.db` | the SQLite file (same as the app) |
| `WORKER_LEASE_SECONDS` | 300 | lease on a claimed job; heartbeated at a third of this. A killed worker's job is reclaimed this long after its last heartbeat. Must exceed nothing about job length (heartbeats extend it) |
| `WORKER_POLL_SECONDS` | 2 | idle poll interval |
| `WORKER_SHUTDOWN_GRACE_SECONDS` | 30 | on SIGTERM, how long the running job may finish before it is released to the queue |
| `WORKER_HANDLER_MODULES` | empty | comma-separated modules whose `@handler("kind")` calls register real handlers |
| `ALERT_EMAIL_TO` | empty | who gets the dead-job email (comma-separated). Email stays off until this and `SMTP_HOST` are set. The log line is always on |
| `SMTP_HOST`, `SMTP_PORT`, `SMTP_USER`, `SMTP_PASSWORD`, `SMTP_FROM` | none, 587 | the mail relay (STARTTLS; port 465 uses implicit TLS). Keep the password in the server's env file, never in the repo |
| `JOB_ALERT_SALT` | empty | salt for the short family hash in alerts and `--status` |
| `SCHEDULER_DEFAULT_TZ` | `America/New_York` | timezone for families whose `family_settings.timezone` is NULL |
| `SCHEDULER_INTERVAL_SECONDS` | 300 | tick interval. Every action is idempotent and compares against a window start, so a slower tick only delays a notice by up to one interval |

## Handlers

`outline`, `author` and `send_notice` ship as **stubs** that log and succeed (`src/job_handlers_stub.py`).
The real ones register with `@handler("outline")` etc. in their own module and are listed in
`WORKER_HANDLER_MODULES`; a real handler replaces the stub, two real ones for a kind is an error.
The worker logs `STUB` or `real` per kind at start-up: check that before trusting a deploy.
A handler takes a `JobContext` (`job`, `connect()`, `heartbeat()`), returns on success and raises
to be retried. It must be idempotent: a job can run twice.

## Job life and the scheduler's windows

`queued -> running -> succeeded`; failure retries with exponential backoff and jitter (30 s base,
1 h cap, 5 attempts) and then the job is `dead`: quarantined, kept, logged at once, and included in one email digest. A crashed worker's
job is reclaimed after lease expiry and costs one attempt.

Idempotency keys (do not change): `outlines:{plan}`, `author:{plan}:{option}`,
`reminder|nudge|lastcall:{family}:{week_start}`; after an outline regeneration `:r{n}` is appended.

Per family, local time, for the school week starting Monday M: Friday 15:00 check-in reminder;
Saturday 10:00 nudge to pick, and the safety net (a child with no check-in is moved on so outlines
still get made); Sunday 08:00 last call; Sunday 12:00 pick deadline (a parent who has not picked gets one of the three outlines chosen at random, fixed per plan, and it is authored so Monday's packet is ready; with no outlines the week expires);
Sunday 20:00 print deadline. Notices catch up to the latest window only. The tick also creates the
coming week's plans from Friday, and re-enqueues the outline/author job for any plan sitting in
`outlining`/`authoring` (a no-op when the endpoint already enqueued it, same key).
Set a family's zone: `INSERT OR REPLACE INTO family_settings (family_id, timezone, updated_at) VALUES ('fam_x','America/Chicago',datetime('now'))`.

## Dead jobs

1. `python -m worker --status` lists dead jobs with kind, hashed family, attempts and error class/text.
2. Read the full error: `sqlite3 $CURRICULUM_DB_PATH "select id,kind,last_error from jobs where state='dead'"`.
3. Fix the cause (or the data), then `python -m worker --retry <id>`: attempts reset, reporting re-armed.
4. A job you decide to abandon stays `dead`; it is never deleted by the system.

Every dead job is logged at ERROR the moment it dies. The email is one digest, sent at most every
15 minutes, listing each newly dead job once (a failed send is retried next time). A line reads
`job=12 kind=author family=ab12cd34 attempts=5/5 error=TimeoutError`: no child data, no error text. Map the hash by computing `sha256(JOB_ALERT_SALT + family_id)[:8]`.

## The weekly loop on the server

The `worker` service in `deploy/docker-compose.yml` runs `python -m worker --scheduler` from the
same image, as `appuser`, on the same data volume. It is deployed on every release but **idle**:
the scheduler and the web app's hooks start only when `LOOP_JOBS_ENABLED=1` is in
`/srv/curriculum/.env`. Off, nothing is planned or queued and no model call is made.

Turn it on (one switch, both containers read it):

```bash
ssh curriculum
cd /srv/curriculum
echo 'LOOP_JOBS_ENABLED=1' >> .env
docker compose --env-file .deploy.env up -d --force-recreate app worker   # a restart does not re-read .env
docker compose --env-file .deploy.env logs --tail 20 worker               # expect: handler outline real, handler author real
```

Turn it off by deleting the line and recreating. Jobs already queued stay queued.

What it does once on: Friday 00:00 local it makes next week's plan for each child; a check-in
queues the outlines at once (Saturday 10:00 does it for a family that skipped); the parent picks
one of three ideas (or, at Sunday 12:00, one is picked for them); the author writes, validates and
saves the week; the plan becomes `ready` and the print screen shows it. Notices (`send_notice`) are
still a stub that logs: no parent is emailed.

The **loop console** at `/loop` (behind login, always available, no switch needed) shows every child's
week as six steps (Feedback, Feed forward, Outlines, Pick, Author, Print) with a button for each, a
preview of the skills the engine would pick, and the jobs queued for the week. It is the easiest way
to try the loop; it also has "Add a demo child" and "Reset this child's weeks". It only does what the
loop itself could do, so it cannot put a week in a state the loop cannot reach.

The same from the command line, with a made-up child (no real data):

```bash
docker compose --env-file .deploy.env exec -u appuser worker python -m loop_integration seed-demo
docker compose --env-file .deploy.env exec -u appuser worker python -m loop_integration start-week demo_child
docker compose --env-file .deploy.env logs -f worker      # outline job, then the three ideas appear in the app
```

Then pick an idea on the child's page. Authoring takes 6 to 8 minutes and costs roughly $0.09 to
$0.26 (capped at `AUTHOR_MAX_RUN_USD`, default $1.50, per attempt; an author job gets 3 attempts).
Use `start-week <student_id>` for a real child the same way.

Cutover also deletes the crontab and the two reminder scripts (M8.7). The worker applies pending
migrations at start-up, as the app does.
