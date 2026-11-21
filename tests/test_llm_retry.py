"""M1.4: one retry layer with backoff, optional fallback model, typed errors."""

import pytest

from llm import (
    LLMAuthError,
    LLMClient,
    LLMRateLimit,
    LLMServerError,
    LLMTimeout,
    RetryPolicy,
    task_config,
)
from tests.llm_provider_fakes import ScriptedProvider

MSGS = [{"role": "user", "content": "x"}]
POLICY = RetryPolicy(max_attempts=3, base_delay_s=1.0, max_delay_s=4.0, jitter=0.0)


def client(*script, env=None, sleeps=None):
    provider = ScriptedProvider(*script)
    sleeps = sleeps if sleeps is not None else []
    return provider, LLMClient(provider, env=env or {}, policy=POLICY, sleep=sleeps.append)


def test_retries_transient_errors_then_succeeds_with_backoff():
    sleeps = []
    provider, c = client(LLMServerError("500"), LLMTimeout("slow"), "ok", sleeps=sleeps)
    assert c.complete("judge", MSGS).text == "ok"
    assert len(provider.requests) == 3
    assert sleeps == [1.0, 2.0]  # exponential


def test_rate_limit_honours_retry_after_capped():
    sleeps = []
    _, c = client(
        LLMRateLimit("429", retry_after=3), LLMRateLimit("429", retry_after=99), "ok", sleeps=sleeps
    )
    c.complete("judge", MSGS)
    assert sleeps == [3.0, 4.0]


def test_non_retryable_errors_surface_immediately():
    provider, c = client(LLMAuthError("401"), "never")
    with pytest.raises(LLMAuthError) as info:
        c.complete("judge", MSGS)
    assert len(provider.requests) == 1 and info.value.attempts == 1


def test_exhaustion_raises_last_typed_error_with_attempt_count():
    env = {"LLM_FALLBACK_MODEL_OUTLINE": ""}
    provider, c = client(
        *[LLMServerError("500") for _ in range(3)], env={**env, "LLM_MODEL": "a/one"}
    )
    with pytest.raises(LLMServerError) as info:
        c.complete("outline", MSGS)
    assert info.value.attempts == 3 and len(provider.requests) == 3


def test_fallback_model_used_after_primary_exhausted():
    env = {"LLM_MODEL_JUDGE": "a/primary", "LLM_FALLBACK_MODEL_JUDGE": "b/fallback"}
    provider, c = client(*[LLMServerError("500")] * 3, "from fallback", env=env)
    result = c.complete("judge", MSGS)
    assert result.text == "from fallback"
    assert [r.model for r in provider.requests] == ["a/primary"] * 3 + ["b/fallback"]


def test_both_models_failing_reports_total_attempts():
    env = {"LLM_MODEL_JUDGE": "a/primary", "LLM_FALLBACK_MODEL_JUDGE": "b/fallback"}
    provider, c = client(*[LLMTimeout("t") for _ in range(6)], env=env)
    with pytest.raises(LLMTimeout) as info:
        c.complete("judge", MSGS)
    assert info.value.attempts == 6 and info.value.model == "b/fallback"


def test_no_fallback_when_it_equals_primary():
    cfg = task_config("judge", env={"LLM_MODEL_JUDGE": "x/y", "LLM_FALLBACK_MODEL_JUDGE": "x/y"})
    assert cfg.fallback_model is None


def test_max_attempts_env():
    provider = ScriptedProvider(LLMServerError("1"), LLMServerError("2"))
    c = LLMClient(
        provider,
        env={"LLM_MAX_ATTEMPTS": "1", "LLM_MODEL": "a/b", "LLM_FALLBACK_MODEL_JUDGE": ""},
        sleep=lambda s: None,
    )
    with pytest.raises(LLMServerError):
        c.complete("judge", MSGS)
    assert len(provider.requests) == 1
