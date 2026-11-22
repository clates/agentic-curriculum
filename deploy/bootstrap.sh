#!/usr/bin/env bash
# Bootstrap a FRESH Debian/Ubuntu host for the curriculum app. Run once as root, from a checkout
# of this repository (it installs the deploy.sh that sits next to it). Safe to run again.
#
#   sudo deploy/bootstrap.sh --domain homeschool.example.com --ci-public-key ./ci_deploy.pub
#
# Flags:
#   --domain NAME            site name; written into /srv/curriculum/caddy.env (SITE_DOMAIN) and
#                            .env (AUTH_ALLOWED_HOSTS) when those files are created
#   --ci-public-key FILE|KEY the CI deploy PUBLIC key (a file path or the key text itself)
#   --dry-run                print what would be done, change nothing (works without root)
#   -h, --help
set -euo pipefail

APP_DIR=/srv/curriculum
DEPLOY_USER=deploy
DEPLOY_SCRIPT_DEST=/usr/local/sbin/curriculum-deploy.sh
CADDY_ENV="$APP_DIR/caddy.env"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

DOMAIN=""
CI_KEY_ARG=""
DRY_RUN=0

usage() { sed -n '2,13p' "${BASH_SOURCE[0]}" | sed 's/^# \{0,1\}//'; }

while [[ $# -gt 0 ]]; do
  case "$1" in
    --domain) DOMAIN="${2:-}"; shift 2 ;;
    --ci-public-key) CI_KEY_ARG="${2:-}"; shift 2 ;;
    --dry-run) DRY_RUN=1; shift ;;
    -h | --help) usage; exit 0 ;;
    *) echo "unknown argument: $1" >&2; usage >&2; exit 2 ;;
  esac
done

if [[ "$DRY_RUN" -eq 0 && "$(id -u)" -ne 0 ]]; then
  echo "refusing: run as root (sudo $0 ...), or add --dry-run to preview" >&2
  exit 1
fi
if [[ -n "$DOMAIN" && ! "$DOMAIN" =~ ^[A-Za-z0-9]([A-Za-z0-9.-]*[A-Za-z0-9])?$ ]]; then
  echo "refusing: --domain must be a bare host name like homeschool.example.com" >&2
  exit 2
fi

say() { printf '==> %s\n' "$*"; }
# Run a command, or only print it under --dry-run.
run() {
  if [[ "$DRY_RUN" -eq 1 ]]; then printf '[dry-run] %s\n' "$*"; else "$@"; fi
}

# --- CI public key: never invented, must be supplied -------------------------------------
CI_KEY=""
if [[ -n "$CI_KEY_ARG" ]]; then
  if [[ -f "$CI_KEY_ARG" ]]; then CI_KEY="$(head -n 1 "$CI_KEY_ARG")"; else CI_KEY="$CI_KEY_ARG"; fi
  if [[ ! "$CI_KEY" =~ ^(ssh-ed25519|ssh-rsa|ecdsa-sha2-[a-z0-9]+|sk-ssh-ed25519@openssh.com)\ [A-Za-z0-9+/=]+(\ .*)?$ ]]; then
    echo "refusing: --ci-public-key is not a single-line SSH PUBLIC key (private keys are never accepted)" >&2
    exit 2
  fi
fi

[[ -f "$SCRIPT_DIR/deploy.sh" ]] || { echo "deploy.sh not found next to bootstrap.sh" >&2; exit 1; }

# --- 1. Docker Engine + compose plugin ----------------------------------------------------
if command -v docker >/dev/null 2>&1 && docker compose version >/dev/null 2>&1; then
  say "docker and the compose plugin are already installed"
