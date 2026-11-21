"""M1.1: provider interface and OpenRouter implementation, against an in-process transport."""

import json

import httpx
import openai
import pytest

from llm import (
    CompletionRequest,
    LLMAuthError,
    LLMBadRequest,
    LLMConfigError,
    LLMRateLimit,
    LLMServerError,
    LLMTimeout,
    OpenRouterProvider,
    ProviderSettings,
    parse_usage,
)

SETTINGS = ProviderSettings(api_key="sk-or-secret-123", base_url="http://127.0.0.1:9/v1")
REQ = CompletionRequest(model="google/test", messages=[{"role": "user", "content": "hi"}])


def provider(handler) -> OpenRouterProvider:
    client = openai.OpenAI(
        api_key=SETTINGS.api_key,
        base_url=SETTINGS.base_url,
        max_retries=0,
        http_client=httpx.Client(transport=httpx.MockTransport(handler)),
    )
    return OpenRouterProvider(SETTINGS, client=client)


def ok(request: httpx.Request) -> httpx.Response:
    return httpx.Response(
        200,
        json={
            "model": "google/test-001",
            "choices": [
                {"message": {"role": "assistant", "content": "hello"}, "finish_reason": "stop"}
            ],
            "usage": {
                "prompt_tokens": 10,
                "completion_tokens": 5,
                "total_tokens": 15,
                "cost": 0.0012,
            },
        },
    )


def test_complete_parses_text_usage_cost_and_latency():
    seen = {}

    def handler(request):
        seen["body"] = json.loads(request.content)
        seen["auth"] = request.headers["authorization"]
        return ok(request)

    result = provider(handler).complete(REQ)
    assert result.text == "hello"
    assert result.model == "google/test-001"
    assert (result.usage.prompt_tokens, result.usage.completion_tokens) == (10, 5)
    assert result.usage.total_tokens == 15
    assert result.usage.cost_usd == pytest.approx(0.0012)
    assert result.latency_s >= 0
    assert result.finish_reason == "stop"
    assert seen["body"]["usage"] == {"include": True}
    assert seen["auth"] == "Bearer sk-or-secret-123"


def test_missing_cost_is_none_not_zero():
    assert parse_usage({"prompt_tokens": 3, "completion_tokens": 2}).cost_usd is None
    assert parse_usage(None).total_tokens == 0


@pytest.mark.parametrize(
    "status,exc",
    [
        (429, LLMRateLimit),
        (500, LLMServerError),
        (503, LLMServerError),
        (401, LLMAuthError),
        (400, LLMBadRequest),
    ],
)
def test_http_errors_map_to_typed_errors(status, exc):
    def handler(request):
        return httpx.Response(
            status, json={"error": {"message": "nope"}}, headers={"retry-after": "7"}
        )

    with pytest.raises(exc) as info:
        provider(handler).complete(REQ)
    assert info.value.model == "google/test"
    if status == 429:
        assert info.value.retry_after == 7.0


def test_timeout_maps_to_typed_error():
    def handler(request):
        raise httpx.ReadTimeout("slow", request=request)

    with pytest.raises(LLMTimeout):
        provider(handler).complete(REQ)


def test_settings_prefer_openrouter_key_and_accept_legacy_names():
    legacy = ProviderSettings.from_env({"OPENAI_API_KEY": "k1", "OPENAI_BASE_URL": "http://x/v1"})
    assert (legacy.api_key, legacy.base_url) == ("k1", "http://x/v1")
    new = ProviderSettings.from_env(
        {"OPENROUTER_API_KEY": "k2", "OPENAI_API_KEY": "k1", "LLM_BASE_URL": "http://y/v1"}
    )
    assert (new.api_key, new.base_url) == ("k2", "http://y/v1")
    assert ProviderSettings.from_env({"OPENROUTER_API_KEY": "k"}).base_url.startswith(
        "https://openrouter.ai"
    )
    with pytest.raises(LLMConfigError):
        ProviderSettings.from_env({})


def test_repr_never_contains_the_key():
    assert "sk-or-secret-123" not in repr(SETTINGS)
    assert "sk-or-secret-123" not in repr(provider(ok))
