"""LLMClient: resolves a task to a model/limits, builds the request, calls the provider."""

from __future__ import annotations

from typing import Any

from .config import TaskConfig, task_config
from .openrouter import OpenRouterProvider
from .settings import ProviderSettings
from .types import Completion, CompletionRequest, Provider


class LLMClient:
    def __init__(self, provider: Provider, *, env=None) -> None:
        self.provider = provider
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
        return self.provider.complete(self._request(cfg, cfg.model, messages, response_format))

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
