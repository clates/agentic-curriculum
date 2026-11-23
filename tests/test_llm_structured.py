"""M1.3: structured output + bounded repair. Bad JSON is repaired or raises, never passes silently."""

import pytest
from pydantic import BaseModel

from llm import LLMClient, StructuredOutputError, extract_json, generate_structured
from tests.llm_provider_fakes import ScriptedProvider


class Plan(BaseModel):
    title: str
    days: int


MSGS = [{"role": "user", "content": "plan"}]
GOOD = '{"title": "Week", "days": 5}'


def run(*script, env=None, **kw):
    provider = ScriptedProvider(*script)
    client = LLMClient(provider, env=env or {})
    return provider, lambda: generate_structured("outline", MSGS, Plan, client=client, **kw)


def test_valid_output_needs_one_call():
    provider, go = run(GOOD)
    result = go()
    assert result.parsed == Plan(title="Week", days=5)
    assert result.repairs == 0 and len(provider.requests) == 1
    assert result.cost_usd == pytest.approx(0.001)


def test_schema_mode_for_supporting_models_json_object_otherwise():
    provider, go = run(GOOD)
    go()
    assert provider.requests[0].response_format["type"] == "json_schema"
    assert provider.requests[0].response_format["json_schema"]["schema"]["title"] == "Plan"
    provider, go = run(GOOD, env={"LLM_MODEL": "meta-llama/x"})
    go()
    req = provider.requests[0]
    assert req.response_format == {"type": "json_object"}
    assert "JSON Schema" in req.messages[-1]["content"]  # schema goes in the prompt instead


@pytest.mark.parametrize(
    "text",
    [
        '```json\n{"title": "Week", "days": 5}\n```',
        'Sure! Here you go: {"title": "Week", "days": 5} Enjoy.',
    ],
)
def test_fences_and_prose_are_stripped_without_a_repair_call(text):
    provider, go = run(text)
    assert go().parsed.days == 5
    assert len(provider.requests) == 1


def test_malformed_json_is_repaired_by_a_repair_call():
    provider, go = run('{"title": "Week", "days": ', GOOD)
    result = go()
    assert result.parsed.title == "Week" and result.repairs == 1
    repair = provider.requests[1]
    assert "invalid JSON" in repair.messages[-1]["content"]
    # the repair call keeps the original brief and shows the model its own bad output
    assert repair.messages[0] == MSGS[0]
    assert any(
        m["role"] == "assistant" and m["content"].startswith('{"title": "Week"')
        for m in repair.messages
    )


def test_schema_violation_is_repaired():
    _, go = run('{"title": "Week", "days": "five"}', GOOD)
    assert go().repairs == 1


def test_exhausted_repairs_raise_typed_error_never_silent():
    provider, go = run("not json", "still not", "nope")
    with pytest.raises(StructuredOutputError) as info:
        go()
    err = info.value
    assert err.attempts == 3 and len(provider.requests) == 3  # 1 call + 2 repairs
    assert err.raw == "nope" and len(err.errors) == 3
    assert "Plan" in str(err)


def test_repair_budget_is_configurable():
    provider, go = run("bad", env={"LLM_MAX_REPAIRS": "0"})
    with pytest.raises(StructuredOutputError):
        go()
    assert len(provider.requests) == 1


def test_truncated_output_is_flagged():
    from llm import Completion, Usage

    class Truncated:
        def complete(self, request):
            return Completion('{"title": "We', request.model, Usage(), 0.0, finish_reason="length")

    with pytest.raises(StructuredOutputError, match="truncated"):
        generate_structured(
            "outline", MSGS, Plan, client=LLMClient(Truncated(), env={}), max_repairs=0
        )


def test_extract_json_raises_on_garbage():
    with pytest.raises(ValueError):
        extract_json("no json here")


def test_repair_uses_author_token_budget_and_usage_context():
    from llm.ledger import UsageContext

    provider, go = run("not json", GOOD)
    ctx = UsageContext(family_id="f1")
    result = generate_structured(
        "author",
        MSGS,
        Plan,
        client=LLMClient(provider, env={"LLM_MAX_TOKENS_AUTHOR": "20000"}),
        usage=ctx,
    )
    assert result.repairs == 1
    assert provider.requests[1].max_tokens == 20000  # not the 4096 repair default


def test_completeness_check_triggers_a_repair():
    provider, go = run('{"title": "Week", "days": 2}', GOOD)
    result = generate_structured(
        "author",
        MSGS,
        Plan,
        client=LLMClient(provider, env={}),
        check=lambda p: None if p.days >= 5 else "only 2 days",
    )
    assert result.repairs == 1
    assert "incomplete: only 2 days" in provider.requests[1].messages[-1]["content"]
