# Family isolation and admin permissions Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Each signed-in family sees only its own children and weeks, and an `admin` permission
(held by `clates` and `claude`) gates the loop console behind a new admin panel.

**Architecture:** Two FastAPI dependencies in `src/auth/web.py` (`current_family`,
`require_permission`) and one in a new `src/tenancy.py` (`owned_student_id`) carry all the rules.
Routes declare them; storage functions mostly stay as they are. A route-inventory test fails if a
route skips them, and a two-family test calls every route with the other family's ids.

**Tech Stack:** FastAPI, SQLite migrations (`src/migrations/NNNN_*.sql`), pytest, Next.js 16 /
React 19, Playwright.

**Spec:** `docs/superpowers/specs/2026-11-25-family-accounts-design.md` (sections E0 and E5).

## Global Constraints

- Another family's data answers **404** with the same body as a missing record (`"Student not
  found"`, `"Packet not found"` and so on). Never 403.
- Login off (`AUTH_REQUIRED` unset): family is `fam_local`, every permission is granted, and
  client-supplied student ids are still accepted. Nothing changes for self-hosters or the main E2E
  suite.
- Login on: new student ids are server-generated, `stu_` plus 10 lowercase base32 characters
  (`[a-z2-7]{10}`). A client-supplied id is ignored.
- A student is the family's when `student_profiles` has `(family_id, student_id)` **or**
  `weekly_packets` has a row for that student with that `family_id`.
- Permissions are rows in `user_permission`; the only value today is `admin`.
- Admin-only routes also depend on `current_family`. No ordinary route gives admins a bypass.
- Standards routes (`/curriculum/graph/{subject}`, `/system/options`) stay unscoped.
- Python: black and ruff, 100-character lines. Frontend: Prettier, `npm run lint:copy`.

## Review Focus

1. **A student id that exists in another family, used on a write route** (PUT/DELETE student,
   POST feedback, pick, regenerate, printed): must 404 and change nothing. Task 4's isolation test
   checks the database is unchanged afterwards, not just the status.
2. **Creating a student with login on while sending a `student_id` that already belongs to another
   family**: must succeed with a fresh `stu_` id, and must not reveal or touch the existing one.
   Task 4 tests it.
3. **A session that outlives a permission revoke**: permissions are read per request, so a revoke
   takes effect on the next request without signing out. Task 2 tests revoke-then-request.
4. **The main E2E suite with login off still reaching `/loop` and seeing the Admin link**: Task 6
   runs the existing loop console specs unchanged.
5. **`/loop-admin` actions on a student of another family by an admin** (`seed`, `start-week`,
   `reset`): 404 and nothing written. Task 5 tests it.

---

### Task 1: Families and permissions in the store

**Files:**
- Create: `src/migrations/0012_permissions.sql`
- Modify: `src/auth/store.py` (lift the `fam_local`-only rule in `create_user`; add family and permission functions)
- Modify: `src/auth/__main__.py` (new `grant`, `revoke` subcommands; `--family` accepts any existing family)
- Test: `tests/test_auth_permissions.py`

**Interfaces:**
- Produces:
  - `store.create_family(conn, name: str) -> str` returns a new `fam_` + 12 hex id (inserts into `family`).
  - `store.create_user(conn, username, password, family_id=DEFAULT_FAMILY) -> User | None`, which now accepts any existing family and keeps raising `UserError("No such family: ...")` for unknown ones.
  - `store.PERMISSIONS = frozenset({"admin"})`
  - `store.permissions(conn, user_id: str) -> frozenset[str]`
  - `store.grant(conn, username: str, permission: str) -> bool` returns False if the user is unknown, raises `UserError` for an unknown permission, and is idempotent.
  - `store.revoke(conn, username: str, permission: str) -> bool`
  - CLI: `python -m auth grant <username> <permission>`, `python -m auth revoke <username> <permission>`. Each exits 1 with a message when the user is unknown.

