"""Utilities for generating odd-one-out worksheet data structures."""

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Sequence

from .base import BaseWorksheet, normalize_entries


@dataclass(frozen=True)
class OddOneOutItem:
    """An item in an odd-one-out row (text and/or image)."""

    text: str | None = None
    image_path: str | None = None

    @classmethod
    def from_mapping(cls, payload: str | dict) -> "OddOneOutItem":
        if isinstance(payload, str):
            return cls(text=payload)
        return cls(
            text=payload.get("text"),
            image_path=payload.get("image_path"),
        )


@dataclass(frozen=True)
class OddOneOutRow:
    """A row of items with one odd item and optional explanation."""

    items: List[OddOneOutItem]
    odd_item: str | None = None  # The correct answer (for answer key)
    explanation: str | None = None  # Why this item is the odd one

    @classmethod
    def from_mapping(cls, payload: dict) -> "OddOneOutRow":
        items_raw = payload.get("items")
        if not items_raw:
            raise ValueError("OddOneOutRow requires an items list")
        if not isinstance(items_raw, list) or len(items_raw) < 3:
            raise ValueError("OddOneOutRow requires at least 3 items")
        return cls(
            items=[OddOneOutItem.from_mapping(i) for i in items_raw],
            odd_item=payload.get("odd_item"),
            explanation=payload.get("explanation"),
        )


@dataclass
class OddOneOutWorksheet(BaseWorksheet):
    """Worksheet with rows of items where students identify the odd one."""

    title: str
    instructions: str
    rows: List[OddOneOutRow]
    show_answers: bool
    reasoning_lines: int  # Number of lines for student reasoning
    metadata: dict | None = None

    def to_markdown(self) -> str:
        """Return a Markdown representation of the odd-one-out worksheet."""
        lines = [
            f"# {self.title}",
            "",
            self.instructions,
            "",
        ]

        for idx, row in enumerate(self.rows, start=1):
            items_str = "   ".join(item.text or "[Image]" for item in row.items)
            lines.append(f"{idx}. {items_str}")

            if self.show_answers and row.odd_item:
                lines.append(f"   **Answer:** {row.odd_item}")
                if row.explanation:
                    lines.append(f"   **Reason:** {row.explanation}")
            else:
                lines.append("   Circle the odd one out.")
                lines.append(f"   Why? {'_' * 40}")
                for _ in range(self.reasoning_lines - 1):
                    lines.append(f"   {'_' * 50}")

            lines.append("")

        return "\n".join(lines)


def generate_odd_one_out_worksheet(
    *,
    rows: Sequence[OddOneOutRow | dict],
    title: str = "Odd One Out",
    instructions: str = "Look at each row. Circle the item that does not belong and explain why.",
    show_answers: bool = False,
    reasoning_lines: int = 2,
    metadata: dict | None = None,
) -> OddOneOutWorksheet:
    """Create an odd-one-out worksheet (reasoning_lines is clamped to at least 1)."""
    normalized_rows = normalize_entries(
        rows, OddOneOutRow, "Rows must be OddOneOutRow or dict entries"
    )
    if not normalized_rows:
        raise ValueError("At least one row is required")

    return OddOneOutWorksheet(
        title=title,
        instructions=instructions,
        rows=normalized_rows,
        show_answers=show_answers,
        reasoning_lines=max(1, reasoning_lines),
        metadata=metadata or {},
    )


__all__ = [
    "OddOneOutRow",
    "OddOneOutWorksheet",
    "generate_odd_one_out_worksheet",
]
