"""Utilities for generating alphabet worksheet data structures."""

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Sequence

from .base import BaseWorksheet


@dataclass
class AlphabetWorksheet(BaseWorksheet):
    """Worksheet for alphabet practice with large letters and specialized handwriting lines."""

    letter: str  # The centerpiece letter (e.g., 'A')
    starting_words: List[str]
    containing_words: List[str]
    character_image_path: str | None = None
    title: str = "Alphabet Practice"
    instructions: str = "Practice your letters and reading words!"
    metadata: dict | None = None

    def to_markdown(self) -> str:
        """Return a Markdown representation of the alphabet worksheet."""
        lines = [
            f"# {self.title}",
            "",
            self.instructions,
            "",
            f"## Centerpiece: {self.letter.upper()} {self.letter.lower()}",
            "",
            "### Starting Words:",
            ", ".join(self.starting_words),
            "",
            "### Containing Words:",
            ", ".join(self.containing_words),
            "",
        ]
        return "\n".join(lines)


def generate_alphabet_worksheet(
    *,
    letter: str,
    starting_words: Sequence[str],
    containing_words: Sequence[str],
    character_image_path: str | None = None,
    title: str = "Alphabet Practice",
    instructions: str = "Practice your letters and reading words!",
    metadata: dict | None = None,
) -> AlphabetWorksheet:
    """Create an alphabet worksheet.

    Args:
        letter: The letter to practice.
        starting_words: List of words starting with the letter.
        containing_words: List of words containing the letter.
        character_image_path: Path to a character image.
        title: Worksheet title.
        instructions: Instructions for students.
        metadata: Optional metadata dictionary.

    Returns:
        AlphabetWorksheet instance.
    """
    if not letter or len(letter) != 1:
        raise ValueError("letter must be a single character")

    return AlphabetWorksheet(
        letter=letter.upper(),
        starting_words=list(starting_words),
        containing_words=list(containing_words),
        character_image_path=character_image_path,
        title=title,
        instructions=instructions,
        metadata=metadata or {},
    )


__all__ = [
    "AlphabetWorksheet",
    "generate_alphabet_worksheet",
]
