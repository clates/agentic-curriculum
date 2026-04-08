"""Utilities for generating writing scaffold worksheet data structures."""

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Sequence

from .base import BaseWorksheet


@dataclass(frozen=True)
class ScaffoldSection:
    """One section of the writing scaffold."""

    label: str  # e.g. "Topic Sentence", "Detail 1", "Conclusion"
    starter: str | None  # sentence starter text, e.g. "I think that..."
    lines: int  # number of blank writing lines (1-6)

    @classmethod
    def from_mapping(cls, payload: dict) -> "ScaffoldSection":
        """Construct a ScaffoldSection from a dict."""
        label = payload.get("label", "")
        starter = payload.get("starter", None)
        lines = int(payload.get("lines", 2))
        return cls(label=label, starter=starter, lines=lines)


@dataclass
class WritingScaffoldWorksheet(BaseWorksheet):
    """Worksheet with a structured writing frame."""

    title: str
    instructions: str
    frame_type: str  # "opinion", "narrative", "informational", "custom"
    sections: List[ScaffoldSection]
    show_example: bool  # show a filled-in example in lighter text
    example_texts: List[str] | None  # one example per section if show_example
    topic: str | None  # optional topic prompt shown at top
    metadata: dict | None = None

    def to_markdown(self) -> str:
        """Return a Markdown representation of the writing scaffold worksheet."""
        lines = [f"# {self.title}", "", self.instructions, ""]
        if self.topic:
            lines.append(f"**Topic:** {self.topic}")
            lines.append("")
        for _i, section in enumerate(self.sections):
            lines.append(f"**{section.label}**")
            if section.starter:
                lines.append(f"_{section.starter}_")
            for _ in range(section.lines):
                lines.append("_" * 60)
            lines.append("")
        return "\n".join(lines)


def _normalize_sections(
    sections: Sequence[ScaffoldSection | dict],
) -> List[ScaffoldSection]:
    """Convert section entries to ScaffoldSection objects."""
    normalized: List[ScaffoldSection] = []
    for item in sections:
        if isinstance(item, ScaffoldSection):
            normalized.append(item)
        elif isinstance(item, dict):
            normalized.append(ScaffoldSection.from_mapping(item))
        else:
            raise TypeError("Sections must be ScaffoldSection or dict entries")
    return normalized


def generate_writing_scaffold_worksheet(
    *,
    sections: Sequence[ScaffoldSection | dict],
    title: str = "Writing Scaffold",
    instructions: str = "Use the sentence starters below to write your paragraph.",
    frame_type: str = "custom",
    topic: str | None = None,
    show_example: bool = False,
    example_texts: list[str] | None = None,
    metadata: dict | None = None,
) -> WritingScaffoldWorksheet:
    """Create a writing scaffold worksheet from a list of sections.

    Args:
        sections: Ordered list of scaffold sections (label, starter, lines).
        title: Worksheet title.
        instructions: Instructions for students.
        frame_type: Type of writing frame: "opinion", "narrative",
            "informational", or "custom".
        topic: Optional topic prompt shown at the top.
        show_example: Whether to render ghosted example text over the lines.
        example_texts: One example string per section (used when show_example=True).
        metadata: Optional metadata dictionary.

    Returns:
        WritingScaffoldWorksheet instance.

    Raises:
        ValueError: If no sections are provided or lines value is out of range.
    """
    normalized_sections = _normalize_sections(sections)

    if not normalized_sections:
        raise ValueError("At least one section is required in a writing scaffold worksheet")

    valid_frame_types = {"opinion", "narrative", "informational", "custom"}
    if frame_type not in valid_frame_types:
        raise ValueError(f"frame_type must be one of {valid_frame_types}, got {frame_type!r}")

    for sec in normalized_sections:
        if not (1 <= sec.lines <= 6):
            raise ValueError(
                f"Section '{sec.label}' has lines={sec.lines}; must be between 1 and 6"
            )

    if show_example and example_texts is not None:
        if len(example_texts) != len(normalized_sections):
            raise ValueError(
                f"example_texts length ({len(example_texts)}) must match "
                f"sections length ({len(normalized_sections)}) when show_example=True"
            )

    return WritingScaffoldWorksheet(
        title=title,
        instructions=instructions,
        frame_type=frame_type,
        sections=normalized_sections,
        show_example=show_example,
        example_texts=list(example_texts) if example_texts is not None else None,
        topic=topic,
        metadata=metadata or {},
    )


__all__ = [
    "ScaffoldSection",
    "WritingScaffoldWorksheet",
    "generate_writing_scaffold_worksheet",
]
