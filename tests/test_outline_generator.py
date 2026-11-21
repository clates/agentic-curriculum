"""M6.3: the outline generator, its gate and the repair loop (scripted provider, no network)."""

import json

import pytest

from candidate_selector import StandardInfo, select_candidates
from llm import LLMClient, StructuredOutputError
from model_context import ModelStudentContext, build_model_context
from outline_generator import build_messages, generate_outlines
from tests.llm_provider_fakes import ScriptedProvider

NOW = "2026-03-01T00:00:00Z"
CTX = ModelStudentContext(
    first_name="Mira", grade=3, interests=("dinosaurs", "baking"), parent_notes="Likes short tasks"
)


def standards():
    out = []
    for g in (2, 3, 4):
        for subject in ("Math", "Science", "English"):
            for n in range(1, 4):
                out.append(
                    StandardInfo(
                        f"{subject[:2].upper()}.{g}.{n}",
                        subject,
                        g,
                        f"The student will skill {g}{n}",
                    )
                )
    return out


CANDS = select_candidates(progress={}, standards=standards(), grade=3, seed="t", now=NOW)


def option(letter, difficulty, title, hook, **over):
    body = {
        "option_id": letter,
        "title": title,
        "hook": hook,
        "activities": f"Hands-on work about {title.lower()} every day.",
        "skills": ["Counting sets of objects", "Reading a short story"],
        "effort": "About 25 minutes a day",
        "standard_ids": CANDS.ids_for(difficulty),
    }
    body.update(over)
    return body


def good_reply(**changes):
    options = [
        option("a", "easier", "Dino Dig Basics", "Dig up dinosaur facts with easy puzzles."),
        option("b", "on_level", "Bake and Measure", "Bake a snack and measure every step."),
        option("c", "stretch", "Fossil Detectives", "Crack a fossil mystery with bigger numbers."),
    ]
    for key, value in changes.items():
        options[int(key[-1])].update(value)
    return json.dumps({"options": options})


def run(*script, **kw):
    provider = ScriptedProvider(*script)
    client = LLMClient(provider, env={}, sleep=lambda s: None)
    return provider, lambda: generate_outlines(CTX, CANDS, client=client, **kw)


def test_a_good_answer_takes_one_call_and_becomes_three_outlines():
    provider, go = run(good_reply())
    result = go()
    assert len(provider.requests) == 1 and result.repairs == 0
    options = result.outlines.options
    assert [o.option_id for o in options] == ["a", "b", "c"]
    assert [o.difficulty for o in options] == ["easier", "on_level", "stretch"]
    assert options[1].standard_ids == CANDS.ids_for("on_level")
    assert options[0].effort == "About 25 minutes a day" and options[0].skills


def test_the_prompt_has_the_childs_first_name_interests_and_notes_and_nothing_else():
    context = build_model_context(
        json.dumps({"name": "Mira Quillfeather", "birthday": "2018-03-04", "avatar_url": "x.png"}),
        json.dumps(
            {"parent_notes": "Likes short tasks", "interests": ["dinosaurs"], "email": "a@b.com"}
        ),
        fallback_grade=3,
    )
    text = "\n".join(m["content"] for m in build_messages(context, CANDS))
    assert "Mira" in text and "dinosaurs" in text and "Likes short tasks" in text
    for leak in ("Quillfeather", "2018", "x.png", "a@b.com", "stu_"):
        assert leak not in text


@pytest.mark.parametrize(
    "bad,why",
    [
        ({"0": {"standard_ids": ["MA.9.9"]}}, "standard_ids must be exactly"),
        ({"1": {"standard_ids": []}}, "standard_ids must be exactly"),
        ({"2": {"title": "Dino Dig Basics"}}, "same title"),
        ({"1": {"hook": "Dig up dinosaur facts with easy puzzles."}}, "same hook"),
        ({"0": {"title": "Lorem ipsum week"}}, "placeholder"),
        ({"0": {"title": "[Child] week"}}, "placeholder"),
        ({"0": {"hook": "TBD"}}, "placeholder"),
        ({"0": {"activities": "Cover the standards fully."}}, "technical word"),
        ({"0": {"skills": ["VA.MATH.3.1"]}}, "standard code"),
        ({"0": {"skills": ["Show mastery of counting"]}}, "technical word"),
        ({"0": {"hook": "A fun week. It is also long."}}, "ONE sentence"),
        ({"0": {"effort": ""}}, "empty"),
    ],
)
def test_the_gate_rejects_bad_answers_and_the_repair_fixes_them(bad, why):
    provider, go = run(good_reply(**{f"o{k}": v for k, v in bad.items()}), good_reply())
    result = go()
    assert result.repairs == 1
    repair_prompt = provider.requests[1].messages[-1]["content"]
    assert why in repair_prompt  # the model is told exactly what to fix
    assert len(result.outlines.options) == 3


def test_exactly_three_options_are_required():
    two = json.dumps(json.loads(good_reply())["options"][:2])
    provider, go = run(json.dumps({"options": json.loads(two)}), good_reply())
    assert go().repairs == 1


def test_repairs_are_capped_at_four_then_a_typed_error():
    provider, go = run(*["not json"] * 5)
    with pytest.raises(StructuredOutputError) as info:
        go()
    assert info.value.attempts == 5 and len(provider.requests) == 5


def test_four_repairs_still_succeed():
    provider, go = run(*["nope"] * 4, good_reply())
    assert go().repairs == 4


def test_option_letters_must_be_a_b_c():
    reply = json.loads(good_reply())
    reply["options"][2]["option_id"] = "a"
    provider, go = run(json.dumps(reply), good_reply())
    assert go().repairs == 1


def test_the_call_uses_the_outline_task_and_is_billed_to_the_child():
    from llm import InMemoryLedger, UsageContext

    ledger = InMemoryLedger()
    provider = ScriptedProvider(good_reply())
    client = LLMClient(provider, env={}, ledger=ledger)
    generate_outlines(CTX, CANDS, client=client, usage=UsageContext("fam_local", "kid"))
    assert [(r["task"], r["family_id"], r["student_id"]) for r in ledger.rows] == [
        ("outline", "fam_local", "kid")
    ]
