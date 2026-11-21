#!/usr/bin/env bash
# Server-side deploy script, installed root-owned at /usr/local/sbin/curriculum-deploy.sh
# (a directory the deploy user cannot write to).
#
# This is the ONLY thing the CI key may run: authorized_keys pins it with
#   command="/usr/local/sbin/curriculum-deploy.sh",restrict ssh-ed25519 AAAA... ci-deploy
# so the SSH client's argument arrives in SSH_ORIGINAL_COMMAND and must be a 40-char
# commit SHA. Anything else is rejected. Because this file is the security boundary,
# changes to it are installed by hand as root (see deploy/README.md), not by CI.
set -euo pipefail

APP_DIR=/srv/curriculum
IMAGE_REPO=chrislates/agentic-curriculum
RAW_BASE=https://raw.githubusercontent.com/clates/agentic-curriculum

SHA="${SSH_ORIGINAL_COMMAND:-${1:-}}"
if [[ ! "$SHA" =~ ^[0-9a-f]{40}$ ]]; then
  echo "refusing: argument must be a 40-character commit SHA" >&2
  exit 2
fi

cd "$APP_DIR"
exec 9>.deploy.lock
flock -n 9 || { echo "another deploy is running" >&2; exit 3; }

PREV="$(cat current_sha 2>/dev/null || true)"
echo "deploying $SHA (previous: ${PREV:-none})"

# Compose file comes from the same commit as the image, so they cannot drift apart.
curl -fsSL "$RAW_BASE/$SHA/deploy/docker-compose.yml" -o docker-compose.yml.new
mv docker-compose.yml.new docker-compose.yml
mkdir -p artifacts logs data
chown 1000:1000 artifacts logs data 2>/dev/null || true

compose() { docker compose --env-file .deploy.env "$@"; }

printf 'IMAGE=%s:%s\n' "$IMAGE_REPO" "$SHA" > .deploy.env
compose pull
compose up -d --remove-orphans

healthy=""
for _ in $(seq 1 30); do
  if curl -fsS -o /dev/null http://127.0.0.1:3000/api/health; then healthy=1; break; fi
  sleep 4
done

if [[ -n "$healthy" ]]; then
  echo "$SHA" > current_sha
  # Keep only the new image and the previous one (for rollback). Each image is ~3 GB, and the
  # plain `image prune` only removes dangling layers, so old tags used to fill the disk.
  docker images --format '{{.Repository}}:{{.Tag}}' \
    | grep -F "$IMAGE_REPO:" \
    | grep -v -F -e "$IMAGE_REPO:$SHA" ${PREV:+-e "$IMAGE_REPO:$PREV"} \
    | xargs -r docker rmi >/dev/null 2>&1 || true
  docker image prune -f >/dev/null
  echo "deploy ok: $SHA"
  exit 0
fi

echo "health check failed for $SHA" >&2
compose logs --tail 50 app >&2 || true
if [[ -n "$PREV" ]]; then
  echo "rolling back to $PREV" >&2
  printf 'IMAGE=%s:%s\n' "$IMAGE_REPO" "$PREV" > .deploy.env
  compose up -d --remove-orphans
fi
exit 1
