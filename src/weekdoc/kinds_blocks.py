"""Layout and narration blocks (M2.9a): colorKey, doingCard, heartBar, logoBadge,
noteBox, richText, taskList, calibrationRuler.

Field names are the renderer's own. Most of these ask the child nothing, so they carry a
documented waiver; only ``taskList`` (numbered prompts) enumerates items.

Safety notes. The renderer escapes every free-text field with ``html.escape`` (``_h``), but a
few fields reach an attribute or style unescaped or fetch something, so the models bound them:
``colorKey.hex`` is injected raw into a style attribute (strict #rgb/#rrggbb pattern);
``logoBadge.src`` becomes an ``<img src>`` (only an inline base64 raster data: URI, size capped,
so rendering can never fetch a remote URL); numeric sizes are bounded.

``taskList`` can embed a ``figure`` block. It must itself be a hosted kind with valid data
(checked lazily against the registry) and may not be another taskList, so nesting is one level.

Not registered: ``cutLine``. The renderer ignores its data entirely, and a stored worksheet
must have non-empty ``data`` (Worksheet envelope check in models.py), so it cannot be hosted
without inventing a field the renderer does not read. Authors can use a page break or a
calibrationRuler/noteBox instead.

Not registered: ``prepCheckList``. It is not an authored worksheet: ``render_week`` builds it
from the week's first-class ``prep_checks`` (render_prep_sheet), where each check has an id,
standard and pass criteria that feed the mastery loop. Hosting it as a worksheet kind would let
a week carry a second, unlinked copy of the checks, so it stays a render block only.
"""

from __future__ import annotations

import re
from typing import Annotated, Any

from pydantic import Field, field_validator, model_validator

from .kinds import ItemRef, KindData, register
from .kinds_comprehension import Text

_HEX = re.compile(r"^#(?:[0-9a-fA-F]{3}|[0-9a-fA-F]{6})$")
_DATA_URI = re.compile(r"^data:image/(?:png|jpeg|gif|webp);base64,[A-Za-z0-9+/]+={0,2}$")
_MAX_SRC = 200_000

# ── doingCard / noteBox ─────────────────────────────────────────────────


class DoingCardData(KindData):
    label: Text = "Go and do"
    text: Text


class NoteBoxData(KindData):
    text: Text


register("doingCard", DoingCardData, waiver="Hands-on prompt card; no answer slot.")
register("noteBox", NoteBoxData, waiver="Static note; asks nothing.")

# ── heartBar ────────────────────────────────────────────────────────────────


class HeartBarData(KindData):
    hearts: Annotated[int, Field(ge=1, le=10)] = 5
    filled_halves: Annotated[int, Field(ge=0, le=20)] = 0
    width_in: Annotated[float, Field(gt=0, le=7.5)] = 5.0
    height_in: Annotated[float, Field(gt=0, le=2.0)] = 0.4
    caption: str = ""

    @model_validator(mode="after")
    def _filled_fits(self) -> "HeartBarData":
        if self.filled_halves > self.hearts * 2:
            raise ValueError(f"filled_halves {self.filled_halves} exceeds {self.hearts * 2} halves")
        return self


register("heartBar", HeartBarData, waiver="Display-only meter; asks nothing.")

# ── colorKey ────────────────────────────────────────────────────────────────


class ColorEntry(KindData):
    fraction: Text
    color_name: Text
    hex: str = "#ffffff"

    @field_validator("hex")
    @classmethod
    def _hex_only(cls, v: str) -> str:
        if not _HEX.match(v):
            raise ValueError("hex must be #rgb or #rrggbb")
        return v


class ColorKeyData(KindData):
    entries: Annotated[list[ColorEntry], Field(min_length=1, max_length=12)]


register("colorKey", ColorKeyData, waiver="Legend for a colouring page; the key asks nothing.")

# ── logoBadge ───────────────────────────────────────────────────────────────


class LogoBadgeData(KindData):
    src: str
    alt: Text
    caption: str = ""

    @field_validator("src")
    @classmethod
    def _inline_image_only(cls, v: str) -> str:
        if len(v) > _MAX_SRC or not _DATA_URI.match(v):
            raise ValueError(
                f"src must be an inline base64 png/jpeg/gif/webp data URI under {_MAX_SRC} chars"
            )
        return v


register("logoBadge", LogoBadgeData, waiver="Decorative badge image with caption; asks nothing.")

# ── calibrationRuler ────────────────────────────────────────────────────────


class CalibrationRulerData(KindData):
    inches: Annotated[int, Field(ge=1, le=7)] = 6
    note: str | None = None

    @field_validator("note")
    @classmethod
    def _note_not_blank(cls, v: str | None) -> str | None:
        if v is not None and not v.strip():
            raise ValueError("note must not be blank (omit it for the default)")
        return v


register(
    "calibrationRuler", CalibrationRulerData, waiver="Print-scale check for the parent; no answer."
)

# ── richText ────────────────────────────────────────────────────────────────


class KV(KindData):
    k: Text
    v: Text


class RichSection(KindData):
    heading: str = ""
    text: str = ""
    bullets: list[Text] = Field(default_factory=list)
    rows: list[KV] = Field(default_factory=list)

    @model_validator(mode="after")
    def _has_content(self) -> "RichSection":
        if not (self.text.strip() or self.bullets or self.rows):
            raise ValueError("a section needs text, bullets or rows")
        return self


class RichTextData(KindData):
    sections: Annotated[list[RichSection], Field(min_length=1, max_length=20)]


register(
    "richText",
    RichTextData,
    waiver="Reading/reference prose (guides, keys); asks nothing. Free text is HTML-escaped.",
)

# ── taskList ────────────────────────────────────────────────────────────────


class Figure(KindData):
    kind: Text
    data: dict[str, Any]


class Task(KindData):
    prompt: Text
    detail: str = ""
    figure: Figure | None = None
    response_lines: Annotated[int, Field(ge=0, le=10)] = 0


class TaskListData(KindData):
    tasks: Annotated[list[Task], Field(min_length=1, max_length=20)]
    start_number: Annotated[int, Field(ge=1, le=99)] = 1

    @model_validator(mode="after")
    def _figures_are_hosted(self) -> "TaskListData":
        from .kinds import HOSTED_KINDS, parse_data

        for i, t in enumerate(self.tasks):
            if t.figure is None:
                continue
            k = t.figure.kind
            if k == "taskList":
                raise ValueError(f"tasks.{i}.figure: taskList cannot nest a taskList")
            if k not in HOSTED_KINDS:
                raise ValueError(f"tasks.{i}.figure: {k!r} is not a hosted kind")
            parse_data(k, t.figure.data)
        return self


def _task_items(d: TaskListData) -> list[ItemRef]:
    return [ItemRef(f"tasks.{i}", t.prompt) for i, t in enumerate(d.tasks)]


register("taskList", TaskListData, _task_items)
