"""Utilities for generating T-chart worksheet data structures."""

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Sequence

from .base import BaseWorksheet


@dataclass(frozen=True)
class TChartColumn:
    """A single column in a T-chart with a label and optional pre-filled answers."""

    label: str
    answers: List[str]  # pre-filled answer rows (empty list = all blank)

    @classmethod
    def from_mapping(cls, payload: dict) -> "TChartColumn":
        label = payload.get("label", "")
        if not label:
            raise ValueError("TChartColumn requires a label")
        answers = list(payload.get("answers", []))
        return cls(label=label, answers=answers)


@dataclass
class TChartWorksheet(BaseWorksheet):
    """Worksheet with a T-chart layout for sorting or comparing items."""

    title: str
    instructions: str
    columns: List[TChartColumn]  # 2 or 3 columns supported
    row_count: int  # number of writing-line rows per column
    word_bank: List[str]  # optional
    show_answers: bool
    metadata: dict | None = None

    def to_markdown(self) -> str:
        """Return a Markdown representation of the T-chart worksheet."""
        lines = [
            f"# {self.title}",
            "",
            self.instructions,
            "",
        ]

        # Column headers
        header_row = " | ".join(col.label for col in self.columns)
        separator_row = " | ".join("---" for _ in self.columns)
        lines.append(f"| {header_row} |")
        lines.append(f"| {separator_row} |")

        # Rows
        for row_idx in range(self.row_count):
            cells = []
            for col in self.columns:
                if self.show_answers and row_idx < len(col.answers):
                    cells.append(col.answers[row_idx])
                else:
                    cells.append("____________")
            lines.append(f"| {' | '.join(cells)} |")

        lines.append("")

        if self.word_bank:
            lines.extend(["## Word Bank", "", ", ".join(self.word_bank)])

        return "\n".join(lines)


def _normalize_columns(columns: Sequence[TChartColumn | dict]) -> List[TChartColumn]:
    """Convert column entries to TChartColumn objects."""
    normalized: List[TChartColumn] = []
    for item in columns:
        if isinstance(item, TChartColumn):
            normalized.append(item)
        elif isinstance(item, dict):
            normalized.append(TChartColumn.from_mapping(item))
        else:
            raise TypeError("Columns must be TChartColumn or dict entries")
    return normalized


def generate_t_chart_worksheet(
    *,
    columns: Sequence[TChartColumn | dict],
    row_count: int = 6,
    word_bank: Sequence[str] | None = None,
    title: str = "T-Chart",
    instructions: str = "Sort the words from the word bank into the correct column.",
    show_answers: bool = False,
    metadata: dict | None = None,
) -> TChartWorksheet:
    """Create a T-chart worksheet for sorting or comparing items.

    Args:
        columns: List of 2 or 3 columns (TChartColumn or dict).
        row_count: Number of writing-line rows per column.
        word_bank: Optional list of words for students to sort.
        title: Worksheet title.
        instructions: Instructions for students.
        show_answers: Whether to render pre-filled answers.
        metadata: Optional metadata dictionary.

    Returns:
        TChartWorksheet instance.

    Raises:
        ValueError: If the number of columns is not 2 or 3, or a column lacks a label.
    """
    normalized_columns = _normalize_columns(columns)

    if len(normalized_columns) not in (2, 3):
        raise ValueError(f"T-chart requires exactly 2 or 3 columns, got {len(normalized_columns)}")

    for col in normalized_columns:
        if not col.label.strip():
            raise ValueError("Each TChartColumn requires a non-empty label")

    return TChartWorksheet(
        title=title,
        instructions=instructions,
        columns=normalized_columns,
        row_count=max(1, row_count),
        word_bank=list(word_bank or []),
        show_answers=show_answers,
        metadata=metadata or {},
    )


__all__ = [
    "TChartColumn",
    "TChartWorksheet",
    "generate_t_chart_worksheet",
]
