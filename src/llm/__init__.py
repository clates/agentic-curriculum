# ruff: noqa: F401, F403
"""Model layer: one provider interface, OpenRouter implementation, typed errors."""

from .errors import *  # noqa: F401,F403
from .openrouter import OpenRouterProvider, parse_usage
from .settings import ProviderSettings
from .types import Completion, CompletionRequest, Provider, Usage
from .client import LLMClient, default_client
from .config import TaskConfig, known_tasks, task_config
from .structured import StructuredResult, extract_json, generate_structured
