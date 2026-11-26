# Family accounts: isolation, permissions, registration, onboarding, dashboard

Date: 2026-11-25. Status: E0 and E5 shipped (PR #240). E1 to E4, E5.4 and E0.5 designed below from
the board decisions D1 to D6, accepted by the owner as Claude's recommended defaults.

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

## Decisions (from the board, accepted 2026-11-25)

- **D1** Admins see every family in the loop console; each look at another family's data is
  recorded in `audit_log`.
- **D2** Registration needs an invite code.
- **D3** Email and password, confirmed with a 6-digit code sent from `homeschool@chrislates.com`
  (Proton SMTP, already configured on the server).
- **D4** Math skills are picked at the child's math grade; every other subject (English, Science,
  History, Computer Science) at the language arts grade.
- **D5** The `claude` account moves to its own test family.
- **D6** Dashboard v1: each child's status, past weeks, and simple coverage bars. The standards map
  waits for a later session.

## Design: E1 registration (invite code + email code)

- **Mailer.** A small `src/mailer.py` with `send(to: str, subject: str, body: str)`, using the
  existing `SMTP_*` settings (STARTTLS on 587). `job_alerts` switches to it. With `SMTP_HOST`
  unset (dev, CI, self-hosters) it logs the message instead of sending, and tests capture it.
- **Invite codes.** Migration `0013_invites.sql`: `invite(code_hash TEXT PRIMARY KEY, created_by
  TEXT REFERENCES app_user(id) ON DELETE SET NULL, created_at, expires_at, used_at, used_by)`.
  Codes are 10 characters from an unambiguous alphabet, stored hashed (SHA-256), valid 14 days,
  single use. Made by `python -m auth invite [--days N]` and by an admin-panel card "Invite a family"
  (`POST /admin-api/invites`, admin only), both showing the code once.
- **Accounts.** `app_user.username` holds the email (lower-cased, validated as an address) for new
  families; existing accounts keep their usernames. Migration adds `app_user.email_verified_at`
  (NULL for unverified; backfilled to now for existing accounts). Login refuses an unverified
  account with the same "invalid credentials" response as a wrong password.
- **Flow.**
  1. `POST /auth/register {email, password, family_name, invite_code}`: checks the invite, the
     password rules (12+ characters) and that the email is free; creates the family, the user
     (unverified) and consumes the invite in one transaction; emails a 6-digit code (stored hashed in
     the existing `auth_challenge` table, purpose `verify_email`, 15 minutes, 5 attempts). Answers
     202 with no session. An email that already has an account gets the same 202 and no new account
     (no account enumeration); the invite isn't consumed in that case.
  2. `POST /auth/verify {email, code}`: on a match, marks the user verified, consumes the code and
     signs the user in (session cookie). Wrong codes count toward the challenge's 5 attempts.
  3. `POST /auth/resend {email}`: a new code if the last is over 60 seconds old; same answer
     whether or not the account exists.
  - All three are public paths, rate-limited per address with the existing lockout machinery, and
    use the existing Origin check.
- **Frontend.** The sign-in page gains "Create an account" (family name, email, password twice,
  invite code), then a "Check your email" step with a 6-digit code field and "Send a new code".
  Successful verification lands on the first-run welcome (E2).
- **Tests.** API: invalid, used or expired invite; duplicate email (same 202, nothing created);
  wrong code five times locks the challenge; verify signs in; an unverified account can't sign in;
  no code or password appears in logs. E2E in the `auth` project: register, read the code from the
  test mailer, verify, land on welcome.

## Design: E5.4 loop console across families, E0.5 the `claude` account

- The console's overview lists every family's children, grouped by family name. Actions,
  feed-forward and review act on the child's own family.
- The console resolves a child with `admin_student(conn, student_id) -> (family_id, ...)`, used only
  under `require_permission("admin")`. No ordinary route changes.
