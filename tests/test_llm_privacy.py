"""M1.8: the API key never reaches logs; no-retention routing; docs name the key."""

import json
import logging
from pathlib import Path

import httpx2
import openai
import pytest

from llm import (
    CompletionRequest,
    LLMClient,
    LLMConfigError,
    LLMServerError,
    OpenRouterProvider,
    ProviderSettings,
    privacy_mode,
    redact,
    routing_preferences,
)

KEY = "sk-or-v1-0123456789abcdefSECRETKEYVALUE"
ROOT = Path(__file__).resolve().parents[1]


def provider(handler, settings=None):
    settings = settings or ProviderSettings(api_key=KEY, base_url="http://127.0.0.1:9/v1")
    client = openai.OpenAI(
        api_key=KEY,
        base_url=settings.base_url,
        max_retries=0,
        http_client=httpx2.Client(transport=httpx2.MockTransport(handler)),
    )
    return OpenRouterProvider(settings, client=client)


def test_key_never_appears_in_any_log_even_on_errors(monkeypatch, caplog):
    monkeypatch.setenv("OPENROUTER_API_KEY", KEY)
    caplog.set_level(logging.DEBUG)  # every logger, including openai and httpx

    def leaky(request):
        # A hostile/buggy upstream that echoes the Authorization header back in its error.
        body = {"error": {"message": f"bad key {request.headers['authorization']}"}}
        return httpx2.Response(401, json=body)

    client = LLMClient(provider(leaky), env={})
    with pytest.raises(Exception) as info:
        client.complete("judge", [{"role": "user", "content": "hi"}])
    logging.getLogger("llm.test").warning("calling with key %s", KEY)
    logging.getLogger("llm.test").error("failure", exc_info=info.value)
    assert KEY not in caplog.text
    assert KEY not in str(info.value)
    assert "SECRETKEYVALUE" not in caplog.text
    assert "calling with key [redacted]" in caplog.text


def test_exception_tracebacks_are_scrubbed(monkeypatch, caplog):
    monkeypatch.setenv("OPENROUTER_API_KEY", KEY)
    LLMClient(provider(lambda r: httpx2.Response(200)), env={})  # installs the redaction
    try:
        raise RuntimeError(f"upstream said {KEY}")
    except RuntimeError:
        logging.getLogger("x").exception("boom")
    assert KEY not in caplog.text and "[redacted]" in caplog.text


def test_redact_handles_configured_and_key_shaped_values(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "custom-endpoint-key-123")
    assert "custom-endpoint-key-123" not in redact("k=custom-endpoint-key-123")
    assert (
        redact("Authorization: Bearer abcdefghijklmnop1234") == "Authorization: Bearer [redacted]"
    )
    assert redact("plain text") == "plain text"


def test_provider_error_messages_never_contain_the_key():
    def handler(request):
        return httpx2.Response(500, json={"error": {"message": f"oops {KEY}"}})

    with pytest.raises(LLMServerError) as info:
        provider(handler).complete(CompletionRequest("m/x", [{"role": "user", "content": "a"}]))
    assert KEY not in str(info.value)


def test_privacy_defaults_off_for_self_hosters_and_strict_when_hosted():
    assert privacy_mode({}) == "off"
    assert privacy_mode({"AGENTIC_HOSTED": "1"}) == "strict"
    assert privacy_mode({"AGENTIC_HOSTED": "1", "LLM_PRIVACY_ROUTING": "off"}) == "off"
    assert privacy_mode({"LLM_PRIVACY_ROUTING": "no-training"}) == "no-training"
    with pytest.raises(LLMConfigError):
        privacy_mode({"LLM_PRIVACY_ROUTING": "maybe"})


def test_strict_routing_is_sent_with_every_request():
    seen = []

    def handler(request):
        seen.append(json.loads(request.content))
        return httpx2.Response(
            200, json={"choices": [{"message": {"content": "x"}, "finish_reason": "stop"}]}
        )

    settings = ProviderSettings.from_env(
        {"OPENROUTER_API_KEY": KEY, "AGENTIC_HOSTED": "1", "LLM_BASE_URL": "http://127.0.0.1:9/v1"}
    )
    provider(handler, settings).complete(
        CompletionRequest("m/x", [{"role": "user", "content": "a"}])
    )
    assert seen[0]["provider"] == {"data_collection": "deny", "zdr": True}
    assert routing_preferences("off") == {}

    seen.clear()
    off = ProviderSettings.from_env(
        {"OPENROUTER_API_KEY": KEY, "LLM_BASE_URL": "http://127.0.0.1:9/v1"}
    )
    provider(handler, off).complete(CompletionRequest("m/x", [{"role": "user", "content": "a"}]))
    assert "provider" not in seen[0]


def test_docs_and_env_example_document_the_key_and_privacy_routing():
    example = (ROOT / ".env.example").read_text()
    for name in (
        "OPENROUTER_API_KEY",
        "LLM_PRIVACY_ROUTING",
        "AGENTIC_HOSTED",
        "LLM_CAP_FAMILY_MONTH_USD",
    ):
        assert name in example
    assert "sk-or-" not in example.replace("sk-or-...", "")
    contributing = (ROOT / "CONTRIBUTING.md").read_text()
    assert "OPENROUTER_API_KEY" in contributing and "LLM_PRIVACY_ROUTING" in contributing
