"""Usage ledger and per-family cost caps.

The ledger stores opaque ids, task, model, token counts, cost and latency. It never stores prompt
or response text. A cap is checked BEFORE the provider is called: if the family has already spent
its cap in the current UTC month the call raises CostCapExceeded and no request is made. (A single
call can overshoot the cap by its own cost; there is no pre-call price estimate.) Caps default to
unlimited so a self-hoster is never blocked.
"""

from __future__ import annotations

import logging
import sqlite3
import threading
import uuid
from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Callable, Protocol

from .errors import CostCapExceeded, LLMConfigError
from .types import Usage

logger = logging.getLogger(__name__)


class RunBudget:
    """A per-run spend cap and meter. Checked before every call (a call can overshoot it by its
    own cost); every completed call is added, so the run record has exact totals."""

    def __init__(self, limit_usd: float | None = None) -> None:
        self.limit_usd = limit_usd
        self.spent_usd = 0.0
        self.calls: list[dict] = []
        self._lock = threading.Lock()

    def check(self, model: str | None = None) -> None:
        if self.limit_usd is not None and self.spent_usd >= self.limit_usd:
            raise CostCapExceeded(
                f"run budget reached (${self.spent_usd:.4f} of ${self.limit_usd:.2f})",
                family_id=None,
                spent=self.spent_usd,
                cap=self.limit_usd,
                model=model,
                attempts=0,
            )

    def add(self, task: str, model: str, usage: Usage) -> None:
        with self._lock:
            self.spent_usd += usage.cost_usd or 0.0
            self.calls.append(
                {
                    "task": task,
                    "model": model,
                    "prompt_tokens": usage.prompt_tokens,
                    "completion_tokens": usage.completion_tokens,
                    "cost_usd": usage.cost_usd,
                }
            )


@dataclass(frozen=True)
class UsageContext:
    """Who a call is billed to. Opaque ids only (fam_..., stu_...)."""

    family_id: str | None = None
    student_id: str | None = None
    budget: RunBudget | None = field(default=None, compare=False, repr=False)


@dataclass(frozen=True)
class CostCaps:
    family_month_usd: float | None = None  # None = unlimited

    @classmethod
    def from_env(cls, env) -> "CostCaps":
        raw = (env or {}).get("LLM_CAP_FAMILY_MONTH_USD")
        if not raw:
            return cls()
        try:
            value = float(raw)
        except ValueError as exc:
            raise LLMConfigError(f"LLM_CAP_FAMILY_MONTH_USD must be a number, got {raw!r}") from exc
        return cls(family_month_usd=value)


def month_start(now: datetime | None = None) -> str:
    now = now or datetime.now(UTC)
    return now.replace(day=1, hour=0, minute=0, second=0, microsecond=0).isoformat()


class Ledger(Protocol):
    def spent_usd(self, family_id: str, since_iso: str) -> float: ...

    def record(
        self,
        ctx: UsageContext,
        *,
        task: str,
        model: str,
        usage: Usage,
        latency_s: float,
        status: str,
    ) -> None: ...


def check_cap(ledger: Ledger, caps: CostCaps, ctx: UsageContext, model: str | None = None) -> None:
    """Raise CostCapExceeded if the family has already reached its cap. Call before the request."""
    if caps.family_month_usd is None or not ctx.family_id:
        return
    spent = ledger.spent_usd(ctx.family_id, month_start())
    if spent >= caps.family_month_usd:
        raise CostCapExceeded(
            f"family {ctx.family_id} reached its monthly model budget "
            f"(${spent:.4f} of ${caps.family_month_usd:.2f})",
            family_id=ctx.family_id,
            spent=spent,
            cap=caps.family_month_usd,
            model=model,
            attempts=0,
        )


class InMemoryLedger:
    def __init__(self) -> None:
        self.rows: list[dict] = []
        self._lock = threading.Lock()

    def spent_usd(self, family_id: str, since_iso: str) -> float:
        with self._lock:
            return sum(
                r["cost_usd"] or 0.0
                for r in self.rows
                if r["family_id"] == family_id and r["created_at"] >= since_iso
            )

    def record(self, ctx, *, task, model, usage, latency_s, status) -> None:
        with self._lock:
            self.rows.append(_row(ctx, task, model, usage, latency_s, status))


def _row(ctx, task, model, usage, latency_s, status) -> dict:
    return {
        "usage_id": "use_" + uuid.uuid4().hex[:16],
        "family_id": ctx.family_id,
        "student_id": ctx.student_id,
        "task": task,
        "model": model,
        "prompt_tokens": usage.prompt_tokens,
        "completion_tokens": usage.completion_tokens,
        "cost_usd": usage.cost_usd,
        "latency_ms": int(latency_s * 1000),
        "status": status,
        "created_at": datetime.now(UTC).isoformat(),
    }


class SqliteLedger:
    """The llm_usage table (migration 0003). ``db_path`` is a callable so the env is read per call."""

    def __init__(self, db_path: Callable[[], str]) -> None:
        self._db_path = db_path

    def _connect(self) -> sqlite3.Connection:
        return sqlite3.connect(self._db_path(), timeout=30)

    def spent_usd(self, family_id: str, since_iso: str) -> float:
        conn = self._connect()
        try:
            row = conn.execute(
                "SELECT COALESCE(SUM(cost_usd), 0) FROM llm_usage "
                "WHERE family_id = ? AND created_at >= ?",
                (family_id, since_iso),
            ).fetchone()
            return float(row[0])
        finally:
            conn.close()

    def record(self, ctx, *, task, model, usage, latency_s, status) -> None:
        row = _row(ctx, task, model, usage, latency_s, status)
        conn = self._connect()
        try:
            conn.execute(
                "INSERT INTO llm_usage (usage_id, family_id, student_id, task, model, "
                "prompt_tokens, completion_tokens, cost_usd, latency_ms, status, created_at) "
                "VALUES (:usage_id, :family_id, :student_id, :task, :model, :prompt_tokens, "
                ":completion_tokens, :cost_usd, :latency_ms, :status, :created_at)",
                row,
            )
            conn.commit()
        finally:
            conn.close()
