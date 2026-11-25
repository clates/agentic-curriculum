# Family accounts: isolation, permissions, registration, onboarding, dashboard

Date: 2026-11-25. Status: E0 and E5 approved; E1 to E4 wait on the decisions on the planning
board (Hosted Loop Board, Today tab) and will be added here when they are answered.

## Why

The hosted app is about to take its first families other than the owner's. Today every signed-in
account sees every child, accounts are made from the server's command line, and the loop console is
open to anyone signed in. Before anyone else signs up, each family must see only its own children,
and the operator tools must belong to admins only.

By the end of the day: a new family registers from the sign-in page, onboards a first child, sees
that child's week on a family dashboard, and can add more children. The owner and the `claude`
account get an admin panel that leads to the loop console.

## Goals

- **E0 Isolation.** Every request acts for exactly one family, the signed-in user's. Another
  family's data is never readable or writable, and a request for it can't tell whether it exists.
- **E5 Permissions.** A small, extensible permission system. The first permission is `admin`, held
  by the owner and the `claude` account. It gates the loop console and the new admin panel.
- **E1 Registration**, **E2 First-child onboarding**, **E3 Family dashboard (small first version)**
  and **E4 Add a child**: see "Pending" below.

## Non-goals

- Several adults in one family (invites to a second parent). Each family has one account for now.
- Billing, plan limits or entitlements.
- Retiring the older pages (Plans, Progress). They keep working, scoped to the family.
- The standards map visualization (shelved for a larger session).

## Anti-goals

- A route that forgets the family check and still works. The design must make that fail a test.
- A "forbidden" response that confirms another family's id exists.
- Changing anything for self-hosters who run with login off.

## Constraints

- The schema already has `family_id` on every tenant table (migration 0002), backfilled to
  `fam_local`. The loop tables (`week_plan`, `jobs`, `week_documents`) already filter by it.
  Routes in `src/main.py` hard-code `LOCAL_FAMILY_ID = "fam_local"`; `src/loop_admin.py` uses a
  module-level `FAMILY`.
- `app_user.family_id` exists (migration 0011). Both production accounts (`clates`, `claude`) are in
  `fam_local`, with two children: the owner's real child and `demo_child`.
- `student_profiles.student_id` is the primary key and is global. The old add-student form lets the
  parent type it.
- Login is off by default (`AUTH_REQUIRED` unset): local dev, CI's main E2E suite and self-hosting.
  The `auth` Playwright project runs with login on.

## Approaches considered

**Isolation.**
1. *One request-level dependency that resolves the family, used by every route; a route-inventory
   test enforces it* (chosen). One place decides the family, and the test fails when a new route
   doesn't ask for it.
2. *Filter inside each query, no shared dependency.* Easy to forget on a new route and nothing
   catches it.
3. *A database per family.* Strongest separation, but the scheduler, worker and loop console all
   work across families, and backups multiply. Too heavy for this stage.

**Permissions.**
1. *A `user_permission` table of (user, permission) rows* (chosen). Adding a permission is a row,
   not a schema change, which matters because more are coming.
2. *An `is_admin` column on `app_user`.* Simplest today, a migration for every future permission.
3. *Roles that bundle permissions.* Premature with one permission and two holders.

## Design: E0 isolation

- `current_family(request) -> str` in `src/auth/web.py`: with login off it returns `fam_local`;
  with login on it returns `request.state.user.family_id` (the global gate has already resolved the
  session). Routes take `family: str = Depends(current_family)`.
- An ownership helper, `owned_student(conn, family, student_id)`, raises 404 (`"Student not found"`,
  the existing message) when the student isn't in the family. A student is the family's when the
  family has its `student_profiles` row **or** any `weekly_packets` row for it, because older flows
  saved packets without a profile row (migration 0002's note). *(Builder-check call.)* Packet, worksheet, artifact,
  feedback, check, print-info and progress routes call it first, and packet lookups also filter on
  `weekly_packets.family_id`.
- `GET /students` lists only the family's children. `POST /generate_weekly_plan` checks that the
  body's `student_id` belongs to the family. `GET /this-week`, pick, regenerate, printed and the
  feedback hooks pass the family instead of `LOCAL_FAMILY_ID`.
- Standards data (`/curriculum/graph/{subject}`, `/system/options`) is shared reference data and
  stays unscoped.
- **Server-generated child ids.** New children get `stu_` plus 10 random lowercase base32
  characters. With login on, a client-supplied id is ignored. With login off it is still accepted,
  so self-hosters' scripts keep working. The add-child form drops its ID field. Existing ids keep
  working.
- **Tests.** `tests/test_family_isolation.py` creates two families with a user each, seeds a child,
  packet, feedback and week plan for family A, then calls every non-public, non-admin route as
  family B with A's ids and expects 404 (or an empty list for list routes). The route-inventory test
  gains a rule: every route is public or depends on `current_family`; admin-only routes also depend
  on `require_permission`.

## Design: E5 permissions and the admin panel

- Migration `0012_permissions.sql`: `user_permission(user_id REFERENCES app_user(id) ON DELETE
  CASCADE, permission TEXT NOT NULL CHECK (permission IN ('admin')), granted_at, PRIMARY KEY
  (user_id, permission))`. The CHECK list grows as permissions are added.
- `src/auth/store.py`: `permissions(conn, user_id)`, `grant(conn, username, permission)`,
  `revoke(conn, username, permission)`. The CLI gains `python -m auth grant <username> <permission>`
  and `revoke`, and `list-users` shows permissions.
- `require_permission("admin")` dependency: with login off it allows (the operator is the only
  user); with login on, a user without the permission gets **404**, so the console's existence
  isn't revealed. Applied to the whole `/loop-admin` router.
- `GET /auth/me` adds `permissions: [...]`. With login off it returns `["admin"]`: the operator is
  the only user, so the Admin link shows and `/loop` keeps working for self-hosters and the main
  E2E suite unchanged. *(Builder-check call.)*
- Frontend: a new `/admin` page with one card, "Loop console", linking to `/loop`. The navigation
  shows an "Admin" link only when `me.permissions` includes `admin`. `/admin` and `/loop` send
  anyone else to the home page.
- Admin-only routes also depend on `current_family`: the module-level `FAMILY` in
  `src/loop_admin.py` goes away and the console acts for the admin's own family. No ordinary route
  gives admins a bypass. Seeing other families is only through the console, and only if D1 says
  so. *(Builder-check call.)*
- **Rollout.** The migration is additive. After deploy, run `grant clates admin` and
  `grant claude admin` on the server, then check the panel appears for both.
- **Tests.** pytest for the store, CLI and dependency (admin, non-admin, login off). In the `auth`
  E2E project, a non-admin gets 404 from `/loop-admin/*`, sees no Admin link and is redirected from
  `/admin`, and an admin sees the panel and reaches the console.

## Pending (answers come from the board)

- **D1** Whose families an admin sees in the loop console (E5.4).
- **D2** Who can register (invite code, open, or approval).
- **D3** Sign-in identity. Email now works through Proton SMTP (`homeschool@chrislates.com`), so
  email plus a 6-digit confirmation code is possible.
- **D4** How the math and language arts grades are used.
- **D5** Where the `claude` account lives (its own test family, or the owner's).
- **D6** How much of the family dashboard lands today.

## Left to the builder

- Exact module placement of the ownership helper (a new `src/tenancy.py` is fine).
- Error copy, as long as 404 bodies don't differ between "doesn't exist" and "not yours".
- Whether `owned_student` reuses an open connection or opens its own.
