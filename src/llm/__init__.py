# ruff: noqa: F401, F403
"""Model layer: one provider interface, OpenRouter implementation, typed errors."""

from .errors import *  # noqa: F401,F403
from .openrouter import OpenRouterProvider, parse_usage
from .settings import ProviderSettings
from .types import Completion, CompletionRequest, Provider, Usage
