"""LLMClient: resolves a task to a model/limits, builds the request, calls the provider."""

from __future__ import annotations

import logging
import os
import time
from dataclasses import replace
from typing import Any, Callable

from .config import TaskConfig, task_config
from .errors import LLMError
from .ledger import CostCaps, Ledger, UsageContext, check_cap
from .redact import install_log_redaction
from .openrouter import OpenRouterProvider
from .retry import RetryPolicy, complete_with_retry
from .settings import ProviderSettings
from .types import Completion, CompletionRequest, Provider, Usage


logger = logging.getLogger(__name__)


class LLMClient:
    def __init__(
        self,
        provider: Provider,
        *,
        env=None,
        policy: RetryPolicy | None = None,
        sleep: Callable[[float], None] = time.sleep,
        ledger: Ledger | None = None,
        caps: CostCaps | None = None,
    ) -> None:
        install_log_redaction()
        self.provider = provider
        self.ledger = ledger
        self._caps = caps
        self._policy = policy
        self._sleep = sleep
        self._env = env  # None = live os.environ, so tests can monkeypatch

    def config(self, task: str) -> TaskConfig:
        return task_config(task, env=self._env)

    def complete(
        self,
        task: str,
        messages: list[dict[str, Any]],
        *,
        response_format: dict[str, Any] | None = None,
        usage: UsageContext | None = None,
        model: str | None = None,
        max_tokens: int | None = None,
        config_task: str | None = None,
    ) -> Completion:
        """Run one task. ``usage`` names who is billed; with a ledger it is checked against the
        family cap before any request is made, and the call is recorded afterwards.

        ``model`` overrides the task's model for this call only (used by the taste-test harness);
        an explicit model never silently falls back to another one.

        ``config_task`` resolves model, fallback and sampling from another task's config while
        ``task`` stays the ledger label: a repair call uses the author's model and sampling.
        """
        cfg = self.config(config_task or task)
        if model:
            cfg = replace(cfg, model=model, fallback_model=None)
        if max_tokens:
            cfg = replace(cfg, max_tokens=max_tokens)
        ctx = usage or UsageContext()
        env = self._env if self._env is not None else os.environ
        if self.ledger is not None:
            check_cap(self.ledger, self._caps or CostCaps.from_env(env), ctx, cfg.model)
        if ctx.budget is not None:
            ctx.budget.check(cfg.model)
        request = self._request(cfg, cfg.model, messages, response_format)

        def request_for(model: str) -> CompletionRequest:
            alt = task_config(config_task or task, env=self._env, model=model)
            if max_tokens:
                alt = replace(alt, max_tokens=max_tokens)
            return self._request(alt, model, messages, response_format)

        policy = self._policy or RetryPolicy.from_env(env)
        try:
            result = complete_with_retry(
                self.provider, request, policy, fallback_model=cfg.fallback_model, sleep=self._sleep,
                request_for=request_for,
            )
        except LLMError as exc:
            self._record(ctx, task, exc.model or cfg.model, Usage(), 0.0, "error")
            raise
        if ctx.budget is not None:
            ctx.budget.add(task, result.model, result.usage)
        self._record(ctx, task, result.model, result.usage, result.latency_s, "ok")
        return result

    def _record(self, ctx, task, model, usage, latency_s, status) -> None:
        if self.ledger is None or not (ctx.family_id or ctx.student_id):
            return
        try:
            self.ledger.record(
                ctx, task=task, model=model, usage=usage, latency_s=latency_s, status=status
            )
        except Exception:  # a ledger fault must never fail the user's generation
            logger.warning("llm usage ledger write failed (task=%s)", task, exc_info=True)

    @staticmethod
    def _request(cfg: TaskConfig, model: str, messages, response_format) -> CompletionRequest:
        return CompletionRequest(
            model=model,
            messages=messages,
            temperature=cfg.temperature,
            top_p=cfg.top_p,
            top_k=cfg.top_k,
            max_tokens=cfg.max_tokens,
            response_format=response_format,
            timeout_s=cfg.timeout_s,
        )


def default_client(env=None) -> LLMClient:
    """Client for the configured OpenRouter-compatible endpoint (reads the environment).

    Usage goes to the llm_usage table of the app database (CURRICULUM_DB_PATH).
    """
    from db_utils import get_db_path

    from .ledger import SqliteLedger

    return LLMClient(
        OpenRouterProvider(ProviderSettings.from_env(env)),
        env=env,
        ledger=SqliteLedger(get_db_path),
    )
