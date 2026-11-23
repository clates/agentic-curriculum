#!/usr/bin/env python3
"""Refresh max_output_tokens in src/llm/models.json from OpenRouter's public model list.

    venv/bin/python scripts/refresh_model_limits.py [--write]

Prints the difference per profiled model; --write updates the file. No API key needed.
"""

from __future__ import annotations

import json
import sys
import urllib.request
from pathlib import Path

MODELS_JSON = Path(__file__).resolve().parents[1] / "src" / "llm" / "models.json"


def max_completion_tokens(listing: dict, model_id: str) -> int | None:
    for m in listing.get("data", []):
        if m.get("id") == model_id:
            return (m.get("top_provider") or {}).get("max_completion_tokens")
    return None


def main(argv: list[str]) -> int:
    with urllib.request.urlopen("https://openrouter.ai/api/v1/models", timeout=60) as r:
        listing = json.load(r)
    data = json.loads(MODELS_JSON.read_text())
    for model, prof in data["model_profiles"].items():
        if model.startswith("_"):
            continue
        new = max_completion_tokens(listing, model)
        flag = "" if new in (None, prof.get("max_output_tokens")) else "  <- changed"
        print(f"{model}: {prof.get('max_output_tokens')} -> {new}{flag}")
        if new and "--write" in argv:
            prof["max_output_tokens"] = int(new)
    if "--write" in argv:
        MODELS_JSON.write_text(json.dumps(data, indent=2) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
