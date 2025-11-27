"""Utilities for generating two-operand math worksheet data structures."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import List, Sequence, Tuple

from .base import BaseWorksheet


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
class MathWorksheet(BaseWorksheet):
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


# Backward compatibility alias
Worksheet = MathWorksheet


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
) -> MathWorksheet:
    """Create a worksheet object for K-1 math practice."""
    normalized = _normalize_problems(problems)
    if not normalized:
        raise ValueError("At least one problem is required")

    return MathWorksheet(
        title=title,
        instructions=instructions,
        problems=normalized,
        metadata=metadata or {},
    )


__all__ = [
    "Operator",
    "TwoOperandProblem",
    "MathWorksheet",
    "Worksheet",  # Backward compatibility alias
    "generate_two_operand_math_worksheet",
    "format_vertical_problem",
]
