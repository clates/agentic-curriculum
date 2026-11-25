# Registration, invites and the cross-family console Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** A new family registers from the sign-in page with an invite code, confirms its email
with a 6-digit code, and lands signed in. Admins can make invite codes, and the loop console shows
every family, with each cross-family look audited.

**Architecture:** A small mailer module sends mail over the configured SMTP (or records it to an
outbox file in dev/tests). Invites and email verification live in the auth package beside accounts,
reusing the `auth_challenge` and `audit_log` tables from migration 0002. Three new public auth
routes carry the flow; the loop console gains an admin-only way to resolve any family's child.

**Tech Stack:** FastAPI, SQLite migrations, pytest, Next.js 16 / React 19, Playwright.

**Spec:** `docs/superpowers/specs/2026-11-25-family-accounts-design.md`: Decisions D1-D3, "Design:
E1 registration", "Design: E5.4 ...", and "Builder-check calls" 1, 3, 4, 5, 9.

## Global Constraints

- Another family's data still answers 404 with the same body as a missing record. Ordinary routes
  never give admins a bypass; only `/loop-admin/*` and `/admin-api/*` (both behind
  `require_permission("admin")`) may reach other families.
- Login off: nothing changes for self-hosters or the main E2E suite.
- Registration never reveals whether an email has an account. Register and resend answer the same
  way either way, and every accepted registration consumes its invite.
- Codes: invite codes are 10 characters from `ABCDEFGHJKMNPQRSTVWXYZ23456789`, stored as SHA-256 hex,
  valid 14 days, single use. Email codes are 6 digits, stored as SHA-256 hex in `auth_challenge`
  (purpose `verify_email`), valid 15 minutes, 5 attempts. Neither code, nor any password, ever
  appears in a log line.
- Passwords: the existing rules (`auth.passwords.validate_new_password`, 12+ characters).
- Email is the username for new accounts: lower-cased, trimmed, at most 64 characters, matching
  `^[^@\s]+@[^@\s]+\.[^@\s]+$`. Existing username accounts keep working.
- Mail goes from `SMTP_FROM` via `SMTP_*` (STARTTLS on 587). With `SMTP_HOST` unset, nothing is
  sent; with `MAILER_OUTBOX` set, each message is appended as one JSON line to that file.
- Python: black and ruff, 100-character lines. Frontend: Prettier, `npm run lint:copy`. No test
  may call a real SMTP server.

## Review Focus

1. **Registering with an email that already has a verified account** must answer exactly like a
   fresh registration (status and body), send no mail to that address, and consume the invite.
   Task 3 tests this by comparing the two responses.
2. **Guessing an email code**: the sixth wrong attempt on one challenge must fail even with the
   right code, and the per-IP lockout must engage. Task 3 tests it.
3. **An admin's cross-family console requests** must write exactly one audit row each, and a
   non-admin must still get 404 with no audit row written. Task 5 tests both.
4. **A replayed verify request after success** (same code twice) must not sign anyone in again.
   Task 3 tests it.
5. **Mail failure during registration** (the SMTP server refuses): the account stays pending, the
   response says to try "Send a new code", and the invite is still consumed. Task 3 tests it with a
   failing transport.

---

### Task 1: Mailer

**Files:**
- Create: `src/mailer.py`
- Modify: `src/job_alerts.py` (`_send_email` uses the mailer; behaviour unchanged)
- Test: `tests/test_mailer.py`; existing `tests/test_job_alerts.py` must pass unchanged

**Interfaces:**
- Produces: `mailer.send(to: str | list[str], subject: str, body: str) -> None`. It raises `mailer.MailError` on a transport failure. `mailer.enabled() -> bool` is true when `SMTP_HOST` is set. With `MAILER_OUTBOX` set, it appends `{"to": [...], "subject": ..., "body": ...}` as JSON lines (always, whether or not SMTP is set; with SMTP unset and no outbox, it logs `mail not sent: no SMTP_HOST` with the subject only).

- [ ] **Step 1:** Write failing tests:
  - outbox: one JSON line per message;
  - no SMTP and no outbox: nothing raises, and the log has the subject but not the body;
  - a fake SMTP transport receives From = `SMTP_FROM`, STARTTLS, and login with `SMTP_USER`;
  - a transport exception raises `MailError` and never includes the password.
