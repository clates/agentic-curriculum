"""Utilities for generating reading comprehension worksheet data structures."""

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Sequence

from .base import BaseWorksheet, normalize_entries


@dataclass(frozen=True)
class ReadingQuestion:
    prompt: str
    response_lines: int = 2

    @classmethod
    def from_mapping(cls, payload: dict) -> "ReadingQuestion":
        prompt = payload.get("prompt")
        if not prompt:
            raise ValueError("ReadingQuestion requires a prompt")
        response_lines = int(payload.get("response_lines", 2))
        return cls(prompt=prompt, response_lines=max(1, response_lines))


@dataclass(frozen=True)
class VocabularyEntry:
    term: str
    definition: str | None = None
    response_lines: int = 1

    @classmethod
    def from_mapping(cls, payload: dict) -> "VocabularyEntry":
        term = payload.get("term")
        if not term:
            raise ValueError("VocabularyEntry requires a term")
        definition = payload.get("definition")
        response_lines = int(payload.get("response_lines", 1))
        return cls(term=term, definition=definition, response_lines=max(1, response_lines))


@dataclass
class ReadingWorksheet(BaseWorksheet):
    title: str
    passage_title: str
    passage: str
    instructions: str
    questions: List[ReadingQuestion]
    vocabulary: List[VocabularyEntry]
    metadata: dict | None = None

    def to_markdown(self) -> str:
        output: List[str] = [
            f"# {self.title}",
            "",
            self.instructions,
            "",
            f"## Passage: {self.passage_title}",
            "",
            self.passage.strip(),
            "",
            "## Questions",
        ]

        for idx, question in enumerate(self.questions, start=1):
            output.extend(["", f"{idx}. {question.prompt}"])
            for _ in range(question.response_lines):
                output.append("_")

        if self.vocabulary:
            output.extend(["", "## Vocabulary"])
            for entry in self.vocabulary:
                line = f"- {entry.term}"
                if entry.definition:
                    line = f"{line}: {entry.definition}"
                output.append(line)
                if not entry.definition:
                    for _ in range(entry.response_lines):
                        output.append("_")

        return "\n".join(output)


def generate_reading_comprehension_worksheet(
    *,
    passage_title: str,
    passage: str,
    questions: Sequence[ReadingQuestion | dict],
    vocabulary: Sequence[VocabularyEntry | dict] | None = None,
    title: str = "Reading Comprehension",
    instructions: str = "Read the passage carefully, then answer the questions and review the vocabulary.",
    metadata: dict | None = None,
) -> ReadingWorksheet:
    normalized_questions = normalize_entries(
        questions, ReadingQuestion, "Questions must be ReadingQuestion or dict entries"
    )
    if not normalized_questions:
        raise ValueError("At least one reading question is required")
    normalized_vocab = normalize_entries(
        vocabulary or [],
        VocabularyEntry,
        "Vocabulary entries must be VocabularyEntry or dict entries",
    )

    if not passage.strip():
        raise ValueError("Reading passage text is required")

    return ReadingWorksheet(
        title=title,
        passage_title=passage_title,
        passage=passage.strip(),
        instructions=instructions,
        questions=normalized_questions,
        vocabulary=normalized_vocab,
        metadata=metadata or {},
    )


__all__ = [
    "ReadingQuestion",
    "VocabularyEntry",
    "ReadingWorksheet",
    "generate_reading_comprehension_worksheet",
]