- [ ] **Step 1: Write the failing tests** in `tests/test_auth_permissions.py` (use the temp-DB fixtures `tests/test_auth.py` uses):
  - `test_create_family_and_user_in_it`: `fid = create_family(conn, "Rivera")`, then `create_user(conn, "ana", PW, fid).family_id == fid`.
  - `test_unknown_family_is_refused`: `create_user(..., "fam_nope")` raises `UserError`.
  - `test_grant_revoke_and_read`: grant `admin` gives `permissions() == {"admin"}`; a second grant is still one row; revoke gives an empty set; granting `"root"` raises `UserError`; granting to an unknown user returns False.
  - `test_permissions_vanish_with_the_user`: deleting the `app_user` row removes the permission rows (FK cascade).
  - `test_cli_grant_and_revoke`: run `python -m auth grant ana admin` via `subprocess` with `CURRICULUM_DB_PATH`; exit 0, the row exists; an unknown user exits 1.
- [ ] **Step 2: Run** `venv/bin/python -m pytest tests/test_auth_permissions.py -q`. Expected: FAIL (`create_family` undefined).
- [ ] **Step 3: Write the migration:**

```sql
CREATE TABLE user_permission (
    user_id TEXT NOT NULL REFERENCES app_user(id) ON DELETE CASCADE,
    permission TEXT NOT NULL CHECK (permission IN ('admin')),
    granted_at TEXT NOT NULL,
    PRIMARY KEY (user_id, permission)
);
```

  Then implement the store functions and the CLI subcommands. Remove the `if family_id != DEFAULT_FAMILY` block in `create_user`.
- [ ] **Step 4: Run** the new tests plus `tests/test_auth.py`. Expected: PASS. If a test in `test_auth.py` asserts the old `fam_local`-only refusal, update it to the new rule (unknown family refused).
- [ ] **Step 5: Commit** `feat(auth): families and a user_permission table, with grant and revoke`.

### Task 2: Request dependencies for family and permission

**Files:**
- Modify: `src/auth/web.py`
- Test: `tests/test_auth_permissions.py` (add to the same file)

**Interfaces:**
- Consumes: `store.permissions` (Task 1).
- Produces:
  - `current_family(request: Request) -> str`: `"fam_local"` when `auth_required()` is false, otherwise `request.state.user.family_id`.
  - `require_permission(permission: str) -> Callable` returns a dependency that, with login on and the user lacking the permission, raises `HTTPException(404, "Not Found")`. With login off it allows.
  - `user_permissions(request: Request) -> frozenset[str]`: `{"admin"}` with login off; otherwise read from the store on every request.
  - `GET /auth/me` adds `"permissions": sorted(list)` to both shapes, so login off gives `{"auth_required": false, "user": null, "permissions": ["admin"]}`.

- [ ] **Step 1: Write the failing tests:**
  - `test_me_reports_permissions_when_login_off`: `/auth/me` permissions are `["admin"]`.
  - `test_me_reports_permissions_when_login_on`: a non-admin gets `[]`; after `grant`, `["admin"]`.
  - `test_revoke_takes_effect_on_the_next_request`: an admin route answers 200, then after revoke and the same cookie, 404.
  - `test_current_family_follows_the_session`: a throwaway route in a test app, `Depends(current_family)`, returns the user's family with login on and `fam_local` with login off.
- [ ] **Step 2: Run them.** Expected: FAIL.
- [ ] **Step 3: Implement** the three functions and the `/auth/me` change in `src/auth/web.py`.
- [ ] **Step 4: Run** `tests/test_auth_permissions.py tests/test_auth.py`. Expected: PASS.
- [ ] **Step 5: Commit** `feat(auth): current_family and require_permission dependencies; /auth/me lists permissions`.

### Task 3: The ownership check

**Files:**
- Create: `src/tenancy.py`
- Test: `tests/test_tenancy.py`

**Interfaces:**
- Consumes: `current_family` (Task 2).
- Produces:
  - `student_in_family(conn, family_id: str, student_id: str) -> bool`, using the profile-or-packet rule from Global Constraints.
  - `owned_student_id(student_id: str, family: str = Depends(current_family)) -> str`: a path dependency that opens its own connection (`db_utils.get_db_path()`), raises `HTTPException(404, "Student not found")` when the student isn't the family's, and returns the id.
  - `new_student_id() -> str`, matching `^stu_[a-z2-7]{10}$` (use `secrets.token_bytes` with base32).

