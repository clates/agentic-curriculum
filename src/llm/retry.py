"""The one retry layer: backoff on 429/5xx/timeouts/connection errors, then an optional fallback.

Only errors marked ``retryable`` are retried; auth and bad-request errors surface at once.
The SDK's own retries are disabled so attempts are counted and bounded here.
"""

from __future__ import annotations

import random
import time
from dataclasses import dataclass, replace
from typing import Callable

from .errors import LLMError
from .types import Completion, CompletionRequest, Provider


@dataclass(frozen=True)
class RetryPolicy:
    max_attempts: int = 3  # per model, including the first try
    base_delay_s: float = 0.5
    max_delay_s: float = 8.0
    jitter: float = 0.25  # +/- fraction of the delay

    def delay(self, attempt: int, error: LLMError) -> float:
        hinted = getattr(error, "retry_after", None)
        if hinted is not None:
            return min(float(hinted), self.max_delay_s)
        base = min(self.base_delay_s * (2 ** (attempt - 1)), self.max_delay_s)
        return base * (1 + random.uniform(-self.jitter, self.jitter))

    @classmethod
    def from_env(cls, env) -> "RetryPolicy":
        raw = (env or {}).get("LLM_MAX_ATTEMPTS")
        return cls(max_attempts=max(1, int(raw))) if raw else cls()


def complete_with_retry(
    provider: Provider,
    request: CompletionRequest,
    policy: RetryPolicy = RetryPolicy(),
    *,
    fallback_model: str | None = None,
    sleep: Callable[[float], None] = time.sleep,
) -> Completion:
    """Call the provider; retry retryable failures; then try ``fallback_model`` the same way.

    Raises the last LLMError with ``attempts`` set to the total number of calls made.
    """
    models = [request.model] + ([fallback_model] if fallback_model else [])
    total = 0
    last: LLMError | None = None
    for model in models:
        req = request if model == request.model else replace(request, model=model)
        for attempt in range(1, policy.max_attempts + 1):
            total += 1
            try:
                return provider.complete(req)
            except LLMError as exc:
                last = exc
                exc.model = model
                if not exc.retryable:
                    exc.attempts = total
                    raise
                if attempt < policy.max_attempts:
                    sleep(policy.delay(attempt, exc))
    assert last is not None
    last.attempts = total
    raise last
