"""M6.3: the outline generator, its gate and the repair loop (scripted provider, no network)."""

import json
import re

import pytest

from candidate_selector import StandardInfo, select_week_standards
from llm import LLMClient
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


STDS = select_week_standards(progress={}, standards=standards(), grade=3, seed="t", now=NOW)
RECENT = ("Space",)


def option(letter, topic, title, hook, **over):
    body = {
        "option_id": letter,
        "topic": topic,
        "title": title,
        "hook": hook,
        "activities": f"Hands-on work about {title.lower()} every day.",
    }
    body.update(over)
    return body


def good_reply(**changes):
    options = [
        option("a", "Weather", "Weather Watchers", "Track the sky and predict tomorrow."),
        option("b", "Baking", "Bakery Boss", "Run a bakery and test every recipe."),
        option("c", "Ocean animals", "Deep Sea Files", "Dive down to meet sea creatures."),
    ]
    for key, value in changes.items():
        options[int(key[-1])].update(value)
    return json.dumps({"options": options})


def run(*script, **kw):
    provider = ScriptedProvider(*script)
    client = LLMClient(provider, env={}, sleep=lambda s: None)
    return provider, lambda: generate_outlines(
        CTX, STDS, recent_topics=RECENT, seed="s", client=client, **kw
    )


def test_a_good_answer_takes_one_call_and_becomes_three_topic_options():
    provider, go = run(good_reply())
    result = go()
    assert len(provider.requests) == 1 and result.repairs == 0
    options = result.outlines.options
    assert [o.option_id for o in options] == ["a", "b", "c"]
    assert [o.topic for o in options] == ["Weather", "Baking", "Ocean animals"]
    assert result.outlines.source == "model"
    # the skills do not depend on the topic: every option carries the engine's one set
    assert all(o.standard_ids == STDS.ids() for o in options)
    assert options[0].skills == options[1].skills == options[2].skills


def test_the_prompt_says_topics_only_and_has_no_difficulty_framing():
    text = "\n".join(m["content"] for m in build_messages(CTX, STDS, recent_topics=RECENT))
    assert "SAME under all three" in text and "Space" in text
    assert not re.search(r"easier|on level|stretch|harder|difficulty|gentler", text, re.I)


def test_the_prompt_has_the_childs_first_name_interests_and_notes_and_nothing_else():
    context = build_model_context(
        json.dumps({"name": "Mira Quillfeather", "birthday": "2018-03-04", "avatar_url": "x.png"}),
        json.dumps(
            {"parent_notes": "Likes short tasks", "interests": ["dinosaurs"], "email": "a@b.com"}
        ),
        fallback_grade=3,
    )
    text = "\n".join(m["content"] for m in build_messages(context, STDS))
    assert "Mira" in text and "dinosaurs" in text and "Likes short tasks" in text
    for leak in ("Quillfeather", "2018", "x.png", "a@b.com", "stu_"):
        assert leak not in text


@pytest.mark.parametrize(
    "bad,why",
    [
        ({"2": {"title": "Weather Watchers"}}, "share the word"),
        ({"2": {"topic": "Rainy weather"}}, "share the word"),
        ({"1": {"hook": "Run a bakery in a big storm."}}, "both about"),
        ({"1": {"topic": "Space", "title": "Moon Landing Crew"}}, "repeats a recent topic"),
        ({"0": {"title": "Weather Watchers Of The Whole Wide World"}}, "at most 6 words"),
        ({"0": {"title": "Lorem ipsum week"}}, "placeholder"),
        ({"0": {"title": "[Child] week"}}, "placeholder"),
        ({"0": {"hook": "TBD"}}, "placeholder"),
        ({"0": {"activities": "Cover the standards fully."}}, "technical word"),
        ({"0": {"activities": "Practice VA.MATH.3.1 daily"}}, "standard code"),
        ({"0": {"hook": "A fun week. It is also long."}}, "ONE sentence"),
        ({"0": {"topic": "A very long topic name here"}}, "1-3 words"),
        ({"0": {"activities": ""}}, "empty"),
        ({"0": {"standard_ids": ["X"]}}, "Extra inputs"),
    ],
)
def test_the_gate_rejects_bad_answers_and_the_repair_fixes_them(bad, why):
    provider, go = run(good_reply(**{f"o{k}": v for k, v in bad.items()}), good_reply())
    result = go()
    assert result.repairs == 1
    repair_prompt = provider.requests[1].messages[-1]["content"]
    assert why in repair_prompt  # the model is told exactly what to fix
    assert len(result.outlines.options) == 3


def test_all_three_repeating_the_same_theme_is_never_accepted():
    dinos = good_reply(
        o0={"topic": "Dinosaurs", "title": "Dino Dig Site", "hook": "Dig up giant bones."},
        o1={"topic": "Fossils", "title": "Fossil Lab Work", "hook": "Crack a fossil mystery."},
        o2={"topic": "Dinosaur eggs", "title": "Egg Hatch Watch", "hook": "Guard a nest."},
    )
    provider, go = run(dinos, good_reply())
    assert go().repairs == 1
    assert "both about dinosaurs" in provider.requests[1].messages[-1]["content"] or (
        "share the word" in provider.requests[1].messages[-1]["content"]
    )


def test_when_the_model_keeps_failing_the_gate_template_topics_are_used():
    provider, go = run(*[good_reply(o2={"title": "Weather Watchers"})] * 5)
    result = go()
    assert result.outlines.source == "template" and result.model is None
    options = result.outlines.options
    assert len({o.topic for o in options}) == 3
    assert all(len(o.title.split()) <= 6 and len(o.title) <= 40 for o in options)
    assert all(o.standard_ids == STDS.ids() for o in options)
    assert not any("space" in (o.topic or "").lower() for o in options)  # recent is excluded


def test_exactly_three_options_are_required():
    two = json.dumps(json.loads(good_reply())["options"][:2])
    provider, go = run(json.dumps({"options": json.loads(two)}), good_reply())
    assert go().repairs == 1


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
    generate_outlines(CTX, STDS, client=client, usage=UsageContext("fam_local", "kid"))
    assert [(r["task"], r["family_id"], r["student_id"]) for r in ledger.rows] == [
        ("outline", "fam_local", "kid")
    ]


def test_a_provider_failure_is_not_hidden_by_the_template_fallback():
    from llm import LLMBadRequest

    class Down(ScriptedProvider):
        def complete(self, request):
            raise LLMBadRequest("down")

    client = LLMClient(Down(), env={}, sleep=lambda s: None)
    with pytest.raises(LLMBadRequest):
        generate_outlines(CTX, STDS, client=client)
