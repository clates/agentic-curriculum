# Deployment

A push to `main` runs the full CI suite, builds the Docker image, pushes it to Docker Hub
(tagged with the commit SHA, a timestamp tag, and `latest`), and deploys it to the server.

```
push to main -> CI (tests) -> build + push image -> ssh deploy@server <sha> -> deploy.sh
```

## How a deploy works

`deploy.sh` runs on the server and is the only command the CI key can run. It:

1. validates that its argument is a 40-character commit SHA,
2. downloads `deploy/docker-compose.yml` from that same commit,
3. pulls `chrislates/agentic-curriculum:<sha>` and restarts the stack (the app and Caddy),
4. waits for the app to answer on `127.0.0.1:3000`,
5. on failure, restarts the previous SHA and exits non-zero (the GitHub job fails).

## Server layout (`/srv/curriculum`)

| Path | What |
|---|---|
| `data/curriculum.db` | SQLite database (bind mount, survives redeploys) |
| `artifacts/`, `logs/` | Generated worksheets and logs (bind mounts) |
| `.env` | The app's secrets and settings (`OPENROUTER_API_KEY`, `AUTH_*`, ...). Never committed. |
| `caddy.env` | Only `SITE_DOMAIN`, read by the Caddy container (mode 640). Missing means a localhost site. |
| `current_sha` | Last successfully deployed commit |

The app listens on `127.0.0.1:3000` only (deploy.sh's health probe and SSH tunnels use it:
`ssh -L 3000:127.0.0.1:3000 deploy@<server>`). The public entrance is the `caddy` service in the
same compose file: it terminates HTTPS on ports 80/443 and forwards to `app:3000` over the compose
network. Its Caddyfile is inline in `docker-compose.yml` (deploy.sh downloads only that file), and
certificates live in the `caddy_data` named volume so they survive redeploys.

Requires Docker Compose >= 2.24.0 (inline `configs: content:`, `env_file` with `required: false`). Preflight:

```bash
docker compose version --short   # must print 2.24.0 or newer
```

## GitHub secrets

| Secret | Value |
|---|---|
| `DOCKERHUB_USERNAME`, `DOCKERHUB_TOKEN` | Docker Hub login (already present) |
| `DEPLOY_HOST` | Server address |
| `DEPLOY_SSH_KEY` | Private half of the CI deploy key |
| `DEPLOY_KNOWN_HOSTS` | The server's `ssh-keyscan -t ed25519` line, so CI verifies the host |

## New server

A fresh Debian/Ubuntu host, a DNS A record and one `.env` is all it takes; nothing is installed by
hand except Docker, and `bootstrap.sh` installs that too. The short walkthrough is
`docs/how-to/set-up-a-server.md`. In brief, as root on the new host:

```bash
git clone https://github.com/clates/agentic-curriculum.git && cd agentic-curriculum
deploy/bootstrap.sh --dry-run --domain homeschool.example.com --ci-public-key ./ci_deploy.pub  # preview
deploy/bootstrap.sh           --domain homeschool.example.com --ci-public-key ./ci_deploy.pub
```

`bootstrap.sh` is idempotent. It installs Docker Engine and the compose plugin if missing, creates
the `deploy` user (docker group, no password), creates `/srv/curriculum/{data,artifacts,logs}`,
installs `deploy.sh` root-owned at `/usr/local/sbin/curriculum-deploy.sh`, adds the CI public key
to `/home/deploy/.ssh/authorized_keys` as

```
command="/usr/local/sbin/curriculum-deploy.sh",restrict ssh-ed25519 AAAA... ci-deploy
```

and writes a `/srv/curriculum/.env` skeleton (mode 600, never overwritten). It then prints what
stays manual: fill in `.env`, DNS A record, cloud firewall, GitHub secrets, first deploy, first user.

Changes to `deploy.sh` are reinstalled by hand (re-run `bootstrap.sh`, or the `install` line). CI
deliberately cannot update it, since it is the security boundary for the CI key.

Two env files, on purpose. `.env` is the app's (`OPENROUTER_API_KEY`, `AUTH_REQUIRED=1`,
`COOKIE_SECURE=1`, `AUTH_ALLOWED_HOSTS`). `caddy.env` holds only `SITE_DOMAIN` (Caddy's site address
and certificate name; missing means a harmless `localhost` site) and is the only file the
internet-facing Caddy container reads, so it never sees the app's secrets. An ACME contact email is
not wired in: Let's Encrypt issues without one.

## Firewall

Allow inbound TCP 80 (certificate check and http-to-https redirect) and 443. Do not open 3000 or
8181. **Docker-published ports bypass ufw/iptables rules you add through ufw**, so `ufw deny` does
not protect `80:80`/`443:443`; use the cloud provider's firewall (for example Hetzner Cloud
Firewalls). The app's port is safe regardless: it is published on `127.0.0.1` only.

## Check the real visitor address reaches the login lockout

The lockout is per client IP, taken from the `X-Forwarded-For` header Caddy writes from the TCP
peer address. If Docker NAT replaced the visitor with the Docker gateway (typically `172.x.0.1`),
every visitor would share one address. The app does not log addresses, but a failed sign-in stores
one in the `login_attempt` table, so check after the first deploy:

