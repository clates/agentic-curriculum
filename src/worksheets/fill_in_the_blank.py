"""Utilities for generating fill-in-the-blank worksheet data structures."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Sequence

from .base import BaseWorksheet


@dataclass(frozen=True)
class FillBlankSegment:
    """A single segment in a fill-in-the-blank passage.

    Exactly one of the three fields should be set:
    - text: plain inline text
    - gap: an integer gap number (1-based) indicating a blank to fill
    - newline: True to force a paragraph break
    """

    text: str | None = None
    gap: int | None = None
    newline: bool = False

    @classmethod
    def from_mapping(cls, payload: dict) -> "FillBlankSegment":
        """Construct a FillBlankSegment from a dict with one of the three keys."""
        if "text" in payload:
            return cls(text=payload["text"])
        if "gap" in payload:
            return cls(gap=int(payload["gap"]))
        if "newline" in payload:
            return cls(newline=bool(payload["newline"]))
        raise ValueError("Segment must have 'text', 'gap', or 'newline' key")


@dataclass
class FillBlankWorksheet(BaseWorksheet):
    """Worksheet with a cloze-style fill-in-the-blank passage."""

    title: str
    instructions: str
    segments: List[FillBlankSegment]
    word_bank: List[str]  # ordered by gap number: word_bank[0] = answer for gap 1
    answers: Dict[str, str]  # {"1": "Sun", "2": "365"} — keyed by str(gap number)
    show_answers: bool
    metadata: dict | None = None

    def to_markdown(self) -> str:
        """Return a Markdown representation of the fill-in-the-blank worksheet."""
        lines = [
            f"# {self.title}",
            "",
            self.instructions,
            "",
        ]

        passage_parts: list[str] = []
        for seg in self.segments:
            if seg.text is not None:
                passage_parts.append(seg.text)
            elif seg.gap is not None:
                passage_parts.append(f"___({seg.gap})___")
            elif seg.newline:
                passage_parts.append("\n\n")

        lines.append("".join(passage_parts))
        lines.append("")

        if self.word_bank:
            lines.append("## Word Bank")
            lines.append("")
            numbered_items = [f"{i + 1}. {word}" for i, word in enumerate(self.word_bank)]
            lines.append("  ".join(numbered_items))
            lines.append("")

        if self.show_answers and self.answers:
            lines.append("## Answer Key")
            lines.append("")
            for gap_num, answer in sorted(self.answers.items(), key=lambda kv: int(kv[0])):
                lines.append(f"{gap_num}. {answer}")

        return "\n".join(lines)


def _normalize_segments(
    segments: Sequence[FillBlankSegment | dict],
) -> List[FillBlankSegment]:
    """Convert segment entries to FillBlankSegment objects."""
    normalized: List[FillBlankSegment] = []
    for item in segments:
        if isinstance(item, FillBlankSegment):
            normalized.append(item)
        elif isinstance(item, dict):
            normalized.append(FillBlankSegment.from_mapping(item))
        else:
            raise TypeError("Segments must be FillBlankSegment or dict entries")
    return normalized


def generate_fill_in_the_blank_worksheet(
    *,
    segments: Sequence[FillBlankSegment | dict],
    word_bank: Sequence[str] | None = None,
    answers: dict | None = None,
    title: str = "Fill in the Blank",
    instructions: str = "Use the word bank to fill in the blanks.",
    show_answers: bool = False,
    metadata: dict | None = None,
) -> FillBlankWorksheet:
    """Create a fill-in-the-blank worksheet from a list of passage segments.

    Args:
        segments: Ordered list of passage segments (text, gap, or newline).
        word_bank: Words for the student to choose from (ordered by gap number).
        answers: Mapping of gap number string to correct answer, e.g. {"1": "Sun"}.
        title: Worksheet title.
        instructions: Instructions for students.
        show_answers: Whether to render answers over the blanks.
        metadata: Optional metadata dictionary.

    Returns:
        FillBlankWorksheet instance.

    Raises:
        ValueError: If no gap segments are present in the passage.
    """
    normalized_segments = _normalize_segments(segments)

    gap_count = sum(1 for seg in normalized_segments if seg.gap is not None)
    if gap_count == 0:
        raise ValueError("At least one gap segment is required in a fill-in-the-blank worksheet")

    return FillBlankWorksheet(
        title=title,
        instructions=instructions,
        segments=normalized_segments,
        word_bank=list(word_bank or []),
        answers=dict(answers or {}),
        show_answers=show_answers,
        metadata=metadata or {},
    )


__all__ = [
    "FillBlankSegment",
    "FillBlankWorksheet",
    "generate_fill_in_the_blank_worksheet",
]
