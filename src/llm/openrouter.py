"""OpenRouter provider, built on the openai SDK (OpenRouter speaks the OpenAI wire format).

Any OpenAI-compatible endpoint works by changing the base URL, which is how tests and the E2E
stub redirect it. Retries are disabled in the SDK on purpose: the retry layer owns that.
"""

from __future__ import annotations

import time
from typing import Any

import openai
from openai import OpenAI

from .errors import (
    LLMAuthError,
    LLMBadRequest,
    LLMConnectionError,
    LLMEmptyResponse,
    LLMError,
    LLMRateLimit,
    LLMServerError,
    LLMTimeout,
)
from .settings import ProviderSettings
from .types import Completion, CompletionRequest, Usage

DEFAULT_TIMEOUT_S = 120.0


def parse_usage(usage: dict[str, Any] | None) -> Usage:
    """Token counts and (OpenRouter) cost from a response's ``usage`` object."""
    usage = usage or {}
    prompt = int(usage.get("prompt_tokens") or 0)
    completion = int(usage.get("completion_tokens") or 0)
    cost = usage.get("cost")
    return Usage(
        prompt_tokens=prompt,
        completion_tokens=completion,
        total_tokens=int(usage.get("total_tokens") or prompt + completion),
        cost_usd=float(cost) if isinstance(cost, (int, float)) else None,
    )


def _retry_after(exc: openai.APIStatusError) -> float | None:
    try:
        return float(exc.response.headers.get("retry-after"))
    except (TypeError, ValueError, AttributeError):
        return None


class OpenRouterProvider:
    def __init__(self, settings: ProviderSettings, client: OpenAI | None = None) -> None:
        self.settings = settings
        self._client = client or OpenAI(
            api_key=settings.api_key, base_url=settings.base_url, max_retries=0
        )

    def __repr__(self) -> str:
        return f"OpenRouterProvider(base_url={self.settings.base_url!r})"

    def complete(self, request: CompletionRequest) -> Completion:
        payload: dict[str, Any] = {"model": request.model, "messages": request.messages}
        if request.temperature is not None:
            payload["temperature"] = request.temperature
        if request.max_tokens is not None:
            payload["max_tokens"] = request.max_tokens
        if request.response_format is not None:
            payload["response_format"] = request.response_format
        # Ask OpenRouter to report cost in the usage block; other endpoints ignore it.
        payload["extra_body"] = {
            "usage": {"include": True},
            **self.settings.routing,
            **request.extra_body,
        }
        payload["timeout"] = request.timeout_s or DEFAULT_TIMEOUT_S

        started = time.monotonic()
        try:
            response = self._client.chat.completions.create(**payload)
        except openai.APITimeoutError as exc:
            raise LLMTimeout(self._scrub(exc), model=request.model) from exc
        except openai.APIConnectionError as exc:
            raise LLMConnectionError(self._scrub(exc), model=request.model) from exc
        except openai.APIStatusError as exc:
            raise self._status_error(exc, request.model) from exc
        latency = time.monotonic() - started

        raw = response.model_dump()
        choices = raw.get("choices") or []
        if not choices:
            raise LLMEmptyResponse("provider returned no choices", model=request.model)
        choice = choices[0]
        text = (choice.get("message") or {}).get("content") or ""
        return Completion(
            text=text,
            model=raw.get("model") or request.model,
            usage=parse_usage(raw.get("usage")),
            latency_s=latency,
            finish_reason=choice.get("finish_reason"),
            raw=raw,
        )

    def _scrub(self, exc: BaseException) -> str:
        return str(exc).replace(self.settings.api_key, "[redacted]")

    def _status_error(self, exc: openai.APIStatusError, model: str) -> LLMError:
        message = f"HTTP {exc.status_code}: {self._scrub(exc)}"
        if exc.status_code == 429:
            return LLMRateLimit(message, retry_after=_retry_after(exc), model=model)
        if exc.status_code in (401, 403):
            return LLMAuthError(message, model=model)
        if exc.status_code >= 500 or exc.status_code == 408:
            return LLMServerError(message, model=model)
        return LLMBadRequest(message, model=model)
