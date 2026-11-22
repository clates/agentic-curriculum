# Runbook: a new server with HTTPS and login

Goal: a fresh Debian/Ubuntu host, one DNS record and one `.env` give a working HTTPS site with
login. Details and background are in `deploy/README.md`. Needs Docker Compose >= 2.24.0
(bootstrap installs a current one).

1. **Create the host** (any provider). Note its public IPv4.
2. **DNS**: `A  <your-domain>  ->  <IPv4>`. Check: `dig +short <your-domain>`.
3. **Cloud firewall**: allow inbound TCP 22, 80 and 443 only. Not 3000, not 8181. (ufw does not
   cover Docker-published ports.)
4. **Bootstrap** (as root on the host, from a checkout of this repo, with the CI *public* key in a file):

   ```bash
   deploy/bootstrap.sh --dry-run --domain <your-domain> --ci-public-key ./ci_deploy.pub   # preview
   deploy/bootstrap.sh           --domain <your-domain> --ci-public-key ./ci_deploy.pub
   ```
5. **`.env`**: edit `/srv/curriculum/.env`, set `OPENROUTER_API_KEY` (and confirm `AUTH_ALLOWED_HOSTS` is your
   domain, `AUTH_REQUIRED=1`, `COOKIE_SECURE=1`). `/srv/curriculum/caddy.env` (only `SITE_DOMAIN=<your-domain>`)
   is written by bootstrap when you pass `--domain`.
6. **GitHub secrets**: `DEPLOY_HOST`, `DEPLOY_SSH_KEY`, `DEPLOY_KNOWN_HOSTS`
   (`ssh-keyscan -t ed25519 <host>`), `DOCKERHUB_USERNAME`, `DOCKERHUB_TOKEN`.
7. **Deploy**: push to main, or re-run the deploy workflow. Caddy gets the certificate on first
   start (DNS and ports 80/443 must work).
8. **First user** (prompts for the password twice):

   ```bash
   cd /srv/curriculum && docker compose --env-file .deploy.env exec -u appuser app python -m auth create-user <username>
   ```
9. **Check**:

   ```bash
   curl -sI https://<your-domain>/ | head -3            # https, valid certificate
   curl -s -o /dev/null -w '%{http_code}\n' https://<your-domain>/api/students   # 401
   docker compose --env-file .deploy.env logs --tail 20 caddy
   ```
   Then confirm the real visitor address reaches the lockout (see "Check the real visitor address"
   in `deploy/README.md`).

Moving an existing install, or the live box that still has host Caddy: see the Migration sections
of `deploy/README.md`. Stop `caddy` on the host (`systemctl disable --now caddy`) before the first
deploy of the compose-managed Caddy.
