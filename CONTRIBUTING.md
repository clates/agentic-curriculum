# Contributing

Developer-facing setup and workflow. If you just want to print or generate lesson weeks, the
[README](README.md) is all you need — this document is for changing the code.

## Development setup

**Python 3.11–3.13 required.** CI runs 3.12. Pillow does not build on 3.14+, so a newer system
Python will fail during install. The virtual environment **must live at the repo root** — the E2E
suite hard-codes `venv/bin/uvicorn` in `frontend/global-setup.ts`.

```bash
uv venv --python 3.12 --seed venv        # or: python3.12 -m venv venv
venv/bin/pip install -r requirements.txt
venv/bin/pre-commit install

cd frontend && npm install && npx playwright install chromium && cd ..

venv/bin/python src/ingest_standards.py  # creates curriculum.db (one-time)
```

Always invoke `venv/bin/python` explicitly rather than relying on an activated shell.

## Commands

| What | Command | Notes |
|------|---------|-------|
| Backend dev server | `cd src && ../venv/bin/uvicorn main:app --reload` | port 8000 |
| Frontend dev server | `cd frontend && npm run dev` | port 3000 |
| Backend tests | `venv/bin/python -m pytest tests/ -v --tb=short` | ~3s |
| Single backend test | `venv/bin/python -m pytest tests/test_feedback_api.py -k mastery -v` | |
| E2E tests | `cd frontend && npm run test:e2e` | self-contained |
| Type check | `cd frontend && npm run type-check` | |
| Format check | `cd frontend && npm run format:check` | Prettier |

The E2E suite spawns its own backend on port 8182 against an isolated database
(`/tmp/playwright-test.db`) and a frontend test server on port 3002. It never touches
`curriculum.db` or your running dev servers.

`tests/validate_chunk*.py` and `tests/verify_fixes.py` are historical milestone scripts, not part of
the pytest suite. `pytest tests/` is the real suite.

## Code style

Python is formatted with [Black](https://github.com/psf/black) and linted with
[Ruff](https://docs.astral.sh/ruff/), 100-character lines. Frontend files go through Prettier. All
three run automatically via [pre-commit](https://pre-commit.com/) on staged files:

```bash
venv/bin/pre-commit install     # once
venv/bin/pre-commit run --all-files
```

Commits fail until lint and formatting pass. A common miss in generator scripts is an f-string with
no placeholders.

`scripts/*.py` are exempt from Ruff's E402 (module-import-not-at-top), because generator scripts
need an `os.chdir` preamble before importing from `src/`.

## Git workflow

**Never commit directly to `main`.** Every change goes through a pull request, regardless of size.

```bash
git fetch origin
git checkout -b <branch-name> origin/main
# ... commits ...
git push -u origin <branch-name>
gh pr create
```

Before pushing, confirm your branch hasn't already been merged — if its tip appears in
`git log origin/main --oneline`, branch again from `origin/main` and cherry-pick anything not yet
landed rather than pushing to the stale branch.

Keep each PR to a single concern. Use conventional commits: `feat:`, `fix:`, `docs:`.

Full rules: [`AGENTS.md` §7](AGENTS.md#7-git-workflow-rules).

## Architecture map

| Path | Responsibility |
|------|----------------|
| `src/main.py` | FastAPI app — students, weekly packets, feedback, artifacts |
| `src/agent.py` | OpenAI-driven weekly plan generation (needs `OPENAI_API_KEY`) |
| `src/trio_generator.py` | Generates 3 candidate plans post-feedback; notifies via `src/ntfy.py` |
| `src/feedback_processor.py` | Applies mastery/quantity feedback to a student's stored blobs |
| `src/worksheet_html_renderer.py` | HTML print-packet engine (preferred for printables) |
| `src/worksheet_renderer.py` | PIL engine (PNG/PDF, image-heavy types) |
| `src/worksheets/` | 20 worksheet types; `factory.py` is the unified entry point |
| `scripts/` | Offline week generators — one tracked script per week |
| `tests/` | pytest; fixtures in `conftest.py`, builders in `factories.py` (temp DBs only) |
| `frontend/e2e/` | Playwright specs; seeding helpers in `fixtures/api.ts` |

Student state lives in three JSON blobs on `student_profiles`: `progress_blob` (mastered and
developing standards), `plan_rules_blob` (activity dosage), and `metadata_blob` (name, birthday,
notes). Feedback submission rewrites the first two — see `src/feedback_processor.py`.

## API surface

Live docs at <http://127.0.0.1:8000/docs> when the server runs; spec in
[`api_reference.yaml`](api_reference.yaml).

**Students** — `GET /students`, `POST /students`, `GET|PUT|DELETE /student/{id}`
**Planning** — `POST /generate_weekly_plan`, `GET /students/{id}/weekly-packets[/{packet_id}]`
**Resources** — `GET /students/{id}/weekly-packets/{id}/worksheets`,
`GET /students/{id}/worksheet-artifacts/{id}`
**Feedback** — `POST /students/{id}/weekly-packets/{id}/feedback`
**Curriculum** — `GET /curriculum/graph/{subject}`, `GET /students/{id}/progress-map/{subject}`
**System** — `GET /health`, `GET /system/options`

## Docker

```bash
docker build -t agentic-curriculum .
docker run --rm -p 8000:8000 -e OPENAI_API_KEY="sk-..." agentic-curriculum
```

The image builds the Next.js frontend, runs `ingest_standards.py` at build time so `curriculum.db`
exists before boot, and starts Uvicorn. Optional env vars: `OPENAI_BASE_URL`, `OPENAI_MODEL`.
Structured request logs are written to `/app/logs` inside the container. `GET /health` is the
container healthcheck endpoint.

## Adding a lesson week

Weeks are authored through Claude Code's `/generate-week` skill rather than written by hand — see
[Make your own week](README.md#make-your-own-week). The skill's own rules live in
`.claude/skills/generate-week/SKILL.md`, and the pedagogy it follows is in
[`AGENTS.md` §2](AGENTS.md#2-instructional-strategies) and §4.

Two conventions matter when reviewing a week PR:

- **Only the script is committed.** Generated `<theme>_week_series/` output is gitignored; the
  script must reproduce the entire week, teacher guide included.
- **Standards must be verified, not remembered.** Every standard ID annotated in the script's
  docstring should exist in `curriculum.db`. Weeks that name-drop standards without teaching them
  are the main failure mode to watch for in review.

Weeks good enough to share get their output copied into [`examples/`](examples/README.md).
