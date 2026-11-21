"""Outline generator (M6.3): ONE framing call that turns candidate standards into 3 options.

The selector (candidate_selector.py) decides WHAT each option covers; the model only FRAMES it:
a title, a one-sentence hook, what the child will do, the skills in plain words and a time hint.
It sees the child's first name, grade, reading level, interests and the parent's notes through
``ModelStudentContext`` and nothing else (D9).

The call goes through ``llm.generate_structured`` (task ``outline``). The schema the model must
satisfy is built per call and carries the gate, so a bad answer is sent back through the repair
loop with a message that says exactly what to fix (up to ``MAX_REPAIRS`` repairs):

  * exactly three options, a/b/c, in the order easier / on level / stretch
  * titles, hooks and activities are all different from each other
  * each option's standard ids are exactly the ids the selector gave it (none added or dropped)
  * no placeholder text, no standard codes, none of the banned technical words
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, ValidationInfo, field_validator, model_validator

try:  # Prefer package-relative import when available
    from .candidate_selector import DIFFICULTIES, CandidateSet  # type: ignore
    from .model_context import ModelStudentContext  # type: ignore
    from .outline_models import OPTION_IDS, Outline, OutlineSet  # type: ignore
    from .progress_summary import skill_label  # type: ignore
except ImportError:  # Fallback for direct script execution / top-level import
    from candidate_selector import DIFFICULTIES, CandidateSet  # type: ignore
    from model_context import ModelStudentContext  # type: ignore
    from outline_models import OPTION_IDS, Outline, OutlineSet  # type: ignore
    from progress_summary import skill_label  # type: ignore

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

DIFFICULTY_WORDS = {
    "easier": "easier: a gentler week; revisit what was tricky and build confidence",
    "on_level": "on level: right where the child is now",
    "stretch": "stretch: a step up that moves them forward",
}


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


def make_draft_model(candidates: CandidateSet) -> type[BaseModel]:
    """The model's answer shape, with the gate built in (closed over this call's candidates)."""
    allowed = {OPTION_IDS[i]: candidates.ids_for(d) for i, d in enumerate(DIFFICULTIES)}

    class DraftOption(BaseModel):
        model_config = ConfigDict(extra="forbid")

        option_id: str = Field(description="a, b or c")
        title: str = Field(max_length=60, description="A short, inviting week title")
        hook: str = Field(max_length=160, description="ONE sentence that makes the child want it")
        activities: str = Field(
            max_length=300, description="What the child will do this week, in plain words"
        )
        skills: list[str] = Field(
            min_length=1, max_length=6, description="Skills covered, one plain phrase each"
        )
        effort: str = Field(max_length=50, description="Time hint, e.g. About 25 minutes a day")
        standard_ids: list[str] = Field(description="Copy this option's ids exactly")

        @field_validator("option_id")
        @classmethod
        def _option(cls, v: str) -> str:
            if v not in allowed:
                raise ValueError(f"option_id must be one of a, b, c (got {v!r})")
            return v

        @field_validator("title", "activities", "effort")
        @classmethod
        def _plain(cls, v: str, info: ValidationInfo) -> str:
            return _clean_text(info.field_name or "text", v)

        @field_validator("hook")
        @classmethod
        def _hook(cls, v: str) -> str:
            v = _clean_text("hook", v)
            if _SENTENCE_BREAK.search(v):
                raise ValueError(f"hook must be ONE sentence: {v!r}")
            return v

        @field_validator("skills")
        @classmethod
        def _skills(cls, v: list[str]) -> list[str]:
            return [_clean_text("a skill", s) for s in v]

        @model_validator(mode="after")
        def _ids(self) -> "DraftOption":
            want = allowed[self.option_id]
            if sorted(self.standard_ids) != sorted(want):
                raise ValueError(
                    f"option {self.option_id}: standard_ids must be exactly {want} "
                    f"(none added, none dropped); got {self.standard_ids}"
                )
            return self

    class Draft(BaseModel):
        model_config = ConfigDict(extra="forbid")

        options: list[DraftOption] = Field(min_length=3, max_length=3)

        @model_validator(mode="after")
        def _distinct(self) -> "Draft":
            ids = [o.option_id for o in self.options]
            if sorted(ids) != list(OPTION_IDS):
                raise ValueError("there must be exactly one option each for a, b and c")
            for field_name in ("title", "hook", "activities"):
                values = [getattr(o, field_name) for o in self.options]
                for i in range(3):
                    for j in range(i + 1, 3):
                        if _similar(values[i], values[j]):
                            raise ValueError(
                                f"options {self.options[i].option_id} and "
                                f"{self.options[j].option_id} have the same {field_name}; "
                                "the three options must be clearly different"
                            )
            return self

    return Draft


SYSTEM = (
    "You write week options for a homeschool parent to choose from. You are warm, concrete and "
    "plain-spoken. A parent reads each option on a phone in a few seconds. You never use "
    "educational jargon, never mention standards or codes, and never invent facts about the child."
)


def build_messages(context: ModelStudentContext, candidates: CandidateSet) -> list[dict[str, str]]:
    options: dict[str, Any] = {}
    for i, difficulty in enumerate(DIFFICULTIES):
        options[OPTION_IDS[i]] = {
            "kind": DIFFICULTY_WORDS[difficulty],
            "standards": [
                {
                    "id": c.standard_id,
                    "subject": c.subject,
                    "plain_skill": skill_label(c.description),
                }
                for c in candidates.for_difficulty(difficulty)
            ],
        }
    user = (
        "ABOUT THE CHILD\n"
        f"{context.prompt_lines()}\n\n"
        "TASK\n"
        f"Write exactly three options for {context.first_name}'s next week: a, b and c. The "
        "skills each option covers are already chosen; you only frame them. Make the three "
        "clearly different in feel, not just in difficulty. Tie each to what "
        f"{context.first_name} enjoys where it fits, and respect the parent's notes.\n\n"
        "For each option give:\n"
        "- title: short and inviting (no more than 60 characters)\n"
        "- hook: ONE sentence that makes the child want to do it\n"
        "- activities: what the child will actually do this week, in plain words\n"
        "- skills: the skills covered, one plain phrase each (never standard codes)\n"
        "- effort: a time or effort hint, like 'About 25 minutes a day'\n"
        "- standard_ids: copy the ids for that option exactly; do not add or drop any\n\n"
        'Reply with one JSON object: {"options": [ {option_id, title, hook, activities, '
        "skills, effort, standard_ids}, ... ]} and nothing else.\n\n"
        f"OPTIONS_JSON: {json.dumps(options, sort_keys=True)}"
    )
    return [{"role": "system", "content": SYSTEM}, {"role": "user", "content": user}]


@dataclass
class OutlineGeneration:
    outlines: OutlineSet
    repairs: int
    model: str | None
    cost_usd: float | None


def generate_outlines(
    context: ModelStudentContext,
    candidates: CandidateSet,
    *,
    client=None,
    usage=None,
    max_repairs: int = MAX_REPAIRS,
) -> OutlineGeneration:
    """One structured call (plus bounded repairs) -> a validated OutlineSet.

    Raises ``llm.StructuredOutputError`` when the model cannot produce a passing answer, or any
    other ``llm.LLMError`` the provider raised. Nothing is stored here.
    """
    from llm import generate_structured

    draft_cls = make_draft_model(candidates)
    result = generate_structured(
        TASK,
        build_messages(context, candidates),
        draft_cls,
        client=client,
        max_repairs=max_repairs,
        usage=usage,
    )
    by_id = {o.option_id: o for o in result.parsed.options}
    options = []
    for i, difficulty in enumerate(DIFFICULTIES):
        letter = OPTION_IDS[i]
        d = by_id[letter]
        options.append(
            Outline(
                option_id=letter,
                title=d.title,
                hook=d.hook,
                difficulty=difficulty,
                standard_ids=candidates.ids_for(difficulty),
                activities=d.activities,
                skills=d.skills,
                effort=d.effort,
            )
        )
    last = result.completions[-1]
    return OutlineGeneration(
        outlines=OutlineSet(options=options),
        repairs=result.repairs,
        model=last.model,
        cost_usd=result.cost_usd,
    )
