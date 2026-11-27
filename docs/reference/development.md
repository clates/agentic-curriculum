# Development reference

Tasks: [`CONTRIBUTING.md`](../../CONTRIBUTING.md). Background:
[Dependencies and test isolation](../explanation/dependencies-and-test-isolation.md).

## Commands

| What | Command | Notes |
|------|---------|-------|
| Backend dev server | `cd src && ../venv/bin/uvicorn main:app --reload` | port 8000 |
| Frontend dev server | `cd frontend && npm run dev` | port 3000 |
| Backend tests | `venv/bin/python -m pytest tests/ -v --tb=short` | about 3 s |
| One backend test | `venv/bin/python -m pytest tests/test_feedback_api.py -k mastery -v` | |
| E2E tests | `cd frontend && npm run test:e2e` | self-contained |
| Type check | `cd frontend && npm run type-check` | |
| Format check | `cd frontend && npm run format:check` | Prettier |
| Lint and format everything | `venv/bin/pre-commit run --all-files` | Black, Ruff, Prettier |
| Compare models | `venv/bin/python scripts/taste_test.py --prompt-file p.txt --max-usd 0.50` | calls the real API |

`tests/validate_chunk*.py` and `tests/verify_fixes.py` are old milestone scripts, not part of the
suite.

## E2E servers

| Server | Port | Override |
|---|---|---|
| Backend | 8182 | `E2E_BACKEND_PORT` |
| Frontend (`next build` + `next start`) | 3002 | `E2E_FRONTEND_PORT` |
| Model stub | 8183 | `E2E_LLM_STUB_PORT` |
| Login project backend and frontend | 8184, 3003 | |
| Database | `/tmp/playwright-test.db` | `PLAYWRIGHT_DB_FILE` |

`E2E_SKIP_AUTH=1` leaves out the login project. Logs: `/tmp/playwright-backend.log`,
`/tmp/playwright-llm-stub.log`.

## Test fakes

| Tool | Use |
|---|---|
| `tests/llm_fakes.FakeProvider`, `fake_client()` | fake model in pytest |
| `frontend/e2e/llm-stub/fixtures/*` | canned model replies, shared by pytest and E2E |
| `createStudent(..., { stubScenario: 'broken-day=Wednesday' })` | per-student stub directive |
| `frontend/e2e/fixtures/stub.ts` | assert on stub calls in specs |
| `tests/test_no_external_calls.py` | fails on a second `OpenAI(` client or new outbound-HTTP module in `src/` |

## Code style

Black and Ruff, 100-character lines, and Prettier for the frontend, all run by pre-commit on
staged files. `scripts/*.py` are exempt from Ruff's E402.

## Code map

| Path | Responsibility |
|------|----------------|
| `src/main.py` | FastAPI app: students, weekly packets, feedback, artifacts |
| `src/llm/` | model layer: OpenRouter provider, per-task models, retries, structured output, usage ledger |
| `src/authoring/` | hosted week authoring: prompts, validation, repair, run records |
| `src/weekdoc/` | the hosted week document: schema and renderers |
| `src/jobs.py`, `src/worker.py`, `src/scheduler.py` | job queue, worker, scheduler |
| `src/loop_admin.py`, `src/week_review.py` | loop console API and the week review |
| `src/auth/` | login |
| `src/agent.py` | single-request weekly plan generation |
| `src/trio_generator.py` | three candidate plans after feedback; notifies through `src/ntfy.py` |
| `src/feedback_processor.py` | applies mastery and workload feedback to a student's stored data |
| `src/worksheet_html_renderer.py` | HTML print-packet engine |
| `src/worksheets/` | worksheet types; `factory.py` is the entry point |
| `scripts/` | offline week generators, one tracked script per week |
| `tests/` | pytest; fixtures in `conftest.py`, builders in `factories.py` |
| `frontend/e2e/` | Playwright specs; seeding helpers in `fixtures/api.ts` |

Student state: three JSON blobs on `student_profiles`, described in
[Student data blobs](data-schemas.md).

## HTTP API

Full spec: [`api_reference.yaml`](../../api_reference.yaml), also at
<http://127.0.0.1:8000/docs> on a running backend.

| Area | Routes |
|---|---|
| Students | `GET /students`, `POST /students`, `POST /children` ([details](children.md)), `GET\|PUT\|DELETE /student/{id}` |
| Planning | `POST /generate_weekly_plan`, `GET /students/{id}/weekly-packets[/{packet_id}]` |
| Resources | `GET /students/{id}/weekly-packets/{id}/worksheets`, `GET /students/{id}/worksheet-artifacts/{id}` |
| Feedback | `POST /students/{id}/weekly-packets/{id}/feedback` ([Friday form](friday-form.md)) |
| Curriculum | `GET /curriculum/graph/{subject}`, `GET /students/{id}/progress-map/{subject}` |
| System | `GET /health`, `GET /system/options` |

## Model settings

Every variable is listed in `.env.example`.

| Variable | Default | Meaning |
|---|---|---|
| `OPENROUTER_API_KEY` | required | model API key. `OPENAI_API_KEY` also works |
| `LLM_BASE_URL` | OpenRouter | `OPENAI_BASE_URL` also works |
| `LLM_MODEL`, `LLM_MODEL_<TASK>` | `src/llm/models.json` | model for every task, or one task (scaffold, lesson, outline, author, judge, repair) |
| `LLM_PRIVACY_ROUTING` | `strict` if `AGENTIC_HOSTED=1`, else `off` | `strict`: zero-retention, no-training endpoints only. `no-training`: no training only. `off`: provider default |
| `AGENTIC_HOSTED` | unset | `1` on the hosted deployment |
| `LLM_CAP_FAMILY_MONTH_USD` | unlimited | a family's monthly spend cap, checked before each call |

Each call is recorded in the `llm_usage` table: ids, tokens and cost, never text.

## Runtime and dependencies

| Item | Value | Set in |
|---|---|---|
| Python | 3.15 | `PYTHON_IMAGE` in `Dockerfile`, `PYTHON_VERSION` in the workflows |
| Node | 26 LTS | `NODE_IMAGE` in `Dockerfile`, `NODE_VERSION` in the workflows |
| ESLint | 9.x, held | `frontend/package.json` |
| TypeScript | 6.0.x, held | `frontend/package.json` |
| Runtime Python packages | `requirements.txt` | installed in the image |
| Test and lint packages | `requirements-dev.txt` | includes `requirements.txt` |

Audits (`.github/workflows/dependency-audit.yml`, on every pull request, Mondays 06:17 UTC and on
demand):

- `npm audit --package-lock-only --audit-level=high` in `frontend/`, once for production
  dependencies and once for all of them;
- `pip-audit --strict` on the exact versions `requirements-dev.txt` resolves to, frozen in a clean
  venv.

Dependabot (`.github/dependabot.yml`): weekly pull requests for npm, pip, Docker and GitHub
Actions, minor and patch updates grouped, majors one per pull request. Nothing merges automatically.

## Docker image

`docker build -t agentic-curriculum .` builds the frontend, runs `ingest_standards.py` so
`curriculum.db` exists at boot, and starts Uvicorn on port 8000. Logs go to `/app/logs`.
`GET /health` is the healthcheck. CI builds the image on every pull request (nothing is pushed),
starts it, and fails if pytest is installed in it.
