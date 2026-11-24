"""Typed errors for the model layer. Every failure a caller can see is an LLMError subclass."""

from __future__ import annotations


class LLMError(Exception):
    """Base class. ``model`` and ``attempts`` are filled in by the layer that knows them."""

    retryable = False  # retry with backoff inside one call (see retry.py)
    # permanent: running the same job again later cannot succeed until a person changes something
    # (a key, a request, a cap). The job queue sends such a failure straight to ``dead``.
    permanent = False

    def __init__(self, message: str, *, model: str | None = None, attempts: int = 1) -> None:
        super().__init__(message)
        self.model = model
        self.attempts = attempts


class LLMConfigError(LLMError, ValueError):
    """Missing or invalid configuration (no API key, unknown task). Also a ValueError."""

    permanent = True  # an operator has to fix the environment first


class LLMAuthError(LLMError):
    """401/403 from the provider: the key is wrong or not allowed."""

    permanent = True


class LLMBadRequest(LLMError):
    """Other 4xx: the request itself is wrong; retrying cannot help."""

    permanent = True


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

    permanent = True  # the cap is monthly: minutes of backoff will not lift it

    def __init__(self, message: str, *, family_id: str, spent: float, cap: float, **kw) -> None:
        super().__init__(message, **kw)
        self.family_id = family_id
        self.spent = spent
        self.cap = cap


def is_permanent(exc: BaseException) -> bool:
    """True when retrying the same work cannot help (see ``LLMError.permanent``). Any exception can
    opt in by carrying a truthy ``permanent`` attribute; the job queue does not string-match."""
    return bool(getattr(exc, "permanent", False))
