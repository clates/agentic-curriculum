# CLAUDE.md

Homeschool curriculum app: FastAPI backend (`src/`) + Next.js frontend (`frontend/`) + offline
worksheet generators (`scripts/`). SQLite DB at `curriculum.db`.

## Environment bootstrap

Always use `venv/bin/python` — never system python. The E2E suite hard-codes `venv/bin/uvicorn`
(`frontend/global-setup.ts`), so the venv must live at the repo root.

```bash
# Python 3.11–3.13 required (CI uses 3.12; Pillow<11 does not build on 3.14+).
# If system python is too new, use uv:
uv venv --python 3.12 --seed venv
venv/bin/pip install -r requirements.txt

cd frontend && npm install && npx playwright install chromium
venv/bin/python src/ingest_standards.py   # creates curriculum.db (one-time)
```

## Commands

| What | Command | Notes |
|------|---------|-------|
| Backend dev server | `cd src && ../venv/bin/uvicorn main:app --reload` | port 8000 |
| Frontend dev server | `cd frontend && npm run dev` | port 3000 |
| Backend tests | `venv/bin/python -m pytest tests/ -v --tb=short` | fast (~3s) |
| E2E tests | `cd frontend && npm run test:e2e` | self-contained, see below |
| Type check | `cd frontend && npm run type-check` | |
| Format check | `cd frontend && npm run format:check` | Prettier |
| Python lint/format | ruff + black, 100-char lines | pre-commit enforces |
| Generate a week packet | `venv/bin/python scripts/generate_<theme>_week_series.py` | see /generate-week skill |

The E2E suite spawns its own backend on port 8182 with an isolated DB (`/tmp/playwright-test.db`)
and a frontend test server on port 3002 — it never touches `curriculum.db` or the dev servers.

## Architecture map

- `src/main.py` — FastAPI app; students, weekly packets, feedback, artifacts endpoints
- `src/agent.py` — OpenAI-driven weekly plan generation (needs `OPENAI_API_KEY`)
- `src/trio_generator.py` — generates 3 plans per student post-feedback; NTFY notify via `src/ntfy.py`
- `src/worksheet_html_renderer.py` — HTML print-packet engine (preferred for printables)
- `src/worksheet_renderer.py` — PIL engine (PNG/PDF, image-heavy types)
- `src/worksheets/` — 20 worksheet types; `factory.py` is the unified entry point
- `tests/` — pytest; fixtures in `conftest.py`, builders in `factories.py` (temp DBs, never `curriculum.db`)
- `frontend/e2e/` — Playwright specs; seeding helpers in `fixtures/api.ts` (backed by `scripts/e2e_seed.py`)

## Conventions

- **Read `AGENTS.md` before any worksheet/lesson work** — worksheet-type table, pedagogy patterns,
  renderer selection, and git workflow rules live there. Do not duplicate them here.
- **Never commit to `main`** — branch from `origin/main`, open a PR (AGENTS.md §7).
- Conventional commits: `feat:` / `fix:` / `docs:`.
- **Week output rule**: a generated week's assets go in its own `<theme>_week_series/` directory at
  the repo root — `<theme>_week.html` (student packet) and `<theme>_week_teacher_guide.html`
  (teacher guide), both emitted by the generator script. Output dirs are gitignored: the script is
  the only tracked artifact and must fully reproduce the week.
- `scripts/reference/` (gitignored, may be absent) holds bespoke one-off generator scripts kept as
  local reference — not canonical patterns.

## Skills

- `/feature <request>` — full pipeline: explore → plan → implement on a branch → tests → PR
- `/generate-week <theme>` — author a themed 5-day printable week offline (no OpenAI key)
- `/test` — run/interpret the pytest and Playwright suites, including single-test invocations
