"""Comprehension kinds: reading, cause/effect, odd-one-out, Frayer (M2.2b).

Field names are the renderer's own (worksheet_html_renderer._render_*). Enumerators list the
items a parent or the answer key must address.
"""

from __future__ import annotations

from typing import Annotated

from pydantic import Field, StringConstraints, model_validator

from .kinds import ItemRef, KindData, register

Text = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1)]
Lines = Annotated[int, Field(ge=0, le=10)]

DEFAULT_QUADRANTS = ["Definition", "Characteristics", "Examples", "Non-Examples"]


# ── readingWorksheet ────────────────────────────────────────────────────────


class Question(KindData):
    prompt: Text
    response_lines: Lines = 2


class VocabEntry(KindData):
    term: Text
    definition: Text


class ReadingData(KindData):
    title: Text
    passage_title: str = ""
    instructions: str | None = None
    passage: Text
    vocabulary: list[VocabEntry] = Field(default_factory=list)
    questions: Annotated[list[Question], Field(min_length=1)]


def _reading_items(d: ReadingData) -> list[ItemRef]:
    return [ItemRef(f"questions.{i}", q.prompt) for i, q in enumerate(d.questions)]


register("readingWorksheet", ReadingData, _reading_items)


# ── causeEffectWorksheet ────────────────────────────────────────────────────


class CauseEffectPair(KindData):
    cause: Text
    effect: str = ""  # blank means the child writes it
    effect_lines: Lines = 2


class CauseEffectData(KindData):
    title: Text
    instructions: str | None = None
    pairs: Annotated[list[CauseEffectPair], Field(min_length=1)]


def _cause_effect_items(d: CauseEffectData) -> list[ItemRef]:
    return [
        ItemRef(f"pairs.{i}.effect", p.cause) for i, p in enumerate(d.pairs) if not p.effect.strip()
    ]


register("causeEffectWorksheet", CauseEffectData, _cause_effect_items)


# ── oddOneOutWorksheet ──────────────────────────────────────────────────────


class OddRow(KindData):
    items: Annotated[list[Text], Field(min_length=3)]
    reasoning_lines: Lines = 1


class OddOneOutData(KindData):
    title: Text
    instructions: str | None = None
    rows: Annotated[list[OddRow], Field(min_length=1)]


def _odd_items(d: OddOneOutData) -> list[ItemRef]:
    return [ItemRef(f"rows.{i}", " / ".join(r.items)) for i, r in enumerate(d.rows)]


register("oddOneOutWorksheet", OddOneOutData, _odd_items)


# ── frayerModelWorksheet ────────────────────────────────────────────────────


class FrayerEntry(KindData):
    word: Text
    # label -> prefilled text or list of bullets; a missing/empty label is left for the child.
    quadrants: dict[str, str | list[str]] = Field(default_factory=dict)


class FrayerData(KindData):
    title: Text
    instructions: str | None = None
    quadrant_labels: Annotated[list[Text], Field(min_length=1)] = Field(
        default_factory=lambda: list(DEFAULT_QUADRANTS)
    )
    entries: Annotated[list[FrayerEntry], Field(min_length=1)]

    @model_validator(mode="after")
    def _quadrants_match_labels(self) -> "FrayerData":
        if len(set(self.quadrant_labels)) != len(self.quadrant_labels):
            raise ValueError("quadrant_labels must be unique")
        for e in self.entries:
            stray = set(e.quadrants) - set(self.quadrant_labels)
            if stray:
                raise ValueError(
                    f"entry {e.word!r} has quadrants not in quadrant_labels: {sorted(stray)}"
                )
        return self


def _frayer_items(d: FrayerData) -> list[ItemRef]:
    refs = []
    for i, e in enumerate(d.entries):
        for label in d.quadrant_labels:
            if not e.quadrants.get(label):
                refs.append(ItemRef(f"entries.{i}.quadrants.{label}", f"{e.word}: {label}"))
    return refs


register("frayerModelWorksheet", FrayerData, _frayer_items)
