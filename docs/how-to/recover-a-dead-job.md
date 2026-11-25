# Recover a dead job

A job is `dead` once it has failed every retry. This guide shows you how to find out why, fix it,
and run the job again. Run the commands where the worker runs. On the server, prefix each one with
`docker compose --env-file .deploy.env exec -u appuser worker`.

1. **List the dead jobs**:

   ```bash
   python -m worker --status
   ```

   Each row shows the job id, its kind, a short hash of the family, the attempts and the error.

2. **Read the full error**:

   ```bash
   python -c "import os,sqlite3;[print(*r) for r in sqlite3.connect(os.environ['CURRICULUM_DB_PATH']).execute(\"select id,kind,last_error from jobs where state='dead'\")]"
   ```

3. **Fix the cause**: the code, a setting, or the data the job works on.

4. **Run it again**:

   ```bash
   python -m worker --retry <id>
   ```

   This resets the attempts and turns alerting back on for that job.

To abandon a job, do nothing. It stays `dead` and is never deleted.

## Find the family behind an alert

Alerts show a hash, never the family id. Compute the hash for a family you suspect, and compare:

```bash
python -c "import hashlib,os;print(hashlib.sha256((os.environ.get('JOB_ALERT_SALT','')+'fam_local').encode()).hexdigest()[:8])"
```

Retry rules and job states: [Worker and scheduler reference](../reference/worker-and-scheduler.md#job-states).
