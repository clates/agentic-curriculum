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
    assert {"0.0.0.0:80:80", "0.0.0.0:443:443"} <= set(caddy["ports"])
    assert not any(str(p).startswith(("80:", "443:")) for p in caddy["ports"])  # no dual-stack
    assert "no-new-privileges:true" in caddy["security_opt"]
    assert caddy["cap_drop"] == ["ALL"] and caddy["cap_add"] == ["NET_BIND_SERVICE"]
    assert "app" in caddy["depends_on"]
    # The internet-facing process must never get the app's secrets (.env), only caddy.env.
    env_files = caddy["env_file"]
    paths = [e["path"] if isinstance(e, dict) else e for e in env_files]
    assert paths == ["caddy.env"]
    assert env_files[0].get("required") is False


def test_worker_runs_the_loop_as_appuser_on_the_apps_data_and_stays_off_the_internet():
    doc = _compose()["services"]
    worker, app = doc["worker"], doc["app"]
    assert worker["image"] == app["image"]
    assert worker["command"] == ["python", "-m", "worker", "--scheduler"]
    # Not root: root-owned SQLite WAL files in /data would lock the app (uid 1000) out of its DB.
    assert worker["user"] == "1000:1000"
    assert "ports" not in worker and worker["restart"] == "unless-stopped"
    assert worker["env_file"] == app["env_file"]  # the one LOOP_JOBS_ENABLED switch is in .env
    assert worker["environment"]["CURRICULUM_DB_PATH"] == app["environment"]["CURRICULUM_DB_PATH"]
    assert worker["environment"]["WORKER_HANDLER_MODULES"] == "job_handlers_real"
    assert "LOOP_JOBS_ENABLED" not in worker["environment"]  # off until the server's .env says so
    assert set(worker["volumes"]) >= {v for v in app["volumes"] if "/data" in v}
    assert worker["stop_grace_period"] == "45s"


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
    for header in ("X-Frame-Options DENY", "frame-ancestors", "Permissions-Policy"):
        assert header in content
    assert "read_header 10s" in content


def test_access_log_is_json_rotated_in_the_persistent_volume_and_never_holds_credentials():
    doc = _compose()
    caddy = doc["services"]["caddy"]
    content = doc["configs"][caddy["configs"][0]["source"]]["content"]
    assert "output file /data/access.log" in content
    assert any(v.startswith("caddy_data:/data") for v in caddy["volumes"])  # survives redeploys
    assert (
        "roll_size 20MiB" in content
        and "roll_keep 10" in content
        and "roll_keep_for 720h" in content
    )
    assert "wrap json" in content
    for field in (
        "request>headers>Cookie",
        "request>headers>Authorization",
        "resp_headers>Set-Cookie",
    ):
        assert f"{field} delete" in content


def test_every_container_log_is_size_capped():
    services = _compose()["services"]
    assert set(services) >= {"app", "worker", "caddy"}
    for name, svc in services.items():
        opts = svc["logging"]["options"]
        assert svc["logging"]["driver"] == "json-file", name
        assert opts["max-size"] == "10m" and opts["max-file"] == "3", name


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
