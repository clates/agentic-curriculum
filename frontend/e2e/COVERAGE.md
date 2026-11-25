# E2E coverage matrix

What the Playwright suite covers today, row by row, and what it does not. Every row was checked
against the spec file it names (the test titles below are the real titles). "Real API" means the
backend runs on its own port against an isolated database, with the LLM replaced by the static
stub in `e2e/llm-stub`; nothing is mocked unless the row says so.

Status: **covered** (the behavior is asserted end to end), **partial** (some of it), **gap** (no
test, or only a marker).

Projects: `mobile` = Pixel 7, `desktop` = Desktop Chrome. Parent screens (`e2e/parent/**`,
`parent-shell.spec.ts`) run on both; the phone tab bar tests run on mobile only (the desktop
project skips them, the header nav test in `parent-screens-hardening.spec.ts` covers desktop).
Journeys, `app-shell` and `print/` run on desktop (`app-shell` on both).

## Loop console (operator tool, `/loop`)

| Route / flow                                    | Spec: tests                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                               | Status            | Missing                                                                                                                                                                                                                                                                      |
| ----------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ----------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `/loop`: push a child's week one step at a time | `loop/console.spec.ts`: "a week waiting on its check-in can be skipped past, and the outlines are queued", "picking an idea moves the week to authoring and queues exactly one author job", "fresh ideas can be asked for past the parent cap", "feed forward shows which skills the engine would pick, and why", "a child's weeks can be reset after a confirm, and started again", "an action that is not possible is disabled and says why", "the console is accessible and does not scroll sideways, even on a phone" | covered (desktop) | No worker runs in this suite, so a queued job stays queued: the outline and author handlers are proven in `tests/test_loop_integration.py` and `tests/test_loop_admin.py`, not here. Dead-job retry and the worker-may-be-down banner are covered in the backend tests only. |

## Parent screens (phone-first, the new product surface)

