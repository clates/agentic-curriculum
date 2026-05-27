# Playwright UI Test Suite — Design Spec

**Date:** 2026-05-26
**Status:** Approved

## Goals

- **Regression safety net:** Tests run in CI and block merges if they fail.
- **Living documentation:** `test.describe` / `test` names read as a behavioral spec — future contributors (human or AI) can understand expected behavior by reading the test tree.

## Architecture

One shared FastAPI process, one shared SQLite test DB, one Next.js process. The full request path (browser → Next.js proxy → FastAPI) is exercised on every test, matching production behavior.

```
Browser ──/api/**──▶  Next.js :3000  ──▶  FastAPI :8182
                      (proxy, same                │
                       as production)      SQLite (test DB)
                                           /tmp/playwright-test.db
```

No per-test server spawning. No route interception. The backend integration is tested for real.

## Server Startup

**`global-setup.ts`**
- Spawns `venv/bin/uvicorn src.main:app --port 8182` from the project root with `DB_FILE` set to the test DB path.
- Polls `GET http://localhost:8182/` until it returns 200 (max 30 s).
- Writes the process PID to `/tmp/playwright-backend.pid`.

**`playwright.config.ts` `webServer`**
- Command: `BACKEND_URL=http://localhost:8182 npm run dev`
- Port: 3000
- `reuseExistingServer: !process.env.CI` — locally skips Next.js startup if port 3000 is already live.

**`global-teardown.ts`**
- Reads PID from `/tmp/playwright-backend.pid` and kills the uvicorn process.
- Test DB is left in place locally (harmless growth); in CI the runner is ephemeral.

**Environment variables**

| Variable | Default | Purpose |
|---|---|---|
| `PLAYWRIGHT_DB_FILE` | `/tmp/playwright-test.db` | SQLite path passed to FastAPI |
| `BACKEND_URL` | `http://localhost:8182` | Set in `webServer` command |
| `CI` | unset locally | Controls `reuseExistingServer` |

## Test Isolation

Each `test.describe` block derives a unique student ID from the spec filename and describe-block name (e.g., `test-feedback-edit-a3f2`). All writes are scoped to that student, so describe blocks are fully independent and can run in parallel. No `afterAll` teardown is needed.

## File Layout

```
frontend/
  playwright.config.ts
  global-setup.ts
  global-teardown.ts
  e2e/
    fixtures/
      api.ts          # typed seed helpers (talk directly to FastAPI via request context)
    feedback.spec.ts  # plans list → plan detail modal → feedback modal
    students.spec.ts  # student CRUD
    print.spec.ts     # worksheet print endpoint
```

## `e2e/fixtures/api.ts` — Seed Helpers

Typed wrappers that call the FastAPI backend directly using Playwright's `request` context (not the browser). Used in `beforeAll` blocks.

```typescript
createStudent(id: string, opts: { name: string; birthday: string }) → Promise<void>
createPacket(studentId: string, opts?: Partial<PacketOpts>)         → Promise<{ packet_id: string }>
submitFeedback(studentId: string, packetId: string, ratings: {
  mastery: 'STRUGGLING' | 'DEVELOPING' | 'MASTERED';
  quantity: -2 | -1 | 0 | 1 | 2;
})                                                                   → Promise<void>
```

Packets are seeded with `status: 'ready'` so they appear in the pending section immediately. The `feedback_completed_at` field is set directly in the DB seed for the locked-feedback test (a timestamp > 3 weeks ago).

## Test Specs

### `feedback.spec.ts`

Covers the full path: plans list → plan detail modal → feedback modal.

