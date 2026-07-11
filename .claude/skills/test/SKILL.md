---
name: test
description: Run and interpret the backend pytest suite and the Playwright E2E suite. Use for regression checks, before any PR, or when asked to run tests.
---

# Running the test suites

Both suites must pass before any PR. Run from the repo root unless noted.

## Backend (pytest)

```bash
venv/bin/python -m pytest tests/ -v --tb=short        # full suite (~135 tests, ~3s)
venv/bin/python -m pytest tests/test_feedback_api.py  # one file
venv/bin/python -m pytest tests/ -k "cooldown"        # by keyword
```

- Fixtures (`tests/conftest.py`) create temp SQLite DBs — tests never touch `curriculum.db`.
- Test-data builders live in `tests/factories.py`; prefer them over hand-rolled dicts.
- On failure: report the failing assertion verbatim, then fix or escalate — do not skip or
  loosen an assertion to get green.

## E2E (Playwright)

```bash
cd frontend
npm run test:e2e                                # full suite (~41 tests, <1 min)
npx playwright test e2e/feedback.spec.ts        # one spec
npx playwright test --grep "Edit Student"       # one test by title
npx playwright test --headed                    # watch the browser
npm run test:e2e:ui                             # interactive UI mode
npm run test:e2e:report                         # open last HTML report
```

- Self-contained: `global-setup.ts` spawns `venv/bin/uvicorn` on port 8182 with an isolated DB
  at `/tmp/playwright-test.db`; the frontend test server runs on port 3002. Dev servers and
  `curriculum.db` are untouched.
- Requires the repo-root `venv/` and `npx playwright install chromium` (see CLAUDE.md bootstrap).
- Seeding helpers for new tests: `frontend/e2e/fixtures/api.ts` (`createStudent`, `createPacket`,
  `submitFeedback`, `backdateFeedback`).

### Troubleshooting

- **Port 8182 or 3002 in use**: a previous run left processes behind — kill stale `uvicorn`
  (`/tmp/playwright-backend.pid`) and `next dev` processes, then re-run.
- **Failure triage**: re-run just the failing spec (optionally `--headed`), read the failing step
  in the report (`frontend/playwright-report/`), and include the report path when summarizing.
- A timeout on the first test of a run usually means the backend never became healthy — check
  that `venv/bin/uvicorn` exists and imports cleanly (`venv/bin/python -c "import sys; sys.path.insert(0,'src'); import main"`).
