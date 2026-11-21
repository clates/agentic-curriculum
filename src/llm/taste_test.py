"""Model taste-test: send one prompt to several models, store outputs, cost and latency.

    venv/bin/python scripts/taste_test.py --prompt-file p.txt --max-usd 0.50

Writes, under --out (default artifacts/taste-tests/<timestamp>/):
  results.json      machine-readable (schema_version 1; shared shape with the eval harness)
  <model>.json      one file per model: output, tokens, cost, latency, error
  comparison.html   the outputs side by side

Calls run one at a time and a hard --max-usd budget is enforced BEFORE each call. If a model
does not report its cost the run stops there (unless --allow-unknown-cost): the budget could not
be proven otherwise.
"""

from __future__ import annotations

import argparse
import html
import importlib
import json
import re
import sys
from dataclasses import asdict, dataclass, field
from datetime import UTC, datetime
from pathlib import Path

from .client import LLMClient, default_client
from .config import _load, DEFAULT_FILE
from .errors import CostCapExceeded, LLMError, StructuredOutputError
from .ledger import CostCaps, InMemoryLedger, UsageContext
from .structured import generate_structured

SCHEMA_VERSION = 1
BUDGET_FAMILY = "taste_test"


@dataclass
class ModelResult:
    model: str
    status: str  # ok | error | skipped
    output: str = ""
    prompt_tokens: int = 0
    completion_tokens: int = 0
    cost_usd: float | None = None
    latency_s: float | None = None
    error: str | None = None
    schema_valid: bool | None = None  # only with --schema
    repairs: int | None = None


@dataclass
class TasteTestRun:
    prompt: str
    max_usd: float
    results: list[ModelResult] = field(default_factory=list)
    created_at: str = field(default_factory=lambda: datetime.now(UTC).isoformat(timespec="seconds"))

    @property
    def total_cost_usd(self) -> float:
        return sum(r.cost_usd or 0.0 for r in self.results)

    def to_json(self) -> dict:
        return {
            "schema_version": SCHEMA_VERSION,
            "kind": "model_taste_test",
            "created_at": self.created_at,
            "prompt": self.prompt,
            "max_usd": self.max_usd,
            "total_cost_usd": self.total_cost_usd,
            "results": [asdict(r) for r in self.results],
        }


