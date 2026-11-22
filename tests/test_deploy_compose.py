"""Guards the HTTPS shape of deploy/docker-compose.yml (Caddy in the stack, inline config)."""

from pathlib import Path

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
    assert caddy["env_file"] == ".env"


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
