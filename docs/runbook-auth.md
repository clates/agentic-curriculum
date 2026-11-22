# Runbook: turning on the login

A small login layer (username and password, no signup page). It is a stopgap that grows into
accounts and families (M7). It is **off by default**: self-hosting, local development, CI and the
main end-to-end suite behave exactly as they did before. Nothing here edits the deploy workflow.

## The one rule: HTTPS only

Never expose the login over plain `http://` to the internet. A password typed there can be read by
anyone on the path. Put TLS in front first:

- **Tailscale** (`tailscale serve` for your devices, or `tailscale funnel` for the public internet),
  which terminates TLS with a real certificate; or
- **Caddy** (or any reverse proxy) with a certificate, forwarding to `127.0.0.1:3000`.

The app itself still listens on `127.0.0.1:3000` only (see `deploy/docker-compose.yml`). The proxy
in front must set `X-Forwarded-For` (the visitor's address) and `X-Forwarded-Proto: https`; Caddy and
Tailscale do. The login uses the first address in `X-Forwarded-For` to rate-limit guessing per
visitor, so do not point the app at the internet directly with no proxy in front: anyone could
make up that header.

## Behind Caddy

Host must reach the app unchanged (Caddy keeps it by default; nginx's default rewrites it, so add
`proxy_set_header Host $host;`). The login's cross-site check compares the browser's Origin with
that host. Example:

```
homeschool.chrislates.com {
    request_body {
        max_size 10MB
    }
    reverse_proxy 127.0.0.1:3000 {
        header_up X-Forwarded-For {remote_host}
        header_up X-Forwarded-Proto {scheme}
    }
}
```

`header_up X-Forwarded-For {remote_host}` replaces whatever the visitor sent, so the address used
for the lockout is the real one (the app reads the rightmost entry, the one your proxy wrote).

Also set `AUTH_ALLOWED_HOSTS=homeschool.chrislates.com` in `.env` (comma-separated for several).
When set, a sign-in or any change request must come from one of those hosts and the proxy's
`X-Forwarded-Host` is ignored, so the check no longer depends on how the proxy treats Host. (A
cross-site page cannot set a custom header such as `X-Forwarded-Host` without a preflight the
server refuses, so this is defence in depth, not a known hole.)

## Turn it on (on the server)

```bash
cd /srv/curriculum

# 1. Add to .env (create the lines if they are missing). Never commit this file.
#      AUTH_REQUIRED=1
#      COOKIE_SECURE=1
$EDITOR .env

# 2. Restart so the container reads the new .env (a plain restart does not re-read it).
docker compose --env-file .deploy.env up -d --force-recreate

# 3. Make your account. You are asked for the password twice (at least 12 characters); it is
#    never a command-line argument, so it does not land in shell history or `ps`.
docker compose --env-file .deploy.env exec -u appuser app python -m auth create-user <username>
```

`create-user` does nothing if the name already exists, so it is safe to run again. The first
account joins the existing family (`fam_local`), so everything already in the app stays visible.

**There is no per-family separation yet.** Every account sees ALL data, and `--family` refuses
anything but `fam_local`. Only make accounts for people you would show every child. Being signed in
is the only check.

Open the site over HTTPS. You land on the login form; after signing in you land on This week.

For a script, set the password in the environment instead of the prompt:
`docker compose --env-file .deploy.env exec -u appuser -e AUTH_NEW_PASSWORD app python -m auth create-user <username>`
(with `AUTH_NEW_PASSWORD` exported in your shell first).

## Day to day

| Task | Command (from `/srv/curriculum`, prefix `docker compose --env-file .deploy.env exec -u appuser app`) |
|---|---|
| Change a password (signs that user out everywhere) | `python -m auth set-password <username>` |
| Lock an account (also signs it out) | `python -m auth disable <username>` |
| Re-enable it (also clears its lockouts) | `python -m auth enable <username>` |
| Clear one user's lockouts | `python -m auth unlock <username>` |
| Clear every lockout, address locks too | `python -m auth unlock` |

## What it does

- Sessions last 30 days from the last visit (they slide), in an `HttpOnly`, `SameSite=Lax` cookie
  that is `Secure` over HTTPS. Only a hash of the cookie value is stored.
- After 3 wrong tries from one address for one username, each further wrong try locks that pair for
  15 s, 30 s, 60 s and so on, doubling up to an hour. A different address is never held back by
  someone else's wrong tries, and a stranger guessing from many addresses can only make strangers
  wait a few minutes. An address you signed in from in the last 30 days is not held by the
  many-names-from-one-address limit or the many-addresses limit. Be aware: someone who shares your
  public address (the same home or office connection) can still trigger the lock on that one
  username-and-address pair by guessing. `python -m auth unlock` clears it, and the 30-day session
  cookie means you rarely need to type the password at all.
- Only 2 password checks run at once (`AUTH_MAX_CONCURRENT_HASHES`); an extra sign-in waits up to
  3 seconds (at most 4 may wait; any more are told at once), then is told "Busy right now" and nothing is counted against anyone. A limit at the proxy (for example fail2ban reading the Caddy access log; stock Caddy has no rate_limit module) is an optional extra, not required.
- Everything except `/health`, `/version` and the sign-in and sign-out calls needs a session.

## Turn it off

Remove `AUTH_REQUIRED` from `.env` and run the `up -d --force-recreate` line again. Accounts and
sessions stay in the database and work again when it is turned back on.

## If you are locked out

Someone else's guesses cannot lock you out from another address, but you can lock your own by
mistyping, and a stranger behind your own public address can lock that pair. From the server (the
command line does not go through the login):

```bash
cd /srv/curriculum
docker compose --env-file .deploy.env exec -u appuser app python -m auth unlock <username>
# or forget every lockout, address locks included:
docker compose --env-file .deploy.env exec -u appuser app python -m auth unlock
```

`python -m auth set-password <username>` and `enable <username>` also clear that user's lockouts.
