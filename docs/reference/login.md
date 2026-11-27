# Login reference

Code: `src/auth/`, the gate in `src/main.py`, `frontend/proxy.ts` and `/login`. Tasks:
[Turn on the login](../how-to/turn-on-login.md), [Manage accounts](../how-to/manage-accounts.md),
[Invite a family](../how-to/invite-a-family.md).
Background: [Why the login needs HTTPS and a proxy](../explanation/login-and-https.md).

## Settings

| Variable | Default | Meaning |
|---|---|---|
| `AUTH_REQUIRED` | unset (off) | `1` requires a session for every route outside the public list |
| `COOKIE_SECURE` | unset | `1` marks the session cookie `Secure` |
| `AUTH_ALLOWED_HOSTS` | unset | comma-separated hosts. When set, a sign-in or any change request must come from one of them, and `X-Forwarded-Host` is ignored |
| `AUTH_MAX_CONCURRENT_HASHES` | 2 | password checks that may run at once |
| `AUTH_NEW_PASSWORD` | unset | the password for `create-user` or `set-password`, in place of the prompt |
| `AUTH_BACKOFF_SCALE` | 1 | multiplies every lockout duration and the resend wait. Tests use it to shorten them |
| `SMTP_HOST`, `SMTP_PORT`, `SMTP_USER`, `SMTP_PASSWORD` | none, 587 | the mail relay for sign-in codes. STARTTLS, or implicit TLS on port 465. With `SMTP_HOST` unset nothing is sent |
| `SMTP_FROM` | `SMTP_USER` | the sender address of sign-in codes |
| `MAILER_OUTBOX` | unset | a file path. Every message is appended to it as one JSON line (`to`, `subject`, `body`). For development and tests |

## Commands

`python -m auth <command>`, run inside the `app` container as `appuser`.

| Command | Effect |
|---|---|
| `create-user <username>` | makes an account, already verified. Does nothing if the name exists. `--family <id>` names any existing family; the default is `fam_local` |
| `invite [--days N]` | prints a new invite code, once. Valid 14 days unless `--days` says otherwise |
| `set-password <username>` | sets the password, signs the user out everywhere, clears their lockouts |
| `disable <username>` | locks the account and signs it out |
| `enable <username>` | unlocks the account and clears its lockouts |
| `unlock <username>` | clears that user's lockouts: sign-in, and the register and verify ones for that email |
| `unlock` | clears every lockout, address locks included |
| `grant <username> <permission>` | gives the user a permission. Known permissions: `admin` |
| `revoke <username> <permission>` | takes it away |
| `list-users` | one line per user: username, family id, `enabled` or `disabled`, comma-separated permissions (`-` for none). Never prints password hashes |

Passwords: at least 12 characters, never accepted as a command-line argument.

## Public routes

Everything needs a session except `/health`, `/version`, sign-in, sign-out and the three
registration routes (`auth.web.PUBLIC_PATHS`). A route-inventory test fails if a new route is left
public.

## Registration

On the sign-in page, "Create an account" asks for a family name, an email, a password twice and an
invite code. Then "Check your email" asks for the 6-digit code. "Wrong email?" there says that a
different email needs a new invite code, and links back to sign-in.

| Route | Body | Answer |
|---|---|---|
| `POST /auth/register` | `email`, `password`, `family_name`, `invite_code` | 202 `{"status": "check_email"}`. 400 for a bad email, family name or password, or `invalid_invite` |
| `POST /auth/verify` | `email`, `code`, `password` | the session cookie and `user` on success. 400 `invalid_code` otherwise |
| `POST /auth/resend` | `email` | 202 `{"status": "check_email"}`, unless the address is held (429) |

