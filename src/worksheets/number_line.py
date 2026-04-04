"""Utilities for generating number line worksheet data structures."""

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Sequence

from .base import BaseWorksheet


@dataclass(frozen=True)
class NumberLineTask:
    """One number line task."""

    start: float  # leftmost number
    end: float  # rightmost number
    step: float  # interval between tick marks
    hidden_positions: List[float]  # values to leave blank (student fills in)
    prompt: str | None  # instruction for this line, e.g. "Count by 2s"
    mark_positions: List[float]  # positions to mark with a dot/arrow

    @classmethod
    def from_mapping(cls, payload: dict) -> "NumberLineTask":
        start = float(payload.get("start", 0))
        end = float(payload.get("end", 10))
        step = float(payload.get("step", 1))
        hidden = [float(x) for x in payload.get("hidden_positions", [])]
        prompt = payload.get("prompt")
        marks = [float(x) for x in payload.get("mark_positions", [])]
        return cls(
            start=start,
            end=end,
            step=step,
            hidden_positions=hidden,
            prompt=prompt,
            mark_positions=marks,
        )


@dataclass
class NumberLineWorksheet(BaseWorksheet):
    """Worksheet with number lines for counting and arithmetic practice."""

    title: str
    instructions: str
    tasks: List[NumberLineTask]
    show_answers: bool
    metadata: dict | None = None

    def to_markdown(self) -> str:
        lines = [f"# {self.title}", "", self.instructions, ""]
        for i, task in enumerate(self.tasks, 1):
            lines.append(f"**{i}.** {task.prompt or ''}")
            # Build tick sequence manually (no numpy)
            positions: list[float] = []
            val = task.start
            while val <= task.end + task.step * 0.001:
                positions.append(round(val, 10))
                val += task.step
            ticks = []
            for p in positions:
                if any(abs(p - h) < 0.001 for h in task.hidden_positions) and not self.show_answers:
                    ticks.append("___")
                else:
                    ticks.append(str(int(p) if p == int(p) else p))
            lines.append(" | ".join(ticks))
            lines.append("")
        return "\n".join(lines)


def _normalize_tasks(tasks: Sequence[NumberLineTask | dict]) -> List[NumberLineTask]:
    normalized: List[NumberLineTask] = []
    for item in tasks:
        if isinstance(item, NumberLineTask):
            normalized.append(item)
        elif isinstance(item, dict):
            normalized.append(NumberLineTask.from_mapping(item))
        else:
            raise TypeError("Tasks must be NumberLineTask or dict entries")
    return normalized


def generate_number_line_worksheet(
    *,
    tasks: Sequence[NumberLineTask | dict],
    title: str = "Number Line",
    instructions: str = "Fill in the missing numbers on each number line.",
    show_answers: bool = False,
    metadata: dict | None = None,
) -> NumberLineWorksheet:
    """Create a number line worksheet.

    Args:
        tasks: List of number line tasks.
        title: Worksheet title.
        instructions: Instructions for students.
        show_answers: Whether to show answers in hidden positions.
        metadata: Optional metadata dictionary.

    Returns:
        NumberLineWorksheet instance.

    Raises:
        ValueError: If no tasks provided or task has invalid step.
    """
    normalized = _normalize_tasks(tasks)
    if not normalized:
        raise ValueError("At least one task is required")
    for task in normalized:
        if task.step <= 0:
            raise ValueError(f"step must be positive, got {task.step}")
        if task.end < task.start:
            raise ValueError(f"end ({task.end}) must be >= start ({task.start})")
    return NumberLineWorksheet(
        title=title,
        instructions=instructions,
        tasks=normalized,
        show_answers=show_answers,
        metadata=metadata or {},
    )


__all__ = [
    "NumberLineTask",
    "NumberLineWorksheet",
    "generate_number_line_worksheet",
]
