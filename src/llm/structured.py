"""generate_structured: model output -> a validated Pydantic object, or a typed error.

Order of defence: (1) ask for the schema (json_schema mode where supported, json_object
otherwise); (2) deterministic cleanup of fences/prose around the JSON; (3) a bounded number of
repair calls (task "repair") that show the model its invalid output and the validation errors.
Nothing is ever swallowed: exhausting the repairs raises StructuredOutputError.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Any, Callable, Generic, TypeVar

from pydantic import BaseModel, ValidationError

from .client import LLMClient, default_client
from .config import max_repairs as configured_max_repairs
from .config import structured_mode
from .errors import StructuredOutputError
from .ledger import UsageContext
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


def _try_parse(
    text: str, model_cls: type[T], check: Callable[[T], str | None] | None = None
) -> tuple[T | None, str | None]:
    """Parse + validate; ``check`` is an optional completeness gate returning an error string."""
    try:
        parsed = model_cls.model_validate(extract_json(text))
        problem = check(parsed) if check else None
        if problem:
            return None, f"incomplete: {problem}"
        return parsed, None
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
    usage: UsageContext | None = None,
    check: Callable[[T], str | None] | None = None,
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

    completions = [
        client.complete(task, msgs, response_format=_response_format(model_cls, mode), usage=usage)
    ]
    parsed, error = _try_parse(completions[0].text, model_cls, check)
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
        # The repair call keeps the ORIGINAL brief (so the model knows what it was asked for),
        # shows its own previous output, and says what is wrong. It gets the author's token
        # budget (a full week does not fit the small repair default), the author's output mode,
        # and is billed to the same usage context as the first call.
        cut_off = completions[-1].finish_reason == "length"
        note = (
            " Your previous output was cut off by the length limit: write the complete object "
            "again, more compactly if you must, and make sure it closes."
            if cut_off
            else ""
        )
        repair_messages = [
            *msgs,
            {"role": "assistant", "content": completions[-1].text},
            {
                "role": "user",
                "content": (
                    f"That output was rejected. Problem: {error}.{note}\n"
                    "Reply with the complete corrected JSON object only, keeping everything "
                    "that was already correct."
                ),
            },
        ]
        completions.append(
            client.complete(
                "repair",
                repair_messages,
                response_format=_response_format(model_cls, mode),
                usage=usage,
                max_tokens=max(cfg.max_tokens or 0, client.config("repair").max_tokens or 0)
                or None,
            )
        )
        parsed, error = _try_parse(completions[-1].text, model_cls, check)
    return StructuredResult(parsed=parsed, completions=completions)
