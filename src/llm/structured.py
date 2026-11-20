"""generate_structured: model output -> a validated Pydantic object, or a typed error.

Order of defence: (1) ask for the schema (json_schema mode where supported, json_object
otherwise); (2) deterministic cleanup of fences/prose around the JSON; (3) a bounded number of
repair calls (task "repair") that show the model its invalid output and the validation errors.
Nothing is ever swallowed: exhausting the repairs raises StructuredOutputError.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Any, Generic, TypeVar

from pydantic import BaseModel, ValidationError

from .client import LLMClient, default_client
from .config import max_repairs as configured_max_repairs
from .config import structured_mode
from .errors import StructuredOutputError
from .types import Completion

T = TypeVar("T", bound=BaseModel)


@dataclass
class StructuredResult(Generic[T]):
    parsed: T
    completions: list[Completion] = field(default_factory=list)  # first call, then repairs

    @property
    def repairs(self) -> int:
        return len(self.completions) - 1

    @property
    def cost_usd(self) -> float | None:
        costs = [c.usage.cost_usd for c in self.completions if c.usage.cost_usd is not None]
        return sum(costs) if costs else None


def extract_json(text: str) -> Any:
    """Parse JSON, tolerating a ```json fence or prose around the outermost object/array."""
    text = (text or "").strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError as first:
        error = first
    if text.startswith("```"):
        inner = text.split("\n", 1)[1] if "\n" in text else ""
        inner = inner.rsplit("```", 1)[0]
        try:
            return json.loads(inner.strip())
        except json.JSONDecodeError:
            text = inner
    for open_ch, close_ch in (("{", "}"), ("[", "]")):
        start, end = text.find(open_ch), text.rfind(close_ch)
        if 0 <= start < end:
            try:
                return json.loads(text[start : end + 1])
            except json.JSONDecodeError:
                continue
    raise error


def _try_parse(text: str, model_cls: type[T]) -> tuple[T | None, str | None]:
    try:
        return model_cls.model_validate(extract_json(text)), None
    except json.JSONDecodeError as exc:
        return None, f"invalid JSON: {exc}"
    except ValidationError as exc:
        details = "; ".join(
            f"{'.'.join(str(p) for p in e['loc']) or '<root>'}: {e['msg']}" for e in exc.errors()
        )
        return None, f"schema validation failed: {details}"


def _response_format(model_cls: type[BaseModel], mode: str) -> dict[str, Any]:
    if mode == "json_schema":
        return {
            "type": "json_schema",
            "json_schema": {
                "name": model_cls.__name__,
                "strict": False,
                "schema": model_cls.model_json_schema(),
            },
        }
    return {"type": "json_object"}


def generate_structured(
    task: str,
    messages: list[dict[str, Any]],
    model_cls: type[T],
    *,
    client: LLMClient | None = None,
    max_repairs: int | None = None,
) -> StructuredResult[T]:
    client = client or default_client()
    budget = configured_max_repairs(client._env) if max_repairs is None else max_repairs
    cfg = client.config(task)
    mode = structured_mode(cfg.model, client._env)
    schema_hint = json.dumps(model_cls.model_json_schema())
    msgs = list(messages)
    if mode == "json_object":
        # json_object mode does not carry the schema, so put it in the prompt.
        msgs.append(
            {
                "role": "user",
                "content": f"Respond with a single JSON object matching this JSON Schema:\n{schema_hint}",
            }
        )

    completions = [client.complete(task, msgs, response_format=_response_format(model_cls, mode))]
    parsed, error = _try_parse(completions[0].text, model_cls)
    errors: list[str] = []
    while parsed is None:
        errors.append(error or "unknown")
        if len(errors) > budget:
            truncated = completions[-1].finish_reason == "length"
            raise StructuredOutputError(
                f"{task}: model output is not valid {model_cls.__name__} after "
                f"{len(completions)} call(s){' (output was truncated)' if truncated else ''}: "
                f"{errors[-1]}",
                raw=completions[-1].text,
                errors=errors,
                model=completions[-1].model,
                attempts=len(completions),
            )
        repair_messages = [
            {
                "role": "system",
                "content": "You repair invalid JSON. Reply with only the corrected JSON object.",
            },
            {
                "role": "user",
                "content": (
                    f"JSON Schema:\n{schema_hint}\n\nProblem: {error}\n\n"
                    f"Invalid output:\n{completions[-1].text}"
                ),
            },
        ]
        completions.append(
            client.complete("repair", repair_messages, response_format={"type": "json_object"})
        )
        parsed, error = _try_parse(completions[-1].text, model_cls)
    return StructuredResult(parsed=parsed, completions=completions)
