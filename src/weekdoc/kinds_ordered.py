"""Ordered and gap kinds: sequencing and fill-in-the-blank (M2.2d).

Fill-in-the-blank segments are a discriminated union (text | gap | newline), matching the
renderer's segment dicts exactly. Answers for gaps and step orders live in the worksheet's
``answers`` (addressed by item_ref), not in ``data``, so ``show_answers`` and the renderer's
``answers`` dict are not hosted fields.

Note for rendering: the renderer shuffles the fill-in word bank with ``random``; render_week
(M2.4) seeds it so output is deterministic.
"""

from __future__ import annotations

from typing import Annotated, Any, Literal, Union

from pydantic import Discriminator, Field, Tag, model_validator

from .kinds import ItemRef, KindData, register
from .kinds_comprehension import Text

# ── sequencingWorksheet ─────────────────────────────────────────────────────


class SeqStep(KindData):
    text: Text
    correct_order: Annotated[int, Field(ge=1, le=12)]


class SequencingData(KindData):
    title: Text
    instructions: str | None = None
    activity_name: Text
    steps: Annotated[list[SeqStep], Field(min_length=3, max_length=12)]

    @model_validator(mode="after")
    def _order_is_a_permutation(self) -> "SequencingData":
        orders = sorted(s.correct_order for s in self.steps)
        if orders != list(range(1, len(self.steps) + 1)):
            raise ValueError(
                f"correct_order must use each of 1..{len(self.steps)} exactly once, got {orders}"
            )
        return self


def _seq_items(d: SequencingData) -> list[ItemRef]:
    return [ItemRef(f"steps.{i}", s.text) for i, s in enumerate(d.steps)]


register("sequencingWorksheet", SequencingData, _seq_items)

# ── fillInBlankWorksheet ────────────────────────────────────────────────────


class TextSeg(KindData):
    text: Text


class GapSeg(KindData):
    gap: Annotated[int, Field(ge=1, le=30)]


class NewlineSeg(KindData):
    newline: Literal[True]


def _segment_tag(v: Any) -> str | None:
    keys = set(v) if isinstance(v, dict) else set(getattr(v, "model_fields_set", ()))
    for tag in ("text", "gap", "newline"):
        if tag in keys:
            return tag
    return None


Segment = Annotated[
    Union[
        Annotated[TextSeg, Tag("text")],
        Annotated[GapSeg, Tag("gap")],
        Annotated[NewlineSeg, Tag("newline")],
    ],
    Discriminator(_segment_tag),
]


class FillInBlankData(KindData):
    title: Text
    instructions: str | None = None
    segments: Annotated[list[Segment], Field(min_length=2)]
    word_bank: list[Text] = Field(default_factory=list)

    @model_validator(mode="after")
    def _gaps(self) -> "FillInBlankData":
        gaps = [s.gap for s in self.segments if isinstance(s, GapSeg)]
        if not gaps:
            raise ValueError("a fill-in-the-blank needs at least one gap")
        if gaps != list(range(1, len(gaps) + 1)):
            raise ValueError(f"gaps must be numbered 1..n in order, got {gaps}")
        if self.word_bank:
            folded = [w.casefold() for w in self.word_bank]
            if len(set(folded)) != len(folded):
                raise ValueError("word_bank must be unique")
            if len(self.word_bank) < len(gaps):
                raise ValueError(f"word_bank has {len(self.word_bank)} words for {len(gaps)} gaps")
        return self


def _fib_items(d: FillInBlankData) -> list[ItemRef]:
    refs = []
    for i, seg in enumerate(d.segments):
        if isinstance(seg, GapSeg):
            before = next((s.text for s in reversed(d.segments[:i]) if isinstance(s, TextSeg)), "")
            refs.append(ItemRef(f"segments.{i}", f"gap {seg.gap}: ...{before[-40:]}"))
    return refs


register("fillInBlankWorksheet", FillInBlankData, _fib_items)
