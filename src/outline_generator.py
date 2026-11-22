"""Outline generator (M6.3): ONE framing call that turns the week's skills into 3 TOPIC options.

The curriculum engine (candidate_selector.py) decides WHAT the week covers: one set of skills
from the child's mastery, review dates and grade. The three options differ only by TOPIC (what the
week is about); every option carries exactly that same set. The model frames each: a topic, a
short title (at most 6 words), a one-sentence hook and what the child will do. It sees the child's
first name, grade, reading level, interests and the parent's notes through ``ModelStudentContext``
and nothing else (D9).

The call goes through ``llm.generate_structured`` (task ``outline``). The schema carries the gate,
so a bad answer is sent back through the repair loop with a message that says what to fix:

  * exactly three options, a/b/c
  * title at most 6 words / 40 characters, hook ONE sentence, no placeholders, codes or jargon
  * topics clearly different from each other and from the child's recent topics (topic_gate)

If the model still cannot pass after the repairs, three options are built from the curated topic
list instead (``source == "template"``), so the parent always gets a usable screen. A provider
failure (timeout, outage) is not hidden: it raises, and the parent sees a retry.

This function is the boundary the job queue (M8.2) will call: it takes plain values, stores
nothing and returns a validated ``OutlineSet``.
"""

from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass
from typing import Any, Sequence

from pydantic import BaseModel, ConfigDict, Field, ValidationInfo, field_validator, model_validator

try:  # Prefer package-relative import when available
    from .candidate_selector import StandardsSet  # type: ignore
    from .model_context import ModelStudentContext  # type: ignore
    from .outline_models import OPTION_IDS, Outline, OutlineSet  # type: ignore
    from .progress_summary import skill_label  # type: ignore
    from .topic_gate import (  # type: ignore
        OptionText,
        distinctness_problems,
        template_options,
        title_problems,
        vetted_menu,
    )
except ImportError:  # Fallback for direct script execution / top-level import
    from candidate_selector import StandardsSet  # type: ignore
    from model_context import ModelStudentContext  # type: ignore
    from outline_models import OPTION_IDS, Outline, OutlineSet  # type: ignore
    from progress_summary import skill_label  # type: ignore
    from topic_gate import (  # type: ignore
        OptionText,
        distinctness_problems,
        template_options,
        title_problems,
        vetted_menu,
    )

MAX_TOPIC_WORDS = 3
TASK = "outline"
MAX_REPAIRS = 4

# Mirrors frontend/lib/bannedWords.ts: words a parent must never read.
JARGON = (
    "standard",
    "standards",
    "mastery",
    "mastered",
    "scaffold",
    "scaffolding",
    "schema",
    "llm",
    "prompt",
    "prompts",
    "token",
    "tokens",
    "json",
    "api",
    "endpoint",
    "payload",
    "tenant",
    "null",
    "undefined",
    "backend",
    "database",
    "skill tree",
)
_JARGON = re.compile(r"(?<![\w])(" + "|".join(re.escape(w) for w in JARGON) + r")(?![\w])", re.I)
_CODE = re.compile(r"\b[A-Z]{2,}[._][A-Z_]+[._]\w+|\bVA\.\w+|\b[A-Z]{2,5}\.\d+\.\d+")
_PLACEHOLDER = re.compile(
    r"lorem|ipsum|\btodo\b|\btbd\b|placeholder|\bxxx+\b|\[[^\]]*\]|\{[^}]*\}|<[^>]+>|%[sd]\b"
    r"|\boption [abc]\b|\bchild'?s? name\b|\bstudent name\b|\bn/a\b",
    re.I,
)
_SENTENCE_BREAK = re.compile(r"[.!?]['\")\]]*\s+\S")


def _words(text: str) -> set[str]:
    return set(re.findall(r"[a-z0-9]+", text.lower()))


def _similar(a: str, b: str) -> bool:
    wa, wb = _words(a), _words(b)
    return bool(wa and wb) and len(wa & wb) / len(wa | wb) >= 0.8


