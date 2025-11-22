"""Utilities for generating printable worksheet data structures."""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import List, Sequence, Tuple


class Operator(str, Enum):
    """Supported binary math operators for early grades."""

    PLUS = "+"
    MINUS = "-"

    def apply(self, left: int, right: int) -> int:
        if self is Operator.PLUS:
            return left + right
        if self is Operator.MINUS:
            return left - right
        raise ValueError(f"Unsupported operator: {self}")


@dataclass(frozen=True)
class TwoOperandProblem:
    operand_one: int
    operand_two: int
    operator: Operator

    @classmethod
    def from_mapping(cls, payload: dict) -> "TwoOperandProblem":
        try:
            operand_one = int(payload["operand_one"])
            operand_two = int(payload["operand_two"])
            operator = payload["operator"]
        except KeyError as exc:
            raise ValueError(f"Missing required key: {exc.args[0]}") from exc
        return cls(
            operand_one=operand_one,
            operand_two=operand_two,
            operator=Operator(operator) if not isinstance(operator, Operator) else operator,
        )

    def expression(self) -> str:
        return f"{self.operand_one} {self.operator.value} {self.operand_two}"

    def answer(self) -> int:
        return self.operator.apply(self.operand_one, self.operand_two)


def format_vertical_problem(problem: TwoOperandProblem) -> Tuple[List[str], int]:
    """Return strings for the operands plus the operand width for answer lines."""

    top = str(problem.operand_one)
    bottom = str(problem.operand_two)
    operand_width = max(len(top), len(bottom))

    top_line = f"  {top.rjust(operand_width)}"
    bottom_line = f"{problem.operator.value} {bottom.rjust(operand_width)}"

    return [top_line, bottom_line], operand_width


@dataclass
class Worksheet:
    title: str
    instructions: str
    problems: List[TwoOperandProblem]
    metadata: dict | None = None

    def to_markdown(self) -> str:
        """Return a Markdown representation with vertically stacked problems."""

        header = [f"# {self.title}", self.instructions]
        body = []
        for problem in self.problems:
            lines, width = format_vertical_problem(problem)
            answer_line = f"  {'_' * width}"
            vertical_block = "\n".join([*lines, answer_line])
            body.append(f"````\n{vertical_block}\n````")

        return "\n\n".join(header + body)


def _normalize_problems(problems: Sequence[TwoOperandProblem | dict]) -> List[TwoOperandProblem]:
    normalized: List[TwoOperandProblem] = []
    for item in problems:
        if isinstance(item, TwoOperandProblem):
            normalized.append(item)
        elif isinstance(item, dict):
            normalized.append(TwoOperandProblem.from_mapping(item))
        else:
            raise TypeError("Problems must be TwoOperandProblem or dict entries")
    return normalized


def generate_two_operand_math_worksheet(
    problems: Sequence[TwoOperandProblem | dict],
    *,
    title: str = "Two-Operand Practice",
    instructions: str = "Solve each problem. Show your work if needed.",
    metadata: dict | None = None,
) -> Worksheet:
    """Create a worksheet object for K-1 math practice."""
    normalized = _normalize_problems(problems)
    if not normalized:
        raise ValueError("At least one problem is required")

    return Worksheet(
        title=title,
        instructions=instructions,
        problems=normalized,
        metadata=metadata or {},
    )


@dataclass(frozen=True)
class ReadingQuestion:
    prompt: str
    response_lines: int = 2

    @classmethod
    def from_mapping(cls, payload: dict) -> "ReadingQuestion":
        prompt = payload.get("prompt")
        if not prompt:
            raise ValueError("ReadingQuestion requires a prompt")
        response_lines = int(payload.get("response_lines", cls.response_lines))
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
        response_lines = int(payload.get("response_lines", cls.response_lines))
        return cls(term=term, definition=definition, response_lines=max(1, response_lines))


@dataclass
class ReadingWorksheet:
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


def _normalize_questions(items: Sequence[ReadingQuestion | dict]) -> List[ReadingQuestion]:
    normalized: List[ReadingQuestion] = []
    for item in items:
        if isinstance(item, ReadingQuestion):
            normalized.append(item)
        elif isinstance(item, dict):
            normalized.append(ReadingQuestion.from_mapping(item))
        else:
            raise TypeError("Questions must be ReadingQuestion or dict entries")
    if not normalized:
        raise ValueError("At least one reading question is required")
    return normalized


def _normalize_vocabulary(items: Sequence[VocabularyEntry | dict] | None) -> List[VocabularyEntry]:
    if not items:
        return []
    normalized: List[VocabularyEntry] = []
    for item in items:
        if isinstance(item, VocabularyEntry):
            normalized.append(item)
        elif isinstance(item, dict):
            normalized.append(VocabularyEntry.from_mapping(item))
        else:
            raise TypeError("Vocabulary entries must be VocabularyEntry or dict entries")
    return normalized


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
    normalized_questions = _normalize_questions(questions)
    normalized_vocab = _normalize_vocabulary(vocabulary)

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
    "Operator",
    "TwoOperandProblem",
    "Worksheet",
    "generate_two_operand_math_worksheet",
    "format_vertical_problem",
    "ReadingQuestion",
    "VocabularyEntry",
    "ReadingWorksheet",
    "generate_reading_comprehension_worksheet",
]
