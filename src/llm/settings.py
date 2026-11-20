"""Connection settings from the environment.

Precedence (first set wins): API key OPENROUTER_API_KEY, then legacy OPENAI_API_KEY. Base URL
LLM_BASE_URL, then legacy OPENAI_BASE_URL, then OpenRouter.
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field

from .errors import LLMConfigError

OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"


@dataclass(frozen=True)
class ProviderSettings:
    api_key: str = field(repr=False)  # never shown in repr/logs
    base_url: str = OPENROUTER_BASE_URL

    @classmethod
    def from_env(cls, env=None) -> "ProviderSettings":
        env = os.environ if env is None else env
        key = env.get("OPENROUTER_API_KEY") or env.get("OPENAI_API_KEY")
        if not key:
            raise LLMConfigError(
                "OPENROUTER_API_KEY environment variable not set (legacy OPENAI_API_KEY also works)"
            )
        base = env.get("LLM_BASE_URL") or env.get("OPENAI_BASE_URL") or OPENROUTER_BASE_URL
        return cls(api_key=key, base_url=base)