- [ ] **Step 1: Write the failing tests:** a profile row in A is owned by A, not by B; a packet-only student in A is owned by A; an unknown id is owned by nobody; `new_student_id()` matches the pattern and 1,000 calls are unique.
- [ ] **Step 2: Run them.** Expected: FAIL.
- [ ] **Step 3: Implement** `src/tenancy.py`.
- [ ] **Step 4: Run them.** Expected: PASS.
- [ ] **Step 5: Commit** `feat: tenancy helpers (student_in_family, owned_student_id, new_student_id)`.

### Task 4: Scope every parent route to the family

**Files:**
- Modify: `src/main.py` (every route with a `student_id`, plus `/students`, `/this-week`, `/generate_weekly_plan`; remove `LOCAL_FAMILY_ID` uses)
- Modify: `src/db_utils.py`: `list_students(family_id: str | None = None)` filters when given; `create_student(student_id, metadata, plan_rules, family_id: str = "fam_local")` writes `family_id`
- Modify: `frontend/app/students/page.tsx` (the create form drops the ID field; edit mode shows the id read-only)
- Test: create `tests/test_family_isolation.py`; modify `tests/test_auth.py` (route inventory)

**Interfaces:**
- Consumes: `current_family` (Task 2), `owned_student_id`, `new_student_id`, `student_in_family` (Task 3).
- Produces: `CreateStudentRequest.student_id: str | None = None`. With login on, or when the id is omitted, the server uses `new_student_id()`. `POST /students` returns the stored id.

- [ ] **Step 1: Write the failing isolation test.** Fixtures: login on, families A and B with one user each (`create_family`, `create_user`), and for A a profile, a legacy packet with feedback, a structured week, and a `week_plan` (reuse `tests/factories.py` and the `scripts/e2e_seed.py` builders). Tests:
  - `test_family_b_cannot_read_family_a`: for every GET route whose path has `{student_id}`, B with A's ids gets 404. `/students` and `/this-week` as B contain none of A's ids.
  - `test_family_b_cannot_write_family_a`: PUT and DELETE `/student/{id}`, POST feedback, `/week-plan/pick`, `/week-plan/regenerate`, `/week-plans/{plan}/printed`, and `/generate_weekly_plan` with A's id all answer 404. Snapshot `student_profiles`, `weekly_packets`, `packet_feedback`, `week_plan` and `jobs` before and after; they must be equal.
  - `test_family_a_still_works`: the same calls as A succeed (200, 201 or 204).
  - `test_new_ids_are_generated_with_login_on`: POST `/students` as B with `student_id` set to A's id answers 201 with a fresh `stu_` id, and A's row is unchanged.
  - `test_client_ids_still_work_with_login_off`: with login off, POST with `student_id: "kid1"` stores `kid1`.
