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
    temperature: float | None = 0.7  # None = send no temperature (provider default)
    max_tokens: int | None = None
    timeout_s: float | None = None
    top_p: float | None = None
    top_k: int | None = None


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


def model_profile(model: str, data: dict) -> dict | None:
    """The per-model sampling/limits entry (``model_profiles`` in models.json), or None."""
    return (data.get("model_profiles") or {}).get(model)


def task_config(
    task: str, env=None, path: Path | None = None, model: str | None = None
) -> TaskConfig:
    """Resolve one task's settings. Unknown task names are an error, never a silent default.

    Sampling (temperature, top_p, top_k) and the output-token limit belong to the MODEL: when the
    resolved model has an entry in ``model_profiles`` it wins over the task's values, including an
    explicit ``null`` temperature (send none). ``max_tokens: "model_max"`` on a task means the
    profile's ``max_output_tokens`` capped by the task's ``max_tokens_ceiling``. Env fields
    (LLM_<FIELD>_<TASK>) still override everything. ``model`` forces a model (no fallback).
    """
    env = os.environ if env is None else env
    path = path or Path(env.get("LLM_MODELS_FILE") or DEFAULT_FILE)
    data = _load(path)
    tasks = data.get("tasks", {})
    if task not in tasks:
        raise LLMConfigError(f"unknown LLM task {task!r}; known: {sorted(tasks)}")
    merged = {**data.get("defaults", {}), **tasks[task]}

    key = task.upper()
    forced_model = model is not None
    model = model or (
        env.get(f"LLM_MODEL_{key}")
        or env.get("LLM_MODEL")
        or env.get("OPENAI_MODEL")
        or merged.get("model")
    )
    if not model:
        raise LLMConfigError(f"no model configured for task {task!r}")

    profile = model_profile(model, data) or {}

    def field(name: str, cast):
        raw = env.get(f"LLM_{name.upper()}_{key}")
        if raw:
            return _num(raw, cast, f"LLM_{name.upper()}_{key}")
        if name in profile:  # explicit null in a profile = send nothing
            return profile[name]
        return merged.get(name)

    max_tokens = field("max_tokens", int)
    if max_tokens == "model_max":
        limit = profile.get("max_output_tokens") or merged.get("max_tokens_fallback") or 32000
        ceiling = env.get(f"LLM_MAX_TOKENS_CEILING_{key}")
        ceiling = int(ceiling) if ceiling else merged.get("max_tokens_ceiling")
        max_tokens = min(limit, ceiling) if ceiling else limit

    # An explicitly empty LLM_FALLBACK_MODEL_<TASK> disables the fallback.
    fallback = env.get(f"LLM_FALLBACK_MODEL_{key}")
    if fallback is None:
        fallback = merged.get("fallback_model")
    if forced_model:
        fallback = None
    return TaskConfig(
        task=task,
        model=model,
        fallback_model=fallback if fallback and fallback != model else None,
        temperature=field("temperature", float),
        max_tokens=max_tokens,
        timeout_s=field("timeout_s", float),
        top_p=field("top_p", float),
        top_k=field("top_k", int),
    )


def known_tasks(path: Path | None = None) -> list[str]:
    return sorted(_load(path or DEFAULT_FILE).get("tasks", {}))


def structured_mode(model: str, env=None, path: Path | None = None) -> str:
    """'json_schema' where the model is known to support schema mode, else 'json_object'.

    LLM_STRUCTURED_MODE=json_schema|json_object forces one mode for every model.
    """
    env = os.environ if env is None else env
    forced = env.get("LLM_STRUCTURED_MODE")
    if forced in ("json_schema", "json_object"):
        return forced
    prefixes = _load(path or Path(env.get("LLM_MODELS_FILE") or DEFAULT_FILE)).get(
        "json_schema_models", []
    )
    return "json_schema" if any(model.startswith(p) for p in prefixes) else "json_object"


def max_repairs(env=None, path: Path | None = None) -> int:
    env = os.environ if env is None else env
    raw = env.get("LLM_MAX_REPAIRS")
    if raw:
        return _num(raw, int, "LLM_MAX_REPAIRS")
    return int(
        _load(path or Path(env.get("LLM_MODELS_FILE") or DEFAULT_FILE)).get("max_repairs", 2)
    )
