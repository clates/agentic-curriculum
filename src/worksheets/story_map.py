"""Utilities for generating story map worksheet data structures."""

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Sequence

from .base import BaseWorksheet


@dataclass(frozen=True)
class StoryMapField:
    """One field in the story map."""

    label: str  # e.g. "Characters", "Setting", "Problem"
    prompt: str | None  # guiding question, e.g. "Who is in the story?"
    lines: int  # blank writing lines (1-4)
    value: str | None  # pre-filled value (for answer keys / partially filled scaffolds)


@dataclass
class StoryMapWorksheet(BaseWorksheet):
    title: str
    instructions: str
    story_title_field: bool  # whether to include a "Story Title:" field at top
    fields: List[StoryMapField]
    show_answers: bool
    metadata: dict | None = None

    def to_markdown(self) -> str:
        lines = [f"# {self.title}", "", self.instructions, ""]
        if self.story_title_field:
            lines.append("**Story Title:** " + "_" * 40)
            lines.append("")
        for f in self.fields:
            lines.append(f"**{f.label}**")
            if f.prompt:
                lines.append(f"_{f.prompt}_")
            if self.show_answers and f.value:
                lines.append(f.value)
            else:
                for _ in range(f.lines):
                    lines.append("_" * 55)
            lines.append("")
        return "\n".join(lines)


def _normalize_fields(fields: Sequence[StoryMapField | dict]) -> List[StoryMapField]:
    """Convert field entries to StoryMapField objects."""
    normalized: List[StoryMapField] = []
    for item in fields:
        if isinstance(item, StoryMapField):
            normalized.append(item)
        elif isinstance(item, dict):
            label = item.get("label", "")
            if not label:
                raise ValueError("StoryMapField requires a label")
            normalized.append(
                StoryMapField(
                    label=label,
                    prompt=item.get("prompt"),
                    lines=max(1, int(item.get("lines", 2))),
                    value=item.get("value"),
                )
            )
        else:
            raise TypeError("Fields must be StoryMapField or dict entries")
    return normalized


def generate_story_map_worksheet(
    *,
    title: str = "Story Map",
    instructions: str = "Fill in each box about the story you read.",
    story_title_field: bool = True,
    fields: Sequence[StoryMapField | dict],
    show_answers: bool = False,
    metadata: dict | None = None,
) -> StoryMapWorksheet:
    """Create a story map worksheet for narrative organization.

    Args:
        title: Worksheet title.
        instructions: Instructions for students.
        story_title_field: Whether to include a "Story Title:" line at top.
        fields: List of StoryMapField entries (or dicts) for each story element.
        show_answers: Whether to render pre-filled answer values.
        metadata: Optional metadata dictionary.

    Returns:
        StoryMapWorksheet instance.

    Raises:
        ValueError: If fields list is empty or a field lacks a label.
    """
    normalized_fields = _normalize_fields(fields)

    if not normalized_fields:
        raise ValueError("Story map requires at least one field")

    for f in normalized_fields:
        if not f.label.strip():
            raise ValueError("Each StoryMapField requires a non-empty label")
        if not (1 <= f.lines <= 10):
            raise ValueError(f"Field lines must be between 1 and 10, got {f.lines}")

    return StoryMapWorksheet(
        title=title,
        instructions=instructions,
        story_title_field=story_title_field,
        fields=normalized_fields,
        show_answers=show_answers,
        metadata=metadata or {},
    )


__all__ = [
    "StoryMapField",
    "StoryMapWorksheet",
    "generate_story_map_worksheet",
]
