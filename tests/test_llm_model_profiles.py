"""Per-model sampling and output limits: applied to author AND repair calls, per model."""

import json

import httpx
import openai
import pytest
from pydantic import BaseModel

from llm import (
    CompletionRequest,
    LLMClient,
    LLMServerError,
    OpenRouterProvider,
    ProviderSettings,
    generate_structured,
    task_config,
)
from llm.ledger import CostCapExceeded, RunBudget, UsageContext
from tests.llm_provider_fakes import ScriptedProvider


class Out(BaseModel):
    n: int


GOOD, BAD = '{"n": 1}', '{"n": "x"}'

EXPECTED = {
    "tencent/hy4": (0.9, 1.0, None),
    "~deepseek/deepseek-v4-flash-latest": (1.0, 1.0, None),
    "deepseek/deepseek-v4-flash": (1.0, 1.0, None),
    "z-ai/glm-5.3": (1.0, 0.95, None),
    "z-ai/glm-5.3-flash": (1.0, 0.95, None),
    "qwen/qwen3.8-flash": (1.0, 0.95, 20),
    "openai/gpt-6-luna": (None, None, None),
    "meta/muse-ember": (None, None, None),
}


def run(model, *script, env=None):
    provider = ScriptedProvider(*script)
    client = LLMClient(provider, env={"LLM_MODEL_AUTHOR": model, **(env or {})})
    generate_structured("author", [{"role": "user", "content": "x"}], Out, client=client,
                        max_repairs=2)
    return provider.requests


@pytest.mark.parametrize("model", sorted(EXPECTED))
def test_author_and_repair_requests_carry_the_models_own_sampling(model):
    temp, top_p, top_k = EXPECTED[model]
    reqs = run(model, BAD, GOOD)
    assert len(reqs) == 2  # author, then one repair
    for req in reqs:
        assert (req.model, req.temperature, req.top_p, req.top_k) == (model, temp, top_p, top_k)
    assert reqs[0].max_tokens == reqs[1].max_tokens > 0


def test_repair_uses_the_author_model_not_the_repair_task_model():
    reqs = run("z-ai/glm-5.3", BAD, GOOD, env={"LLM_MODEL_REPAIR": "other/model"})
    assert {r.model for r in reqs} == {"z-ai/glm-5.3"}


def test_default_author_model_and_fallback_and_ceiling():
    cfg = task_config("author", env={})
    assert cfg.model == "z-ai/glm-5.3" and cfg.fallback_model == "z-ai/glm-5.3-flash"
    assert cfg.max_tokens == 131072  # 943718 vendor max, capped by the task ceiling
    assert task_config("author", env={"LLM_MODEL_AUTHOR": "tencent/hy4"}).max_tokens == 65536
    assert task_config("author", env={"LLM_MAX_TOKENS_AUTHOR": "5000"}).max_tokens == 5000


def test_env_overrides_models_and_temperature():
    cfg = task_config("author", env={"LLM_MODEL_AUTHOR": "m/x", "LLM_FALLBACK_MODEL_AUTHOR": ""})
    assert cfg.model == "m/x" and cfg.fallback_model is None and cfg.temperature == 0.7
    assert task_config("author", env={"LLM_TEMPERATURE_AUTHOR": "0.2"}).temperature == 0.2


def test_fallback_model_gets_its_own_sampling():
    class Flaky(ScriptedProvider):
        pass

    provider = Flaky(LLMServerError("boom"), LLMServerError("boom"), GOOD)
    client = LLMClient(provider, env={"LLM_MAX_ATTEMPTS": "2"}, sleep=lambda _s: None)
    client.complete("author", [{"role": "user", "content": "x"}])
    primary, fallback = provider.requests[0], provider.requests[-1]
    assert primary.model == "z-ai/glm-5.3" and fallback.model == "z-ai/glm-5.3-flash"
    assert (fallback.temperature, fallback.top_p) == (1.0, 0.95)
    qwen = LLMClient(
        ScriptedProvider(LLMServerError("x"), GOOD),
        env={"LLM_MODEL_AUTHOR": "z-ai/glm-5.3", "LLM_FALLBACK_MODEL_AUTHOR": "qwen/qwen3.8-flash",
             "LLM_MAX_ATTEMPTS": "1"},
        sleep=lambda _s: None,
    )
    qwen.complete("author", [{"role": "user", "content": "x"}])
    assert (qwen.provider.requests[-1].top_k, qwen.provider.requests[-1].model) == (
        20, "qwen/qwen3.8-flash")


def _payload_of(request: CompletionRequest) -> dict:
    seen = {}

    def handler(req: httpx.Request) -> httpx.Response:
        seen.update(json.loads(req.content))
        return httpx.Response(200, json={"model": "m", "choices": [
            {"message": {"role": "assistant", "content": "{}"}, "finish_reason": "stop"}],
            "usage": {}})

    settings = ProviderSettings(api_key="k", base_url="http://127.0.0.1:9/v1")
    client = openai.OpenAI(api_key="k", base_url=settings.base_url, max_retries=0,
                           http_client=httpx.Client(transport=httpx.MockTransport(handler)))
    OpenRouterProvider(settings, client=client).complete(request)
    return seen


def test_wire_format_top_p_top_k_in_body_and_no_temperature_when_none():
    base = dict(model="m", messages=[{"role": "user", "content": "x"}])
    body = _payload_of(CompletionRequest(**base, temperature=1.0, top_p=0.95, top_k=20))
    assert body["temperature"] == 1.0 and body["top_p"] == 0.95 and body["top_k"] == 20
    body = _payload_of(CompletionRequest(**base))
    assert "temperature" not in body and "top_p" not in body and "top_k" not in body


def test_run_budget_halts_before_the_next_call_and_meters_calls():
    budget = RunBudget(limit_usd=0.0015)
    provider = ScriptedProvider(BAD, BAD, GOOD, cost=0.001)
    client = LLMClient(provider, env={"LLM_MODEL_AUTHOR": "z-ai/glm-5.3"})
    with pytest.raises(CostCapExceeded):
        generate_structured("author", [{"role": "user", "content": "x"}], Out, client=client,
                            max_repairs=4, usage=UsageContext(budget=budget))
    assert len(provider.requests) == 2 and budget.spent_usd == pytest.approx(0.002)
    assert [c["task"] for c in budget.calls] == ["author", "repair"]


def test_a_stalled_upstream_hits_a_hard_wall_clock_deadline():
    """httpx read timeouts reset on every byte; the provider enforces its own deadline."""
    import threading
    import time

    from llm import LLMTimeout

    release = threading.Event()

    def handler(req: httpx.Request) -> httpx.Response:
        release.wait(5)  # an upstream that never answers within the deadline
        return httpx.Response(200, json={})

    settings = ProviderSettings(api_key="k", base_url="http://127.0.0.1:9/v1")
    client = openai.OpenAI(api_key="k", base_url=settings.base_url, max_retries=0,
                           http_client=httpx.Client(transport=httpx.MockTransport(handler)))
    started = time.monotonic()
    try:
        with pytest.raises(LLMTimeout):
            OpenRouterProvider(settings, client=client).complete(
                CompletionRequest(model="m", messages=[{"role": "user", "content": "x"}],
                                  timeout_s=0.3))
        assert time.monotonic() - started < 2
    finally:
        release.set()