429 `too_many_attempts` and 503 `busy` can answer any of them, with `retry_after` in seconds.
Sign-in to an unverified account with the right password answers 403 `email_not_verified` and
mails a fresh code if the last one is over a minute old. Registering again with a pending email
always issues a new code (and replaces that account's password and family name).

### Invite codes

| Property | Value |
|---|---|
| Length and characters | 10, from `ABCDEFGHJKMNPQRSTVWXYZ23456789` (no `0 O 1 I L U`) |
| Stored | as a hash. The plain code is shown once |
| Valid for | 14 days by default |
| Uses | one |
| Made by | `python -m auth invite`, or the "Invite a family" card in the admin panel |

Every accepted registration uses up its invite, including one for an email that already has an
account (nothing is created and no mail is sent).

### Sign-in codes

| Property | Value |
|---|---|
| Format | 6 digits, mailed from `SMTP_FROM` |
| Valid for | 15 minutes |
| Tries | 5 per code. A new code replaces the old one. A try with the wrong password uses none (the lockout still counts it) |
| To verify | the email, the code and the account's password |
| Resend | at most once a minute per email, for an account that is still unverified |
| Codes per account | at most 10 in any 24 hours, from register, resend and sign-in together. Past that the answer is the same and nothing is sent |
| Resend per address | every resend counts against the address's sign-in limit (20 in 10 minutes holds it for 10 minutes), whatever the email |
| Lockouts | wrong registers and verifies count per email and per address, like sign-in tries |
| Email | lower-cased and trimmed, at most 64 characters, letters, digits and `. _ % + -` before the `@`, and dot-separated letters, digits and `-` after it. It is the username |
| Family name | 1 to 80 characters |

Register and resend answer the same whether or not the email has an account. Accounts made with
`create-user` are verified when they are made.

### Limits

- Someone who sends many wrong codes for a pending email can lock out its verification, as with
  sign-in usernames.
- Mail still queued when the server stops is lost without a message. The user can ask for a new code.
- There is no password reset. The operator runs `set-password`.
- Accounts that never verify are not cleaned up.

## Sessions

- Lifetime: 30 days, sliding from the last visit.
- Cookie: `HttpOnly`, `SameSite=Lax`, and `Secure` over HTTPS.
- Storage: a hash of the cookie value only.
- Passwords: scrypt.

## Lockouts

- After 3 wrong tries from one address for one username, each further wrong try locks that
  address-and-username pair for 15 s, then 30 s, 60 s and so on, doubling up to 1 hour.
- Wrong tries from one address never hold back a different address.
- Guessing from many addresses can make other visitors wait a few minutes at most.
- An address that signed in successfully in the last 30 days is exempt from the
  many-usernames-from-one-address limit and the many-addresses limit.
- Someone on the same public address can still lock that one pair by guessing.
- The address used is the rightmost `X-Forwarded-For` entry: the one your proxy wrote.

## Load limits

At most 2 password checks run at once. An extra sign-in waits up to 3 seconds, and at most 4 may
wait. After that, the reply is "Busy right now" and no wrong try is counted.

## Families

- Every account belongs to one family and sees only that family's children, packets, weeks, plans
  and jobs. The exception is an admin in the loop console, which shows every family's children,
  plans and jobs (see [The loop console and the audit log](#the-loop-console-and-the-audit-log)).
- Another family's record answers 404 with the same body as a missing record, never 403.
- With login off, every request acts for `fam_local`.
- With login on, new child ids are server-generated: `stu_` plus 10 characters. The add-child form
  has no ID field.

## Permissions

Stored in the `user_permission` table. The only permission is `admin`.

| Where | Behaviour |
|---|---|
| Check | read on every request, so a revoke applies on the next request |
| Login off | the operator counts as admin |
| `GET /auth/me` | returns `permissions`, a sorted list |
| `/admin` | page with a "Loop console" card linking to `/loop`. Non-admins are sent home |
| `/loop` | admin only. Non-admins are sent home |
| `/loop-admin/*` | admin only. Everyone else gets 404 |
| `/admin-api/invites` | admin only. `POST` makes an invite and returns `code` and `expires_at` |
| Header | the "Admin" link shows only for admins |

## The loop console and the audit log

The console lists every family, the admin's own first. For another family's data:

- Each request that shows or changes another family's child, plan or job writes one `audit_log`
  row: the family id, the admin's user id, the action (`console.view`, `console.retry` or another
  `console.<action>`) and the child or job id. Once the child or job is found, the row is
  written whatever the answer, including a 404 for a week or a 409 for an action the week's state
  doesn't allow. An unknown action name writes none.
- Loading the overview writes a `console.overview` row with the number of other families, at most
  once per admin per 10 minutes.
- Rows hold ids and the action only, never names or content. The `console.overview` row also
  holds `{"families": N}`.
- A job's error shows only its exception type.

Looks at the admin's own family are not logged. The demo child is always the admin's own.
