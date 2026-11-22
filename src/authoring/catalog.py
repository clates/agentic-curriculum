"""Kind menu and per-kind schema blocks, generated from the hosted-kind registry (M3.1, M3.1b).

The menu (one line per kind) is the stable prompt prefix of the planning step; the blocks
(purpose, answer item_ref shapes, compact JSON schema) are loaded only for the kinds a plan
picks. Both come from ``weekdoc.HOSTED_KINDS`` so they cannot drift from the typed models; the
human-written purposes live in ``prompts/kind_purposes.json`` and a test fails if a registered
kind has no purpose (and therefore no menu line).
"""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any

from pydantic import TypeAdapter
from weekdoc import HOSTED_KINDS

PROMPTS_DIR = Path(__file__).with_name("prompts")


class CatalogError(RuntimeError):
    """The prompt assets and the hosted-kind registry disagree."""


@lru_cache(maxsize=1)
def _purposes() -> dict[str, str]:
    return json.loads((PROMPTS_DIR / "kind_purposes.json").read_text(encoding="utf-8"))


@lru_cache(maxsize=1)
def _ref_patterns() -> dict[str, list[str]]:
    return json.loads((PROMPTS_DIR / "kind_ref_patterns.json").read_text(encoding="utf-8"))


def hosted_kinds() -> list[str]:
    return list(HOSTED_KINDS)


def purpose(kind: str) -> str:
    try:
        return _purposes()[kind]
    except KeyError:
        raise CatalogError(
            f"hosted kind {kind!r} has no entry in prompts/kind_purposes.json"
        ) from None


def kind_menu(kinds: list[str] | None = None) -> str:
    """One line per kind: ``- kind [answerable|no answers]: purpose``."""
    lines = []
    for kind in kinds or hosted_kinds():
        asks = "answerable" if HOSTED_KINDS[kind].enumerate is not None else "no answers"
        lines.append(f"- {kind} [{asks}]: {purpose(kind)}")
    return "\n".join(lines)


def kind_schema(kind: str) -> dict[str, Any]:
    """Compact JSON Schema of a kind's data (titles and additionalProperties dropped)."""
    model = HOSTED_KINDS[kind].model
    if kind == "shapeIdWorksheet":  # its data model is a discriminated union of modes
        from weekdoc.kinds_visual import ShapeIdData

        schema = TypeAdapter(ShapeIdData).json_schema()
    else:
        schema = model.model_json_schema()

    def walk(x: Any) -> Any:
        if isinstance(x, dict):
            return {
                k: walk(v)
                for k, v in x.items()
                if k != "additionalProperties" and not (k == "title" and isinstance(v, str))
            }
        if isinstance(x, list):
            return [walk(v) for v in x]
        return x

    return walk(schema)


def kind_block(kind: str) -> str:
    patterns = _ref_patterns().get(kind, [])
    if patterns:
        ref_line = f"Answer item_refs look like: {', '.join(patterns)} (N = zero-based index)"
    elif HOSTED_KINDS[kind].enumerate is None:
        ref_line = "Answer item_refs: none (this kind carries no answers)"
    else:
        ref_line = "Answer item_refs: dotted path into the data lists, zero-based index"
    schema = json.dumps(kind_schema(kind), separators=(",", ":"))
    return f"### {kind}\nPurpose: {purpose(kind)}\n{ref_line}\nData schema:\n{schema}"


def kind_blocks(kinds: list[str]) -> str:
    return "\n\n".join(kind_block(k) for k in kinds)
