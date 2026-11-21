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
3. pulls `chrislates/agentic-curriculum:<sha>` and restarts the container,
4. waits for the app to answer on `127.0.0.1:3000`,
5. on failure, restarts the previous SHA and exits non-zero (the GitHub job fails).

## Server layout (`/srv/curriculum`)

| Path | What |
|---|---|
| `data/curriculum.db` | SQLite database (bind mount, survives redeploys) |
| `artifacts/`, `logs/` | Generated worksheets and logs (bind mounts) |
| `.env` | Secrets, for example `OPENAI_API_KEY`. Never committed. |
| `current_sha` | Last successfully deployed commit |

The app listens on `127.0.0.1:3000` only. Nothing is exposed publicly until the hosted
product has accounts; reach it over Tailscale or an SSH tunnel
(`ssh -L 3000:127.0.0.1:3000 deploy@<server>`).

## GitHub secrets

| Secret | Value |
|---|---|
| `DOCKERHUB_USERNAME`, `DOCKERHUB_TOKEN` | Docker Hub login (already present) |
| `DEPLOY_HOST` | Server address |
| `DEPLOY_SSH_KEY` | Private half of the CI deploy key |
| `DEPLOY_KNOWN_HOSTS` | The server's `ssh-keyscan -t ed25519` line, so CI verifies the host |

## One-time server setup

Done once by hand as root:

```bash
# deploy script (root-owned, so the deploy user cannot modify it)
install -o root -g root -m 755 deploy/deploy.sh /usr/local/sbin/curriculum-deploy.sh

# CI key in /home/deploy/.ssh/authorized_keys, restricted to that script:
command="/usr/local/sbin/curriculum-deploy.sh",restrict ssh-ed25519 AAAA... ci-deploy
```

Changes to `deploy.sh` are reinstalled by hand. CI deliberately cannot update it, since it
is the security boundary for the CI key.

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