def slug(model: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", model.lower()).strip("-")


def run_taste_test(
    client: LLMClient,
    prompt: str,
    models: list[str],
    *,
    max_usd: float,
    task: str = "author",
    system: str | None = None,
    schema=None,
    allow_unknown_cost: bool = False,
) -> TasteTestRun:
    run = TasteTestRun(prompt=prompt, max_usd=max_usd)
    # The harness meters itself: a private ledger + cap, checked before every call.
    meter = InMemoryLedger()
    client.ledger = meter
    client._caps = CostCaps(family_month_usd=max_usd)
    ctx = UsageContext(family_id=BUDGET_FAMILY)
    messages = ([{"role": "system", "content": system}] if system else []) + [
        {"role": "user", "content": prompt}
    ]
    blocked: str | None = None
    for model in models:
        if blocked:
            run.results.append(ModelResult(model, "skipped", error=blocked))
            continue
        try:
            if schema is None:
                done = client.complete(task, messages, usage=ctx, model=model)
                result = ModelResult(
                    model,
                    "ok",
                    done.text,
                    done.usage.prompt_tokens,
                    done.usage.completion_tokens,
                    done.usage.cost_usd,
                    done.latency_s,
                )
            else:
                result = _structured(client, task, messages, schema, model, ctx)
        except CostCapExceeded as exc:
            blocked = f"budget reached before call: {exc}"
            run.results.append(ModelResult(model, "skipped", error=blocked))
            continue
        except LLMError as exc:
            run.results.append(ModelResult(model, "error", error=f"{type(exc).__name__}: {exc}"))
            continue
        run.results.append(result)
        if result.cost_usd is None and not allow_unknown_cost:
            blocked = f"{model} did not report a cost; stopping so --max-usd stays provable"
    return run


def _structured(client, task, messages, schema, model, ctx) -> ModelResult:
    # Pin this model for the first call and any repairs by overriding via env-free wrapper.
    pinned = _PinnedClient(client, model)
    try:
        out = generate_structured(task, messages, schema, client=pinned, usage=ctx)
    except StructuredOutputError as exc:
        return ModelResult(
            model,
            "ok",
            exc.raw,
            cost_usd=pinned.cost,
            latency_s=pinned.latency,
            prompt_tokens=pinned.prompt_tokens,
            completion_tokens=pinned.completion_tokens,
            error=f"StructuredOutputError: {exc}",
            schema_valid=False,
            repairs=exc.attempts - 1,
        )
    return ModelResult(
        model,
        "ok",
        out.parsed.model_dump_json(indent=2),
        pinned.prompt_tokens,
        pinned.completion_tokens,
        pinned.cost,
        pinned.latency,
        schema_valid=True,
        repairs=out.repairs,
    )


class _PinnedClient:
    """Routes every call (including repairs) to one model and totals usage."""

    def __init__(self, client: LLMClient, model: str) -> None:
        self._client, self._model = client, model
        self._env = client._env
        self.prompt_tokens = self.completion_tokens = 0
        self.cost: float | None = None
        self.latency = 0.0

    def config(self, task):
        from dataclasses import replace

        return replace(self._client.config(task), model=self._model)

    def complete(self, task, messages, **kw):
        done = self._client.complete(task, messages, model=self._model, **kw)
        self.prompt_tokens += done.usage.prompt_tokens
        self.completion_tokens += done.usage.completion_tokens
        self.latency += done.latency_s
        if done.usage.cost_usd is not None:
            self.cost = (self.cost or 0.0) + done.usage.cost_usd
        return done


def render_html(run: TasteTestRun) -> str:
    cols = []
    for r in run.results:
        meta = [
            f"status: {r.status}",
            f"tokens: {r.prompt_tokens} in / {r.completion_tokens} out",
            f"cost: {'unknown' if r.cost_usd is None else f'${r.cost_usd:.5f}'}",
            f"latency: {'-' if r.latency_s is None else f'{r.latency_s:.2f}s'}",
        ]
        if r.schema_valid is not None:
            meta.append(f"schema valid: {r.schema_valid} (repairs: {r.repairs})")
        err = f'<p class="err">{html.escape(r.error)}</p>' if r.error else ""
        cols.append(
            f"<section><h2>{html.escape(r.model)}</h2><ul>"
            + "".join(f"<li>{html.escape(m)}</li>" for m in meta)
            + f"</ul>{err}<pre>{html.escape(r.output)}</pre></section>"
        )
    return (
        "<!doctype html><meta charset='utf-8'><title>Model taste test</title><style>"
        "body{font:14px system-ui;margin:1rem;background:#fff;color:#111}"
        ".grid{display:grid;grid-auto-flow:column;grid-auto-columns:minmax(22rem,1fr);gap:1rem;"
        "overflow-x:auto}section{border:1px solid #ccc;border-radius:6px;padding:.75rem}"
        "pre{white-space:pre-wrap;word-break:break-word}.err{color:#b00020}"
        "@media(prefers-color-scheme:dark){body{background:#111;color:#eee}"
        "section{border-color:#444}}</style>"
        f"<h1>Model taste test</h1><p>{html.escape(run.created_at)} - total "
        f"${run.total_cost_usd:.5f} of ${run.max_usd:.2f} budget</p>"
        f"<details open><summary>Prompt</summary><pre>{html.escape(run.prompt)}</pre></details>"
        f"<div class='grid'>{''.join(cols)}</div>"
    )


def write_outputs(run: TasteTestRun, out_dir: Path) -> Path:
    out_dir.mkdir(parents=True, exist_ok=True)
    for r in run.results:
        (out_dir / f"{slug(r.model)}.json").write_text(json.dumps(asdict(r), indent=2))
    (out_dir / "results.json").write_text(json.dumps(run.to_json(), indent=2))
    page = out_dir / "comparison.html"
    page.write_text(render_html(run), encoding="utf-8")
    return page


def _load_schema(spec: str):
    module, _, name = spec.partition(":")
    return getattr(importlib.import_module(module), name)


def main(argv: list[str] | None = None, client: LLMClient | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawTextHelpFormatter)
    src = ap.add_mutually_exclusive_group(required=True)
    src.add_argument("--prompt")
    src.add_argument("--prompt-file", type=Path)
    ap.add_argument("--system", help="optional system prompt")
    ap.add_argument("--model", action="append", help="repeatable; default: taste_test_models")
    ap.add_argument("--task", default="author", help="task whose limits apply (default author)")
    ap.add_argument("--schema", help="module:PydanticClass to validate/repair against")
    ap.add_argument("--max-usd", type=float, default=0.50, help="hard budget (default 0.50)")
    ap.add_argument("--allow-unknown-cost", action="store_true")
    ap.add_argument("--out", type=Path)
    args = ap.parse_args(argv)

    prompt = args.prompt if args.prompt is not None else args.prompt_file.read_text()
    models = args.model or _load(DEFAULT_FILE)["taste_test_models"]
    out = args.out or Path("artifacts/taste-tests") / datetime.now(UTC).strftime("%Y%m%d-%H%M%S")
    run = run_taste_test(
        client or default_client(),
        prompt,
        models,
        max_usd=args.max_usd,
        task=args.task,
        system=args.system,
        schema=_load_schema(args.schema) if args.schema else None,
        allow_unknown_cost=args.allow_unknown_cost,
    )
    page = write_outputs(run, out)
    print(f"{'model':45} {'status':8} {'in':>6} {'out':>6} {'cost USD':>10} {'latency':>8}")
    for r in run.results:
        cost = "unknown" if r.cost_usd is None else f"{r.cost_usd:.5f}"
        lat = "-" if r.latency_s is None else f"{r.latency_s:.2f}s"
        print(
            f"{r.model:45} {r.status:8} {r.prompt_tokens:>6} {r.completion_tokens:>6} "
            f"{cost:>10} {lat:>8}" + (f"  [{r.error}]" if r.error else "")
        )
    print(f"total ${run.total_cost_usd:.5f} of ${args.max_usd:.2f} budget")
    print(f"comparison: {page}")
    return 0 if all(r.status == "ok" for r in run.results) else 1


if __name__ == "__main__":
    sys.exit(main())
