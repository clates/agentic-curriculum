"""The production week author (M3.3, M3.5-M3.7): plan, then the full WeekDoc, then save.

Two steps, as the quality check proved: (1) plan (narrator, arc, days, worksheet kinds + focus,
chosen from the kind menu); (2) the full WeekDoc with schemas only for the planned kinds. Both go
through ``generate_structured`` (repair keeps the original brief and the author's model and
sampling), step 2 with the completeness gate as its ``check`` hook. The outcome is always an
``AuthorResult``: a validated week and a run record, or a failure with the last errors. Nothing
is swallowed. No migration: the run record is returned and also written as a JSON file next to
the database (``AUTHORING_RUNS_DIR`` overrides).
"""

from __future__ import annotations

import json
import os
import time
import uuid
from dataclasses import asdict, dataclass, field
from datetime import UTC, date, datetime
from pathlib import Path
from typing import Any

from db_utils import get_db_path
from llm import LLMClient, default_client
from llm.errors import CostCapExceeded, LLMError, StructuredOutputError
from llm.ledger import RunBudget, UsageContext
from llm.structured import generate_structured
from weekdoc import WeekDoc

from .context import ModelStudentContext, Tenant
from .gate import make_week_check
from .plan import WeekPlan, make_plan_check
from .prompts_builder import build_prompts
from .standards import Standard, UnknownStandardsError, load_standards

MAX_REPAIRS = 4  # per step
DEFAULT_MAX_RUN_USD = 1.5  # a week costs about $0.10-0.30; override with AUTHOR_MAX_RUN_USD

SUCCESS = "success"
INVALID_INPUT = "invalid_input"
PLAN_FAILED = "plan_failed"
WEEK_FAILED = "week_failed"
BUDGET_EXCEEDED = "budget_exceeded"
PROVIDER_ERROR = "provider_error"
SAVE_FAILED = "save_failed"


@dataclass
class StepRecord:
    name: str
    ok: bool
    calls: int = 0
    repairs: int = 0
    prompt_tokens: int = 0
    completion_tokens: int = 0
    cost_usd: float = 0.0
    wall_s: float = 0.0
    models: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)  # what each rejected attempt was told
    finish_reasons: list[str | None] = field(default_factory=list)


@dataclass
class RunRecord:
    run_id: str
    prompt_version: str
    prompt_hash: str
    status: str = ""
    model: str = ""
    standards: list[str] = field(default_factory=list)
    topic: str = ""
    steps: list[StepRecord] = field(default_factory=list)
    started_at: str = ""
    wall_s: float = 0.0
    packet_id: str | None = None
    uncovered_standards: list[str] = field(default_factory=list)
    final_errors: list[str] = field(default_factory=list)

    @property
    def repairs(self) -> int:
        return sum(s.repairs for s in self.steps)

    @property
    def cost_usd(self) -> float:
        return round(sum(s.cost_usd for s in self.steps), 6)

    @property
    def prompt_tokens(self) -> int:
        return sum(s.prompt_tokens for s in self.steps)

    @property
    def completion_tokens(self) -> int:
        return sum(s.completion_tokens for s in self.steps)

    def to_dict(self) -> dict[str, Any]:
        d = asdict(self)
        d.update(
            repairs=self.repairs,
            cost_usd=self.cost_usd,
            prompt_tokens=self.prompt_tokens,
            completion_tokens=self.completion_tokens,
        )
        return d


@dataclass
class AuthorResult:
    """Success carries the week; failure carries ``errors`` (the last validation errors)."""

    status: str
    run: RunRecord
    week: WeekDoc | None = None
    plan: WeekPlan | None = None
    errors: list[str] = field(default_factory=list)
    packet_id: str | None = None
    saved: bool = False

    @property
    def ok(self) -> bool:
        return self.status == SUCCESS and self.week is not None


def _runs_dir() -> Path:
    env = os.environ.get("AUTHORING_RUNS_DIR")
    return Path(env) if env else Path(get_db_path()).resolve().parent / "authoring_runs"


def _step_from_budget(name: str, budget: RunBudget, start: int, wall: float) -> StepRecord:
    calls = budget.calls[start:]
    return StepRecord(
        name=name,
        ok=False,
        calls=len(calls),
        repairs=max(0, len(calls) - 1),
        prompt_tokens=sum(c["prompt_tokens"] for c in calls),
        completion_tokens=sum(c["completion_tokens"] for c in calls),
        cost_usd=round(sum(c["cost_usd"] or 0.0 for c in calls), 6),
        wall_s=round(wall, 2),
        models=sorted({c["model"] for c in calls}),
    )


