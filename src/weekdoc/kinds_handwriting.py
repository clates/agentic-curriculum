"""Handwriting and writing-practice kinds (M2.9c).

Hosted: alphabetWorksheet, handwritingWorksheet, letterWorksheet, writingScaffoldWorksheet,
mirrorMessageWorksheet. All five render from inline HTML/CSS/SVG only.

Renderer dependency audit (src/worksheet_html_renderer.py):
- Fonts: embedded inline by print_fonts (data: URIs) or system stacks; there is no @import or
  webfont URL, so nothing is fetched while rendering or printing. The "trace" look is plain grey
  text, not a dotted or school-style font.
- Images: handwriting ``items[].image_path`` and alphabet ``character_image_path`` become
  ``<img src=...>`` verbatim. A model-written value could be a local path or a remote URL
  (a tracking beacon the viewer's browser would fetch, or an unresolved local file). These
  fields are therefore NOT part of the hosted models (extra is forbidden); the renderer's own
  fallback draws a blank dashed drawing box. Pictures can come back later as stored uploads.
- Glyphs: mirror/trace letters render in system serif via CSS text-stroke on transparent text
  (needs a modern browser; print preview in a legacy one shows blank boxes), so mirror text and
  the alphabet letter are limited to ASCII letters and basic punctuation. The letter-writing
  parchment seal and the envelope scissors use symbols the renderer chooses itself.

None of the five is unsafe to host. Nothing here is a ``Not hosted`` kind.

Enumerators: alphabet, handwriting and mirror message are copy/trace practice with no answer
(waivers). The writing scaffold's sections and a letter's reply paragraphs and self-edit
checklist are prompts a parent reviews, so they are addressable.
"""

from __future__ import annotations

import re
from typing import Annotated, Literal

from pydantic import Field, model_validator

from .kinds import ItemRef, KindData, register
from .kinds_comprehension import Text

Lines = Annotated[int, Field(ge=1, le=12)]
Word = Annotated[str, Field(min_length=1, max_length=24, pattern=r"^\S.*\S$|^\S$")]

# ── writingScaffoldWorksheet ────────────────────────────────────────────────


class ScaffoldSection(KindData):
    label: Text
    starter: str = ""
    lines: Lines = 3


class WritingScaffoldData(KindData):
    title: Text
    instructions: str | None = None
    topic: str = ""
    sections: Annotated[list[ScaffoldSection], Field(min_length=1, max_length=8)]


def _scaffold_items(d: WritingScaffoldData) -> list[ItemRef]:
    return [
        ItemRef(f"sections.{i}", f"{s.label}: {s.starter}" if s.starter else s.label)
        for i, s in enumerate(d.sections)
    ]


register("writingScaffoldWorksheet", WritingScaffoldData, _scaffold_items)

# ── handwritingWorksheet ────────────────────────────────────────────────────


class BottomRail(KindData):
    bottom_rail: bool = False


class HandwritingItem(KindData):
    text: Annotated[str, Field(min_length=1, max_length=16, pattern=r"^\S+$")]
    sub_label: str | None = None
    metadata: BottomRail | None = None


class HandwritingData(KindData):
    title: Text
    instructions: str | None = None
    items: Annotated[list[HandwritingItem], Field(min_length=1, max_length=16)]
    rows: Annotated[int, Field(ge=1, le=8)] = 4
    cols: Annotated[int, Field(ge=1, le=4)] = 2

    @model_validator(mode="after")
    def _fits_the_grid(self) -> "HandwritingData":
        # The renderer silently drops items beyond rows*cols; hosting rejects instead.
        if len(self.items) > self.rows * self.cols:
            raise ValueError(
                f"{len(self.items)} items do not fit a {self.rows}x{self.cols} grid "
                f"({self.rows * self.cols} cells)"
            )
        return self


register(
    "handwritingWorksheet",
    HandwritingData,
    waiver="Copy-and-trace practice; the child writes the printed word, nothing to answer or check.",
)

# ── alphabetWorksheet ───────────────────────────────────────────────────────