- [ ] **Step 2:** Run them; they fail. Implement. Switch `job_alerts._send_email` to call `mailer.send(recipients(), subject, body)`.
- [ ] **Step 3:** Run `tests/test_mailer.py tests/test_job_alerts.py`, then the full suite. Commit `feat: a mailer for account email (SMTP, or an outbox file in dev and tests)`.

### Task 2: Invite codes, verified flag, and the invite tools

**Files:**
- Create: `src/migrations/0013_invites.sql` (`invite` table; `ALTER TABLE app_user ADD COLUMN email_verified_at TEXT`; backfill existing users to their `created_at`)
- Modify: `src/auth/store.py`, `src/auth/__main__.py` (new `invite [--days N]` subcommand that prints the code once)
- Create: `src/admin_api.py`, a router at `/admin-api` with `dependencies=[Depends(require_permission("admin"))]`. Include it in `src/main.py`.
- Modify: `frontend/app/admin/page.tsx` and `frontend/lib/copy.ts` (an "Invite a family" card with a button that shows the new code once, and a "Copy" button)
- Test: `tests/test_invites.py`; extend `frontend/e2e/auth/admin.spec.ts`

**Interfaces:**
- Produces:
  - `store.create_invite(conn, created_by: str | None, days: int = 14) -> str` returns the plain code.
  - `store.consume_invite(conn, code: str, user_id: str) -> bool` is true only for an unused, unexpired code. It is atomic: `UPDATE ... WHERE code_hash=? AND used_at IS NULL AND expires_at > now`, then check the rowcount.
  - `POST /admin-api/invites` returns `{"code": str, "expires_at": str}`.
  - The route-inventory test treats `/admin-api/*` like `/loop-admin/*` (must reach `require_permission`).

- [ ] **Step 1:** Write failing tests:
  - a code matches the alphabet and length;
  - consuming it twice gives True then False;
  - an expired code gives False;
  - only a hash is stored;
  - the CLI prints one code;
  - `POST /admin-api/invites` gives 404 to a non-admin (login on) and 200 with a code to an admin;
  - after migration, existing users have `email_verified_at` set.
- [ ] **Step 2:** Implement until green. Add the E2E test "an admin makes an invite code and sees it once".
- [ ] **Step 3:** Full backend suite, then commit `feat: invite codes (CLI and admin panel)`.

### Task 3: Registration, email verification and resend

**Files:**
- Create: `src/auth/registration.py` (service functions)
- Modify: `src/auth/web.py`:
  - three routes: `POST /auth/register`, `POST /auth/verify`, `POST /auth/resend`;
  - add them to `PUBLIC_PATHS`;
  - login answers `403 {"detail": "email_not_verified"}` for a correct password on an unverified account, and sends a fresh code subject to the resend limit.
- Modify: `src/auth/store.py` (the user lookup reads `email_verified_at`)
- Test: `tests/test_registration.py`; update the `PUBLIC_PATHS` assertion in `tests/test_auth.py`

**Interfaces:**
- Consumes: `mailer.send` (Task 1); `create_family`, `consume_invite` and `create_session` (store); `lockout.reserve` and `lockout.record_success` for per-IP limits.
- Produces:
  - `POST /auth/register {email, password, family_name (1-80 chars), invite_code}` answers `202 {"status": "check_email"}` for every accepted request, and 400 `{"detail": "invalid_invite"}` for a bad invite. A malformed email or weak password gets 400 with a plain message, which reveals nothing about accounts.
  - `POST /auth/verify {email, code}` answers 200 and sets the session cookie on success. Otherwise it answers `400 {"detail": "invalid_code"}`.
  - `POST /auth/resend {email}` always answers `202 {"status": "check_email"}`.
  - Email subject: "Your sign-in code". Body: the 6-digit code, that it expires in 15 minutes, and that they can ignore the email if they didn't sign up.

- [ ] **Step 1: Write the failing tests.**
  - A fresh registration creates a family, an unverified user and an outbox message with a 6-digit code.
  - Verify signs in and `/auth/me` shows the user.
  - Errors:
    - bad, used or expired invite gives `invalid_invite` and creates nothing;
    - a verified email registers again: same 202 body, no mail to that address, invite consumed, nothing created;
    - an unverified email registers again: replaces the password and family name, consumes the invite, sends a new code.
  - Code guessing:
    - five wrong codes, then the right one, fails;
    - verifying the same code twice signs in once only;
    - wrong codes from one IP trigger the lockout.
  - Resend: at most once a minute per email; always 202.
  - Login:
    - unverified with the correct password gives `email_not_verified`;
    - unverified with a wrong password gives `invalid_credentials`.
  - A failing mail transport: 202, the account stays pending, the invite is consumed.
  - Captured logs contain no code and no password.
  - The `PUBLIC_PATHS` set is updated in the existing assertion.