else
  say "installing Docker Engine and the compose plugin (official apt repository)"
  if [[ -r /etc/os-release ]]; then
    # shellcheck disable=SC1091
    OS_ID="$(. /etc/os-release && echo "$ID")"
  elif [[ "$DRY_RUN" -eq 1 ]]; then
    OS_ID=ubuntu # previewing on a non-Linux machine
  else
    echo "cannot read /etc/os-release" >&2; exit 1
  fi
  case "$OS_ID" in debian | ubuntu) ;; *) echo "unsupported OS '$OS_ID' (Debian/Ubuntu only)" >&2; exit 1 ;; esac
  run apt-get update
  run apt-get install -y ca-certificates curl
  run install -m 0755 -d /etc/apt/keyrings
  run curl -fsSL "https://download.docker.com/linux/$OS_ID/gpg" -o /etc/apt/keyrings/docker.asc
  run chmod a+r /etc/apt/keyrings/docker.asc
  if [[ "$DRY_RUN" -eq 1 ]]; then
    echo "[dry-run] write /etc/apt/sources.list.d/docker.list for https://download.docker.com/linux/$OS_ID"
  else
    # shellcheck disable=SC1091
    CODENAME="$(. /etc/os-release && echo "${UBUNTU_CODENAME:-$VERSION_CODENAME}")"
    printf 'deb [arch=%s signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/%s %s stable\n' \
      "$(dpkg --print-architecture)" "$OS_ID" "$CODENAME" > /etc/apt/sources.list.d/docker.list
  fi
  run apt-get update
  run apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
  run systemctl enable --now docker
fi

# --- 2. deploy user ------------------------------------------------------------------------
if id "$DEPLOY_USER" >/dev/null 2>&1; then
  say "user '$DEPLOY_USER' exists; making sure it is in the docker group"
  run usermod -aG docker "$DEPLOY_USER"
else
  say "creating user '$DEPLOY_USER' (docker group, no password, key login only)"
  run useradd --create-home --shell /bin/bash --groups docker "$DEPLOY_USER"
  # '*' = no password can ever match, but the account is not locked, so sshd accepts the key.
  run usermod --password '*' "$DEPLOY_USER"
fi

# --- 3. directories --------------------------------------------------------------------------
say "creating $APP_DIR/{data,artifacts,logs}"
run mkdir -p "$APP_DIR/data" "$APP_DIR/artifacts" "$APP_DIR/logs"
run chown "$DEPLOY_USER:$DEPLOY_USER" "$APP_DIR"
# The container's app user is uid 1000, same as deploy.sh's chown.
run chown 1000:1000 "$APP_DIR/data" "$APP_DIR/artifacts" "$APP_DIR/logs"

# --- 4. deploy script (root-owned: the deploy user must not be able to edit it) ---------------
say "installing $DEPLOY_SCRIPT_DEST (root:root 755)"
run install -o root -g root -m 755 "$SCRIPT_DIR/deploy.sh" "$DEPLOY_SCRIPT_DEST"

# --- 5. CI key, restricted to the deploy script ------------------------------------------------
if [[ -n "$CI_KEY" ]]; then
  say "authorizing the CI key (restricted to $DEPLOY_SCRIPT_DEST)"
  SSH_DIR="/home/$DEPLOY_USER/.ssh"
  AUTH="$SSH_DIR/authorized_keys"
  KEY_BLOB="$(echo "$CI_KEY" | awk '{print $2}')"
  LINE="command=\"$DEPLOY_SCRIPT_DEST\",restrict $CI_KEY"
  if [[ "$DRY_RUN" -eq 1 ]]; then
    echo "[dry-run] append to $AUTH (unless that key is already present):"
    echo "[dry-run]   command=\"$DEPLOY_SCRIPT_DEST\",restrict ${CI_KEY%% *} ${KEY_BLOB:0:12}..."
  else
    install -d -o "$DEPLOY_USER" -g "$DEPLOY_USER" -m 700 "$SSH_DIR"
    touch "$AUTH"
    if grep -qF -- "$KEY_BLOB" "$AUTH"; then
      echo "key already present, leaving authorized_keys alone"
    else
      echo "$LINE" >> "$AUTH"
    fi
    chown "$DEPLOY_USER:$DEPLOY_USER" "$AUTH"
    chmod 600 "$AUTH"
  fi
else
  say "no --ci-public-key given: skipping authorized_keys (re-run with the flag to add it)"
fi

