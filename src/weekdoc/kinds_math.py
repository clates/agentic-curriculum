"""Math kinds for K-2: two-operand, ten frame, number line, speed math (M2.2e).

K-2 bounds are enforced here so a model cannot hand a kindergartner a three-digit problem or a
negative answer. Speed math is typed ``{a, op, b}`` (the renderer also still accepts the older
free-text ``{q}`` / string problems for the offline scripts). The legacy ``mathWorksheet`` alias
is registered in kinds_graphs with this same model.
"""

from __future__ import annotations

from typing import Annotated, Literal

from pydantic import Field, StringConstraints, model_validator

from .kinds import ItemRef, KindData, register
from .kinds_comprehension import Text

Op = Literal["+", "-"]
Fill = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=8)]


def _no_negative(a: int, op: str, b: int) -> None:
    if op == "-" and b > a:
        raise ValueError(f"{a} - {b} is negative; K-2 problems must not go below zero")


# ── twoOperandWorksheet ─────────────────────────────────────────────────────


class TwoOperandProblem(KindData):
    operand_one: Annotated[int, Field(ge=0, le=999)]
    operand_two: Annotated[int, Field(ge=0, le=999)]
    operator: Op = "+"

    @model_validator(mode="after")
    def _bounds(self) -> "TwoOperandProblem":
        _no_negative(self.operand_one, self.operator, self.operand_two)
        return self


class TwoOperandData(KindData):
    title: Text
    instructions: str | None = None
    problems: Annotated[list[TwoOperandProblem], Field(min_length=1, max_length=20)]


def _two_operand_items(d: TwoOperandData) -> list[ItemRef]:
    return [
        ItemRef(f"problems.{i}", f"{p.operand_one} {p.operator} {p.operand_two}")
        for i, p in enumerate(d.problems)
    ]


register("twoOperandWorksheet", TwoOperandData, _two_operand_items)


# ── tenFrameWorksheet ───────────────────────────────────────────────────────


class TenFrameProblem(KindData):
    addend_a: Annotated[int, Field(ge=0, le=10)]
    addend_b: Annotated[int, Field(ge=0, le=10)]
    label: str = ""
    fill_a: Fill = "black"  # CSS colour or one emoji
    fill_b: Fill = "black"


class TenFrameData(KindData):
    title: Text
    instructions: str | None = None
    problems: Annotated[list[TenFrameProblem], Field(min_length=1, max_length=8)]
    equation_lines: Annotated[int, Field(ge=1, le=4)] = 2


def _ten_frame_items(d: TenFrameData) -> list[ItemRef]:
    return [
        ItemRef(f"problems.{i}", f"{p.addend_a} + {p.addend_b}") for i, p in enumerate(d.problems)
    ]


register("tenFrameWorksheet", TenFrameData, _ten_frame_items)


# ── numberLineWorksheet ─────────────────────────────────────────────────────

_STEPS = (1, 2, 5, 10)


class Jump(KindData):
    from_: Annotated[float, Field(alias="from")]
    to: float
    label: str = ""


class NumberLineTask(KindData):
    prompt: Text
    start: Annotated[int, Field(ge=0, le=100)] = 0
    end: Annotated[int, Field(ge=1, le=120)] = 10
    step: Annotated[int, Field(ge=1, le=10)] = 1
    hidden_positions: list[int] = Field(default_factory=list)
    mark_positions: list[int] = Field(default_factory=list)
    jumps: list[Jump] = Field(default_factory=list)
    hop_space: bool = False

    @model_validator(mode="after")
    def _on_the_line(self) -> "NumberLineTask":
        if self.step not in _STEPS:
            raise ValueError(f"step must be one of {_STEPS}")
        if self.end <= self.start:
            raise ValueError("end must be greater than start")
        if (self.end - self.start) % self.step:
            raise ValueError("end must land on a tick (start + k*step)")
        ticks = set(range(self.start, self.end + 1, self.step))
        if not 2 <= len(ticks) <= 21:
            raise ValueError(f"a number line needs 2-21 ticks, got {len(ticks)}")
        for name in ("hidden_positions", "mark_positions"):
            off = [v for v in getattr(self, name) if v not in ticks]
            if off:
                raise ValueError(f"{name} {off} are not tick positions")
        for j in self.jumps:
            if j.from_ not in ticks or j.to not in ticks:
                raise ValueError(f"jump {j.from_}->{j.to} must start and end on ticks")
        if not (self.hidden_positions or self.hop_space or self.jumps):
            raise ValueError("task has nothing for the child to do (no hidden positions or hops)")
        return self


class NumberLineData(KindData):
    title: Text
    instructions: str | None = None
    tasks: Annotated[list[NumberLineTask], Field(min_length=1, max_length=6)]


def _number_line_items(d: NumberLineData) -> list[ItemRef]:
    return [ItemRef(f"tasks.{i}", t.prompt) for i, t in enumerate(d.tasks)]


register("numberLineWorksheet", NumberLineData, _number_line_items)


# ── speedMath ───────────────────────────────────────────────────────────────


class SpeedProblem(KindData):
    a: Annotated[int, Field(ge=0, le=20)]
    op: Op
    b: Annotated[int, Field(ge=0, le=20)]

    @model_validator(mode="after")
    def _bounds(self) -> "SpeedProblem":
        _no_negative(self.a, self.op, self.b)
        return self


class SpeedMathData(KindData):
    title: str = ""
    instructions: str = ""
    problems: Annotated[list[SpeedProblem], Field(min_length=1, max_length=40)]
    columns: Annotated[int, Field(ge=1, le=6)] = 4
    answer_style: Literal["blank", "box"] = "blank"
    timer: str = ""


def _speed_items(d: SpeedMathData) -> list[ItemRef]:
    return [ItemRef(f"problems.{i}", f"{p.a} {p.op} {p.b}") for i, p in enumerate(d.problems)]


register("speedMath", SpeedMathData, _speed_items)
