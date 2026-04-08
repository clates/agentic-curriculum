"""Utilities for generating cause-and-effect organizer worksheet data structures."""

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Sequence

from .base import BaseWorksheet


@dataclass(frozen=True)
class CauseEffectPair:
    """One cause-effect relationship.

    Either cause or effect (or both) may be None, indicating the student fills
    in that field.  The optional label is displayed to the left of the pair row.
    """

    cause: str | None  # None → student fills in
    effect: str | None  # None → student fills in
    label: str | None = None  # e.g. "Event 1"

    @classmethod
    def from_mapping(cls, payload: dict) -> "CauseEffectPair":
        return cls(
            cause=payload.get("cause"),
            effect=payload.get("effect"),
            label=payload.get("label"),
        )


@dataclass
class CauseEffectWorksheet(BaseWorksheet):
    """Worksheet with cause→effect paired boxes."""

    title: str
    instructions: str
    pairs: List[CauseEffectPair]
    show_answers: bool
    layout: str  # "horizontal" or "vertical"
    metadata: dict | None = None

    def to_markdown(self) -> str:
        lines = [f"# {self.title}", "", self.instructions, ""]
        for i, pair in enumerate(self.pairs, 1):
            label = pair.label or f"Pair {i}"
            cause_text = (
                pair.cause
                if (pair.cause and self.show_answers) or pair.cause
                else "_______________"
            )
            effect_text = (
                pair.effect
                if (pair.effect and self.show_answers) or pair.effect
                else "_______________"
            )
            lines.append(f"**{label}**")
            lines.append(f"Cause: {cause_text}  →  Effect: {effect_text}")
            lines.append("")
        return "\n".join(lines)


def _normalize_pairs(pairs: Sequence[CauseEffectPair | dict]) -> List[CauseEffectPair]:
    """Convert pair entries to CauseEffectPair objects."""
    normalized: List[CauseEffectPair] = []
    for item in pairs:
        if isinstance(item, CauseEffectPair):
            normalized.append(item)
        elif isinstance(item, dict):
            normalized.append(CauseEffectPair.from_mapping(item))
        else:
            raise TypeError("Pairs must be CauseEffectPair or dict entries")
    return normalized


def generate_cause_effect_worksheet(
    *,
    pairs: Sequence[CauseEffectPair | dict],
    title: str = "Cause and Effect",
    instructions: str = "Read each cause. Write what you think will happen (the effect).",
    layout: str = "horizontal",
    show_answers: bool = False,
    metadata: dict | None = None,
) -> CauseEffectWorksheet:
    """Create a cause-and-effect organizer worksheet.

    Args:
        pairs: List of cause/effect relationships (CauseEffectPair or dict).
               Each dict may contain keys: ``cause``, ``effect``, ``label``
               (all optional — None means student fills in).
        title: Worksheet title.
        instructions: Instructions for students.
        layout: ``"horizontal"`` (cause and effect side by side) or
                ``"vertical"`` (cause above, arrow, effect below).
        show_answers: If True, pre-filled cause/effect text is rendered.
        metadata: Optional metadata dictionary.

    Returns:
        CauseEffectWorksheet instance.

    Raises:
        ValueError: If no pairs are provided or layout is unrecognised.
    """
    normalized = _normalize_pairs(pairs)
    if not normalized:
        raise ValueError("At least one cause-effect pair is required")
    if layout not in ("horizontal", "vertical"):
        raise ValueError(f"layout must be 'horizontal' or 'vertical', got {layout!r}")
    return CauseEffectWorksheet(
        title=title,
        instructions=instructions,
        pairs=normalized,
        show_answers=show_answers,
        layout=layout,
        metadata=metadata or {},
    )


__all__ = [
    "CauseEffectPair",
    "CauseEffectWorksheet",
    "generate_cause_effect_worksheet",
]
