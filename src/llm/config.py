"""Per-task model configuration: a checked-in JSON file plus environment overrides.

Override precedence for a task's model (first set wins):
  LLM_MODEL_<TASK>  >  LLM_MODEL  >  OPENAI_MODEL (legacy)  >  models.json task  >  defaults
Other fields: LLM_<FIELD>_<TASK> (FIELD in MAX_TOKENS, TIMEOUT_S, TEMPERATURE, FALLBACK_MODEL).
LLM_MODELS_FILE points at an alternative JSON file (same shape).
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path

from .errors import LLMConfigError

DEFAULT_FILE = Path(__file__).with_name("models.json")


@dataclass(frozen=True)
class TaskConfig:
    task: str
    model: str
    fallback_model: str | None = None
    temperature: float | None = 0.7
    max_tokens: int | None = None
    timeout_s: float | None = None


def _load(path: Path) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise LLMConfigError(f"cannot read model config {path}: {exc}") from exc


def _num(value: str, cast, name: str):
    try:
        return cast(value)
    except ValueError as exc:
        raise LLMConfigError(f"{name} must be a number, got {value!r}") from exc


def task_config(task: str, env=None, path: Path | None = None) -> TaskConfig:
    """Resolve one task's settings. Unknown task names are an error, never a silent default."""
    env = os.environ if env is None else env
    path = path or Path(env.get("LLM_MODELS_FILE") or DEFAULT_FILE)
    data = _load(path)
    tasks = data.get("tasks", {})
    if task not in tasks:
        raise LLMConfigError(f"unknown LLM task {task!r}; known: {sorted(tasks)}")
    merged = {**data.get("defaults", {}), **tasks[task]}

    key = task.upper()
    model = (
        env.get(f"LLM_MODEL_{key}")
        or env.get("LLM_MODEL")
        or env.get("OPENAI_MODEL")
        or merged.get("model")
    )
    if not model:
        raise LLMConfigError(f"no model configured for task {task!r}")

    def field(name: str, cast):
        raw = env.get(f"LLM_{name.upper()}_{key}")
        return _num(raw, cast, f"LLM_{name.upper()}_{key}") if raw else merged.get(name)

    fallback = env.get(f"LLM_FALLBACK_MODEL_{key}") or merged.get("fallback_model")
    return TaskConfig(
        task=task,
        model=model,
        fallback_model=fallback if fallback and fallback != model else None,
        temperature=field("temperature", float),
        max_tokens=field("max_tokens", int),
        timeout_s=field("timeout_s", float),
    )


def known_tasks(path: Path | None = None) -> list[str]:
    return sorted(_load(path or DEFAULT_FILE).get("tasks", {}))