def _clean_text(label: str, text: str) -> str:
    text = " ".join(text.split())
    if not text:
        raise ValueError(f"{label} is empty")
    if _PLACEHOLDER.search(text):
        raise ValueError(f"{label} looks like placeholder text: {text!r}")
    if _CODE.search(text):
        raise ValueError(f"{label} must not contain a standard code: {text!r}")
    hit = _JARGON.search(text)
    if hit:
        raise ValueError(f"{label} uses the technical word {hit.group(1)!r}; say it plainly")
    return text


def make_draft_model(recent_topics: Sequence[str] = ()) -> type[BaseModel]:
    """The model's answer shape, with the gate built in (closed over this child's recent topics)."""
    recent = tuple(recent_topics)

    class DraftOption(BaseModel):
        model_config = ConfigDict(extra="forbid")

        option_id: str = Field(description="a, b or c")
        topic: str = Field(max_length=40, description="What the week is about, 1-3 words")
        title: str = Field(max_length=60, description="At most 6 words, inviting")
        hook: str = Field(max_length=160, description="ONE sentence that makes the child want it")
        activities: str = Field(
            max_length=300, description="What the child will do this week, in plain words"
        )

        @field_validator("option_id")
        @classmethod
        def _option(cls, v: str) -> str:
            if v not in OPTION_IDS:
                raise ValueError(f"option_id must be one of a, b, c (got {v!r})")
            return v

        @field_validator("topic", "title", "activities")
        @classmethod
        def _plain(cls, v: str, info: ValidationInfo) -> str:
            v = _clean_text(info.field_name or "text", v)
            if info.field_name == "topic" and len(v.split()) > MAX_TOPIC_WORDS:
                raise ValueError(f"topic must be 1-{MAX_TOPIC_WORDS} words: {v!r}")
            if info.field_name == "title":
                problem = title_problems(v)
                if problem:
                    raise ValueError(problem)
            return v

        @field_validator("hook")
        @classmethod
        def _hook(cls, v: str) -> str:
            v = _clean_text("hook", v)
            if _SENTENCE_BREAK.search(v):
                raise ValueError(f"hook must be ONE sentence: {v!r}")
            return v

    class Draft(BaseModel):
        model_config = ConfigDict(extra="forbid")

        options: list[DraftOption] = Field(min_length=3, max_length=3)

        @model_validator(mode="after")
        def _distinct(self) -> "Draft":
            ids = [o.option_id for o in self.options]
            if sorted(ids) != list(OPTION_IDS):
                raise ValueError("there must be exactly one option each for a, b and c")
            ordered = sorted(self.options, key=lambda o: o.option_id)
            problems = distinctness_problems(
                [OptionText(o.topic, o.title, o.hook) for o in ordered], recent
            )
            if problems:
                raise ValueError("; ".join(problems))
            for field_name in ("hook", "activities"):
                values = [getattr(o, field_name) for o in ordered]
                for i in range(3):
                    for j in range(i + 1, 3):
                        if _similar(values[i], values[j]):
                            raise ValueError(
                                f"options {ordered[i].option_id} and {ordered[j].option_id} "
                                f"have the same {field_name}; the topics must be different"
                            )
            return self

    return Draft


SYSTEM = (
    "You write week options for a homeschool parent to choose from. You are warm, concrete and "
    "plain-spoken. A parent reads each option on a phone in a few seconds. You never use "
    "educational jargon, never mention standards or codes, and never invent facts about the child."
)


def plain_skills(standards: StandardsSet) -> list[str]:
    seen: list[str] = []
    for c in standards.items:
        label = skill_label(c.description)
        if label not in seen:
            seen.append(label)
    return seen[:6]


