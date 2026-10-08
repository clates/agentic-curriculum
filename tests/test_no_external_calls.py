"""Structural guards: the code base has one LLM call site and one outbound-HTTP module, and both
honour env-configurable endpoints so tests and E2E can redirect them to local stubs.

If one of these fails you added a new way to reach an external service. Route it through the
existing, env-driven client (or extend this allow-list deliberately, together with the stub).
"""

import os
import re
import socket
from pathlib import Path

import pytest

from tests.conftest import ExternalNetworkBlocked

SRC = Path(__file__).resolve().parents[1] / "src"

# Modules allowed to make outbound HTTP calls, and the env var that redirects each one.
OUTBOUND_HTTP_ALLOWLIST = {"ntfy.py": "NTFY_URL"}

HTTP_CLIENT_PATTERN = re.compile(
    r"^\s*(?:import|from)\s+(requests|httpx|aiohttp|urllib\.request|http\.client|smtplib)\b",
    re.MULTILINE,
)
OTHER_LLM_SDK_PATTERN = re.compile(
    r"^\s*(?:import|from)\s+(anthropic|litellm|cohere|mistralai|groq|google\.generativeai|"
    r"langchain\w*|ollama|replicate)\b",
    re.MULTILINE,
)
HARDCODED_LLM_HOST_PATTERN = re.compile(
    r"(api\.openai\.com|openrouter\.ai|api\.anthropic\.com|generativelanguage\.googleapis)"
)


def _source_files():
    return sorted(p for p in SRC.rglob("*.py") if "__pycache__" not in p.parts)


def test_exactly_one_openai_client_and_it_honours_base_url():
    constructions = []
    for path in _source_files():
        text = path.read_text(encoding="utf-8")
        for match in re.finditer(r"\bOpenAI\(", text):
            constructions.append((path.name, text[: match.start()].count("\n") + 1))
    assert [name for name, _ in constructions] == [
        "agent.py"
    ], f"expected exactly one OpenAI( construction in src/agent.py, found: {constructions}"

    agent = (SRC / "agent.py").read_text(encoding="utf-8")
    assert 'os.environ.get("OPENAI_BASE_URL"' in agent
    assert re.search(
        r"OpenAI\(\s*api_key=[^)]*base_url=base_url", agent
    ), "the OpenAI client must be built with base_url taken from OPENAI_BASE_URL"
    assert 'os.environ.get("OPENAI_API_KEY")' in agent


def test_no_other_llm_sdk_or_hardcoded_llm_host():
    offenders = []
    for path in _source_files():
        text = path.read_text(encoding="utf-8")
        if OTHER_LLM_SDK_PATTERN.search(text) or HARDCODED_LLM_HOST_PATTERN.search(text):
            offenders.append(path.name)
    assert not offenders, f"unexpected LLM SDK / hardcoded LLM host in: {offenders}"


def test_outbound_http_only_from_allowlisted_env_driven_modules():
    offenders = [
        path.name
        for path in _source_files()
        if HTTP_CLIENT_PATTERN.search(path.read_text(encoding="utf-8"))
        and path.name not in OUTBOUND_HTTP_ALLOWLIST
    ]
    assert not offenders, f"HTTP client imported outside the allow-list: {offenders}"

    for name, env_var in OUTBOUND_HTTP_ALLOWLIST.items():
        assert env_var in (SRC / name).read_text(
            encoding="utf-8"
        ), f"{name} must read its endpoint from ${env_var}"


def test_hermetic_env_is_applied_to_every_test():
    assert os.environ["OPENAI_BASE_URL"].startswith("http://127.0.0.1:")
    assert os.environ["NTFY_URL"].startswith("http://127.0.0.1:")
    assert os.environ["OPENAI_API_KEY"] == "pytest-not-a-real-key"


def test_socket_guard_blocks_non_loopback_hosts():
    with pytest.raises(ExternalNetworkBlocked):
        socket.getaddrinfo("example.com", 443)
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        with pytest.raises(ExternalNetworkBlocked):
            sock.connect(("93.184.216.34", 80))
    finally:
        sock.close()