```bash
# 1. from your laptop: one wrong sign-in with a throwaway name (expect 401)
curl -s -o /dev/null -w '%{http_code}\n' -X POST https://$SITE_DOMAIN/api/auth/login \
  -H 'Content-Type: application/json' -d '{"username":"ipcheck","password":"wrong-password-1"}'
curl -s https://api.ipify.org; echo            # your public address (use `curl -4`/`-6` to pick a family)
# 2. on the server: the address the app recorded for that attempt
cd /srv/curriculum && docker compose --env-file .deploy.env exec -u appuser app python -c \
  "import sqlite3; print(sqlite3.connect('/data/curriculum.db').execute(\"select key from login_attempt where key like 'ipcheck|%'\").fetchall())"
```

The key `ipcheck|<address>` must end in your public address, not `172.*`/`10.*`. Clear it afterwards
with `python -m auth unlock ipcheck` (same `exec` prefix). Over
IPv4 Docker preserves the source address. Over IPv6 the userland proxy can hide it: if you publish
an AAAA record and the recorded key shows a gateway address for IPv6 visitors, either leave out the AAAA
record or enable IPv6 in Docker with `ip6tables` (`/etc/docker/daemon.json`:
`{"ipv6": true, "ip6tables": true, "fixed-cidr-v6": "fd00:d0c::/64"}`) and restart Docker. Skip
this if you only publish an A record.

## IPv6 (off on purpose)

The compose file publishes `0.0.0.0:80` and `0.0.0.0:443` only, so Caddy is IPv4 only. A plain
`443:443` would also listen on `[::]`, where Docker's userland proxy can replace the visitor's
address with the Docker gateway and put every IPv6 visitor in one login-lockout bucket. Publish only
an A record. To turn IPv6 on deliberately: enable it in Docker (`/etc/docker/daemon.json`:
`{"ipv6": true, "ip6tables": true, "fixed-cidr-v6": "fd00:d0c::/64"}`, restart Docker), add
`"[::]:80:80"` and `"[::]:443:443"` to the caddy `ports`, add an AAAA record, then repeat the client
address check above from an IPv6 client (`curl -6`) and confirm the key ends in your IPv6 address.

## Do not delete the certificates

`docker compose down -v` deletes the `caddy_data` volume (certificates and the ACME account);
re-issuing hits Let's Encrypt rate limits. Never use `-v` in production.

## Migration: the live box (Caddy installed on the host)

The existing server runs Caddy as a host service (see the old manual runbook). It holds ports
80/443, so the new Caddy container cannot bind. That is NOT a clean rollback: `deploy.sh` runs
`docker compose up -d` under `set -e`, so the bind failure aborts the script before its health check
and rollback code. The CI job fails, the app container is already on the new SHA, `current_sha` is not
updated and there is no caddy container (the site stays down). **Before the first deploy of this
change**, on the server as root:

```bash
systemctl disable --now caddy        # frees 80/443; the site is down from here until the deploy ends
ss -ltn | grep -E ':(80|443)\b'      # preflight: must print nothing before you deploy
```

Then merge/deploy. Caddy in the container will obtain a fresh certificate for `SITE_DOMAIN`, so make
sure `caddy.env` exists first (`AUTH_ALLOWED_HOSTS` is already in `.env`):

```bash
printf 'SITE_DOMAIN=homeschool.chrislates.com\n' > /srv/curriculum/caddy.env
chown deploy:deploy /srv/curriculum/caddy.env && chmod 640 /srv/curriculum/caddy.env
```

If `SITE_DOMAIN` is still set in `.env` from an earlier attempt, remove that line; Caddy no longer reads it.

After the first deploy, check the public URL yourself: `curl -sI https://homeschool.chrislates.com/`.
`deploy.sh` only probes `127.0.0.1:3000`, so a missing `caddy.env` (a silent localhost site) or a failed
certificate does not fail the deploy.

Expect a short outage (the pull plus certificate issuance, usually under a minute or two). The host
package can be removed afterwards (`apt purge caddy`). To roll back to the host Caddy: stop the
container (`docker compose --env-file .deploy.env stop caddy`), then `systemctl enable --now caddy`.

## Moving to another provider

1. On the old server stop writes and copy state: `rsync -a /srv/curriculum/data /srv/curriculum/artifacts <new>:/srv/curriculum/`
   (and keep a copy of `.env`; do not commit it).
2. Create the new server, run `deploy/bootstrap.sh` (above), copy `.env` into place.
3. Update the `DEPLOY_HOST` and `DEPLOY_KNOWN_HOSTS` GitHub secrets; the CI key can stay.
4. Lower the DNS TTL beforehand, then point the A record at the new IP. Certificates are issued
   on the new host once DNS resolves to it.
5. Deploy (push to main or re-run the workflow), verify, then shut down the old server.

## Rolling back by hand

```bash
ssh deploy@<server>
cd /srv/curriculum
echo "IMAGE=chrislates/agentic-curriculum:<older-sha>" > .deploy.env
docker compose --env-file .deploy.env up -d
```

## Rotating the CI key

Generate a new key, replace the `ci-deploy` line in `authorized_keys`, and update the
`DEPLOY_SSH_KEY` secret.