def build_messages(
    context: ModelStudentContext,
    standards: StandardsSet,
    *,
    recent_topics: Sequence[str] = (),
    seed: str = "",
) -> list[dict[str, str]]:
    skills = [
        {"subject": c.subject, "plain_skill": skill_label(c.description)} for c in standards.items
    ]
    menu = [t.label for t in vetted_menu(seed, context.interests, recent_topics)]
    avoid = list(recent_topics)
    user = (
        "ABOUT THE CHILD\n"
        f"{context.prompt_lines()}\n\n"
        "TASK\n"
        f"Write exactly three week options for {context.first_name}: a, b and c. The skills for "
        "the week are already chosen and are the SAME under all three options; you choose only "
        "the TOPIC (what the week is about) that wraps them. The parent is choosing what "
        f"{context.first_name} will enjoy, not how hard it is.\n\n"
        "Topic rules:\n"
        "- Each option is ONE coherent theme a child would care about, like a real subject or "
        "a role they could play for a week.\n"
        + (
            "- Use the child's interests and the parent's notes, a different interest for each "
            "option. If they give fewer than three themes, choose the rest from this vetted "
            f"list (it already leaves out recent topics): {json.dumps(menu)}.\n"
            if context.interests
            else "- The child has no interests on file: choose all three topics from this vetted "
            f"list (it already leaves out recent topics): {json.dumps(menu)}.\n"
        )
        + "- The three topics must be completely different from each other: no shared main noun "
        "and no shared theme in topic, title or hook.\n"
        f"- Do not reuse these recent topics: {json.dumps(avoid)}.\n"
        "- Every skill below must be practised inside the topic; say how in activities.\n\n"
        "For each option give:\n"
        "- topic: the theme in 1-3 words\n"
        "- title: at most 6 words, inviting\n"
        "- hook: ONE sentence that makes the child want to do it\n"
        "- activities: what the child will actually do this week, in plain words\n\n"
        'Reply with one JSON object: {"options": [ {option_id, topic, title, hook, '
        "activities}, ... ]} and nothing else.\n\n"
        f"SKILLS_JSON: {json.dumps(skills, sort_keys=True)}"
    )
    return [{"role": "system", "content": SYSTEM}, {"role": "user", "content": user}]


@dataclass
class OutlineGeneration:
    outlines: OutlineSet
    repairs: int
    model: str | None
    cost_usd: float | None


def _outline_set(items: Sequence[dict[str, Any]], ids: list[str], skills: list[str], source: str):
    return OutlineSet(
        source=source,
        options=[
            Outline(
                option_id=OPTION_IDS[i],
                topic=d["topic"],
                title=d["title"],
                hook=d["hook"],
                standard_ids=list(ids),
                activities=d["activities"],
                skills=skills,
                effort=None,
            )
            for i, d in enumerate(items)
        ],
    )


def template_outlines(
    context: ModelStudentContext,
    standards: StandardsSet,
    *,
    recent_topics: Sequence[str] = (),
    seed: str = "",
) -> OutlineSet:
    """Three options from the curated topic list. No model call; deterministic for ``seed``."""
    topics = template_options(seed, context.first_name, context.interests, recent_topics)
    items = []
    for t in topics:
        items.append(
            {
                "topic": t.label,
                "title": t.titles[
                    int(hashlib.sha256(f"{seed}{t.key}".encode()).hexdigest(), 16) % len(t.titles)
                ],
                "hook": t.hook.format(name=context.first_name),
                "activities": t.activities.format(name=context.first_name),
            }
        )
    return _outline_set(items, standards.ids(), plain_skills(standards), "template")


def generate_outlines(
    context: ModelStudentContext,
    standards: StandardsSet,
    *,
    recent_topics: Sequence[str] = (),
    seed: str = "",
    client=None,
    usage=None,
    max_repairs: int = MAX_REPAIRS,
) -> OutlineGeneration:
    """One structured call (plus bounded repairs) -> a validated OutlineSet.

    When the model cannot pass the gate, falls back to the curated topic list. Any other
    ``llm.LLMError`` the provider raised propagates. Nothing is stored here.
    """
    from llm import StructuredOutputError, generate_structured

    try:
        result = generate_structured(
            TASK,
            build_messages(context, standards, recent_topics=recent_topics, seed=seed),
            make_draft_model(recent_topics),
            client=client,
            max_repairs=max_repairs,
            usage=usage,
        )
    except StructuredOutputError:
        return OutlineGeneration(
            outlines=template_outlines(context, standards, recent_topics=recent_topics, seed=seed),
            repairs=max_repairs,
            model=None,
            cost_usd=None,
        )
    by_id = {o.option_id: o for o in result.parsed.options}
    items = [by_id[letter].model_dump() for letter in OPTION_IDS]
    last = result.completions[-1]
    return OutlineGeneration(
        outlines=_outline_set(items, standards.ids(), plain_skills(standards), "model"),
        repairs=result.repairs,
        model=last.model,
        cost_usd=result.cost_usd,
    )
