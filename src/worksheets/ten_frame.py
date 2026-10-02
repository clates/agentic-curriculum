"""Utilities for generating ten-frame "make ten" worksheet data structures.

Addition-within-20 practice built on double ten-frames: each problem shows
two ten-frames — the first holding ``addend_a`` counters, the second holding
``addend_b`` counters. The student "moves" counters from the second frame to
fill the first to ten (the make-ten split), then records the proof on ruled
equation lines::

    8 + 5  ->  8 + 2 = 10,  10 + 3 = 13

Carrying vs non-carrying: a pair whose sum exceeds 10 must bridge the ten
(carrying); a pair summing to 10 or less does not (non-carrying). Both kinds
render as double ten-frames so the structure stays consistent.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Sequence

from .base import BaseWorksheet

MIN_ADDEND = 0
MAX_ADDEND = 10
MAX_SUM = 20


@dataclass(frozen=True)
class TenFrameProblem:
    """One double ten-frame addition problem, plus the make-ten answer."""

    addend_a: int  # counters shown in the FIRST ten-frame (0-10)
    addend_b: int  # counters shown in the SECOND ten-frame (0-10)
    label: str = ""  # optional story context, e.g. "Sam has 8 red marbles..."

    @property
    def total(self) -> int:
        return self.addend_a + self.addend_b

    @property
    def carries(self) -> bool:
        """True when the pair must bridge ten (sum > 10)."""
        return self.total > 10

    @property
    def make_ten_split(self) -> int:
        """Counters moved from frame two to fill frame one to ten."""
        if self.addend_a >= 10:
            return 0
        return min(self.addend_b, 10 - self.addend_a)

    @property
    def remainder(self) -> int:
        """Counters left in frame two after the move."""
        return self.addend_b - self.make_ten_split

    @classmethod
    def from_mapping(cls, payload: dict) -> "TenFrameProblem":
        return cls(
            addend_a=int(payload.get("addend_a", 0)),
            addend_b=int(payload.get("addend_b", 0)),
            label=payload.get("label", "") or "",
        )

    def proof_equations(self) -> List[str]:
        """Answer-key equations for the make-ten proof."""
        split = self.make_ten_split
        if split and split < self.addend_b:
            return [
                f"{self.addend_a} + {split} = 10",
                f"10 + {self.remainder} = {self.total}",
            ]
        if split and self.total == 10:
            # The move uses all of addend_b and lands exactly on ten.
            return [f"{self.addend_a} + {self.addend_b} = 10"]
        return [f"{self.addend_a} + {self.addend_b} = {self.total}"]


@dataclass
class TenFrameWorksheet(BaseWorksheet):
    """Double ten-frame addition worksheet with make-ten proof lines."""

    title: str
    instructions: str
    problems: List[TenFrameProblem]
    show_answers: bool = False
    equation_lines: int = 2  # ruled lines per problem
    metadata: dict | None = None

    def to_markdown(self) -> str:
        """Return a Markdown representation of the worksheet."""
        header = [f"# {self.title}", self.instructions]
        body = []
        for idx, prob in enumerate(self.problems, start=1):
            block = [f"## Problem {idx}: {prob.addend_a} + {prob.addend_b}"]
            if prob.label:
                block.append(f"    {prob.label}")
            block.append("    [ten-frame: {} filled] [ten-frame: {} filled]".format(
                prob.addend_a, prob.addend_b
            ))
            if self.show_answers:
                block.append(
                    f"    **Proof:** {' , '.join(prob.proof_equations())}"
                )
            else:
                block.append("    Proof:" + " _" * 20 * self.equation_lines)
            body.append("\n".join(block))
        return "\n\n".join(header + body)


def _normalize_problems(
    problems: Sequence[TenFrameProblem | dict],
) -> List[TenFrameProblem]:
    normalized: List[TenFrameProblem] = []
    for item in problems:
        if isinstance(item, TenFrameProblem):
            normalized.append(item)
        elif isinstance(item, dict):
            normalized.append(TenFrameProblem.from_mapping(item))
        else:
            raise TypeError("Problems must be TenFrameProblem or dict entries")
    return normalized


def _validate_problem(problem: TenFrameProblem) -> None:
    for name, value in (("addend_a", problem.addend_a), ("addend_b", problem.addend_b)):
        if not MIN_ADDEND <= value <= MAX_ADDEND:
            raise ValueError(
                f"{name} must be between {MIN_ADDEND} and {MAX_ADDEND}, got {value}"
            )
    if problem.total > MAX_SUM:
        raise ValueError(
            f"{problem.addend_a} + {problem.addend_b} = {problem.total} "
            f"exceeds the addition-within-{MAX_SUM} limit"
        )


def generate_ten_frame_worksheet(
    problems: Sequence[TenFrameProblem | dict],
    *,
    title: str = "Make Ten!",
    instructions: str = (
        "Move counters to fill the first ten-frame to ten. "
        "Write the make-ten proof on the lines."
    ),
    show_answers: bool = False,
    equation_lines: int = 2,
    metadata: dict | None = None,
) -> TenFrameWorksheet:
    """Create a double ten-frame addition worksheet.

    Args:
        problems: Addition pairs (at least one required). Each pair must
            have addends 0-10 and sum to 20 or less.
        title: Worksheet title.
        instructions: Student instructions.
        show_answers: Answer-key mode (fills the make-ten equations).
        equation_lines: Ruled proof lines per problem.
        metadata: Optional metadata dictionary.
    """
    normalized = _normalize_problems(problems)
    if not normalized:
        raise ValueError("At least one problem is required")
    for problem in normalized:
        _validate_problem(problem)
    if equation_lines < 1:
        raise ValueError("equation_lines must be at least 1")

    return TenFrameWorksheet(
        title=title,
        instructions=instructions,
        problems=normalized,
        show_answers=show_answers,
        equation_lines=equation_lines,
        metadata=metadata or {},
    )


__all__ = [
    "TenFrameProblem",
    "TenFrameWorksheet",
    "generate_ten_frame_worksheet",
    "MIN_ADDEND",
    "MAX_ADDEND",
    "MAX_SUM",
]
