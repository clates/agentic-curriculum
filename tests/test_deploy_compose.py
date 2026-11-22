"""Guards the HTTPS shape of deploy/docker-compose.yml (Caddy in the stack, inline config)."""

import json
import shutil
import subprocess
from pathlib import Path

import pytest
import yaml

COMPOSE = Path(__file__).resolve().parent.parent / "deploy" / "docker-compose.yml"


def _compose() -> dict:
    return yaml.safe_load(COMPOSE.read_text())


def test_caddy_service_is_pinned_and_publishes_web_ports():
    caddy = _compose()["services"]["caddy"]
    image = caddy["image"]
    assert image.startswith("caddy:2.") and not image.endswith(":latest")
    assert caddy["restart"] == "unless-stopped"
    assert {"80:80", "443:443"} <= set(caddy["ports"])
    assert "app" in caddy["depends_on"]
    # The internet-facing process must never get the app's secrets (.env), only caddy.env.
    env_files = caddy["env_file"]
    paths = [e["path"] if isinstance(e, dict) else e for e in env_files]
    assert paths == ["caddy.env"]
    assert env_files[0].get("required") is False


def test_caddyfile_is_inline_and_proxies_to_the_app():
    doc = _compose()
    caddy = doc["services"]["caddy"]
    assert caddy["configs"][0]["target"] == "/etc/caddy/Caddyfile"
    content = doc["configs"][caddy["configs"][0]["source"]]["content"]
    # `$$` in the YAML source renders as one `$`; PyYAML shows the raw text, so check both.
    assert "{$$SITE_DOMAIN:localhost}" in content
    assert "reverse_proxy app:3000" in content
    assert "header_up X-Forwarded-For {remote_host}" in content
    assert "header_up X-Forwarded-Proto {scheme}" in content
    assert "max_size 10MB" in content
    assert "Strict-Transport-Security" in content


def test_app_keeps_loopback_binding_for_deploy_probe():
    assert "127.0.0.1:3000:3000" in _compose()["services"]["app"]["ports"]


def test_certificates_live_in_named_volumes():
    doc = _compose()
    mounts = doc["services"]["caddy"]["volumes"]
    assert "caddy_data:/data" in mounts and "caddy_config:/config" in mounts
    assert {"caddy_data", "caddy_config"} <= set(doc["volumes"])


# --- Real validation, only where Docker works (GitHub's ubuntu runners have it) ---------------


def _docker_ok() -> bool:
    if not shutil.which("docker"):
        return False
    try:
        r = subprocess.run(["docker", "compose", "version"], capture_output=True, timeout=30)
    except (OSError, subprocess.SubprocessError):
        return False
    return r.returncode == 0


needs_docker = pytest.mark.skipif(not _docker_ok(), reason="docker compose not available")


@needs_docker
def test_compose_renders_and_caddyfile_validates(tmp_path):
    # Copy the file next to an empty .env (the app's env_file is required); caddy.env stays absent
    # on purpose, which also proves `required: false` lets the stack render without it.
    shutil.copy(COMPOSE, tmp_path / "docker-compose.yml")
    (tmp_path / ".env").write_text("")
    sample = tmp_path / "deploy.env"
    sample.write_text("IMAGE=example/app:test\n")
    r = subprocess.run(
        ["docker", "compose", "--env-file", str(sample), "-f", "docker-compose.yml",
         "config", "--format", "json"],
        cwd=tmp_path, capture_output=True, text=True, timeout=60,
    )  # fmt: skip
    assert r.returncode == 0, r.stderr
    rendered = json.loads(r.stdout)
    # `config` re-escapes `$` as `$$` in its output; undo that to get what the container reads.
    content = rendered["configs"]["caddyfile"]["content"].replace("$$", "$")
    # Proves the `$$` in the source survived interpolation (a bare `$` would have been emptied).
    assert "{$SITE_DOMAIN:localhost}" in content

    caddyfile = tmp_path / "Caddyfile"
    caddyfile.write_text(content)
    try:
        v = subprocess.run(
            ["docker", "run", "--rm", "-e", "SITE_DOMAIN=example.com",
             "-v", f"{caddyfile}:/etc/caddy/Caddyfile:ro", "caddy:2.10",
             "caddy", "validate", "--config", "/etc/caddy/Caddyfile", "--adapter", "caddyfile"],
            capture_output=True, text=True, timeout=300,
        )  # fmt: skip
    except subprocess.TimeoutExpired:
        pytest.skip("caddy image could not be pulled in time")
    pull_failed = "Unable to find image" in v.stderr and "Error response" in v.stderr
    if v.returncode != 0 and (pull_failed or "pull access denied" in v.stderr):
        pytest.skip(f"caddy image could not be pulled: {v.stderr[-200:]}")
    assert v.returncode == 0, v.stderr
