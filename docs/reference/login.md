# Login reference

Code: `src/auth/`, the gate in `src/main.py`, `frontend/proxy.ts` and `/login`. Tasks:
[Turn on the login](../how-to/turn-on-login.md), [Manage accounts](../how-to/manage-accounts.md).
Background: [Why the login needs HTTPS and a proxy](../explanation/login-and-https.md).

## Settings

| Variable | Default | Meaning |
|---|---|---|
| `AUTH_REQUIRED` | unset (off) | `1` requires a session for every route outside the public list |
| `COOKIE_SECURE` | unset | `1` marks the session cookie `Secure` |
| `AUTH_ALLOWED_HOSTS` | unset | comma-separated hosts. When set, a sign-in or any change request must come from one of them, and `X-Forwarded-Host` is ignored |
| `AUTH_MAX_CONCURRENT_HASHES` | 2 | password checks that may run at once |
| `AUTH_NEW_PASSWORD` | unset | the password for `create-user` or `set-password`, in place of the prompt |
| `AUTH_BACKOFF_SCALE` | 1 | multiplies every lockout duration. Tests use it to shorten lockouts |

## Commands

`python -m auth <command>`, run inside the `app` container as `appuser`.

| Command | Effect |
|---|---|
| `create-user <username>` | makes an account in `fam_local`. Does nothing if the name exists. `--family` accepts only `fam_local` |
| `set-password <username>` | sets the password, signs the user out everywhere, clears their lockouts |
| `disable <username>` | locks the account and signs it out |
| `enable <username>` | unlocks the account and clears its lockouts |
| `unlock <username>` | clears that user's lockouts |
| `unlock` | clears every lockout, address locks included |

Passwords: at least 12 characters, never accepted as a command-line argument.

## Public routes

Everything needs a session except `/health`, `/version`, sign-in and sign-out (`auth.web.PUBLIC_PATHS`).
A route-inventory test fails if a new route is left public.

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

There is no separation between families yet. Every account sees all data in the install.
