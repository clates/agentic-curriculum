"""Step 1 of the pipeline: the week plan (narrator, arc, days, worksheet kinds + focus)."""

from __future__ import annotations

from typing import Callable

from pydantic import BaseModel, Field, model_validator
from weekdoc import HOSTED_KINDS

from .gate import DAYS, MIN_WORKSHEETS_PER_DAY


class PlanWorksheet(BaseModel):
    id: str
    kind: str
    focus: str = Field(min_length=3)

    @model_validator(mode="after")
    def _kind_exists(self) -> "PlanWorksheet":
        if self.kind not in HOSTED_KINDS:
            raise ValueError(f"kind {self.kind!r} is not in the kind menu")
        return self


class PlanDay(BaseModel):
    day: str
    title: str = Field(min_length=1)
    standards: list[str] = Field(min_length=1)
    worksheets: list[PlanWorksheet]


class WeekPlan(BaseModel):
    narrator: str = Field(min_length=1)
    arc: str = Field(min_length=1)
    days: list[PlanDay]

    @model_validator(mode="after")
    def _shape(self) -> "WeekPlan":
        if [d.day for d in self.days] != DAYS:
            raise ValueError(
                "plan must cover Monday, Tuesday, Wednesday, Thursday, Friday in order"
            )
        if any(len(d.worksheets) < MIN_WORKSHEETS_PER_DAY for d in self.days):
            raise ValueError("each day needs at least 2 worksheets")
        ids = [w.id for d in self.days for w in d.worksheets]
        if len(set(ids)) != len(ids):
            raise ValueError("worksheet ids must be unique across the week")
        return self

    def kinds(self) -> list[str]:
        return sorted({w.kind for d in self.days for w in d.worksheets})


def make_plan_check(allowed_standards: set[str]) -> Callable[[WeekPlan], str | None]:
    def check(plan: WeekPlan) -> str | None:
        bad = sorted({s for d in plan.days for s in d.standards if s not in allowed_standards})
        if bad:
            return f"plan uses standards not in the STANDARDS list: {', '.join(bad)}"
        return None

    return check