```
Plans page
  ├── shows empty state when no packets exist
  ├── renders a pending packet card with name, subject, grade, days, worksheet counts
  └── clicking a completed packet row opens the plan detail modal

Plan detail modal
  ├── shows student name, week, subject, grade
  ├── shows daily plan content (day label, focus, objective, procedure steps)
  ├── shows a download button for each worksheet artifact
  ├── clicking a download button opens the artifact URL in a new tab
  ├── Close button dismisses the modal
  ├── clicking the backdrop dismisses the modal
  ├── Escape key dismisses the modal
  ├── Print All button opens the print URL in a new tab
  ├── shows "Provide Feedback" for a ready packet with no feedback
  ├── shows "Edit Feedback" for a ready packet with existing feedback (not locked)
  └── shows disabled "Feedback Submitted" for a packet with feedback older than 3 weeks

Feedback modal — first submission
  ├── title reads "Provide Feedback"
  ├── Submit button is disabled until both ratings are selected
  ├── selecting a mastery rating highlights it with a ring
  ├── selecting a workload rating highlights it
  ├── Cancel button closes the modal without submitting
  ├── Escape key closes the modal
  ├── backdrop click closes the modal
  └── submitting closes the modal and the button changes to "Edit Feedback"

Feedback modal — editing existing feedback
  ├── title reads "Edit Feedback"
  ├── mastery and workload ratings are pre-populated from the stored values
  ├── Submit button reads "Update Feedback"
  └── changing a rating and submitting succeeds

Feedback modal — locked
  └── "Feedback Submitted" button is disabled (clicking it does not open a modal)
```

### `students.spec.ts`

```
Student management
  ├── empty state
  │     shows "No Students Yet" and an "Add Student" button
  │
  ├── creating a student
  │     "Add Student" header button opens the modal titled "Add New Student"
  │     shows validation error for Student ID with invalid characters
  │     shows validation error for missing required fields
  │     shows validation error for a badly formatted birthday
  │     successfully creates a student and it appears in the list
  │     Cancel button closes the modal without creating
  │     Escape key closes the modal
  │
  ├── editing a student
  │     "Edit" button opens the modal titled "Edit Student"
  │     Student ID field is disabled (cannot be changed)
  │     pre-populates all editable fields from existing data
  │     saving updates the student's name in the list
  │
  └── deleting a student
        "Delete" button opens the confirmation modal
        Cancel button closes confirmation without deleting
        confirming delete removes the student from the list
```

### `print.spec.ts`

```
Worksheet print view
  ├── GET /api/students/{id}/weekly-packets/{id}/print returns 200
  ├── response Content-Type is text/html
  ├── rendered HTML contains print-color-adjust: exact in a <style> block
  └── day-header elements are present in the markup
```

## Implementation Notes

### `window.open` interactions

"Print All" and worksheet download buttons use `window.open()`. Tests capture the new tab via:

```typescript
const [popup] = await Promise.all([
  page.waitForEvent('popup'),
  page.getByRole('button', { name: 'Print All' }).click(),
]);
await expect(popup).toHaveURL(/\/print$/);
```

### Locked feedback seeding

The locked-feedback test requires `feedback_completed_at` to be > 3 weeks ago. After calling `submitFeedback` via the API, the fixture backdates the timestamp with a direct `sqlite3` CLI call using Node's `execSync`:

```typescript
execSync(
  `sqlite3 "${dbPath}" "UPDATE packet_feedback SET completed_at='2026-01-01T00:00:00Z' WHERE packet_id='${packetId}'"`,
);
```

No test-only API endpoints are added to production code. The `PLAYWRIGHT_DB_FILE` env var gives the fixture a known path to the DB.

### npm scripts

```json
"test:e2e":        "playwright test",
"test:e2e:ui":     "playwright test --ui",
"test:e2e:report": "playwright show-report"
```

### CI integration

Add to the existing CI pipeline after unit tests:

```yaml
- name: Install Playwright browsers
  run: npx playwright install --with-deps chromium

- name: Run E2E tests
  run: npm run test:e2e
  env:
    CI: true
    PLAYWRIGHT_DB_FILE: /tmp/playwright-test.db
```

Only Chromium is needed for this suite (no cross-browser coverage required for an internal tool).
