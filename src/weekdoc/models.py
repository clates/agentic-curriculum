"""WeekDoc v1: the structured form of a whole authored week (decision D3).

A hosted week is stored as data, never as a generator script. The renderer consumes the same
``kind`` + data-dict shapes the offline scripts use, so ``Worksheet.data`` keeps the renderer's
exact camelCase kinds and snake_case field names (no translation layer). Per-kind typing is added
by the hosted-kind registry (M2.2); the envelope here only guarantees structure.

The child's name: the model may write the first name directly, or the token ``{{student_name}}``
(fixtures and shared examples use the token so no real name is committed). Rendering substitutes
and escapes (M2.4); the stored document is never rendered to HTML with the name baked in.
"""

from __future__ import annotations

import re
from typing import Annotated, Any, Literal

from pydantic import BaseModel, ConfigDict, Field, StringConstraints, model_validator

from .kinds import item_refs

SCHEMA_VERSION = 1
STUDENT_NAME_TOKEN = "{{student_name}}"

_TOKEN_RE = re.compile(r"\{\{\s*([^{}]*?)\s*\}\}")
_ID_RE = r"^[a-z0-9][a-z0-9_-]{0,63}$"

DayName = Literal["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
GuideStyle = Literal["answer", "misconception", "extension", "discuss"]
CheckKind = Literal["quiz", "oral", "review", "activity", "observation"]

Text = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1)]
StableId = Annotated[str, StringConstraints(pattern=_ID_RE)]
# Standard ids look like JURIS.SUBJECT.GRADE.code (D5); existence is checked by the gate (M4).
StandardId = Annotated[str, StringConstraints(pattern=r"^[A-Z0-9]+(\.[A-Za-z0-9_-]+)+$")]


class _Strict(BaseModel):
    model_config = ConfigDict(extra="forbid")


class Answer(_Strict):
    """One answer-key entry, addressed by the item it answers (D3)."""

    item_ref: Text = Field(
        description="Address of the question/slot this answers, e.g. 'questions.0'."
    )
    answer: Text


class Worksheet(_Strict):
    """One printable page (or block) in a day."""

    id: StableId = Field(description="Stable within the packet; item refs and checks hang off it.")
    kind: Text = Field(description="Renderer kind, camelCase, e.g. 'readingWorksheet'.")
    data: dict[str, Any] = Field(description="Renderer data dict for this kind.")
    answers: list[Answer] = Field(default_factory=list)

    @model_validator(mode="after")
    def _typed_and_non_empty(self) -> "Worksheet":
        if not self.data:
            raise ValueError(f"worksheet {self.id!r} ({self.kind}) has empty data")
        # Unknown kinds raise UnknownKindError (a ValueError), so they surface as validation
        # errors rather than being skipped at render time.
        valid_refs = {r.ref for r in item_refs(self.kind, self.data)}
        for a in self.answers:
            if a.item_ref not in valid_refs:
                raise ValueError(
                    f"worksheet {self.id!r}: answer for unknown item_ref {a.item_ref!r}"
                )
        return self


class Day(_Strict):
    day: DayName
    title: Text
    standards: list[StandardId] = Field(default_factory=list)
    worksheets: Annotated[list[Worksheet], Field(min_length=1)]


class PrepCheck(_Strict):
    """A parent-run check, emitted as data so results can be recorded per check (D4)."""

    id: StableId = Field(description="Stable per packet; feedback results key on it.")
    day: DayName
    standard_id: StandardId
    kind: CheckKind
    prompt: Text = Field(description="What the parent asks or does.")
    pass_criteria: Text = Field(description="What a good answer sounds like, in plain words.")


class GuideBlock(_Strict):
    """A heading, or a styled callout of paragraphs, in a teacher-guide day."""

    heading: Text | None = None
    style: GuideStyle | None = None
    paragraphs: list[Text] = Field(default_factory=list)

    @model_validator(mode="after")
    def _one_shape(self) -> "GuideBlock":
        if self.heading is not None:
            if self.style is not None or self.paragraphs:
                raise ValueError("a heading block carries no style or paragraphs")
        elif self.style is None or not self.paragraphs:
            raise ValueError("a callout block needs a style and at least one paragraph")
        return self


class GuideDay(_Strict):
    day: DayName
    title: Text
    page_break_before: bool = False
    blocks: Annotated[list[GuideBlock], Field(min_length=1)]


class GuideSummary(_Strict):
    heading: Text
    intro: Text
    items: Annotated[list[Text], Field(min_length=1)]
    closing: Text | None = None


class TeacherGuide(_Strict):
    title: Text
    html_title: Text | None = Field(default=None, description="<title> tag; defaults to title.")
    meta: list[tuple[Text, Text]] = Field(
        default_factory=list, description="Label/value pairs shown under the title."
    )
    arc: Text | None = None
    days: Annotated[list[GuideDay], Field(min_length=1)]
    summary: GuideSummary | None = None


class WeekDoc(_Strict):
    schema_version: Literal[1] = Field(default=SCHEMA_VERSION)
    title: Text
    packet_title: Text
    theme: Text
    subject: Text | None = None
    grade_band: Text
    narrator: Text | None = None
    arc: Text | None = None
    days: Annotated[list[Day], Field(min_length=1, max_length=7)]
    prep_checks: Annotated[list[PrepCheck], Field(min_length=1)]
    teacher_guide: TeacherGuide

    @model_validator(mode="after")
    def _cross_checks(self) -> "WeekDoc":
        names = [d.day for d in self.days]
        if len(set(names)) != len(names):
            raise ValueError("duplicate day in days")
        ws_ids = [w.id for d in self.days for w in d.worksheets]
        if len(set(ws_ids)) != len(ws_ids):
            raise ValueError("worksheet ids must be unique within the week")
        check_ids = [c.id for c in self.prep_checks]
        if len(set(check_ids)) != len(check_ids):
            raise ValueError("prep check ids must be unique within the week")
        for c in self.prep_checks:
            if c.day not in names:
                raise ValueError(f"prep check {c.id!r} is on {c.day}, which is not in the week")
        for g in self.teacher_guide.days:
            if g.day not in names:
                raise ValueError(f"teacher guide covers {g.day}, which is not in the week")
        for token in _tokens(self.model_dump(mode="json")):
            if token != "student_name":
                raise ValueError(f"unknown placeholder {{{{{token}}}}}; only student_name exists")
        return self


def _tokens(value: Any) -> set[str]:
    if isinstance(value, str):
        return set(_TOKEN_RE.findall(value))
    if isinstance(value, dict):
        return set().union(*map(_tokens, value.values()))
    if isinstance(value, (list, tuple)):
        return set().union(*map(_tokens, value))
    return set()


def week_json_schema() -> dict[str, Any]:
    """The published contract: what week.v1.schema.json holds."""
    schema = WeekDoc.model_json_schema()
    schema["$schema"] = "https://json-schema.org/draft/2020-12/schema"
    schema["$id"] = "https://github.com/clates/agentic-curriculum/week.v1.schema.json"
    schema["title"] = "WeekDoc v1"
    return schema