# --- 6. .env skeleton (never overwritten) -----------------------------------------------------
ENV_FILE="$APP_DIR/.env"
if [[ -e "$ENV_FILE" ]]; then
  say "$ENV_FILE exists; not touching it"
elif [[ "$DRY_RUN" -eq 1 ]]; then
  say "would write $ENV_FILE skeleton (mode 600, owner $DEPLOY_USER)"
else
  say "writing $ENV_FILE skeleton (mode 600)"
  if [[ -n "$DOMAIN" ]]; then
    DOMAIN_LINES="AUTH_ALLOWED_HOSTS=$DOMAIN"
  else
    DOMAIN_LINES="#AUTH_ALLOWED_HOSTS=homeschool.example.com"
  fi
  umask 077
  cat > "$ENV_FILE" <<ENVEOF
# Secrets and site settings for the curriculum stack. Never commit this file.
# After editing: cd $APP_DIR && docker compose --env-file .deploy.env up -d --force-recreate
# (a plain restart does not re-read it)

# Model access (required for plan generation)
#OPENROUTER_API_KEY=sk-or-...

# The public host name: login/change requests must come from it. Same name as SITE_DOMAIN in
# caddy.env (Caddy's own env file; kept separate so the web-facing process never sees this file).
$DOMAIN_LINES

# Login on, cookies HTTPS-only. Make the first account after the first deploy (see docs/runbook-https.md).
AUTH_REQUIRED=1
COOKIE_SECURE=1
ENVEOF
  chown "$DEPLOY_USER:$DEPLOY_USER" "$ENV_FILE"
  chmod 600 "$ENV_FILE"
fi

if [[ -n "$DOMAIN" ]]; then
  ENV_TODO="set OPENROUTER_API_KEY (AUTH_ALLOWED_HOSTS is already $DOMAIN; $CADDY_ENV holds SITE_DOMAIN)."
else
  ENV_TODO="set OPENROUTER_API_KEY and AUTH_ALLOWED_HOSTS, and create $CADDY_ENV with: printf 'SITE_DOMAIN=<your-domain>\\n' > $CADDY_ENV"
fi

# --- 7. caddy.env: the only thing the internet-facing container may read ---------------------
if [[ -e "$CADDY_ENV" ]]; then
  say "$CADDY_ENV exists; not touching it"
elif [[ -z "$DOMAIN" ]]; then
  say "no --domain given: not writing $CADDY_ENV (Caddy serves a localhost site until you create it)"
elif [[ "$DRY_RUN" -eq 1 ]]; then
  say "would write $CADDY_ENV (mode 640, owner $DEPLOY_USER) with SITE_DOMAIN=$DOMAIN"
else
  say "writing $CADDY_ENV (mode 640)"
  printf 'SITE_DOMAIN=%s\n' "$DOMAIN" > "$CADDY_ENV"
  chown "$DEPLOY_USER:$DEPLOY_USER" "$CADDY_ENV"
  chmod 640 "$CADDY_ENV"
fi

# --- done ---------------------------------------------------------------------------------------
cat <<DONE

Bootstrap finished. What remains manual:
  1. Edit $ENV_FILE: $ENV_TODO
  2. DNS: add an A record  ${DOMAIN:-<your-domain>}  ->  this server's public IPv4 (and AAAA only if
     you have enabled IPv6 for Docker; see deploy/README.md).
  3. Firewall: allow inbound TCP 80 and 443 in the CLOUD firewall (Docker-published ports bypass
     ufw). Do NOT open 3000 or 8181.
  4. GitHub repo secrets: DEPLOY_HOST, DEPLOY_SSH_KEY (private half of the CI key),
     DEPLOY_KNOWN_HOSTS (output of: ssh-keyscan -t ed25519 <server>), DOCKERHUB_USERNAME,
     DOCKERHUB_TOKEN.
  5. First deploy: push to main (or re-run the deploy workflow). Caddy fetches the certificate on
     first start; it needs DNS and ports 80/443 working.
  6. Create the first user (prompts for the password, twice):
       cd $APP_DIR && docker compose --env-file .deploy.env exec -u appuser app python -m auth create-user <username>
DONE
