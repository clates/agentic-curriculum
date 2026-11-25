# Run the worker and turn the weekly loop on

This guide shows you how to run the background worker on your own computer, switch the weekly loop
on or off on the server, and push one week through by hand. What the loop does and why:
[The weekly loop](../explanation/the-weekly-loop.md).

## Run it on your own computer

From `src/`, with the venv:

```bash
cd src
../venv/bin/python -m worker --scheduler    # worker plus the scheduler, in one process
```

To watch a whole simulated week on a temporary database instead:

```bash
../venv/bin/python ../scripts/demo_weekly_loop.py
```

Other ways to start it are listed under [Commands](../reference/worker-and-scheduler.md#commands).

## Turn the loop on, on the server

The `worker` container is deployed with every release but does nothing until it's switched on.

```bash
ssh curriculum
cd /srv/curriculum
echo 'LOOP_JOBS_ENABLED=1' >> .env
docker compose --env-file .deploy.env up -d --force-recreate app worker   # a restart does not re-read .env
docker compose --env-file .deploy.env logs --tail 20 worker
```

The log should name the real handlers: `handler outline real` and `handler author real`. If it
says `STUB` for either, the handler modules aren't loaded. Check `WORKER_HANDLER_MODULES`.

To turn it off, delete the line from `.env` and run the same `up -d --force-recreate` line. Jobs
already queued stay queued.

## Push one week through by hand

The quickest way is the loop console. Sign in and open `/loop`. Each child's week is shown as six
steps with a button for each. **Add a demo child** makes a made-up child, so no real data is
involved.

Or, from the command line:

```bash
docker compose --env-file .deploy.env exec -u appuser worker python -m loop_integration seed-demo
docker compose --env-file .deploy.env exec -u appuser worker python -m loop_integration start-week demo_child
docker compose --env-file .deploy.env logs -f worker
```

When the three ideas appear, pick one on the child's page. Authoring takes several minutes. For a
real child, pass their student id to `start-week` in place of `demo_child`.

## Check a written week

On `/loop`, find the week under **Recent weeks** and choose **Review this week**. It reports the
reading level and word count for each day, the skills covered, and anything worth fixing, and it
links to the three printable documents.

## Set a family's timezone

```bash
docker compose --env-file .deploy.env exec -u appuser worker python -c "
import os, sqlite3
db = sqlite3.connect(os.environ['CURRICULUM_DB_PATH'])
db.execute(\"INSERT OR REPLACE INTO family_settings (family_id, timezone, updated_at) VALUES ('fam_local', 'America/Chicago', datetime('now'))\")
db.commit()"
```

Families with no timezone use `SCHEDULER_DEFAULT_TZ`.

If something fails: [Recover a dead job](recover-a-dead-job.md).