- [ ] **Step 2:** Run them; they fail. Implement. Wrap each registration in one transaction (family, user, invite and challenge together). Send mail after commit.
- [ ] **Step 3:** Full backend suite. Commit `feat: registration with an invite code and an emailed 6-digit code`.

### Task 4: Sign-up screens

**Files:**
- Modify: `frontend/app/login/page.tsx` (a "Create an account" mode: family name, email, password twice, invite code; then a "Check your email" step with a 6-digit field and "Send a new code"; a sign-in answered `email_not_verified` goes to the same step)
- Modify: `frontend/lib/copy.ts`
- Modify: the `auth` Playwright project config, so its backend runs with `MAILER_OUTBOX=/tmp/e2e-outbox-<port>.jsonl`
- Create: `frontend/e2e/auth/register.spec.ts` and a fixture `latestCode(email)` that reads the outbox
- Test: the new spec, plus an axe check and no sideways scroll at 360px on both new steps

- [ ] **Step 1:** Write the failing spec:
  - register with an invite made through the CLI, read the code from the outbox, verify, and land signed in on This week;
  - a wrong code shows "That code didn't work";
  - "Send a new code" works;
  - signing in to an unverified account shows the code step.
- [ ] **Step 2:** Implement. Copy stays plain and passes `lint:copy`.
- [ ] **Step 3:** Run the full E2E suite, type-check, prettier on changed files and lint:copy. Commit `feat(frontend): create an account and confirm the email`.

### Task 5: The loop console across families, audited

**Files:**
- Modify: `src/loop_admin.py`:
  - add `admin_student(conn, student_id) -> tuple[str, sqlite3.Row]` (the child's own family and row; 404 if the child doesn't exist);
  - the overview lists every family's children grouped by `family.name`;
  - actions, feed-forward, review and retry act on the child's or job's own family;
  - add `_audit(conn, request, family_id, action, target)`.
- Modify: `frontend/components/loop/LoopConsole.tsx` (group by family name; the admin's own family first)
- Modify: `tests/test_loop_admin.py` (the cross-family tests from PR #240 that expected 404 for another family's child now expect success plus an audit row; non-admins still get 404)

**Interfaces:**
- Consumes: `require_permission` and `current_family` (the admin's own family, used to decide when to audit).
- Produces audit rows:
  - `action` is `console.overview`, `console.view` or `console.<action name>`;
  - `family_id` is the other family;
  - `user_id` is the admin;
  - `target` is the student id or `job:<id>`;
  - `detail_json` is `{"families": n}` for the overview only.
  - No row is written when the data is the admin's own family.

- [ ] **Step 1:** Write failing tests:
  - an admin in family B acts on A's child, which succeeds and writes exactly one audit row with `family_id` A;
  - the overview with two other families writes one row with `{"families": 2}`;
  - acting on the admin's own child writes no row;
  - a non-admin gets 404 on every console route and no audit row is written.
- [ ] **Step 2:** Implement. Ordinary routes are untouched, and `tests/test_family_isolation.py` must pass unchanged.
- [ ] **Step 3:** Run the full backend suite, the loop console E2E specs and type-check. Commit `feat: the loop console shows every family, and each cross-family look is audited`.

### Task 6: Docs

**Files:** `docs/reference/login.md` (registration routes, codes and limits, the `invite` command), a new `docs/how-to/invite-a-family.md`, `docs/explanation/login-and-https.md` (why invites, why emails are confirmed, why register never reveals accounts, and that admins' cross-family looks are audited), `docs/README.md` index.

- [ ] Keep each page its own Diátaxis kind, run the link check (0 problems), and commit `docs: registration, invites and the audited console`.

### After merge (operator)

- Set `LLM_CAP_FAMILY_MONTH_USD` in `/srv/curriculum/.env` before handing out invites. Value: the owner's choice.
- Move the `claude` account to its own family (E0.5). Show the owner the script first.