def author_week(
    tenant: Tenant,
    student_context: ModelStudentContext | dict[str, Any],
    topic: str,
    standards: list[str] | list[Standard],
    *,
    student_id: str | None = None,
    packet_id: str | None = None,
    week_of: str | None = None,
    client: LLMClient | None = None,
    max_repairs: int = MAX_REPAIRS,
    max_cost_usd: float | None = None,
    db_path: str | None = None,
    persist_run: bool = True,
    save: bool = True,
) -> AuthorResult:
    """Author, validate and (given a ``student_id``) save one week. Never raises for model or
    validation failures; those come back as ``AuthorResult(status=..., errors=[...])``."""
    started = time.monotonic()
    run = RunRecord(
        run_id="run_" + uuid.uuid4().hex[:12],
        prompt_version="",
        prompt_hash="",
        topic=topic.strip(),
        started_at=datetime.now(UTC).isoformat(),
    )

    def finish(status: str, **kw: Any) -> AuthorResult:
        run.status = status
        run.wall_s = round(time.monotonic() - started, 2)
        result = AuthorResult(status=status, run=run, errors=run.final_errors, **kw)
        if persist_run:
            _write_run(result)
        return result

    # ── input ──
    try:
        student = (
            student_context
            if isinstance(student_context, ModelStudentContext)
            else ModelStudentContext.from_profile(student_context)
        )
        if not topic.strip():
            raise ValueError("topic is empty")
        std_list = (
            [s for s in standards if isinstance(s, Standard)]
            if standards and all(isinstance(s, Standard) for s in standards)
            else load_standards([str(s) for s in standards], db_path)
        )
        if not std_list:
            raise ValueError("at least one standard is required")
    except (ValueError, UnknownStandardsError) as exc:
        run.final_errors = [str(exc)]
        return finish(INVALID_INPUT)

    prompts = build_prompts(student, topic, std_list)
    run.prompt_version, run.prompt_hash = prompts.version, prompts.hash
    run.standards = [s.standard_id for s in std_list]
    allowed = set(run.standards)
    client = client or default_client()
    run.model = client.config("author").model
    budget = RunBudget(
        max_cost_usd
        if max_cost_usd is not None
        else float(os.environ.get("AUTHOR_MAX_RUN_USD") or DEFAULT_MAX_RUN_USD)
    )
    usage = UsageContext(family_id=tenant.family_id, student_id=student_id, budget=budget)

    def run_step(name, messages, model_cls, check):
        start, t0 = len(budget.calls), time.monotonic()
        try:
            res = generate_structured(
                "author",
                messages,
                model_cls,
                client=client,
                max_repairs=max_repairs,
                usage=usage,
                check=check,
            )
        except LLMError as exc:
            step = _step_from_budget(name, budget, start, time.monotonic() - t0)
            run.steps.append(step)
            if isinstance(exc, StructuredOutputError):
                step.errors = list(exc.errors)
                run.final_errors = list(exc.errors)
                return None, "validation"
            if isinstance(exc, CostCapExceeded):
                run.final_errors = [str(exc)]
                return None, BUDGET_EXCEEDED
            run.final_errors = [f"{type(exc).__name__}: {exc}"]
            return None, PROVIDER_ERROR
        step = _step_from_budget(name, budget, start, time.monotonic() - t0)
        step.ok = True
        step.errors = list(res.errors)
        step.finish_reasons = [c.finish_reason for c in res.completions]
        run.steps.append(step)
        return res.parsed, None

    # ── step 1: plan ──
    plan, fail = run_step("plan", prompts.plan_messages(), WeekPlan, make_plan_check(allowed))
    if plan is None:
        return finish({"validation": PLAN_FAILED}.get(fail, fail))

    # ── step 2: the week ──
    week_msgs = prompts.week_messages(
        json.dumps(plan.model_dump(mode="json"), ensure_ascii=False), plan.kinds(), student
    )
    week, fail = run_step(
        "week",
        week_msgs,
        WeekDoc,
        make_week_check(allowed_standards=allowed),
    )
    if week is None:
        return finish({"validation": WEEK_FAILED}.get(fail, fail), plan=plan)

    used = {s for d in week.days for s in d.standards} | {c.standard_id for c in week.prep_checks}
    run.uncovered_standards = sorted(allowed - used)

    # ── save ──
    saved = False
    if save and student_id:
        import week_store

        run.packet_id = packet_id or "pk_" + uuid.uuid4().hex[:12]
        try:
            week_store.save_week(
                student_id,
                run.packet_id,
                week,
                grade_level=student.grade,
                week_of=week_of or date.today().isoformat(),
                family_id=tenant.family_id,
            )
            saved = True
        except Exception as exc:  # reported, not swallowed: the week is still in the result
            run.final_errors = [f"save failed: {type(exc).__name__}: {exc}"]
            return finish(SAVE_FAILED, week=week, plan=plan, packet_id=run.packet_id)
    return finish(SUCCESS, week=week, plan=plan, packet_id=run.packet_id, saved=saved)


def _write_run(result: AuthorResult) -> None:
    """Best effort: a run-record write failure must not lose a good week."""
    try:
        folder = _runs_dir()
        folder.mkdir(parents=True, exist_ok=True)
        name = result.run.packet_id or result.run.run_id
        (folder / f"{name}.json").write_text(
            json.dumps(result.run.to_dict(), indent=1, ensure_ascii=False), encoding="utf-8"
        )
    except OSError:
        pass
