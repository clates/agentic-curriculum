"""Utilities for generating matching worksheet data structures."""

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Sequence

from .base import BaseWorksheet


@dataclass(frozen=True)
class MatchingItem:
    """An item on one side of a matching worksheet."""

    text: str | None = None
    image_path: str | None = None
    as_shadow: bool = False

    @classmethod
    def from_mapping(cls, payload: dict | str) -> "MatchingItem":
        if isinstance(payload, str):
            return cls(text=payload)
        return cls(
            text=payload.get("text"),
            image_path=payload.get("image_path"),
            as_shadow=payload.get("as_shadow", False),
        )


@dataclass
class MatchingWorksheet(BaseWorksheet):
    """Worksheet for matching items between two columns."""

    title: str
    instructions: str
    left_items: List[MatchingItem]
    right_items: List[MatchingItem]
    metadata: dict | None = None

    def to_markdown(self) -> str:
        """Return a Markdown representation of the matching worksheet."""
        lines = [
            f"# {self.title}",
            "",
            self.instructions,
            "",
        ]

        max_len = max(len(self.left_items), len(self.right_items))
        for i in range(max_len):
            left = ""
            if i < len(self.left_items):
                item = self.left_items[i]
                left = item.text or "[Image]"

            right = ""
            if i < len(self.right_items):
                item = self.right_items[i]
                right = item.text or ("[Shadow]" if item.as_shadow else "[Image]")

            lines.append(f"{i + 1}. {left} <---> {right}")

        return "\n".join(lines)


def _normalize_items(items: Sequence[MatchingItem | dict | str]) -> List[MatchingItem]:
    """Convert items to MatchingItem objects."""
    normalized: List[MatchingItem] = []
    for item in items:
        if isinstance(item, MatchingItem):
            normalized.append(item)
        else:
            normalized.append(MatchingItem.from_mapping(item))
    return normalized


def generate_matching_worksheet(
    *,
    left_items: Sequence[MatchingItem | dict | str],
    right_items: Sequence[MatchingItem | dict | str],
    title: str = "Match the Pairs",
    instructions: str = "Draw a line to match the item on the left with the correct one on the right.",
    metadata: dict | None = None,
) -> MatchingWorksheet:
    """Create a matching worksheet.

    Args:
        left_items: Items for the left column.
        right_items: Items for the right column.
        title: Worksheet title.
        instructions: Instructions for students.
        metadata: Optional metadata dictionary.

    Returns:
        MatchingWorksheet instance.
    """
    left = _normalize_items(left_items)
    right = _normalize_items(right_items)

    if not left or not right:
        raise ValueError("Both columns must have at least one item")

    return MatchingWorksheet(
        title=title,
        instructions=instructions,
        left_items=left,
        right_items=right,
        metadata=metadata or {},
    )


__all__ = [
    "MatchingItem",
    "MatchingWorksheet",
    "generate_matching_worksheet",
]