- [ ] **Step 2: Extend the route-inventory test** in `tests/test_auth.py`: `test_every_route_declares_its_family`. Walk `route.dependant` recursively; every APIRoute whose path is not in `PUBLIC_PATHS` and doesn't start with `/auth/`, `/curriculum/`, or equal `/system/options`, must reach `current_family`; every path containing `{student_id}` must reach `owned_student_id`.
- [ ] **Step 3: Run both.** Expected: FAIL.
- [ ] **Step 4: Implement.** Replace `student_id: str` path parameters with `student_id: str = Depends(owned_student_id)`. Add `family: str = Depends(current_family)` where a family is passed on (this-week, printed, pick, regenerate, the feedback hooks' `loop_integration.on_feedback`, `/students`, create). Check `request.student_id` with `student_in_family` in `/generate_weekly_plan`. Drop the ID input from the add-child form.
- [ ] **Step 5: Run** the full backend suite: `venv/bin/python -m pytest tests/ -q`. Expected: all pass. Existing tests run with login off, so `fam_local` and client ids behave as before.
- [ ] **Step 6: Commit** `feat: every parent route acts for the signed-in family; server-generated child ids`.

### Task 5: Loop console is admin-only and family-aware

**Files:**
- Modify: `src/loop_admin.py` (router gains `dependencies=[Depends(require_permission("admin"))]`; module-level `FAMILY` removed; each route takes `family: str = Depends(current_family)` and passes it to the helpers that used `FAMILY`)
- Modify: `src/loop_integration.py` only if a helper there still reads the module constant on the console's path
- Test: `tests/test_loop_admin.py` (add tests)

**Interfaces:**
- Consumes: `require_permission`, `current_family` (Task 2), `student_in_family` (Task 3).

- [ ] **Step 1: Write the failing tests:**
  - `test_console_is_404_for_non_admins_with_login_on`: every `/loop-admin/*` route (GET and POST) answers 404 for a signed-in non-admin.
  - `test_console_acts_for_the_admins_family`: an admin in family B sees only B's children in the overview, and a student id from A on `start-week` or `reset` answers 404 with no `week_plan` or `jobs` rows written.
  - The existing loop-admin tests (login off) pass unchanged.
- [ ] **Step 2: Run them.** Expected: FAIL.
- [ ] **Step 3: Implement.**
- [ ] **Step 4: Run** `tests/test_loop_admin.py tests/test_auth.py tests/test_family_isolation.py`. Expected: PASS.
- [ ] **Step 5: Commit** `feat: loop console requires admin and acts for the admin's own family`.

### Task 6: Admin panel and the Admin link

**Files:**
- Create: `frontend/app/admin/page.tsx` (title "Admin"; one card: heading "Loop console", one sentence "Drive any child's week through each step of the loop.", a link to `/loop`)
- Create: `frontend/lib/useMe.ts`: `useMe()` returns `{ data: { auth_required: boolean; user: { username: string } | null; permissions: string[] } }` via TanStack Query, key `['me']`
- Modify: `frontend/components/parent/ParentShell.tsx` (an "Admin" link in the header, beside sign-out, only when `permissions` includes `admin`; not in the mobile tab bar)
- Modify: `frontend/app/loop/page.tsx` and the admin page (client guard: when `auth_required && !permissions.includes('admin')`, `router.replace('/')`)
- Modify: `frontend/lib/copy.ts` (new strings under `admin`); the `frontend/e2e/fixtures/auth.ts` helper `grant(username, permission)` via `execFileSync` like `createAccount`
- Test: create `frontend/e2e/auth/admin.spec.ts`

- [ ] **Step 1: Write the failing E2E tests** in the `auth` project:
  - `a parent without admin sees no Admin link and is sent home from /admin and /loop`
  - `an admin sees the Admin link, opens the panel and reaches the loop console`
  - `the console API answers 404 to a non-admin` (`request.get('/api/loop-admin/overview')`)
  - One axe check on `/admin`, and no sideways scroll at 360px (copy the pattern from `e2e/loop/console.spec.ts`).
- [ ] **Step 2: Run** `cd frontend && npx playwright test --project=auth e2e/auth/admin.spec.ts`. Expected: FAIL.
- [ ] **Step 3: Implement.**
- [ ] **Step 4: Run** the full E2E suite: `npm run test:e2e`. Expected: all pass, with the loop console specs (login off) unchanged. Then `npm run type-check`, `npx prettier --check` on the changed files, and `npm run lint:copy`.
- [ ] **Step 5: Commit** `feat(frontend): admin panel with the loop console, shown only to admins`.

### Task 7: Docs and rollout

**Files:**
- Modify: `docs/reference/login.md` (Commands table: `grant`, `revoke`; a "Permissions" section; the Families section now says each account sees only its family)
- Modify: `docs/how-to/manage-accounts.md` (a "Make someone an admin" section)
- Modify: `docs/explanation/login-and-https.md` (replace "Why every account sees everything" with how families are separated, and why other families get 404 rather than 403)

- [ ] **Step 1: Update the three pages** (each stays its own Diátaxis kind).
- [ ] **Step 2: Run** the link check: `python3 $CLAUDE_JOB_DIR/tmp/linkcheck.py` from the repo root, or any relative-link check. Expected: 0 problems.
- [ ] **Step 3: Commit** `docs: families, permissions and the admin panel`.
- [ ] **Step 4: After merge and deploy (operator step, not code):** on the server, `docker compose --env-file .deploy.env exec -u appuser app python -m auth grant clates admin` and the same for `claude`. Sign in as each and confirm the Admin link and the console.
