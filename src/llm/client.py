"""LLMClient: resolves a task to a model/limits, builds the request, calls the provider."""

from __future__ import annotations

import os
import time
from typing import Any, Callable

from .config import TaskConfig, task_config
from .openrouter import OpenRouterProvider
from .retry import RetryPolicy, complete_with_retry
from .settings import ProviderSettings
from .types import Completion, CompletionRequest, Provider


class LLMClient:
    def __init__(
        self,
        provider: Provider,
        *,
        env=None,
        policy: RetryPolicy | None = None,
        sleep: Callable[[float], None] = time.sleep,
    ) -> None:
        self.provider = provider
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
    ) -> Completion:
        cfg = self.config(task)
        request = self._request(cfg, cfg.model, messages, response_format)
        policy = self._policy or RetryPolicy.from_env(
            self._env if self._env is not None else os.environ
        )
        return complete_with_retry(
            self.provider, request, policy, fallback_model=cfg.fallback_model, sleep=self._sleep
        )

    @staticmethod
    def _request(cfg: TaskConfig, model: str, messages, response_format) -> CompletionRequest:
        return CompletionRequest(
            model=model,
            messages=messages,
            temperature=cfg.temperature,
            max_tokens=cfg.max_tokens,
            response_format=response_format,
            timeout_s=cfg.timeout_s,
        )


def default_client(env=None) -> LLMClient:
    """Client for the configured OpenRouter-compatible endpoint (reads the environment)."""
    return LLMClient(OpenRouterProvider(ProviderSettings.from_env(env)), env=env)
