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

Open the site over HTTPS. You land on the login form; after signing in you land on This week.

For a script, set the password in the environment instead of the prompt:
`docker compose --env-file .deploy.env exec -u appuser -e AUTH_NEW_PASSWORD app python -m auth create-user <username>`
(with `AUTH_NEW_PASSWORD` exported in your shell first).

## Day to day

| Task | Command (from `/srv/curriculum`, prefix `docker compose --env-file .deploy.env exec -u appuser app`) |
|---|---|
| Change a password (signs that user out everywhere) | `python -m auth set-password <username>` |
| Lock an account (also signs it out) | `python -m auth disable <username>` |
| Unlock it | `python -m auth enable <username>` |

## What it does

- Sessions last 30 days from the last visit (they slide), in an `HttpOnly`, `SameSite=Lax` cookie
  that is `Secure` over HTTPS. Only a hash of the cookie value is stored.
- After 3 wrong tries from one address for one username, each further wrong try locks that pair for
  15 s, 30 s, 60 s and so on, doubling up to an hour. A different address is never held back by
  someone else's wrong tries, and a stranger guessing from many addresses can only make strangers
  wait a few minutes; an address you have signed in from before is not held at all.
- Everything except `/health`, `/version` and the sign-in and sign-out calls needs a session.

## Turn it off

Remove `AUTH_REQUIRED` from `.env` and run the `up -d --force-recreate` line again. Accounts and
sessions stay in the database and work again when it is turned back on.

## If you are locked out

You cannot be locked out by someone else's guesses, but you can lock your own address by mistyping.
Wait a few minutes, or reset from the server: `python -m auth set-password <username>` still works
because the command line does not go through the login.
