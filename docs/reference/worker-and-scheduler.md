# Worker and scheduler reference

Code: `src/jobs.py` (queue), `src/worker.py`, `src/scheduler.py`, `src/job_registry.py`,
`src/job_alerts.py`, `src/job_handlers_real.py`, `src/job_handlers_stub.py`. Schema: migration
`0010_jobs.sql`. Both processes use the same SQLite file as the app and apply pending migrations at
start-up.

Tasks: [Run the worker](../how-to/run-the-worker.md), [Recover a dead job](../how-to/recover-a-dead-job.md).
Background: [The weekly loop](../explanation/the-weekly-loop.md).

## Commands

Run from `src/`. In the container, `PYTHONPATH=/app/src` is already set.

| Command | Effect |
|---|---|
| `python -m worker` | worker loop |
| `python -m worker --scheduler` | worker plus a scheduler tick, in one process. The server runs this |
| `python -m scheduler` | scheduler only |
| `python -m worker --once` | runs everything runnable now, then exits |
| `python -m worker --status` | queue depth, running jobs, dead jobs. `--json` for machine output |
| `python -m worker --retry <id>` | puts dead job `<id>` back in the queue with its attempts reset |
| `python -m loop_integration seed-demo` | creates the made-up child `demo_child` |
| `python -m loop_integration start-week <student_id> [--week YYYY-MM-DD]` | starts a week for a child. Default: next Monday |
| `python ../scripts/demo_weekly_loop.py` | simulates a whole week on a temporary database |

Several workers on one database is safe: claims take SQLite's write lock. Two schedulers is
harmless, because every tick action is idempotent.

## Settings

| Variable | Default | Meaning |
|----------|---------|---------|
| `LOOP_JOBS_ENABLED` | unset (off) | `1` turns on the scheduler and the web app's hooks. Read by both `app` and `worker`. Off, nothing is planned or queued and no model is called. The loop console works either way |
| `CURRICULUM_DB_PATH` | `<repo>/curriculum.db` | the SQLite file |
| `WORKER_LEASE_SECONDS` | 300 | lease on a claimed job, heartbeated every third of it. A killed worker's job is reclaimed this long after its last heartbeat |
| `WORKER_POLL_SECONDS` | 2 | idle poll interval |
| `WORKER_SHUTDOWN_GRACE_SECONDS` | 30 | after SIGTERM, how long the running job may finish before it is released to the queue |
| `WORKER_HANDLER_MODULES` | empty | comma-separated modules whose `@handler("kind")` calls register real handlers |
| `SCHEDULER_INTERVAL_SECONDS` | 300 | tick interval |
| `SCHEDULER_DEFAULT_TZ` | `America/New_York` | timezone for families whose `family_settings.timezone` is NULL |
| `AUTHOR_MAX_RUN_USD` | 1.50 | spend cap for one authoring attempt |
| `AUTHORING_RUNS_DIR` | `authoring_runs/` beside the database | where authoring run records are written |
| `ALERT_EMAIL_TO` | empty | comma-separated recipients of the dead-job email. Email is off until this and `SMTP_HOST` are set |
| `SMTP_HOST`, `SMTP_PORT`, `SMTP_USER`, `SMTP_PASSWORD`, `SMTP_FROM` | none, 587 | mail relay. STARTTLS, or implicit TLS on port 465 |
| `JOB_ALERT_SALT` | empty | salt for the family hash in alerts and `--status` |

## Handlers

| Kind | Real handler | Stub |
|---|---|---|
| `outline` | `job_handlers_real` | logs and succeeds |
| `author` | `job_handlers_real` | logs and succeeds |
| `send_notice` | none yet | logs and succeeds. No parent is emailed |

A real handler replaces the stub for its kind. Two real handlers for one kind is a start-up error.
The worker logs `STUB` or `real` for each kind at start-up.

Contract: a handler takes a `JobContext` (`job`, `connect()`, `heartbeat()`), returns on success
and raises to be retried. It must be idempotent: a job can run twice.

## Job states

`queued` → `running` → `succeeded`, or `dead` after the last failed attempt.

| Rule | Value |
|---|---|
| Attempts | 5 |
| Backoff | exponential with jitter, 30 s base, 1 h cap |
| Crashed worker | job reclaimed after the lease expires; costs one attempt |
| Dead job | kept, never deleted; logged at ERROR at once |
| Dead-job email | one digest at most every 15 minutes, each job listed once; a failed send is retried |

Alert line format: `job=12 kind=author family=ab12cd34 attempts=5/5 error=TimeoutError`. No child
data or error text. The family hash is `sha256(JOB_ALERT_SALT + family_id)[:8]`.

## Idempotency keys

Don't change these.

| Job | Key |
|---|---|
| Outlines | `outlines:{plan}`, with `:r{n}` appended after a regeneration |
| Authoring | `author:{plan}:{option}` |
| Notices | `reminder:{family}:{week_start}`, `nudge:…`, `lastcall:…` |

## Scheduler windows

Family-local time, for the school week starting Monday.

| When | What |
|---|---|
| Friday 00:00 | the coming week's plan is created for each child |
| Friday 15:00 | check-in reminder |
| Saturday 10:00 | nudge to pick. Safety net: a child with no check-in is moved on so outlines still get made |
| Sunday 08:00 | last call |
| Sunday 12:00 | pick deadline: if nobody picked, one of the three outlines is chosen at random (fixed per plan) and authored. With no outlines, the week expires |
| Sunday 20:00 | print deadline |

Notices catch up to the latest window only. Each tick also re-enqueues the outline or author job
for any plan in `outlining` or `authoring`; the shared key makes that a no-op if the job exists.

## Authoring

One attempt typically takes 6 to 12 minutes and costs about $0.10 to $0.35, capped by
`AUTHOR_MAX_RUN_USD`. An author job gets 3 attempts. Each run writes a record to
`authoring_runs/<packet_id>.json` next to the database (`/data/authoring_runs/` on the server;
override with `AUTHORING_RUNS_DIR`): status, model, cost, time, rewrites and the skills left out.