- Every console request about a child outside the admin's own family writes one `audit_log` row:
  `family_id` (the child's), `user_id`, `action` (`console.view` or `console.<action>`),
  `target` (the student id), `created_at`. No names or child data in the row.
- **E0.5.** After deploy, an operator step sets `claude`'s `family_id` to a new family "Claude test
  family". Only that one row changes; `demo_child` stays in the owner's family. The script is
  shown to the owner before it runs.

## Design: E2 onboarding and E4 add a child

- **Child profile.** A child has first name, interests (a short list), approximate math grade,
  language arts grade (K to 8, K stored as 0) and optional notes. They are stored in
  `metadata_blob` as `name`, `interests`, `math_grade`, `la_grade`, `notes`, plus `grade_level` set
  to the language arts grade so existing readers keep working.
- **Planner.** `model_context` exposes `grade_for(subject)`: `math_grade` for Math, else
  `la_grade`, else the existing rule. The candidate selector compares each skill to its own
  subject's grade, and the standards loader loads the span around both grades. The model sees both
  grades.
- **Form.** One shared form component used by the welcome page and by "Add a child". It carries a
  short note: "These are starting points. We'll calibrate after the first few activities." and the
  existing plain note that an AI service reads what you write. Saving creates the child and starts
  their first week (`loop_integration.start_week` for the family), then shows This week.
- **First run.** A signed-in family with no children is sent to `/welcome`, which explains the
  weekly rhythm in two sentences and shows the form.
- **Add a child (E4).** A button on the family dashboard opens the same form.

## Design: E3 family dashboard (v1)

- The This week page is the family dashboard. Each child's card keeps its status and next action
  and gains links to "Past weeks" and "How it's going".
- **Past weeks.** `/children/[studentId]` lists the child's weeks, newest first, with title, dates
  and status, and opens the student packet, teacher guide and prep sheet for each.
- **Coverage bars.** On the same page, one bar per subject the child has been taught: skills solid,
  shaky and still to come, from the progress data. Plain words, no standard codes.
- The full standards map is out of scope.

## Builder-check calls (Claude's, 2026-11-25)

1. **Unverified accounts.** Registering again with an email whose account is still unverified
   replaces that pending account (new password and family name), consumes the new invite and sends
   a fresh code. Signing in with the correct password to an unverified account answers
   `403 {"detail": "email_not_verified"}` and sends a fresh code (subject to the resend limit); the
   page moves to the code step. A wrong password still gets the ordinary "invalid credentials", so
   nothing is revealed without the password. Pending accounts aren't cleaned up automatically yet.
2. **First-run redirect** to `/welcome` applies only with login on. Self-hosters and the main E2E
   suite are unchanged.
3. **Audit rows.** One row per console request that shows or changes another family's data:
   `console.overview` once per overview load (detail: the number of other families shown), and
   `console.view` or `console.<action>` per child request. Never one row per child.
4. **Rate limits** apply both per IP address (the existing lockout machinery) and per email: a resend
   at most once a minute per email, and the code's own 5-attempt cap.
5. **Invites are consumed on every accepted registration**, including when the email already has a
   verified account (that registration still answers 202 and creates nothing). An invite therefore
   can't be used to test whether an email has an account.
6. **Past weeks** are the child's written weeks from the existing weekly-packets list, newest first,
   with the documents print-info says exist. A week still being written shows on the This week card
   and not in Past weeks.
7. **Coverage bars**, per subject: *solid* and *shaky* from the progress data; *still to come* is
   the number of that subject's skills at the child's grade for the subject (math grade for Math,
   language arts grade otherwise) that are neither.
8. **First week.** Onboarding starts the current week if the child is added Monday to Wednesday,
   otherwise next week. A family can have at most 5 children (the owner's limit on an axis parents
   can see; 409 with a plain message after that).
9. **Password reset** is out of scope today. The operator resets with `python -m auth set-password`.

## Left to the builder

- Exact module placement of the ownership helper (a new `src/tenancy.py` is fine).
- Error copy, as long as 404 bodies don't differ between "doesn't exist" and "not yours".
- Whether `owned_student` reuses an open connection or opens its own.