class AlphabetData(KindData):
    title: Text
    instructions: str | None = None
    letter: Annotated[str, Field(pattern=r"^[A-Za-z]$")]
    starting_words: Annotated[list[Word], Field(min_length=1, max_length=8)]
    containing_words: Annotated[list[Word], Field(min_length=1, max_length=8)]

    @model_validator(mode="after")
    def _words_match_the_letter(self) -> "AlphabetData":
        ch = self.letter.casefold()
        bad = [w for w in self.starting_words if not w.casefold().startswith(ch)]
        if bad:
            raise ValueError(f"starting_words must begin with {self.letter!r}: {bad}")
        bad = [w for w in self.containing_words if ch not in w.casefold()]
        if bad:
            raise ValueError(f"containing_words must contain {self.letter!r}: {bad}")
        return self


register(
    "alphabetWorksheet",
    AlphabetData,
    waiver="Letter tracing and free practice; word lists are examples to read, not questions.",
)

# ── mirrorMessageWorksheet ──────────────────────────────────────────────────

_PHRASE_RE = re.compile(r"^[A-Za-z][A-Za-z '!.?,-]*$")


class MirrorMessageData(KindData):
    title: Text
    instructions: str | None = None
    mode: Literal["intro", "trace"] = "trace"
    letters: list[Annotated[str, Field(pattern=r"^[A-Za-z]$")]] | None = None
    phrase: str | None = None
    reveal_note: str | None = None

    @model_validator(mode="after")
    def _mode_fields(self) -> "MirrorMessageData":
        if self.mode == "intro":
            if not self.letters or len(self.letters) > 8:
                raise ValueError("intro mode needs 1-8 single letters")
            if self.phrase is not None or self.reveal_note is not None:
                raise ValueError("intro mode takes letters only, not phrase or reveal_note")
        else:
            if self.letters is not None:
                raise ValueError("trace mode takes a phrase, not letters")
            if self.phrase is None or not _PHRASE_RE.match(self.phrase) or len(self.phrase) > 20:
                raise ValueError(
                    "trace mode needs a phrase of up to 20 characters: letters, spaces, "
                    "and basic punctuation, starting with a letter"
                )
        return self


register(
    "mirrorMessageWorksheet",
    MirrorMessageData,
    waiver="Mirror-trace activity; the child traces printed letters, nothing to answer.",
)

# ── letterWorksheet ─────────────────────────────────────────────────────────


class IncomingLetter(KindData):
    place_date: str | None = None
    greeting: str | None = None
    body: Text
    closing: str | None = None
    signature: str | None = None
    seal: Annotated[str, Field(min_length=1, max_length=1)] | None = None


class ReplyParagraph(KindData):
    starter: str = ""
    lines: Annotated[int, Field(ge=1, le=12)] = 2


class ReplyLetter(KindData):
    greeting: str = "Dear ________________,"
    paragraphs: Annotated[list[ReplyParagraph], Field(min_length=1, max_length=6)] = Field(
        default_factory=lambda: [ReplyParagraph(lines=6)]
    )
    closing_options: list[Text] = Field(default_factory=list, max_length=6)
    signature_line: bool = True


class Envelope(KindData):
    """Pre-printed address lines; first names only (the child's name may appear, nothing else)."""

    to: str = ""
    from_: str = Field(default="", alias="from")


class LetterData(KindData):
    title: Text
    instructions: str | None = None
    style: Literal["plain", "parchment"] = "plain"
    incoming: IncomingLetter | None = None
    reply: ReplyLetter | None = None
    word_bank: list[Text] = Field(default_factory=list, max_length=20)
    checklist: list[Text] = Field(default_factory=list, max_length=10)
    envelope: bool | Envelope | None = None

    @model_validator(mode="after")
    def _has_a_letter(self) -> "LetterData":
        if self.incoming is None and self.reply is None:
            raise ValueError("a letter worksheet needs an incoming letter, a reply, or both")
        return self


def _letter_items(d: LetterData) -> list[ItemRef]:
    refs: list[ItemRef] = []
    if d.reply is not None:
        for i, p in enumerate(d.reply.paragraphs):
            refs.append(ItemRef(f"reply.paragraphs.{i}", p.starter or f"reply paragraph {i + 1}"))
    refs += [ItemRef(f"checklist.{i}", c) for i, c in enumerate(d.checklist)]
    return refs


register("letterWorksheet", LetterData, _letter_items)
