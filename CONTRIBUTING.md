# Contributing

How to change the code. To print or write lesson weeks, start with the [README](README.md)
instead. Commands, ports and settings: [Development reference](docs/reference/development.md).
Why the setup is the way it is:
[Dependencies and test isolation](docs/explanation/dependencies-and-test-isolation.md).

## Set up a development checkout

The virtual environment must be at the repo root, because the E2E suite runs `venv/bin/uvicorn`.

```bash
uv venv --python 3.15 --seed venv
venv/bin/pip install -r requirements-dev.txt
venv/bin/pre-commit install

cd frontend && npm install && npx playwright install chromium && cd ..

venv/bin/python src/ingest_standards.py   # creates curriculum.db
```

Always call `venv/bin/python` directly rather than relying on an activated shell.

## Run the tests

```bash
venv/bin/python -m pytest tests/ -v --tb=short   # backend, about 3 seconds
cd frontend && npm run test:e2e                  # browser suite, starts its own servers
```

To run a single backend test: `venv/bin/python -m pytest tests/test_feedback_api.py -k mastery -v`.

## Fake a new model reply

Add a canned reply under `frontend/e2e/llm-stub/fixtures/`. Both pytest and the E2E suite use it.
For behaviour that a file can't express, add a directive to `frontend/e2e/llm-stub/server.mjs` and
`tests/llm_fakes.py`, then turn it on for one student:

```ts
createStudent(..., { stubScenario: 'broken-day=Wednesday' })
```

In pytest, use `tests/llm_fakes.FakeProvider` with `fake_client()`.

## Submit a change

1. Branch from the latest `main`:

   ```bash
   git fetch origin
   git checkout -b <branch-name> origin/main
   ```

2. Commit with a conventional prefix: `feat:`, `fix:` or `docs:`. Pre-commit runs Black, Ruff and
   Prettier, and the commit fails until they pass. A common miss in generator scripts is an
   f-string with no placeholders.
3. Before pushing, check the branch hasn't already been merged. If its tip shows up in
   `git log origin/main --oneline`, branch again from `origin/main` and cherry-pick what hasn't
   landed.
4. Push and open a pull request, one concern per pull request:

   ```bash
   git push -u origin <branch-name>
   gh pr create
   ```

Never commit to `main` directly. Full rules: [`AGENTS.md` §7](AGENTS.md#7-git-workflow-rules).

## Review a lesson-week pull request

Weeks are written with `/generate-week`, not by hand. The skill's rules are in
`.claude/skills/generate-week/SKILL.md`, and its pedagogy is in
[`AGENTS.md` §2](AGENTS.md#2-instructional-strategies) and §4. When reviewing, check:

- **Only the script is committed.** The `<theme>_week_series/` output must not be, and the script
  must produce the whole week, teacher guide included.
- **Every standard is taught, not just named.** Each standard id in the script's docstring must
  exist in `curriculum.db` and be covered by a day. Name-dropped standards are the most common
  failure.

A week good enough to share also gets its output copied into [`examples/`](examples/README.md).

## Fix a failing dependency audit

1. Open the failed job's log. It names the package, the installed version, the advisory id and the
   version that fixes it.
2. Raise the lower bound in `requirements*.txt`, or run `npm install <pkg>@latest` in `frontend/`.
3. Push and let the audit run again.

If there is no fixed version yet, add `--ignore-vuln <ID>` to the `pip-audit` line in
`.github/workflows/dependency-audit.yml`. Put a comment next to it naming the package, why it
can't be exploited here, and a date to look again. Never ignore a whole package or severity.

## Move to a new Python or Node version

Change `PYTHON_IMAGE` in the `Dockerfile` and `PYTHON_VERSION` in the workflows together. For
Node, change `NODE_IMAGE` and `NODE_VERSION`. CI builds and starts the image on the pull request,
so a broken change shows up before it's merged.

## Change which model a task uses

Edit `src/llm/models.json`, or set `LLM_MODEL_<TASK>` in the environment. To compare candidates
on a real prompt first:

```bash
venv/bin/python scripts/taste_test.py --prompt-file p.txt --max-usd 0.50
```

Never commit the API key. Keep it in a git-ignored `.env` or your shell.
