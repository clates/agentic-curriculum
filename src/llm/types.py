"""Provider-neutral request/response types."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Protocol


@dataclass(frozen=True)
class Usage:
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0
    cost_usd: float | None = None  # None = provider did not report a cost


@dataclass(frozen=True)
class CompletionRequest:
    model: str
    messages: list[dict[str, Any]]
    temperature: float | None = None
    max_tokens: int | None = None
    response_format: dict[str, Any] | None = None
    top_p: float | None = None  # sent in the request body (extra_body), not as an SDK kwarg
    top_k: int | None = None
    timeout_s: float | None = None
    # Provider routing options, e.g. {"provider": {"data_collection": "deny"}} for OpenRouter.
    extra_body: dict[str, Any] = field(default_factory=dict)


@dataclass
class Completion:
    text: str
    model: str
    usage: Usage
    latency_s: float
    finish_reason: str | None = None
    raw: dict[str, Any] = field(default_factory=dict)  # provider response, for generation logs

    def model_dump(self) -> dict[str, Any]:
        """The raw provider response (what the generation logger stores)."""
        return self.raw


class Provider(Protocol):
    """One method: turn a request into a Completion or raise a typed LLMError."""

    def complete(self, request: CompletionRequest) -> Completion: ...
