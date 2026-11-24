# Contributing

Developer-facing setup and workflow. If you just want to print or generate lesson weeks, the
[README](README.md) is all you need — this document is for changing the code.

## Development setup

**Python 3.12 or newer required; CI and production run 3.15.** (networkx 3.7 needs 3.12+.) The virtual environment **must live at the repo root** — the E2E
suite hard-codes `venv/bin/uvicorn` in `frontend/global-setup.ts`.

```bash
uv venv --python 3.15 --seed venv        # or: python3.15 -m venv venv
venv/bin/pip install -r requirements-dev.txt
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

### Tests never call a real LLM or ntfy

- **pytest**: `tests/conftest.py` sets a fake `OPENROUTER_API_KEY` and points `LLM_BASE_URL` /
  `NTFY_URL` at a dead local port for every test, and blocks non-loopback sockets.
  `tests/test_no_external_calls.py` fails if `src/` gains a second `OpenAI(` client or a new
  outbound-HTTP module. Fake the model with `tests/llm_fakes.FakeProvider` + `fake_client()`.
- **E2E**: `global-setup.ts` starts `frontend/e2e/llm-stub/server.mjs` (127.0.0.1:8183, override
  with `E2E_LLM_STUB_PORT`) and spawns the backend with `LLM_*`/`OPENAI_*`/`NTFY_URL` forced to it,
  overriding your shell. Backend log: `/tmp/playwright-backend.log`; stub log:
  `/tmp/playwright-llm-stub.log`; specs assert on calls with `e2e/fixtures/stub.ts`.
- **New canned scenario**: edit `frontend/e2e/llm-stub/fixtures/*` (shared with pytest), or add a
  directive handled in `server.mjs` / `tests/llm_fakes.py` and set it per student with
  `createStudent(..., { stubScenario: 'broken-day=Wednesday' })`.

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
| `src/llm/` | Model layer: OpenRouter provider, per-task models, retries, structured output, usage ledger |
| `src/agent.py` | LLM-driven weekly plan generation via `src/llm` (needs `OPENROUTER_API_KEY`) |
| `src/trio_generator.py` | Generates 3 candidate plans post-feedback; notifies via `src/ntfy.py` |
| `src/feedback_processor.py` | Applies mastery/quantity feedback to a student's stored blobs |
| `src/worksheet_html_renderer.py` | HTML print-packet engine (preferred for printables) |
| `src/worksheet_html_renderer.py` | HTML engine (all 24 types, browser-printable) |
| `src/worksheets/` | 22 worksheet types; `factory.py` is the unified entry point |
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

## Model layer and secrets

All model calls go through `src/llm/` (OpenRouter by default). Tasks (scaffold, lesson, outline,
author, judge, repair) map to models in `src/llm/models.json`; change a model by editing that file
or setting `LLM_MODEL_<TASK>`. See `.env.example` for every variable.

- **Key**: `OPENROUTER_API_KEY` (legacy `OPENAI_API_KEY` works). Put it in a git-ignored `.env`
  or your shell; never commit it. The key is excluded from reprs, scrubbed from error messages
  and from every log record (`src/llm/redact.py`), and tests assert it never appears in logs.
- **Privacy routing**: a child's first name, grade, interests and the parent's notes are sent to
  the provider. `LLM_PRIVACY_ROUTING=strict` restricts OpenRouter to endpoints with zero data
  retention that do not train on prompts; `no-training` only forbids collection; `off` is the
  provider default. Unset, it is `strict` when `AGENTIC_HOSTED=1` (the hosted deployment must set
  this) and `off` for self-hosters.
- **Spend**: every call is recorded in the `llm_usage` table (ids, tokens, cost, never text).
  `LLM_CAP_FAMILY_MONTH_USD` stops a family's calls before they are made; unset means unlimited.
- **Compare models**: `venv/bin/python scripts/taste_test.py --prompt-file p.txt --max-usd 0.50`.

## Docker

```bash
docker build -t agentic-curriculum .
docker run --rm -p 8000:8000 -e OPENROUTER_API_KEY="sk-or-..." agentic-curriculum
```

The image builds the Next.js frontend, runs `ingest_standards.py` at build time so `curriculum.db`
exists before boot, and starts Uvicorn. Optional env vars: `LLM_BASE_URL`, `LLM_MODEL` (legacy `OPENAI_BASE_URL` / `OPENAI_MODEL` still work).
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

## Dependency and runtime policy

- **Runtime vs dev Python packages.** `requirements.txt` holds runtime dependencies only and is the
  only file the production Docker image installs. Test and lint tooling (pytest, black, ruff,
  pre-commit, jsonschema, httpx2, pip-audit) lives in `requirements-dev.txt`, which includes
  `requirements.txt`. If a module under `src/` imports a package, it belongs in `requirements.txt`.
  CI's image build fails if pytest ends up in the production image.
- **What is audited.** `.github/workflows/dependency-audit.yml` runs on every pull request, every
  Monday at 06:17 UTC and on demand, so an advisory published after a merge still surfaces:
  - `npm audit --package-lock-only --audit-level=high` in `frontend/`, for production dependencies
    and for everything (build and test tools included);
  - `pip-audit --strict` on the exact versions `requirements-dev.txt` resolves to today (runtime and
    dev), installed into a clean venv and frozen first, because the requirements files hold ranges.
- **Reading a failing audit.** Open the job log: it lists the package, installed version, advisory
  ID and fixed version. Raise the lower bound in `requirements*.txt` (or `npm install <pkg>@latest`
  in `frontend/`) and re-run. If an advisory has no fix yet, add `--ignore-vuln <ID>` to the
  pip-audit line in `dependency-audit.yml` with a comment naming the package and why it is not
  exploitable here, and a date to revisit. Never ignore a whole package or severity class.
- **The image build is tested.** CI builds the production Docker image on every pull request
  (nothing is pushed) and checks it starts, reports its Node and Python versions, and imports the
  backend. A broken Dockerfile is caught before merge, not after.
- **Node.** The newest LTS: Node 26 (supported to April 2029). One `NODE_IMAGE` build argument in
  the Dockerfile feeds both the frontend build and the runtime (copied from the official image, no
  install script piped into a shell); CI uses the same major. Move to the next LTS well before the
  current one reaches end of life.
- **Python.** The newest stable: Python 3.15 (supported to October 2031), set by `PYTHON_IMAGE` in
  the Dockerfile and `PYTHON_VERSION` in the workflows. Change them together.
- **Frontend tooling held back on purpose.** ESLint stays on 9.x and TypeScript on 6.0.x: Next.js's
  lint config (`eslint-config-next`, which bundles typescript-eslint, eslint-plugin-import and
  jsx-a11y) does not load under ESLint 10, and typescript-eslint supports TypeScript below 6.1
  only. Move both when those packages add support (Dependabot will propose it).
- **Updates.** Dependabot (`.github/dependabot.yml`) opens weekly PRs for npm, pip, Docker and
  GitHub Actions: minor and patch updates grouped, majors one per PR. They are reviewed and merged
  by hand; auto-merge is not enabled.