| Route / flow                                          | Spec: tests                                                                                                                                                                                                                                                                                                                                                     | Status                     | Missing                                                                                                                                                                             |
| ----------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Parent shell: tab bar, header nav, states             | `parent-shell.spec.ts`: "This week shows an empty state with a next step, accessibly", "...a loading state, then content", "...a plain error with a retry that works", "the tab bar is at the bottom, marks the current tab and reaches the other tabs"; `parent/parent-screens-hardening.spec.ts`: "Desktop width: the header navigation replaces the tab bar" | covered                    | The Children tab target (`/students`) is only checked as a URL, not its content (legacy page, see below).                                                                           |
| Banned-words copy lint on parent copy                 | `parent-shell.spec.ts`: "the banned-words lint passes on all parent copy" (runs `scripts/lint-copy.mjs`); `expectNoBannedWords` is called in most parent specs                                                                                                                                                                                                  | covered                    | The lint only reads `lib/copy.ts` and parent components; copy returned by the backend (a generated week's titles) is not linted.                                                    |
| `/week` This week: one card per child, per loop state | `parent/this-week.spec.ts`: "a child whose week is "<status>" gets one next step" x7 (awaiting_feedback, outlining, awaiting_pick, expired, authoring, ready, printed); `parent/parent-screens-hardening.spec.ts`: "Loop-state copy" x7                                                                                                                         | covered                    | `needs_attention` is served as a canned reply (cannot be reached through the loop yet).                                                                                             |
| `/week` error + retry, empty, loading                 | `this-week.spec.ts`: "an error from the server shows a plain message with a retry"; `parent-shell.spec.ts` (empty/loading/error rows above)                                                                                                                                                                                                                     | covered (mocked responses) | Offline copy (`states.offlineBody`) is never exercised.                                                                                                                             |
| This week: where each button leads                    | `parent/this-week-destinations.spec.ts`: "awaiting_feedback button "Check in" leads to a real screen", and one test per other state                                                                                                                                                                                                                             | covered                    | Every card button leads to a real screen (check-in, pick, print); the writing/printed states assert there is no button.                                                             |
| This week with two children                           | `parent-screens-hardening.spec.ts`: "This week shows one card each, with the right step and the right link"                                                                                                                                                                                                                                                     | covered                    | Ordering of cards is not asserted (backend order is unspecified).                                                                                                                   |
| `/week/pick/<id>` pick one of three: happy path       | `parent/pick.spec.ts`: "from This week to the writing state, recorded by the backend" (request body, loop state, stored option and the `pick_made` loop event read back), "Back to the ideas leaves the confirm step and sends nothing"                                                                                                                         |
| Pick: double tap, repeat, conflict                    | same file: "tapping Yes twice quickly sends one request", "the API: the same pick twice is a no-op; a different pick afterwards is a clear 409", "a choice made on another device is explained, not overwritten"                                                                                                                                                |
| Pick: expired -> fresh ideas, allowance (max 2)       | same file: "expired -> Get fresh ideas -> new ideas -> pick one", "a model reply that fails the gate is repaired...", "the allowance: two sets of fresh ideas, then a plain message and no button", "an expired set at the cap says so..."                                                                                                                      |
| Pick: loading, errors, empty states                   | same file: loading (ideas, fresh ideas), error with Try again (load, save the choice, write fresh ideas), unknown child, still writing, check in first, already chosen                                                                                                                                                                                          |
| Pick: keyboard, 320px, axe, banned words              | same file: "choose and confirm without a pointer", "on a 320px-wide phone: nothing scrolls sideways in any state"; axe and `expectNoBannedWords` in every state                                                                                                                                                                                                 |
| `/week/check-in/<id>` quick check-in: UI              | `parent/check-in-quick.spec.ts`: "two taps and Send record the rating and workload", "the rating alone is enough; workload is optional", "a child with no finished week sees what to expect, not a form", "a failed send shows a plain message and keeps the choices", "loading shows while the week is fetched, and an unknown child is handled"               | covered                    | Loading skeleton while the check list loads is not asserted separately.                                                                                                             |
| Quick check-in: what is stored                        | `parent/check-in-recorded.spec.ts`: "Got it" + "Too little" / "Shaky" + "Just right" / "Lost it" + "Too much" (request body and the stored row read back from the API), "without a workload, none is stored"                                                                                                                                                    | covered                    | After Send the child's card still says "check in" (the seeded plan is not advanced by feedback: the loop automation that moves it is not built). No test asserts the card moves on. |
| Quick check-in: double tap                            | `check-in-recorded.spec.ts`: "Send fires one request even when tapped twice quickly"                                                                                                                                                                                                                                                                            | covered                    | Fixed in #211: an in-flight guard set before the request.                                                                                                                           |
| Quick check-in: keyboard only                         | `parent-screens-hardening.spec.ts`: "rate, choose workload and Send without a pointer"                                                                                                                                                                                                                                                                          | covered                    | Screen-reader announcements are only checked through axe, not a real screen reader.                                                                                                 |
| `/week/check-in/<id>/by-check`: UI                    | `parent/check-in-by-check.spec.ts`: "answer some, skip the rest, send: only the answers are recorded", "answering nothing cannot send and points to the quick rating", "a week with no check list falls back to the quick rating", "a failure loading the checks shows a plain message with a retry"                                                            | covered                    |                                                                                                                                                                                     |
| By-check: stored values and skip semantics            | `check-in-recorded.spec.ts`: "all three results are stored against the right checks; skipped ones are absent", "going back and changing an answer stores the last choice, and Skip never erases one", "a failed send keeps every answer and a retry records them"                                                                                               | covered                    | Whether stored results move the child's progress (`progress-summary`) is not asserted.                                                                                              |
| By-check: keyboard only                               | `parent-screens-hardening.spec.ts`: "the check-by-check cards answer, skip and send from the keyboard"                                                                                                                                                                                                                                                          | partial                    | No assertion on stored values in that test (the stored values are covered above).                                                                                                   |
| `/how-its-going` progress                             | `parent/progress.spec.ts`: "shows what the child has down, is working on and has coming up", "a child with no history sees what will appear and when", "no children shows an empty state with a way forward", "a failure gets a plain message and a retry that works", "the tab bar reaches it from This week"                                                  | covered                    | The "last four weeks" numbers are seeded, not produced by a real check-in.                                                                                                          |
| Progress with two children (picker)                   | `parent-screens-hardening.spec.ts`: "How it’s going has a child picker; each child shows only their own progress"                                                                                                                                                                                                                                               | covered                    |                                                                                                                                                                                     |
| 320px-wide phone, no sideways scroll                  | `parent-screens-hardening.spec.ts`: "A 320px-wide phone" x5: This week with every loop state, the quick check-in (before, chosen, done), the by-check card/review/done, How it's going with the picker, the empty and error states                                                                                                                              | covered                    | The legacy desktop pages are not checked at 320px.                                                                                                                                  |
| Accessibility (axe, WCAG A/AA)                        | `expectNoViolations` in every parent spec, in each state it visits                                                                                                                                                                                                                                                                                              | covered                    | Axe finds only machine-checkable issues.                                                                                                                                            |

## Login (`auth` project, phone, AUTH_REQUIRED=1)

Own backend (8184, fresh database) and own frontend build (3003); the other projects run with login
off. Each test makes its own account (real `python -m auth create-user`) and its own client
address (X-Forwarded-For), so lockout state never leaks between parallel tests. `auth/login.spec.ts`:
the login form is the first page (axe, banned words, autocomplete, focus); sign in lands on This
week; wrong password and unknown name give one message; show/hide; keyboard only; loading (button
disabled); error with Try again; deep link returns to the page; off-site `next` ignored; 401 JSON
without a cookie and `/api/health` open; stale cookie and a session ended on the server go back to
the login; Sign out; lockout after 4 wrong tries shows the calm wait and the right password works
after it (`AUTH_BACKOFF_SCALE=0.2`); 429 with Retry-After; an owner is not locked from another
address; a foreign Origin is refused. Backend rules (hashing, expiry, lockout math, route inventory,
CLI) are in `tests/test_auth.py`. Open-redirect variants (`%09`, `%0a`, `%0d`, `%5c`, `//`, full URL), the rightmost forwarded address, the busy message, 413 and no-echo 422 are covered too. `E2E_SKIP_AUTH=1` leaves this project and its servers out (CI runs them). Gap: the Secure cookie flag is only asserted in pytest.

## Admin panel and Admin link (`auth` project)

| Route / flow                                            | Spec: tests                                                                                                                                                                            | Status  | Missing                                          |
| ------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------- | ------------------------------------------------ |
| Admin link in the header, `/admin` panel, `/loop` guard | `auth/admin.spec.ts`: "a parent without admin sees no Admin link and is sent home from /admin and /loop", "an admin sees the Admin link, opens the panel and reaches the loop console" | covered | The link is not in the mobile tab bar by design. |
| Admin link with login off (operator is admin)           | `parent-shell.spec.ts`: "with login off the operator is the admin..."                                                                                                                  | covered |                                                  |
| `/api/loop-admin/*` for a non-admin                     | `auth/admin.spec.ts`: "the console API answers 404 to a non-admin"                                                                                                                     | covered |                                                  |
| Admin panel accessibility, 360px                        | `auth/admin.spec.ts`: "the admin panel is accessible and does not scroll sideways at 360px"                                                                                            | covered |                                                  |

## Creating an account (`auth` project)

| Route / flow                                           | Spec: tests                                                                                                                                                                                      | Status  | Missing                                                                       |
| ------------------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | ------- | ----------------------------------------------------------------------------- |
| Create an account, emailed code, signed in             | `auth/register.spec.ts`: "register, enter the emailed code and land on This week", "a wrong code says so and the right one still works", "a bad invite code gets a plain message and no account" | covered | Backend rules (single-use invites, attempts, expiry) are in the pytest suite. |
| "Send a new code"                                      | `auth/register.spec.ts`: "\"Send a new code\" confirms and mails another code"                                                                                                                   | covered | Reads the backend's `MAILER_OUTBOX` file; no real mail is sent.               |
| Sign in to an unverified account goes to the code step | `auth/register.spec.ts`: "signing in to an unverified account shows the code step"                                                                                                               | covered |                                                                               |
| Both new steps: accessibility, 360px                   | `auth/register.spec.ts`: "both new steps are accessible and do not scroll sideways at 360px"                                                                                                     | covered |                                                                               |

## Hosted-week printing (backend serves, the app proxies)

| Route / flow                                                                      | Spec: tests                                                                                                                                                                                                | Status  | Missing                                                                                 |
| --------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------- | --------------------------------------------------------------------------------------- |
| `GET /api/students/{id}/weekly-packets/{pid}/print` (packet) of a structured week | `print/hosted-week-print.spec.ts`: "the packet loads as HTML and holds every day’s worksheets", "the packet is the default document and equals ?doc=packet"                                                | covered | Worksheet bodies are checked by title and count, not question by question.              |
| `?doc=guide` teacher guide                                                        | same file: "the teacher guide has an answer key for each day, Monday to Friday"                                                                                                                            | covered | Answer correctness is not asserted.                                                     |
| `?doc=prep` prep sheet                                                            | same file: "the prep sheet lists every prep check"                                                                                                                                                         | covered |                                                                                         |
| First name only, no placeholder                                                   | same file: "<doc>: the child’s first name is used and no placeholder or last name shows" x3                                                                                                                | covered |                                                                                         |
| Fits at print width                                                               | same file: "<doc>: nothing overflows sideways at print width" x3 (816px, screen and print media)                                                                                                           | partial | No page-break or PDF rendering assertion (headless Chromium, no real printer).          |
| Errors                                                                            | same file: "an unknown packet is a 404", "another child cannot print this packet", "an unknown document name is rejected" (422), "a legacy packet has no teacher guide or prep sheet (404)"                | covered |                                                                                         |
| Legacy packet print (HTML artifacts on disk)                                      | `journeys/3-teach-the-week.spec.ts`: "the print route answers through the app's /api proxy" (accepts 200 or 404), "Print All opens the printable packet in a new tab"                                      | **gap** | No test renders a legacy packet that has real HTML artifacts; backend pytest covers it. |
| The parent print screen `/week/print/<id>`                                        | `parent/print-week.spec.ts` (M10.7): happy path through all three documents, mark printed, all-set card; double tap; not ready; printed; older week; deadline; loading; errors with retry; keyboard; 320px | **gap** | Not built (M10.7).                                                                      |

## Legacy desktop pages (the original app, journeys 1 to 5)

| Route / flow | Spec: tests | Status | Missing |
| --------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | ------------------- | ------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | ------- | --- |
| `/` redirect, page titles, no sideways scroll, header nav | `app-shell.spec.ts`: "/dashboard | /students | /plans | /progress loads with its own title and no horizontal scroll", "/ sends the parent to the dashboard", "every page is reachable from the header", "the current page is marked in the header" | covered | |
| `/students` add child | `journeys/1-onboard-a-student.spec.ts` 1.1: "the parent can always find "Add Student"", "...opens the "Add New Student" form", "the form asks for no ID (the server picks one) and flags a missing name", "the form flags a missing birthday", "the parent can back out with Cancel or Escape", "a valid child is created and shows up on the students list and the dashboard" | covered | |
| Edit / delete child | 1.2: ""Edit" opens the form pre-filled, with the ID locked", "saving a new name updates the list"; 1.3: ""Delete" asks for confirmation, and Cancel keeps the student", "confirming removes the student" | covered | |
| Dashboard card shows age-appropriate grade | 1.1 `test.fixme` | gap | Behavior does not exist (dashboard hard-codes grade 0). |
| `/dashboard` cards and stats | `journeys/5-keep-going.spec.ts` 5.1: "each child has a card with a "Generate Plan" action" | partial | Stat tiles are not asserted; three `test.fixme` (real-standard progress, "Worksheets Ready" counts, past weeks) are unbuilt behavior. |
| Generate a week (`POST /generate_weekly_plan`) | `journeys/2-plan-the-week.spec.ts` 2.1: "from the dashboard, "Generate Plan" produces a five-day week" (also asserts the stub saw 1 scaffold + 5 day calls and the usage ledger), "every day has real content - no generic fallback on Day 1 (#134)"; 2.1b: "a day with an unusable reply falls back to a generic lesson; the other days are untouched" | covered | |
| Duplicate generation warning (#137) | 2.1: "generating the same week twice warns instead of toasting success (#137)" | gap (known bug) | `test.fail`, #137 open. |
| `/plans` pending list and detail | 2.2 "has no pending card on the plans page"; 2.3: "the pending card summarises subject, grade, and number of days", "opening the card shows who, which week, subject, and grade", "each day reads as a lesson: focus, objective, procedure", "the detail view closes with Close, Escape, or a backdrop click" | covered | |
| Legacy feedback modal | `journeys/4-reflect-on-the-week.spec.ts` 4.1: "a week without feedback offers "Provide Feedback"", "submit stays disabled until both mastery and workload are rated", "the parent can back out with Cancel, Escape, or a backdrop click", "submitting moves the week to Completed, where it can be edited"; 4.2: ""Edit Feedback" reopens the form with the earlier ratings selected", "changing a rating and saving succeeds"; 4.3: "feedback older than three weeks shows a disabled "Feedback Submitted"" | covered | Stored values are not read back for the legacy modal (the parent check-ins are). |
| Legacy modal double click | 4.1: "double-clicking submit sends feedback once" | covered | Fixed in #211. |
| Feedback triggers next plans + notification | 5.2: "after feedback, three fresh plans are generated and the parent is notified", "after "Too Much" feedback, the next week asks for fewer activities" | covered | Mastered standards not re-taught: `test.fixme` (needs real standard ids). |
| `/progress` curriculum map | 4.4: "choosing a child and subject draws their curriculum map" | partial | Mastery colors on the map: `test.fixme` (needs real standard ids). Prune toggle and subject switching are not tested. |

## API endpoints behind the screens

| Endpoint | Exercised by | Status | Missing |
| ---------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------- | ------------------------------------------- | ---------------------------------------------------------------------------------------------------- | ------- | ---------------------- |
| `GET /this-week` | `this-week.spec.ts`, `this-week-destinations.spec.ts`, check-in specs (through the screens, real) | covered | No deadline fields (`pick_deadline`, `print_deadline`) are asserted. |
| `GET /students/{id}/weekly-packets/{pid}/checks` | `check-in-by-check.spec.ts`, `check-in-recorded.spec.ts` (screens, real) | covered | |
| `POST /students/{id}/weekly-packets/{pid}/feedback` (quick, by-check) | `check-in-recorded.spec.ts` (request body asserted, row read back) | covered | |
| `GET /students/{id}/weekly-packets/{pid}/feedback` | `storedFeedback()` helper in every recorded-values test | covered | |
| `POST .../feedback` (legacy mastery form) | journeys 4.1, 4.2, 5.2 | covered | |
| `GET /students/{id}/progress-summary` | `progress.spec.ts` (screen, real, seeded) | covered | Never produced by a real check-in. |
| `GET .../print?doc=packet                                                                            | guide                                                                                             | prep` | `print/hosted-week-print.spec.ts` | covered | see the printing table |
| `GET /students`, `POST /students`, `PUT                                                              | DELETE /student/{id}` | journeys 1.1 to 1.3, `createStudent` helper | covered | |
| `POST /generate_weekly_plan` | journeys 2.1, 2.1b | covered | |
| `GET /students/{id}/weekly-packets` (+ detail) | `/plans` journeys | covered | |
| `GET /students/{id}/weekly-packets/{pid}/worksheets`, `GET /students/{id}/worksheet-artifacts/{aid}` | nothing | **gap** | Worksheet manifest and artifact download are not exercised in a browser; backend pytest covers them. |
| `GET /curriculum/graph/{subject}`, `GET /students/{id}/progress-map/{subject}` | journey 4.4 (draws a node) | partial | |
| `GET /system/options`, `/version`, `/health` | indirectly (modal options, footer, readiness polling) | partial | No direct assertion. |
| `GET /students/{id}/week-plan`, `POST .../week-plan/pick`, `POST .../week-plan/regenerate` | `parent/pick.spec.ts` (screens and direct API calls, real, outlines from the LLM stub) | covered | The week author and print endpoints stay a gap (stream A/D). |
| Week authoring, print endpoints for the new loop | nothing | **gap** | Not built (M10.7, stream A/D). |

## Fixme and fail markers (all of them)

| Marker                              | Where        | Why                                              | Unblocked by                            |
| ----------------------------------- | ------------ | ------------------------------------------------ | --------------------------------------- |
| `test.fixme` dashboard grade        | journeys 1   | dashboard hard-codes grade 0                     | a grade-from-birthday feature (no card) |
| `test.fail` #137                    | journeys 2.1 | duplicate generation silently accepted           | fix #137                                |
| `test.fixme` Mastered shows on map  | journeys 4.4 | seed packets use a synthetic standard            | seeding real standard ids               |
| `test.fixme` real-standard progress | journeys 5.1 | feedback is synthetic ("overall")                | real standard ids in feedback           |
| `test.fixme` "Worksheets Ready"     | journeys 5.1 | global stat over a shared DB, behavior not built | a per-family stats endpoint             |
| `test.fixme` past weeks             | journeys 5.1 | no design                                        | a design for past weeks                 |
| `test.fixme` Mastered not re-taught | journeys 5.2 | stub reply does not depend on taught standards   | real standard ids and a smarter stub    |

## How to run

```bash
cd frontend
npm ci && npx playwright install chromium
npx playwright test                     # everything (builds the app once, ~3 minutes)
npx playwright test e2e/print           # one folder
npx playwright test --project=mobile    # one project
E2E_DEV_SERVER=1 npx playwright test e2e/parent/progress.spec.ts   # dev server, quick iteration
```

The suite builds the frontend (`next build`) into `.next-e2e-<port>` and serves it with
`next start`, starts its own backend and LLM stub, and wipes its database at the start of every run.
Ports and the database path are overridable so several worktrees can run at once without
colliding: `E2E_BACKEND_PORT` (8182), `E2E_FRONTEND_PORT` (3002), `E2E_LLM_STUB_PORT` (8183) and
`PLAYWRIGHT_DB_FILE` (`/tmp/playwright-test.db`). On a failure, `console` output contains a
`TRACE-API` block with every `/api` call the page made and how long it took.

## Stability evidence

Measured on a loaded 8-core Mac (system load average 90 to 190 from other work during the
session), `CI=` unset, `--retries=0`, default workers, all 189 tests (182 pass, 7 skip):

| Run                        | Result                                        | Wall time |
| -------------------------- | --------------------------------------------- | --------- |
| 1                          | 182 passed, 7 skipped                         | 134 s     |
| 2                          | 182 passed, 7 skipped                         | 138 s     |
| 3                          | 182 passed, 7 skipped                         | 129 s     |
| 4                          | 182 passed, 7 skipped                         | 125 s     |
| 5                          | 182 passed, 7 skipped                         | 117 s     |
| journeys `--repeat-each=3` | 102 passed, 18 skipped (the fixme markers x3) | 78 s      |

Root causes found (not papered over; no retries and no global timeout change):

1. **`next dev` under load.** The dev server compiles pages on first hit and, with the machine
   busy, aborted page loads (`net::ERR_ABORTED`) and starved requests. With 8 CPU burners the dev
   server run failed 3 tests and took 4.4 min; the same tests on a production build passed in 1.9
   min. The suite now builds and serves with `next start`.
2. **Idle keep-alive sockets closing at exactly 5 s.** uvicorn and the Node stub server both close
   idle connections after 5 s. A client that reuses a socket at that instant gets `ECONNRESET`: this
   is the "Backend proxy error: fetch failed" in the web server log, and it failed an unrelated
   test at teardown once (stub `/__requests`). Both now keep sockets for 120 s.
3. **A 5 s assertion on a legitimately slow operation.** `POST /generate_weekly_plan` is
   synchronous (a scaffold call, five lesson calls, rendering). The backend's own request logs show
   3 to 14 s per generation on a busy machine, and two journeys fire it at the same moment. The
   specs now wait for the response (90 s) and then assert the dialog closes.
4. **Fixed ids and names under `--repeat-each`.** Rounds share one database, so a second round saw
   the first round's weeks, feedback and rename. Journey children now get a per-round id and name
   (`repeatIdentity`); round 0 is unchanged.
5. **Cross-run collisions.** Ports 8182/3002/8183, the pid and log files and the build directory
   were shared by every worktree on the machine, so two agents running the suite killed each
   other's servers. All are now overridable and the pid/log files are named by port.

Also found and kept as `test.fail` rather than hidden: the double-submit bug (issue #211, since
fixed), and the `/week/print` 404 (M10.7). The `/week/pick` marker was flipped by M10.6.
