"""Connection settings from the environment.

Precedence (first set wins): API key OPENROUTER_API_KEY, then legacy OPENAI_API_KEY. Base URL
LLM_BASE_URL, then legacy OPENAI_BASE_URL, then OpenRouter.
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field

from .errors import LLMConfigError

OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"


PRIVACY_MODES = ("strict", "no-training", "off")


def privacy_mode(env=None) -> str:
    """Provider-routing privacy mode.

    ``strict``: OpenRouter may only use endpoints that do not store prompts (zero data
    retention) and do not train on them. ``no-training``: no training/collection but retention
    allowed. ``off``: provider default. LLM_PRIVACY_ROUTING sets it; when unset it is ``strict``
    for a hosted deployment (AGENTIC_HOSTED=1), because a child's first name and the parent's
    notes go to the provider, and ``off`` for self-hosters who bring their own key.
    """
    env = os.environ if env is None else env
    mode = env.get("LLM_PRIVACY_ROUTING")
    if mode is None or mode == "":
        return "strict" if env.get("AGENTIC_HOSTED") in ("1", "true", "yes") else "off"
    if mode not in PRIVACY_MODES:
        raise LLMConfigError(f"LLM_PRIVACY_ROUTING must be one of {PRIVACY_MODES}, got {mode!r}")
    return mode


def routing_preferences(mode: str) -> dict:
    """The OpenRouter ``provider`` request field for a privacy mode (empty for ``off``)."""
    if mode == "strict":
        return {"provider": {"data_collection": "deny", "zdr": True}}
    if mode == "no-training":
        return {"provider": {"data_collection": "deny"}}
    return {}


@dataclass(frozen=True)
class ProviderSettings:
    api_key: str = field(repr=False)  # never shown in repr/logs
    base_url: str = OPENROUTER_BASE_URL
    routing: dict = field(default_factory=dict)  # extra request body (privacy routing)

    @classmethod
    def from_env(cls, env=None) -> "ProviderSettings":
        env = os.environ if env is None else env
        key = env.get("OPENROUTER_API_KEY") or env.get("OPENAI_API_KEY")
        if not key:
            raise LLMConfigError(
                "OPENROUTER_API_KEY environment variable not set (legacy OPENAI_API_KEY also works)"
            )
        base = env.get("LLM_BASE_URL") or env.get("OPENAI_BASE_URL") or OPENROUTER_BASE_URL
        return cls(api_key=key, base_url=base, routing=routing_preferences(privacy_mode(env)))
