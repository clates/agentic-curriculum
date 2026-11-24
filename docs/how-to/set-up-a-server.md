# Set up a new server with HTTPS

This guide takes a fresh Debian or Ubuntu host to a working HTTPS site with login, deployed from
GitHub. You need a domain you can add DNS records to, and the public half of the CI deploy key in
a file (`ci_deploy.pub` below). How deploys work, the server layout and moving an existing
install are covered in [`deploy/README.md`](../../deploy/README.md).

1. **Create the host** with any provider and note its public IPv4 address.

2. **Point DNS at it**: add `A  <your-domain>  ->  <IPv4>`, then check it:

   ```bash
   dig +short <your-domain>
   ```

3. **Open the cloud firewall** for inbound TCP 22, 80 and 443 only. Don't open 3000 or 8181. Set
   this in the provider's firewall: `ufw` doesn't cover ports Docker publishes.

4. **Bootstrap**, as root on the host, from a checkout of this repo. Preview first, then run it:

   ```bash
   deploy/bootstrap.sh --dry-run --domain <your-domain> --ci-public-key ./ci_deploy.pub
   deploy/bootstrap.sh           --domain <your-domain> --ci-public-key ./ci_deploy.pub
   ```

   It installs Docker Compose 2.24.0 or newer if needed, and writes `/srv/curriculum/caddy.env`.

5. **Fill in `/srv/curriculum/.env`**: set `OPENROUTER_API_KEY`, and check that
   `AUTH_ALLOWED_HOSTS` is your domain, `AUTH_REQUIRED=1` and `COOKIE_SECURE=1`.

6. **Add the GitHub secrets** `DEPLOY_HOST`, `DEPLOY_SSH_KEY`, `DEPLOY_KNOWN_HOSTS`,
   `DOCKERHUB_USERNAME` and `DOCKERHUB_TOKEN`. Get the known-hosts line with
   `ssh-keyscan -t ed25519 <host>`.

7. **Deploy**: push to `main`, or re-run the deploy workflow. Caddy gets a certificate on first
   start, which needs DNS and ports 80 and 443 working.

8. **Make the first account** (it asks for the password twice):

   ```bash
   cd /srv/curriculum
   docker compose --env-file .deploy.env exec -u appuser app python -m auth create-user <username>
   ```

9. **Check it**:

   ```bash
   curl -sI https://<your-domain>/ | head -3                                     # a valid certificate
   curl -s -o /dev/null -w '%{http_code}\n' https://<your-domain>/api/students   # 401
   docker compose --env-file .deploy.env logs --tail 20 caddy
   ```

   Then confirm the lockout sees the real visitor address: follow "Check the real visitor address"
   in [`deploy/README.md`](../../deploy/README.md).

10. **Harden SSH**. `bootstrap.sh` doesn't touch `sshd_config`. Set `PasswordAuthentication no` and
    `PermitRootLogin no`, reload sshd, and limit port 22 in the cloud firewall to your own
    addresses.

Never run `docker compose down -v` on the server. It deletes the `caddy_data` volume with the
certificates, and issuing them again runs into Let's Encrypt rate limits.

## If the host already runs Caddy

Stop it before the first deploy, and check nothing still holds the ports:

```bash
systemctl disable --now caddy
ss -ltn | grep -E ':(80|443)\b'     # must print nothing
```

If 80 or 443 is still held, `deploy.sh` stops without rolling back. `deploy.sh` only checks
`127.0.0.1:3000`, so always run `curl -sI https://<your-domain>/` after a first deploy.

Next: [Run the worker and turn the weekly loop on](run-the-worker.md).
