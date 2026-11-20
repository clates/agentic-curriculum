"""Typed errors for the model layer. Every failure a caller can see is an LLMError subclass."""

from __future__ import annotations


class LLMError(Exception):
    """Base class. ``model`` and ``attempts`` are filled in by the layer that knows them."""

    retryable = False

    def __init__(self, message: str, *, model: str | None = None, attempts: int = 1) -> None:
        super().__init__(message)
        self.model = model
        self.attempts = attempts


class LLMConfigError(LLMError):
    """Missing or invalid configuration (no API key, unknown task)."""


class LLMAuthError(LLMError):
    """401/403 from the provider: the key is wrong or not allowed."""


class LLMBadRequest(LLMError):
    """Other 4xx: the request itself is wrong; retrying cannot help."""


class LLMRateLimit(LLMError):
    retryable = True

    def __init__(self, message: str, *, retry_after: float | None = None, **kw) -> None:
        super().__init__(message, **kw)
        self.retry_after = retry_after


class LLMServerError(LLMError):
    retryable = True


class LLMTimeout(LLMError):
    retryable = True


class LLMConnectionError(LLMError):
    retryable = True


class LLMEmptyResponse(LLMError):
    """The provider answered with no usable choice or content."""


class StructuredOutputError(LLMError):
    """Model output could not be parsed/validated into the requested schema, even after repair."""

    def __init__(self, message: str, *, raw: str = "", errors: list[str] | None = None, **kw):
        super().__init__(message, **kw)
        self.raw = raw
        self.errors = errors or []


class CostCapExceeded(LLMError):
    """Raised BEFORE a call is made when the family's spend cap is already reached."""

    def __init__(self, message: str, *, family_id: str, spent: float, cap: float, **kw) -> None:
        super().__init__(message, **kw)
        self.family_id = family_id
        self.spent = spent
        self.cap = cap
