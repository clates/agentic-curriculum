#!/usr/bin/env python3
"""Quality-check harness: a multi-model comparison of one authored week, and a kind sampler.

Part A  one-shot week author (student context + topic + real standards + weather-week structure
        + kind menu/schemas + AGENTS.md rules) run on several OpenRouter models with the SAME
        input; validated with load_week through the repo's structured-output + repair loop;
        rendered to packet / teacher guide / prep sheet PDFs; objective checks; feedback sheets;
        comparison.pdf.
Part B  one packet PDF exercising every hosted kind; each worksheet's data is authored by a model
        from a per-kind prompt (that kind's schema + the theme only), with the deterministic test
        sample as a labelled fallback.

Sub-commands (each step is separate so rendering can be redone without spending anything):

    author-a   call the models, save weeks + run records     (spends money)
    render-a   PDFs, checks, feedback sheets, comparison.pdf (free)
    author-b   author every kind with one model              (spends money)
    render-b   build the sampler PDF                         (free)
    kinds      list the registry's kinds (and the kind menu) (free)

Budget: every provider call (including the repair calls, which generate_structured does not bill
to a UsageContext) goes through MeteredProvider, which appends to a JSONL usage ledger, refuses a
call whose worst-case cost would pass --max-usd, and stops if a price is unknown. Keys are read
from the environment (OPENROUTER_API_KEY) and never printed or stored.

PDF output needs `pip install playwright pypdf pymupdf` and a Chromium (QC_CHROMIUM_PATH, or the
one `playwright install chromium` put in the Playwright cache).
"""

from __future__ import annotations

import argparse
import copy
import glob
import html
import json
import os
import re
import sqlite3
import sys
import threading
import time
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
for _p in (str(ROOT), str(ROOT / "src")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from pydantic import BaseModel, model_validator  # noqa: E402

from llm import LLMClient, OpenRouterProvider, ProviderSettings  # noqa: E402
from llm.errors import LLMError, StructuredOutputError  # noqa: E402
from llm.ledger import CostCaps, UsageContext  # noqa: E402
from llm.structured import _try_parse, extract_json, generate_structured  # noqa: E402
from llm.types import Completion, CompletionRequest  # noqa: E402
from src import worksheet_html_renderer as _r  # noqa: E402
from src.weekdoc import HOSTED_KINDS, Answer, WeekDoc, Worksheet, item_refs, load_week  # noqa: E402
from src.weekdoc.render import (  # noqa: E402
    _render_worksheet,
    render_packet,
    render_prep_sheet,
    render_teacher_guide,
    substitute_name,
)
from src.weekdoc.versioning import migrate_week_data  # noqa: E402

STUDENT = {
    "first_name": "Ada",
    "grade": 2,
    "reading_level": "on grade level (grade 2)",
    "interests": ["space", "drawing"],
    "parent_note": "loves hands-on activities, gets tired of long writing",
}
TOPIC = (
    "Weather and seasons (Virginia Grade 2 Science 2.6 and 2.7: weather types, tracking weather, "
    "seasonal change)"
)
TOPIC_STANDARDS = [
    "VA.SCIENCE.2.2.6.a",
    "VA.SCIENCE.2.2.6.b",
    "VA.SCIENCE.2.2.6.c",
    "VA.SCIENCE.2.2.7.a",
    "VA.SCIENCE.2.2.7.b",
    "VA.SCIENCE.2.2.7.c",
]
WEATHER_FIXTURE = ROOT / "tests" / "fixtures" / "weekdoc" / "weather_week.json"

# Exact OpenRouter ids, confirmed against https://openrouter.ai/api/v1/models on 2026-11-21.
MODELS = {
    "cheap": "google/gemini-3.1-flash-lite",  # $0.25 / $1.50 per M tokens
    "mid": "anthropic/claude-haiku-4.5",  # $1.00 / $5.00
    "top": "anthropic/claude-sonnet-5.5",  # $2.00 / $10.00 (newest sonnet)
    "bonus": "anthropic/claude-haiku-5.5",  # $0.10 / $0.50 (newest haiku; price-inverted)
}
MAX_REPAIRS = 3
DAY_CYCLE = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]

# One line per kind. main() refuses to run if the registry has a kind missing here.
PURPOSE: dict[str, str] = {
    "storyPanel": "Narrator beat: a short in-character story paragraph; asks nothing.",
    "readingWorksheet": "Passage with vocabulary and numbered comprehension questions; the core reading page.",
    "causeEffectWorksheet": "Cause/effect pairs where the child completes the missing half.",
    "oddOneOutWorksheet": "Rows of items; circle the one that does not belong and say why.",
    "frayerModelWorksheet": "Four-box vocabulary organizer around one term.",
    "doingCard": "Dashed hands-on or outdoor activity card; explicitly not desk work.",
    "noteBox": "Short callout for an instruction or aside.",
    "heartBar": "Themed half-heart meter (status or progress flourish).",
    "colorKey": "Legend mapping labels (fractions) to colours for a colouring page.",
    "logoBadge": "Small decorative badge image with caption; needs an inline raster image.",
    "calibrationRuler": "Printed ruler so a parent can verify 100% print scale.",
    "richText": "Headed prose with bullets and key/value rows; a reference or information page.",
    "taskList": "Numbered open tasks with response lines; a task may embed a figure block.",
    "wordSortWorksheet": "Sort word tiles into 2-4 labelled categories.",
    "treeMapWorksheet": "Classify items under branches of one root idea, with a word bank.",
    "tChartWorksheet": "Two-column comparison chart with blank rows to fill.",
    "featureMatrixWorksheet": "Grid of items by properties; tick which properties apply.",
    "matchingWorksheet": "Match items in a left column to items in a right column.",
    "cutCards": "Cut-apart card kit used by a later task.",
    "colorTask": "Colour-by-key: a fraction figure plus a colour key.",
    "pixelCopyWorksheet": "Copy a small coloured pixel picture onto a blank grid.",
    "fractionStrips": "Printable fraction strips to cut and compare.",
    "fractionCircles": "Circles divided into equal parts (fraction models).",
    "fractionArea": "Grid/area fraction models, including unequal parts.",
    "fractionNumberLine": "0-to-1 number lines partitioned into fractional steps.",
    "twoOperandWorksheet": "Two-number arithmetic problems to solve (add/subtract).",
    "tenFrameWorksheet": "Ten-frame addition problems with coloured counters.",
    "numberLineWorksheet": "Number-line tasks: fill hidden numbers or show jumps.",
    "speedMath": "Dense timed warm-up grid of arithmetic facts.",
    "barGraphWorksheet": "Bar graph from categories and values, with questions about it.",
    "pictographWorksheet": "Pictograph with a symbol worth N units, with questions.",
    "comparePairs": "Grid of 'left [ ] right' pairs to compare with <, > or =.",
    "mathWorksheet": "Same fields and bounds as twoOperandWorksheet (arithmetic problems).",
    "writingScaffoldWorksheet": "Writing frame with sentence starters per section.",
    "handwritingWorksheet": "Copy-and-trace handwriting practice for given words.",
    "alphabetWorksheet": "Letter tracing plus words that start with or contain a letter.",
    "mirrorMessageWorksheet": "Secret message to trace and read with a mirror.",
    "letterWorksheet": "A letter to read and/or a reply frame, with optional envelope.",
    "sequencingWorksheet": "Put written steps in the correct order.",
    "fillInBlankWorksheet": "Sentences with blanks and a word bank.",
    "labeledDiagramWorksheet": "Numbered framed diagram box to label; child draws or glues the picture.",
    "vennDiagramWorksheet": "Two-circle Venn diagram to compare and contrast.",
    "storyMapWorksheet": "Story-map graphic organizer with fields to fill.",
    "shapeIdWorksheet": "Shape identification in five modes: gallery, attributes, pattern, sort, mirror_match.",
    "pictureSequenceWorksheet": "Emoji picture cards (given shuffled) to put in order.",
    "errorAuditWorksheet": "Find-the-mistake audit of drawn specimens (clocks, dots, partitions).",
}


# ── Samples (the deterministic fallback), mirrored from tests/test_weekdoc_golden.py ───────────


def sample_data() -> dict[str, dict]:
    from tests.test_weekdoc_kinds_blocks import CASES as BLOCKS
    from tests.test_weekdoc_kinds_classification import CASES as CLASSIFICATION
    from tests.test_weekdoc_kinds_comprehension import CASES as COMPREHENSION
    from tests.test_weekdoc_kinds_crafts import CASES as CRAFTS
    from tests.test_weekdoc_kinds_fractions import CASES as FRACTIONS
    from tests.test_weekdoc_kinds_graphs import CASES as GRAPHS
    from tests.test_weekdoc_kinds_handwriting import CASES as HANDWRITING
    from tests.test_weekdoc_kinds_math import CASES as MATH
    from tests.test_weekdoc_kinds_ordered import CASES as ORDERED
    from tests.test_weekdoc_kinds_visual import SAMPLES as VISUAL

    samples = {
        **COMPREHENSION,
        **CLASSIFICATION,
        **ORDERED,
        **MATH,
        **BLOCKS,
        **FRACTIONS,
        **HANDWRITING,
        **GRAPHS,
        **VISUAL,
        **CRAFTS,
    }
    samples["storyPanel"] = {"who": "Zara", "text": "A beat."}
    return copy.deepcopy(samples)


# ── Kind catalog / menu ────────────────────────────────────────────────────────────────────────


def kind_schema(kind: str) -> dict:
    """Compact JSON Schema of a kind's data (titles and additionalProperties dropped)."""
    if kind == "shapeIdWorksheet":
        from pydantic import TypeAdapter

        from src.weekdoc.kinds_visual import ShapeIdData

        schema = TypeAdapter(ShapeIdData).json_schema()
    else:
        schema = HOSTED_KINDS[kind].model.model_json_schema()

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


def answer_ref_patterns(kind: str, samples: dict[str, dict]) -> list[str]:
    """Shapes of the item_refs an answer may use, e.g. ['questions.N'] (from the registry)."""
    if HOSTED_KINDS[kind].enumerate is None or kind not in samples:
        return []
    try:
        refs = item_refs(kind, samples[kind])
    except Exception:
        return []
    return sorted({re.sub(r"\d+", "N", r.ref) for r in refs})


def kind_menu() -> str:
    """The short menu: one line per kind (stage 1 of the M3.1b kind-menu prototype)."""
    lines = []
    for kind in HOSTED_KINDS:
        asks = "answerable" if HOSTED_KINDS[kind].enumerate is not None else "no answers"
        lines.append(f"- {kind} [{asks}]: {PURPOSE[kind]}")
    return "\n".join(lines)


def kind_block(kind: str, samples: dict[str, dict]) -> str:
    refs = answer_ref_patterns(kind, samples)
    if refs:
        ref_line = f"Answer item_refs look like: {', '.join(refs)} (N = zero-based index)"
    elif HOSTED_KINDS[kind].enumerate is None:
        ref_line = "Answer item_refs: none (this kind carries no answers)"
    else:
        ref_line = "Answer item_refs: dotted path into the data lists, zero-based index"
    return f"### {kind}\nPurpose: {PURPOSE[kind]}\n{ref_line}\nData schema:\n" + json.dumps(
        kind_schema(kind), separators=(",", ":")
    )


def full_catalog(samples: dict[str, dict]) -> str:
    return "\n\n".join(kind_block(k, samples) for k in HOSTED_KINDS)


# ── Metering: usage ledger + hard budget ───────────────────────────────────────────────────────


class BudgetStop(Exception):
    """Raised before a call that could take total spend past the cap (or whose price is unknown)."""


def fetch_prices(path: Path) -> dict[str, tuple[float, float]]:
    """{model_id: (usd_per_prompt_token, usd_per_completion_token)} from OpenRouter's list."""
    if not path.exists():
        path.parent.mkdir(parents=True, exist_ok=True)
        with urllib.request.urlopen("https://openrouter.ai/api/v1/models", timeout=60) as r:
            path.write_bytes(r.read())
    data = json.loads(path.read_text())["data"]
    return {
        m["id"]: (float(m["pricing"]["prompt"]), float(m["pricing"]["completion"]))
        for m in data
        if m.get("pricing")
    }


@dataclass
class CallRecord:
    label: str
    model: str
    prompt_tokens: int
    completion_tokens: int
    cost_usd: float
    cost_estimated: bool
    latency_s: float
    finish_reason: str | None
    text: str = field(repr=False, default="")


class MeteredProvider:
    """Wraps a Provider: pre-call cap, per-call JSONL ledger row (never prompt/response text)."""

    def __init__(self, inner: Any, ledger_path: Path, cap_usd: float, prices: dict) -> None:
        self.inner = inner
        self.ledger_path = ledger_path
        self.cap = cap_usd
        self.prices = prices
        self.calls: list[CallRecord] = []
        self._lock = threading.Lock()
        self._local = threading.local()
        ledger_path.parent.mkdir(parents=True, exist_ok=True)

    def set_label(self, label: str) -> None:
        self._local.label = label

    def spent(self) -> float:
        if not self.ledger_path.exists():
            return 0.0
        return sum(
            json.loads(line)["cost_usd"]
            for line in self.ledger_path.read_text().splitlines()
            if line.strip()
        )

    def complete(self, request: CompletionRequest) -> Completion:
        pin, pout = self.prices.get(request.model, (None, None))
        if pin is None:
            raise BudgetStop(f"no price known for {request.model}; cannot bound its cost")
        est_in = len(json.dumps(request.messages)) / 3.0  # conservative chars -> tokens
        worst = est_in * pin + (request.max_tokens or 4096) * pout
        with self._lock:
            spent = self.spent()
            if spent + worst > self.cap:
                raise BudgetStop(
                    f"budget guard: spent ${spent:.4f} + worst case ${worst:.4f} would pass "
                    f"${self.cap:.2f}"
                )
        done = self.inner.complete(request)
        cost = done.usage.cost_usd
        estimated = cost is None
        if estimated:
            cost = done.usage.prompt_tokens * pin + done.usage.completion_tokens * pout
        rec = CallRecord(
            label=getattr(self._local, "label", ""),
            model=done.model or request.model,
            prompt_tokens=done.usage.prompt_tokens,
            completion_tokens=done.usage.completion_tokens,
            cost_usd=float(cost),
            cost_estimated=estimated,
            latency_s=done.latency_s,
            finish_reason=done.finish_reason,
            text=done.text,
        )
        with self._lock:
            self.calls.append(rec)
            row = {k: v for k, v in rec.__dict__.items() if k != "text"}
            row["ts"] = time.strftime("%Y-%m-%dT%H:%M:%S")
            with self.ledger_path.open("a") as fh:
                fh.write(json.dumps(row) + "\n")
        return done


class _LedgerView:
    """Feeds LLMClient's own check_cap the metered total. Recording is done by MeteredProvider
    (so repair calls, which generate_structured does not bill to a UsageContext, count too)."""

    def __init__(self, provider: MeteredProvider) -> None:
        self._p = provider

    def spent_usd(self, family_id: str, since_iso: str) -> float:
        return self._p.spent()

    def record(self, *args: Any, **kwargs: Any) -> None:
        return None


def make_client(
    model: str, provider: MeteredProvider, *, max_tokens: int = 24000, structured: str | None = None
) -> LLMClient:
    """A client whose author AND repair tasks both use ``model`` (no silent fallback model)."""
    env = {
        "LLM_PRIVACY_ROUTING": "no-training",
        "LLM_MODEL_AUTHOR": model,
        "LLM_MODEL_REPAIR": model,
        "LLM_FALLBACK_MODEL_AUTHOR": "",
        "LLM_FALLBACK_MODEL_REPAIR": "",
        "LLM_MAX_TOKENS_AUTHOR": str(max_tokens),
        "LLM_MAX_TOKENS_REPAIR": str(max_tokens),
        "LLM_TIMEOUT_S_AUTHOR": "420",
        "LLM_TIMEOUT_S_REPAIR": "420",
        "LLM_TEMPERATURE_AUTHOR": "0.5",
        "LLM_MAX_ATTEMPTS": "2",
    }
    if structured:
        env["LLM_STRUCTURED_MODE"] = structured
    return LLMClient(provider, env=env, ledger=_LedgerView(provider), caps=CostCaps(provider.cap))


def real_provider(out: Path, cap_usd: float) -> MeteredProvider:
    env = dict(os.environ, LLM_PRIVACY_ROUTING="no-training")
    prices = fetch_prices(out / "work" / "models_list.json")
    return MeteredProvider(
        OpenRouterProvider(ProviderSettings.from_env(env)),
        out / "work" / "usage_ledger.jsonl",
        cap_usd,
        prices,
    )


# ── Part A: prompts ────────────────────────────────────────────────────────────────────────────

RULES = """\
HARD RULES
1. Output ONE JSON object only (no prose, no code fences): a WeekDoc, schema_version 1.
2. The week is DATA, never code. No HTML, CSS, SVG, JavaScript, URLs, file paths, image paths or
   data: URIs anywhere. Colours are '#rrggbb' only. Emoji characters are fine. Only the hosted
   kinds provided may be used, with exactly their fields (extra fields are rejected).
3. Answer keys. Every worksheet that has gradable items carries `answers`: a list of
   {"item_ref", "answer"} using only the item_ref shapes given for that kind. The answer must be
   correct and match the worksheet content exactly. An item_ref addresses a slot the child must
   fill in; content already printed on the page (a pre-filled cause, a given example) has no
   item_ref and must not be answered. The teacher_guide repeats each day's answers
   with a short explanation in an `answer` callout, and adds a `misconception`, an `extension`
   and a `discuss` callout per day.
4. Shuffle word banks, sort tiles and fill-in answer lists so the displayed order never matches
   the answer-key order or the passage order.
5. Every readingWorksheet: `instructions` frames a brief hands-on (indoors or outdoors)
   before/during/after activity tied to that day's idea; vocabulary of 3-4 terms; three or four
   questions; the LAST question is an oral "LET'S DISCUSS: ..." prompt with response_lines 0 (a
   tricky real-world case that applies the day's idea).
6. A recurring narrator character: introduce them on Monday with a "meet <character>" sentence
   before the science content; keep the hook on later days.
7. The child's first name may appear only as the literal token {{student_name}}; never write the
   name, and no other {{...}} placeholder exists.
8. Student-facing text must be readable at grade 2: short sentences, common words, one idea per
   sentence; define science words in context. Keep writing demands tiny (circle, match, sort,
   fill a word, draw, tick, one short line) because the child tires of long writing. Favour
   hands-on and drawing tasks. Each worksheet must fit on ONE letter page.
9. Prep checks: about 10 total (two per day), each with a standard_id taken from the STANDARDS list
   below, kind in quiz|oral|review|activity|observation, a prompt the parent can say aloud or do
   in two minutes, and a plain-words pass_criteria. Ids chk-1, chk-2, ...
10. Every Day.standards entry and every prep check standard_id must come from the STANDARDS list.
11. Worksheet ids are unique lowercase slugs such as mon-1. Days are Monday..Friday.
12. No empty strings, no placeholder text (no "TBD", "lorem", "...").
13. Shape reminders. The top level has "schema_version": 1. A teacher_guide block is EITHER a
    heading block {"heading": "..."} with nothing else, OR a callout block {"style":
    "answer|misconception|extension|discuss", "paragraphs": ["..."]} with no heading; to title a
    callout, put a separate heading block before it. teacher_guide.meta is a list of
    ["Label", "Value"] pairs.
"""


def standards_from_db(db: Path, ids: list[str]) -> list[dict]:
    conn = sqlite3.connect(db)
    try:
        out = []
        for sid in ids:
            row = conn.execute(
                "SELECT standard_id, description FROM standards WHERE standard_id = ?", (sid,)
            ).fetchone()
            if row is None:
                raise SystemExit(f"standard {sid} not in the DB")
            out.append({"standard_id": row[0], "description": row[1]})
        return out
    finally:
        conn.close()


def reference_structure() -> str:
    ref = json.loads(WEATHER_FIXTURE.read_text())
    lines = []
    for d in ref["days"]:
        kinds = ", ".join(f"{w['id']}={w['kind']}" for w in d["worksheets"])
        lines.append(f"  {d['day']}: {d['title']}  [{kinds}]  standards={d['standards']}")
    ex_ws = copy.deepcopy(ref["days"][0]["worksheets"][0])
    ex_check = ref["prep_checks"][0]
    ex_guide = copy.deepcopy(ref["teacher_guide"]["days"][0])
    ex_guide["blocks"] = ex_guide["blocks"][:3]
    return (
        "REFERENCE WEEK (a good Kindergarten-Grade 1 weather week; copy its STRUCTURE and care, "
        "not its content or its K-1 level):\n"
        + "\n".join(lines)
        + "\nEach day: one readingWorksheet (the daily lesson) plus one or two activity pages; "
        "Friday is a capstone. A Parent Prep Sheet of about 10 quick checks; a teacher guide with "
        "answer keys.\n\nExample readingWorksheet (K-1 level, for shape and quality only):\n"
        + json.dumps(ex_ws, ensure_ascii=False)
        + "\n\nExample prep check:\n"
        + json.dumps(ex_check)
        + "\n\nExample teacher_guide day (first blocks):\n"
        + json.dumps(ex_guide, ensure_ascii=False)
        + '\nTeacher guide summary shape: {"heading":..., "intro":..., "items":[...], "closing":...}'
    )


def student_block(standards: list[dict]) -> str:
    return (
        "STUDENT (the only personal data you get):\n"
        + json.dumps(STUDENT)
        + f"\n\nTOPIC: {TOPIC}\n\nSTANDARDS (use ONLY these ids):\n"
        + "\n".join(f"- {s['standard_id']}: {s['description']}" for s in standards)
    )


SYSTEM = (
    "You are a curriculum author for a homeschool parent. You write one complete printable "
    "week as structured JSON data that a deterministic renderer prints. You never write code."
)


def build_prompts(standards: list[dict]) -> dict[str, str]:
    """Everything the models share; ``common`` is identical for every model and every mode."""
    common = "\n\n".join([student_block(standards), reference_structure(), RULES])
    return {"common": common, "menu": kind_menu()}


class PlanWorksheet(BaseModel):
    id: str
    kind: str
    focus: str

    @model_validator(mode="after")
    def _kind_exists(self) -> "PlanWorksheet":
        if self.kind not in HOSTED_KINDS:
            raise ValueError(f"kind {self.kind!r} is not in the menu")
        return self


class PlanDay(BaseModel):
    day: str
    title: str
    standards: list[str]
    worksheets: list[PlanWorksheet]


class WeekPlan(BaseModel):
    narrator: str
    arc: str
    days: list[PlanDay]

    @model_validator(mode="after")
    def _shape(self) -> "WeekPlan":
        if [d.day for d in self.days] != DAY_CYCLE:
            raise ValueError(
                "plan must cover Monday, Tuesday, Wednesday, Thursday, Friday in order"
            )
        if any(len(d.worksheets) < 2 for d in self.days):
            raise ValueError("each day needs at least 2 worksheets")
        return self

    def kinds(self) -> list[str]:
        return sorted({w.kind for d in self.days for w in d.worksheets})


class AuthoredWeek(WeekDoc):
    """WeekDoc validated the way load_week does it (schema_version required, migrated)."""

    @model_validator(mode="before")
    @classmethod
    def _like_load_week(cls, raw: Any) -> Any:
        return migrate_week_data(raw) if isinstance(raw, dict) else raw


# ── Part A: running one model ──────────────────────────────────────────────────────────────────


def run_stage(
    client: LLMClient,
    provider: MeteredProvider,
    label: str,
    messages: list[dict],
    model_cls: type[BaseModel],
    max_repairs: int,
) -> dict:
    """One generate_structured run; returns per-call stats and per-round validation errors."""
    provider.set_label(label)
    start = time.monotonic()
    parsed, error = None, None
    try:
        res = generate_structured(
            "author",
            messages,
            model_cls,
            client=client,
            max_repairs=max_repairs,
            usage=UsageContext(family_id="quality_check"),
        )
        parsed = res.parsed
    except StructuredOutputError as exc:
        error = str(exc)[:600]
    except BudgetStop as exc:
        error = f"BUDGET STOP: {exc}"
    except LLMError as exc:
        error = f"{type(exc).__name__}: {str(exc)[:400]}"
    wall = time.monotonic() - start
    calls = [c for c in provider.calls if c.label == label]
    rounds = []
    for i, c in enumerate(calls):
        _, err = _try_parse(c.text, model_cls)
        rounds.append(
            {
                "call": i,
                "role": "author" if i == 0 else f"repair {i}",
                "prompt_tokens": c.prompt_tokens,
                "completion_tokens": c.completion_tokens,
                "cost_usd": round(c.cost_usd, 6),
                "latency_s": round(c.latency_s, 2),
                "finish_reason": c.finish_reason,
                "valid": err is None,
                "error": err,
            }
        )
    return {
        "label": label,
        "valid": parsed is not None,
        "repair_rounds": max(0, len(calls) - 1),
        "calls": len(calls),
        "prompt_tokens": sum(c.prompt_tokens for c in calls),
        "completion_tokens": sum(c.completion_tokens for c in calls),
        "cost_usd": round(sum(c.cost_usd for c in calls), 6),
        "cost_estimated": any(c.cost_estimated for c in calls),
        "latency_s_calls": round(sum(c.latency_s for c in calls), 2),
        "wall_s": round(wall, 2),
        "rounds": rounds,
        "final_error": error,
        "raw_texts": [c.text for c in calls],
        "parsed": parsed.model_dump(mode="json", by_alias=True) if parsed is not None else None,
    }


def author_week(
    model_id: str, mode: str, provider: MeteredProvider, prompts: dict, samples: dict
) -> dict:
    """mode 'menu': stage 1 picks kinds from the short menu, stage 2 sees only their schemas.
    mode 'full': one stage with every kind's schema in the prompt."""
    # Finding: Anthropic's json_schema mode rejects the WeekDoc schema (minItems > 1 on arrays,
    # HTTP 400), though src/llm/models.json lists claude-haiku/sonnet as json_schema models. The
    # harness therefore uses json_object mode (schema in the prompt) for Anthropic models.
    client = make_client(
        model_id, provider, structured="json_object" if model_id.startswith("anthropic/") else None
    )
    common = prompts["common"]
    rec: dict[str, Any] = {"model": model_id, "mode": mode, "stages": {}}
    stages: list[dict] = []
    if mode == "menu":
        stage1 = (
            f"{common}\n\nKIND MENU (the only kinds that exist; one line each):\n{prompts['menu']}\n\n"
            'TASK STEP 1 of 2: plan the week. Return JSON {"narrator": str, "arc": str, '
            '"days": [{"day", "title", "standards": [ids], "worksheets": [{"id", '
            '"kind", "focus"}]}]} covering Monday..Friday, 2-3 worksheets per day, choosing kinds '
            "from the menu that suit a grade-2 hands-on science week. Use a varied but sensible "
            "set of kinds (not every kind). Do not write worksheet content yet."
        )
        s1 = run_stage(
            client,
            provider,
            f"{model_id}|{mode}|plan",
            [{"role": "system", "content": SYSTEM}, {"role": "user", "content": stage1}],
            WeekPlan,
            2,
        )
        stages.append(s1)
        rec["stages"]["plan"] = {k: v for k, v in s1.items() if k not in ("parsed", "raw_texts")}
        rec["plan_raw"] = s1["raw_texts"]
        if not s1["valid"]:
            rec.update(
                valid=False,
                week=None,
                final_error="stage 1 (kind menu plan) failed: " + str(s1["final_error"]),
            )
            return _finish(rec, stages)
        plan = WeekPlan.model_validate(s1["parsed"])
        rec["kinds_planned"] = plan.kinds()
        catalog = "\n\n".join(kind_block(k, samples) for k in plan.kinds())
        stage2 = (
            f"{common}\n\nYOUR PLAN FROM STEP 1 (follow it):\n{json.dumps(s1['parsed'])}\n\n"
            f"SCHEMAS for the kinds in your plan:\n{catalog}\n\n"
            "TASK STEP 2 of 2: write the complete WeekDoc JSON following your plan: title, "
            "packet_title (use {{student_name}} for the child), theme, subject, grade_band '2', "
            "narrator, arc, days (with worksheets and answers), prep_checks, teacher_guide."
        )
    else:
        stage2 = (
            f"{common}\n\nKIND CATALOG (every hosted kind with its schema):\n"
            f"{full_catalog(samples)}\n\nTASK: write the complete WeekDoc JSON: title, packet_title "
            "(use {{student_name}} for the child), theme, subject, grade_band '2', narrator, arc, "
            "days (with worksheets and answers), prep_checks, teacher_guide. Choose kinds from the "
            "catalog."
        )
    s2 = run_stage(
        client,
        provider,
        f"{model_id}|{mode}|week",
        [{"role": "system", "content": SYSTEM}, {"role": "user", "content": stage2}],
        AuthoredWeek,
        MAX_REPAIRS,
    )
    stages.append(s2)
    rec["stages"]["week"] = {k: v for k, v in s2.items() if k not in ("parsed", "raw_texts")}
    rec["week_raw"] = s2["raw_texts"]
    rec.update(valid=s2["valid"], final_error=s2["final_error"], week=s2["parsed"])
    rec["prompt_chars"] = len(stage2)
    return _finish(rec, stages)


def _finish(rec: dict, stages: list[dict]) -> dict:
    rec["cost_usd"] = round(sum(s["cost_usd"] for s in stages), 6)
    rec["prompt_tokens"] = sum(s["prompt_tokens"] for s in stages)
    rec["completion_tokens"] = sum(s["completion_tokens"] for s in stages)
    rec["latency_s_calls"] = round(sum(s["latency_s_calls"] for s in stages), 2)
    rec["wall_s"] = round(sum(s["wall_s"] for s in stages), 2)
    rec["calls"] = sum(s["calls"] for s in stages)
    rec["repair_rounds"] = sum(s["repair_rounds"] for s in stages)
    rec["cost_estimated"] = any(s["cost_estimated"] for s in stages)
    rec["validation_errors"] = [
        {"stage": s["label"].split("|")[-1], "round": r["role"], "error": r["error"]}
        for s in stages
        for r in s["rounds"]
        if r["error"]
    ]
    return rec


def ensure_db(out: Path) -> Path:
    """Standards DB built by the repo's own ingest into the work dir (never the app DB)."""
    db = out / "work" / "curriculum.db"
    if not db.exists():
        import subprocess

        db.parent.mkdir(parents=True, exist_ok=True)
        env = dict(os.environ, CURRICULUM_DB_PATH=str(db))
        subprocess.run(
            [sys.executable, str(ROOT / "src" / "ingest_standards.py")],
            env=env,
            check=True,
            capture_output=True,
        )
    return db


def cmd_author_a(args: argparse.Namespace) -> int:
    out = Path(args.out)
    work = out / "work"
    work.mkdir(parents=True, exist_ok=True)
    db = ensure_db(out)
    samples = sample_data()
    prompts = build_prompts(standards_from_db(db, TOPIC_STANDARDS))
    (work / "prompt_common.txt").write_text(prompts["common"])
    (work / "kind_menu.txt").write_text(prompts["menu"])
    provider = real_provider(out, args.max_usd)
    for item in args.runs.split(","):
        key, mode = item.split(":")
        path = work / f"run_{key}-{mode}.json"
        if path.exists() and not args.redo:
            print(f"skip {key}:{mode} (exists)")
            continue
        print(f"== {key} {MODELS[key]} [{mode}] spent so far ${provider.spent():.4f}", flush=True)
        rec = author_week(MODELS[key], mode, provider, prompts, samples)
        rec["key"] = key
        path.write_text(json.dumps(rec, indent=1, ensure_ascii=False))
        print(
            f"   valid={rec['valid']} repairs={rec['repair_rounds']} cost=${rec['cost_usd']:.4f} "
            f"tokens={rec['prompt_tokens']}/{rec['completion_tokens']} wall={rec['wall_s']}s "
            f"{rec.get('final_error') or ''}"[:300],
            flush=True,
        )
    print(f"TOTAL SPENT ${provider.spent():.4f} of ${args.max_usd:.2f}")
    return 0


# ── Objective checks ───────────────────────────────────────────────────────────────────────────

_SKIP_KEYS = {
    "kind", "mode", "style", "hex", "color", "colors", "symbol", "op", "emoji", "type", "fix_mode",
    "answer_style", "src", "alt", "id", "answer", "correct_order", "fill_a", "fill_b",
}  # fmt: skip
_PLACEHOLDER = re.compile(
    r"\b(todo|tbd|lorem|ipsum|placeholder|xxx|fixme|insert .* here|your (text|answer) here)\b"
    r"|\[[^\]]{0,40}\]|\.\.\.|…|\bN/A\b",
    re.I,
)


def _strings(x: Any, key: str = "") -> list[str]:
    if isinstance(x, str):
        return [] if key in _SKIP_KEYS else [x]
    if isinstance(x, dict):
        return [s for k, v in x.items() for s in _strings(v, k)]
    if isinstance(x, list):
        return [s for v in x for s in _strings(v, key)]
    return []


def syllables(word: str) -> int:
    w = re.sub(r"[^a-z]", "", word.lower())
    if not w:
        return 0
    if len(w) <= 3:
        return 1
    w = re.sub(r"(?:es|ed|e)$", "", w) or w
    return max(1, len(re.findall(r"[aeiouy]+", w)))


def fk_grade(texts: list[str]) -> dict:
    """Flesch-Kincaid grade over student-facing sentences (strings of 3+ words)."""
    prose = [t for t in texts if len(re.findall(r"[A-Za-z']+", t)) >= 3]
    words = sents = syl = 0
    for t in prose:
        for s in re.split(r"(?<=[.!?])\s+|\n+", t.strip()):
            ws = re.findall(r"[A-Za-z']+", s)
            if not ws:
                continue
            sents += 1
            words += len(ws)
            syl += sum(syllables(w) for w in ws)
    if not sents or not words:
        return {"fk_grade": None, "words": 0, "avg_sentence_words": None}
    return {
        "fk_grade": round(0.39 * words / sents + 11.8 * syl / words - 15.59, 1),
        "words": words,
        "avg_sentence_words": round(words / sents, 1),
    }


def analyze_week(week_json: dict, db: Path | None, brief_ids: list[str]) -> dict:
    """Deterministic checks over a valid week (given as a dict)."""
    week = load_week(week_json)
    ws = [(d.day, w) for d in week.days for w in d.worksheets]
    kinds = [w.kind for _, w in ws]
    gradable = answered_ws = total_items = answered_items = 0
    for _, w in ws:
        refs = item_refs(w.kind, w.data)
        if refs:
            gradable += 1
            total_items += len(refs)
            answered_ws += 1 if w.answers else 0
            answered_items += len({a.item_ref for a in w.answers})
    ids = {s for d in week.days for s in d.standards} | {c.standard_id for c in week.prep_checks}
    existing: set[str] = set()
    if db is not None and db.exists():
        conn = sqlite3.connect(db)
        existing = {r[0] for r in conn.execute("SELECT standard_id FROM standards")}
        conn.close()
    doc = week.model_dump(mode="json", by_alias=True)
    student_texts = [t for d in doc["days"] for w in d["worksheets"] for t in _strings(w["data"])]
    all_texts = student_texts + _strings(doc["teacher_guide"]) + _strings(doc["prep_checks"])
    placeholders = [t[:60] for t in all_texts if _PLACEHOLDER.search(t)]
    check_ids = [c.standard_id for c in week.prep_checks]
    return {
        "worksheets": len(ws),
        "worksheets_per_day": {d.day: len(d.worksheets) for d in week.days},
        "kinds_used": sorted(set(kinds)),
        "distinct_kinds": len(set(kinds)),
        "kind_counts": {k: kinds.count(k) for k in sorted(set(kinds))},
        "gradable_worksheets": gradable,
        "gradable_worksheets_with_answers": answered_ws,
        "gradable_items": total_items,
        "items_with_answer_key": answered_items,
        "answer_coverage": round(answered_items / total_items, 2) if total_items else None,
        "teacher_guide_answer_blocks": sum(
            1 for g in week.teacher_guide.days for b in g.blocks if b.style == "answer"
        ),
        "reading_level": fk_grade(student_texts),
        "standards_referenced": sorted(ids),
        "standards_count": len(ids),
        "standards_in_db": sorted(ids & existing),
        "standards_missing_from_db": sorted(ids - existing),
        "standards_from_brief": sorted(ids & set(brief_ids)),
        "brief_standards_uncovered_by_prep_checks": sorted(set(brief_ids) - set(check_ids)),
        "prep_checks": len(week.prep_checks),
        "prep_check_standards_all_in_db": all(s in existing for s in check_ids),
        "empty_strings": sum(1 for t in all_texts if not t.strip()),
        "placeholder_hits": placeholders[:10],
        "placeholder_count": len(placeholders),
        "narrator": week.narrator,
    }


# ── PDF rendering ──────────────────────────────────────────────────────────────────────────────


def _chromium_path() -> str | None:
    if os.environ.get("QC_CHROMIUM_PATH"):
        return os.environ["QC_CHROMIUM_PATH"]
    pats = [
        "~/Library/Caches/ms-playwright/chromium_headless_shell-*/*/chrome-headless-shell",
        "~/.cache/ms-playwright/chromium_headless_shell-*/*/chrome-headless-shell",
    ]
    hits = sorted(h for p in pats for h in glob.glob(os.path.expanduser(p)))
    return hits[-1] if hits else None


class Pdfer:
    """HTML -> PDF with headless Chromium: CSS page size, backgrounds on, print media."""

    def __enter__(self) -> "Pdfer":
        from playwright.sync_api import sync_playwright

        self._pw = sync_playwright().start()
        exe = _chromium_path()
        self._browser = (
            self._pw.chromium.launch(executable_path=exe) if exe else self._pw.chromium.launch()
        )
        return self

    def __exit__(self, *exc: Any) -> None:
        self._browser.close()
        self._pw.stop()

    def pdf(self, html_text: str, path: Path, *, landscape: bool = False) -> int:
        page = self._browser.new_page()
        try:
            page.set_content(html_text, wait_until="load")
            page.emulate_media(media="print")
            kw: dict[str, Any] = {"print_background": True, "prefer_css_page_size": True}
            if landscape:  # no CSS @page in the doc: fall back to the explicit format
                kw.update(prefer_css_page_size=False, landscape=True, format="Letter")
            path.parent.mkdir(parents=True, exist_ok=True)
            page.pdf(path=str(path), **kw)
        finally:
            page.close()
        from pypdf import PdfReader

        return len(PdfReader(str(path)).pages)


def margin_label_css(text: str) -> str:
    safe = text.replace("\\", "\\\\").replace('"', '\\"')
    return (
        "<style>@page { size: letter; margin: 0.45in 0.5in; "
        f'@top-left {{ content: "{safe}"; font: 7pt monospace; color: #666; }} }}</style>'
    )


def _page_doc(body: str, title: str, extra_css: str = "", page_css: str = "") -> str:
    return (
        '<!DOCTYPE html><html lang="en"><head><meta charset="UTF-8">'
        f"<title>{html.escape(title)}</title><style>"
        f"{page_css or '@page { size: letter; margin: 0.5in 0.55in; }'}"
        "* { box-sizing: border-box; } body { font-family: 'Trebuchet MS', Arial, sans-serif;"
        " font-size: 10.5pt; color: #111; line-height: 1.4; margin: 0; }"
        "h1 { font-size: 22pt; margin: 0 0 6px; } h2 { font-size: 14pt; margin: 14px 0 6px; }"
        "table { border-collapse: collapse; width: 100%; } td, th { border: 1px solid #888;"
        " padding: 4px 6px; vertical-align: top; font-size: 9pt; } th { background: #eee; text-align: left; }"
        ".box { display:inline-block; width: 11px; height: 11px;"
        " border: 1.5px solid #222; margin-right: 3px; vertical-align: -2px; }"
        ".circ { display:inline-block; width: 15px; height: 15px; border: 1.5px solid #222;"
        " border-radius: 50%; text-align: center; font-size: 8pt; line-height: 13px; margin: 0 5px 0 1px; }"
        ".line { border-bottom: 1px solid #555; height: 24px; }"
        f"{extra_css}</style></head><body>{body}</body></html>"
    )


def _lines(n: int) -> str:
    return '<div class="line"></div>' * n


# ── Feedback sheet (one page per model packet) ─────────────────────────────────────────────────

CRITERIA = [
    ("Age-appropriateness", "too young / too hard", "just right for Ada"),
    ("Clarity of instructions", "confusing", "clear without help"),
    ("Usefulness of activities", "busywork", "worth doing"),
    ("Answer-key correctness", "wrong answers found", "all correct"),
    ("Layout / printability", "cut off, cramped", "clean page"),
    ("Standards alignment", "off topic", "on the standards"),
]


def feedback_sheet_html(code: str, model: str, title: str) -> str:
    rows = ""
    for name, lo, hi in CRITERIA:
        circles = "".join(f'<span class="circ">{i}</span>' for i in range(1, 6))
        rows += (
            f"<tr><td style='width:30%'><b>{name}</b></td><td style='width:17%'>{lo}</td>"
            f"<td style='width:32%;text-align:center'>{circles}</td><td>{hi}</td></tr>"
        )
    box = '<span class="box"></span>'
    body = (
        f"<h1>Feedback: Packet {html.escape(code)}</h1>"
        f"<div>{html.escape(title)} &nbsp;|&nbsp; Reviewer: ______________ &nbsp; Date: __________</div>"
        "<h2>Circle one number per row (1 = poor, 5 = great)</h2>"
        f"<table>{rows}</table>"
        "<h2>Quick marks</h2>"
        f"<div>{box} Ada asked for help a lot &nbsp; {box} Ada finished everything &nbsp; "
        f"{box} Ada asked for more &nbsp; {box} Too much writing &nbsp; "
        f"{box} Would use this week again</div>"
        f"<h2>Which worksheet worked best, and why?</h2>{_lines(2)}"
        f"<h2>Which worksheet should be fixed or dropped, and why?</h2>{_lines(2)}"
        f"<h2>Wrong or confusing answer-key entries (page / question)</h2>{_lines(2)}"
        f"<h2>Anything else</h2>{_lines(4)}"
        f'<p style="margin-top:12px;font:7pt monospace;color:#777">model: {html.escape(model)}</p>'
    )
    return _page_doc(body, f"Feedback {code}")


# ── render-a ───────────────────────────────────────────────────────────────────────────────────


def slug(model_id: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", model_id.lower()).strip("-")


def render_set(pdfer: Pdfer, week: WeekDoc, name: str, folder: Path, code: str, model: str) -> dict:
    """Render packet / teacher guide / prep sheet (+ day-1 packet) to HTML and PDF."""
    (folder / "html").mkdir(parents=True, exist_ok=True)
    info: dict[str, Any] = {}
    docs = {
        "student_packet": render_packet(week, name),
        "teacher_guide": render_teacher_guide(week, name),
        "parent_prep_sheet": render_prep_sheet(week, name),
    }
    for stem, doc in docs.items():
        (folder / "html" / f"{stem}.html").write_text(doc)
        info[f"{stem}_pages"] = pdfer.pdf(doc, folder / f"{stem}.pdf")
    day1 = render_packet(week.model_copy(update={"days": week.days[:1]}), name)
    info["day1_pages"] = pdfer.pdf(day1, folder / "work_day1_packet.pdf")
    info["feedback_pages"] = pdfer.pdf(
        feedback_sheet_html(code, model, week.title), folder / "feedback_sheet.pdf"
    )
    return info


def cmd_render_a(args: argparse.Namespace) -> int:
    from pypdf import PdfReader, PdfWriter

    out = Path(args.out)
    work, parta = out / "work", out / "part-a"
    db = ensure_db(out)
    sources: list[dict] = []
    baseline = json.loads(WEATHER_FIXTURE.read_text())
    order = {"cheap": 0, "mid": 1, "top": 2, "bonus": 3}
    recs = sorted(
        (json.loads(p.read_text()) for p in work.glob("run_*.json")),
        key=lambda r: (r["mode"] != "menu", order.get(r["key"], 9)),
    )
    with Pdfer() as pdfer:
        bfolder = parta / "baseline-weather"
        sources.append(
            {
                "code": "Z",
                "label": "Baseline: reference weather week (K-1, hand-authored, not a model)",
                "folder": bfolder,
                "valid": True,
                "render": render_set(
                    pdfer, load_week(baseline), "Ada", bfolder, "Z", "reference weather week"
                ),
                "checks": analyze_week(baseline, db, TOPIC_STANDARDS),
                "run": None,
            }
        )
        for code, rec in zip("ABCDEFGH", recs, strict=False):
            folder = parta / f"{rec['key']}-{slug(rec['model'])}-{rec['mode']}"
            src: dict[str, Any] = {
                "code": code,
                "label": f"{rec['key']} {rec['model']} [{rec['mode']}]",
                "folder": folder,
                "valid": rec["valid"],
                "run": rec,
                "render": {},
                "checks": None,
            }
            folder.mkdir(parents=True, exist_ok=True)
            slim = {k: v for k, v in rec.items() if k not in ("week_raw", "plan_raw", "week")}
            (folder / "run_record.json").write_text(json.dumps(slim, indent=1))
            for tag in ("week_raw", "plan_raw"):
                for i, t in enumerate(rec.get(tag, [])):
                    (folder / "attempts").mkdir(exist_ok=True)
                    (folder / "attempts" / f"{tag[:-4]}_call{i}.txt").write_text(t)
            if rec["valid"]:
                (folder / "week.json").write_text(
                    json.dumps(rec["week"], indent=1, ensure_ascii=False)
                )
                try:
                    src["render"] = render_set(
                        pdfer, load_week(rec["week"]), "Ada", folder, code, rec["model"]
                    )
                except Exception as exc:  # a render failure is a finding, not a crash
                    src["render_error"] = f"{type(exc).__name__}: {exc}"
                src["checks"] = analyze_week(rec["week"], db, TOPIC_STANDARDS)
            sources.append(src)

        summary = [
            {
                "code": s["code"],
                "label": s["label"],
                "valid": s["valid"],
                "checks": s["checks"],
                "render": s["render"],
                "render_error": s.get("render_error"),
                "run": (
                    None
                    if s["run"] is None
                    else {
                        k: v
                        for k, v in s["run"].items()
                        if k not in ("week", "week_raw", "plan_raw")
                    }
                ),
            }
            for s in sources
        ]
        (parta / "objective_checks.json").write_text(
            json.dumps(summary, indent=1, ensure_ascii=False)
        )
        (parta / "objective_checks.md").write_text(objective_markdown(sources))

        # comparison.pdf: overview table, then per source a divider and its Day-1 pages in sequence
        tmp = parta / "work"
        pdfer.pdf(_overview_html(sources), tmp / "overview.pdf", landscape=True)
        parts = [tmp / "overview.pdf"]
        for s in sources:
            pdfer.pdf(_divider_html(s), tmp / f"divider_{s['code']}.pdf")
            parts.append(tmp / f"divider_{s['code']}.pdf")
            d1 = s["folder"] / "work_day1_packet.pdf"
            if d1.exists():
                parts.append(d1)
        writer = PdfWriter()
        for part in parts:
            for pg in PdfReader(str(part)).pages:
                writer.add_page(pg)
        with (parta / "comparison.pdf").open("wb") as fh:
            writer.write(fh)
    _side_by_side(sources, parta / "comparison_day1_page1_side_by_side.pdf")
    import shutil

    shutil.rmtree(parta / "work")
    for s in sources:
        (s["folder"] / "work_day1_packet.pdf").unlink(missing_ok=True)
    print(json.dumps({s["label"]: s["render"] for s in sources}, indent=1))
    return 0


def _side_by_side(sources: list[dict], path: Path) -> None:
    """Page 1 of each packet next to each other on one tabloid-landscape sheet."""
    try:
        import fitz
    except ImportError:
        return
    shown = [s for s in sources if (s["folder"] / "student_packet.pdf").exists()]
    if not shown:
        return
    doc = fitz.open()
    page = doc.new_page(width=1224, height=792)
    cell = 1224 / len(shown)
    for i, s in enumerate(shown):
        src = fitz.open(str(s["folder"] / "student_packet.pdf"))
        scale = min((cell - 12) / 612, 700 / 792)
        rect = fitz.Rect(i * cell + 6, 60, i * cell + 6 + 612 * scale, 60 + 792 * scale)
        page.show_pdf_page(rect, src, 0)
        page.draw_rect(rect, color=(0.5, 0.5, 0.5), width=0.5)
        page.insert_text((i * cell + 8, 40), f"{s['code']}: {s['label'][:44]}", fontsize=8)
    page.insert_text((10, 18), "Page 1 (Monday) of each student packet, side by side", fontsize=10)
    doc.save(str(path))


def _fmt(v: Any) -> str:
    return "-" if v is None else str(v)


def objective_rows(sources: list[dict]) -> list[list[str]]:
    rows: list[list[str]] = []

    def row(name: str, fn: Any) -> None:
        cells = []
        for s in sources:
            try:
                cell = _fmt(fn(s))
                cells.append("-" if cell in ("None/None", "None / None") else cell)
            except Exception:
                cells.append("-")
        rows.append([name] + cells)

    def run(s: dict, k: str) -> Any:
        return None if s["run"] is None else s["run"].get(k)

    def chk(s: dict, k: str) -> Any:
        return None if s["checks"] is None else s["checks"].get(k)

    row("ended valid (load_week)", lambda s: s["valid"])
    row(
        "cost USD (all calls)", lambda s: "n/a" if s["run"] is None else f"{run(s, 'cost_usd'):.4f}"
    )
    row(
        "prompt / completion tokens",
        lambda s: (
            None if s["run"] is None else f"{run(s,'prompt_tokens')} / {run(s,'completion_tokens')}"
        ),
    )
    row("API calls", lambda s: run(s, "calls"))
    row("latency, sum of calls (s)", lambda s: run(s, "latency_s_calls"))
    row("repair rounds used", lambda s: run(s, "repair_rounds"))
    row(
        "validation errors seen",
        lambda s: None if s["run"] is None else len(run(s, "validation_errors")),
    )
    row("worksheets", lambda s: chk(s, "worksheets"))
    row("distinct kinds", lambda s: chk(s, "distinct_kinds"))
    row("kinds used", lambda s: ", ".join(chk(s, "kinds_used") or []))
    row(
        "gradable worksheets with answers",
        lambda s: f"{chk(s,'gradable_worksheets_with_answers')}/{chk(s,'gradable_worksheets')}",
    )
    row(
        "items with answer key / gradable items",
        lambda s: f"{chk(s,'items_with_answer_key')}/{chk(s,'gradable_items')}",
    )
    row("teacher-guide answer blocks", lambda s: chk(s, "teacher_guide_answer_blocks"))
    row("FK reading grade (student text)", lambda s: chk(s, "reading_level")["fk_grade"])
    row("avg sentence length (words)", lambda s: chk(s, "reading_level")["avg_sentence_words"])
    row("standards referenced", lambda s: chk(s, "standards_count"))
    row("  of which exist in DB", lambda s: len(chk(s, "standards_in_db")))
    row("  missing from DB", lambda s: ", ".join(chk(s, "standards_missing_from_db")) or "none")
    row(
        "brief standards not covered by a prep check",
        lambda s: len(chk(s, "brief_standards_uncovered_by_prep_checks")),
    )
    row("prep checks", lambda s: chk(s, "prep_checks"))
    row("empty strings (may be intentional blank slots)", lambda s: chk(s, "empty_strings"))
    row("placeholder-like text hits", lambda s: chk(s, "placeholder_count"))
    row(
        "packet pages / worksheets",
        lambda s: f"{s['render']['student_packet_pages']}/{chk(s,'worksheets')}",
    )
    row("teacher guide pages", lambda s: s["render"]["teacher_guide_pages"])
    row("prep sheet pages", lambda s: s["render"]["parent_prep_sheet_pages"])
    return rows


def objective_markdown(sources: list[dict]) -> str:
    head = ["metric"] + [
        f"{s['code']}: {s['label'].split('[')[0].strip()[:34]}"
        + (f" [{s['label'].split('[')[1]}" if "[" in s["label"] else "")
        for s in sources
    ]
    lines = ["| " + " | ".join(head) + " |", "|" + "---|" * len(head)]
    lines += ["| " + " | ".join(r) + " |" for r in objective_rows(sources)]
    return "\n".join(lines) + "\n"


def _overview_html(sources: list[dict]) -> str:
    head = ["metric"] + [f"{s['code']}" for s in sources]
    legend = "".join(f"<li><b>{s['code']}</b>: {html.escape(s['label'])}</li>" for s in sources)
    trs = "<tr>" + "".join(f"<th>{html.escape(h)}</th>" for h in head) + "</tr>"
    for r in objective_rows(sources):
        trs += "<tr>" + "".join(f"<td>{html.escape(c)}</td>" for c in r) + "</tr>"
    return _page_doc(
        "<h1 style='font-size:16pt'>Packet comparison: same brief, different models</h1>"
        f"<ul style='font-size:8pt'>{legend}</ul><table>{trs}</table>"
        "<p style='font-size:8pt'>Z is a hand-authored weather week for K-1, a baseline for polish, "
        "not a like-for-like topic. Following pages: a divider and the Day-1 pages of each packet, in "
        "sequence.</p>",
        "comparison",
        "td, th { font-size: 6pt; padding: 2px 3px; }",
        "@page { size: letter landscape; margin: 0.4in; }",
    )


def _divider_html(s: dict) -> str:
    run = s["run"]
    body = f"<h1>Packet {html.escape(s['code'])}</h1><h2>{html.escape(s['label'])}</h2>"
    if run is None:
        body += "<p>Hand-authored reference (weather, K-1). Baseline for structure and polish.</p>"
    else:
        body += (
            f"<p>cost ${run['cost_usd']:.4f} | {run['calls']} call(s) | repair rounds "
            f"{run['repair_rounds']} | ended valid: <b>{run['valid']}</b></p>"
        )
        if not run["valid"]:
            body += f"<p><b>No valid week was produced.</b> {html.escape(str(run['final_error']))[:800]}</p>"
    if s.get("render_error"):
        body += f"<p><b>Render error:</b> {html.escape(s['render_error'])}</p>"
    return _page_doc(body, "divider")


# ── Part B: the sampler ────────────────────────────────────────────────────────────────────────

THEME = (
    "an ocean unit (sea animals, tides, the shore, coral reefs) for Ada, grade 2, who loves space "
    "and drawing"
)

SAMPLER_SYSTEM = (
    "You author the data for ONE printable worksheet of a grade-2 homeschool packet. You never "
    'write code. Reply with a single JSON object {"data": {...}, "answers": [...]} only.'
)


def sheet_model(kind: str) -> type[BaseModel]:
    """{data, answers} validated like a Worksheet. ``data`` is typed with the kind's own model so
    the schema sent to the model (and shown again in repairs) is the real one; the kind-less
    shapeIdWorksheet wrapper stays a dict and is validated by Worksheet below."""
    data_type: Any = dict[str, Any] if kind == "shapeIdWorksheet" else HOSTED_KINDS[kind].model

    class Sheet(BaseModel):
        data: data_type  # type: ignore[valid-type]
        answers: list[Answer] = []

        @model_validator(mode="after")
        def _as_worksheet(self) -> "Sheet":
            raw = (
                self.data
                if isinstance(self.data, dict)
                else self.data.model_dump(mode="json", by_alias=True, exclude_none=True)
            )
            Worksheet(id="x", kind=kind, data=raw, answers=self.answers)
            return self

    Sheet.__name__ = f"Sheet_{kind}"
    return Sheet


def kind_prompt(kind: str, samples: dict[str, dict]) -> str:
    refs = answer_ref_patterns(kind, samples)
    if HOSTED_KINDS[kind].enumerate is None:
        answers_note = 'This kind has no answers: return "answers": []. '
    else:
        answers_note = (
            "If the page has right answers, list them in `answers` as "
            '{"item_ref", "answer"}; item_ref shapes for this kind: '
            f"{', '.join(refs) or 'dotted path into the data lists, zero-based'} "
            "(N = zero-based index). An item_ref addresses a slot the child fills in, never content "
            "already printed on the page. "
        )
    return (
        f"THEME: {THEME}. Student: Ada (use the literal token {{{{student_name}}}} if the name is "
        "needed), reading level grade 2, interests space and drawing; she tires of long writing.\n\n"
        f"KIND: {kind}\nPurpose: {PURPOSE[kind]}\n\n"
        "The `data` object must match this JSON Schema exactly (extra fields are rejected):\n"
        f"{json.dumps(kind_schema(kind), separators=(',', ':'))}\n\n"
        "RULES: plain text and emoji only: no HTML/CSS/SVG/JS, no URLs, no file paths, no image "
        "data. Colours are '#rrggbb'. Short sentences, common words. Make the page genuinely usable "
        "by a 7-year-old: real ocean content, sized to fit ONE letter page. Shuffle any word bank so "
        "its order differs from the answer order. " + answers_note + "Return only the JSON object."
    )


def fallback_badge() -> str:
    """A tiny valid PNG data URI (blue wave badge) made with Pillow, used only as fallback."""
    import base64
    import io

    from PIL import Image, ImageDraw

    im = Image.new("RGB", (96, 96), "#0e7490")
    d = ImageDraw.Draw(im)
    for x in range(0, 96, 24):
        d.arc((x - 12, 40, x + 12, 70), 180, 360, fill="#ffffff", width=3)
    buf = io.BytesIO()
    im.save(buf, "PNG")
    return "data:image/png;base64," + base64.b64encode(buf.getvalue()).decode()


NOT_AUTHORABLE = {
    "logoBadge": "requires an inline raster image (base64 data URI); a text model cannot author "
    "pixels, so no call was made and the harness drew a placeholder wave badge.",
}


def author_kind(kind: str, model_id: str, provider: MeteredProvider, samples: dict) -> dict:
    if kind in NOT_AUTHORABLE:
        return {
            "kind": kind,
            "source": "fallback",
            "reason": NOT_AUTHORABLE[kind],
            "cost_usd": 0.0,
            "data": samples[kind],
            "answers": [],
        }
    client = make_client(
        model_id,
        provider,
        max_tokens=8000,
        structured="json_object" if model_id.startswith("anthropic/") else None,
    )
    rec = run_stage(
        client,
        provider,
        f"{model_id}|sampler|{kind}",
        [
            {"role": "system", "content": SAMPLER_SYSTEM},
            {"role": "user", "content": kind_prompt(kind, samples)},
        ],
        sheet_model(kind),
        MAX_REPAIRS,
    )
    out: dict[str, Any] = {
        "kind": kind,
        "cost_usd": rec["cost_usd"],
        "repair_rounds": rec["repair_rounds"],
        "calls": rec["calls"],
        "prompt_tokens": rec["prompt_tokens"],
        "completion_tokens": rec["completion_tokens"],
        "latency_s": rec["latency_s_calls"],
        "errors": [r["error"] for r in rec["rounds"] if r["error"]],
        "raw_texts": rec["raw_texts"],
    }
    if rec["valid"]:
        parsed = extract_json(rec["raw_texts"][-1])  # the model's own JSON, not a re-dump
        try:
            _render_worksheet(kind, substitute_name(parsed["data"], "Ada"), "Monday", "probe")
            out.update(source="model", data=parsed["data"], answers=parsed["answers"])
            return out
        except Exception as exc:  # validated but unprintable: a finding, treat as failure
            rec["final_error"] = f"render check failed: {type(exc).__name__}: {exc}"
            out["errors"].append(rec["final_error"])
    out.update(
        source="fallback",
        reason=(rec["final_error"] or "invalid")[:500],
        data=samples[kind],
        answers=[],
    )
    return out


def cmd_author_b(args: argparse.Namespace) -> int:
    out = Path(args.out)
    (out / "work").mkdir(parents=True, exist_ok=True)
    samples = sample_data()
    samples["logoBadge"] = {
        "src": fallback_badge(),
        "alt": "wave badge",
        "caption": "Ocean explorer",
    }
    model_id = MODELS[args.model]
    provider = real_provider(out, args.max_usd)
    path = out / "work" / f"sampler_{args.model}.json"
    done = json.loads(path.read_text()) if path.exists() and not args.redo else {}
    todo = [k for k in HOSTED_KINDS if k not in done]

    def one(kind: str) -> dict:
        try:
            return author_kind(kind, model_id, provider, samples)
        except BudgetStop as exc:
            return {
                "kind": kind,
                "source": "fallback",
                "reason": f"BUDGET STOP: {exc}",
                "cost_usd": 0.0,
                "data": samples[kind],
                "answers": [],
            }

    with ThreadPoolExecutor(max_workers=args.workers) as ex:
        for res in ex.map(one, todo):
            done[res["kind"]] = res
            path.write_text(json.dumps(done, indent=1, ensure_ascii=False))
            print(
                f"{res['kind']:28s} {res['source']:8s} repairs={res.get('repair_rounds', 0)} "
                f"${res['cost_usd']:.4f} {(res.get('reason') or '')[:90]}",
                flush=True,
            )
    print(
        f"model={model_id} sampler cost ${sum(r['cost_usd'] for r in done.values()):.4f}; "
        f"ledger total ${provider.spent():.4f}"
    )
    return 0


def _answer_rows(kind: str, data: dict, answers: list[dict]) -> list[tuple[str, str]]:
    prompts = {r.ref: r.prompt for r in item_refs(kind, data)}
    return [(prompts.get(a["item_ref"], a["item_ref"]), a["answer"]) for a in answers]


def cmd_render_b(args: argparse.Namespace) -> int:
    import shutil

    from pypdf import PdfReader, PdfWriter

    out = Path(args.out)
    partb = out / "part-b"
    res = json.loads((out / "work" / f"sampler_{args.model}.json").read_text())
    order = list(HOSTED_KINDS)
    assert set(res) == set(order), set(order) ^ set(res)
    tmp = partb / "work_pages"
    pages: dict[str, int] = {}
    with Pdfer() as pdfer:
        for i, kind in enumerate(order, 1):
            r = res[kind]
            day = DAY_CYCLE[(i - 1) % 5]
            frag = _render_worksheet(
                kind, substitute_name(r["data"], "Ada"), day, f"sampler-{kind}"
            )
            tag = f"#{i} {kind}  [{'FALLBACK sample' if r['source'] == 'fallback' else 'model-authored'}]"
            doc = _r.build_print_packet_html([(day, frag)], kind)
            doc = doc.replace("</head>", margin_label_css(tag) + "</head>")
            pages[kind] = pdfer.pdf(doc, tmp / f"{i:02d}_{kind}.pdf")
        n_model = sum(1 for r in res.values() if r["source"] == "model")
        toc_pages = 1
        for _ in range(2):  # the TOC's own length shifts the page numbers it prints
            toc_pages = pdfer.pdf(_toc_html(order, res, pages, 1 + toc_pages), tmp / "00b_toc.pdf")
        cover = _page_doc(
            "<div style='margin-top:2.2in;text-align:center'>"
            "<h1 style='font-size:34pt'>Ocean Explorer Kind Sampler</h1>"
            "<h2 style='font-size:18pt'>for Ada, grade 2</h2>"
            f"<p style='font-size:13pt'>{len(order)} worksheet kinds, one page each, one ocean theme.<br>"
            f"{n_model} model-authored, {len(order) - n_model} deterministic fallback samples.</p>"
            "<p style='margin-top:40px;font-size:11pt'>Each page has its kind name in the top margin. "
            "At the back, the feedback table has one row per kind: useful? distinct? prints well? "
            "keep / fix / drop.</p>"
            f"<p style='font:8pt monospace;color:#777'>authoring model: {html.escape(MODELS[args.model])}</p></div>",
            "cover",
        )
        pdfer.pdf(cover, tmp / "00a_cover.pdf")
        pdfer.pdf(_answer_key_html(order, res), tmp / "98_answer_key.pdf")
        pdfer.pdf(_feedback_table_html(order), tmp / "99_feedback.pdf")
    writer = PdfWriter()
    for f in sorted(tmp.glob("*.pdf")):
        for pg in PdfReader(str(f)).pages:
            writer.add_page(pg)
    target = partb / "kind_sampler.pdf"
    with target.open("wb") as fh:
        writer.write(fh)
    slim = {
        k: {kk: vv for kk, vv in v.items() if kk not in ("raw_texts", "data")}
        for k, v in res.items()
    }
    for k in slim:
        slim[k]["printed_pages"] = pages[k]
    (partb / "kind_results.json").write_text(json.dumps(slim, indent=1))
    shutil.rmtree(tmp)
    print(
        f"{target} pages={len(PdfReader(str(target)).pages)} model-authored={n_model}/{len(order)}"
    )
    return 0


def _toc_html(order: list[str], res: dict, pages: dict, first_page_no: int) -> str:
    rows, page_no = "", first_page_no + 1
    for i, kind in enumerate(order, 1):
        src = "model" if res[kind]["source"] == "model" else "<b>FALLBACK</b>"
        rows += (
            f"<tr><td>{i}</td><td><code>{kind}</code></td><td>{html.escape(PURPOSE[kind])}</td>"
            f"<td>{src}</td><td>{page_no}</td></tr>"
        )
        page_no += pages[kind]
    return _page_doc(
        "<h1>Contents</h1><p>Page numbers count the cover as page 1. Source says who wrote the "
        "worksheet's content: the model, or the repo's deterministic test sample as a fallback.</p>"
        "<table><tr><th>#</th><th>kind</th><th>purpose</th><th>source</th><th>page</th></tr>"
        f"{rows}</table>",
        "toc",
    )


def _answer_key_html(order: list[str], res: dict) -> str:
    body = (
        "<h1>Answer key</h1><p>Model-authored answers by kind. Fallback samples carry no key.</p>"
    )
    for kind in order:
        r = res[kind]
        try:
            rows = _answer_rows(kind, r["data"], r.get("answers", []))
        except Exception:
            rows = [(a["item_ref"], a["answer"]) for a in r.get("answers", [])]
        if not rows:
            why = "open-ended or display-only" if r["source"] == "model" else "fallback sample"
            body += f"<p><code>{kind}</code>: no answer key ({why}).</p>"
            continue
        trs = "".join(
            f"<tr><td>{html.escape(str(p))[:90]}</td><td>{html.escape(str(a))[:160]}</td></tr>"
            for p, a in rows
        )
        body += f"<h2 style='font-size:11pt;margin:10px 0 3px'><code>{kind}</code></h2><table>{trs}</table>"
    return _page_doc(body, "answer key")


def _feedback_table_html(order: list[str]) -> str:
    box = '<span class="box"></span>'
    rows = "".join(
        f"<tr><td><code>{k}</code></td><td>{box}Y {box}N</td><td>{box}Y {box}N</td>"
        f"<td>{box}Y {box}N</td><td>{box}keep {box}fix {box}drop</td><td style='width:24%'></td></tr>"
        for k in order
    )
    return _page_doc(
        "<h1>Feedback: one row per kind</h1><p>useful = would I print this for a child? distinct = "
        "not the same job as another kind. prints well = nothing cut off, readable.</p>"
        "<table><tr><th>kind</th><th>useful?</th><th>distinct?</th><th>prints well?</th>"
        f"<th>decision</th><th>note</th></tr>{rows}</table><h2>Overall</h2>{_lines(6)}",
        "feedback",
        "tr { break-inside: avoid; } td { height: 0.26in; }",
    )


# ── CLI ────────────────────────────────────────────────────────────────────────────────────────


def cmd_kinds(args: argparse.Namespace) -> int:
    print(f"{len(HOSTED_KINDS)} hosted kinds")
    print(kind_menu())
    return 0


def main(argv: list[str] | None = None) -> int:
    missing = set(HOSTED_KINDS) - set(PURPOSE)
    if missing:
        raise SystemExit(f"PURPOSE is missing kinds: {sorted(missing)}")
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--out", default="artifacts/quality-check")
    sub = ap.add_subparsers(dest="cmd", required=True)
    a = sub.add_parser("author-a")
    a.add_argument("--runs", default="cheap:menu,mid:menu,top:menu,cheap:full")
    a.add_argument("--max-usd", type=float, default=4.0)
    a.add_argument("--redo", action="store_true")
    a.set_defaults(fn=cmd_author_a)
    sub.add_parser("render-a").set_defaults(fn=cmd_render_a)
    b = sub.add_parser("author-b")
    b.add_argument("--model", default="mid", choices=list(MODELS))
    b.add_argument("--max-usd", type=float, default=4.0)
    b.add_argument("--workers", type=int, default=4)
    b.add_argument("--redo", action="store_true")
    b.set_defaults(fn=cmd_author_b)
    rb = sub.add_parser("render-b")
    rb.add_argument("--model", default="mid", choices=list(MODELS))
    rb.set_defaults(fn=cmd_render_b)
    sub.add_parser("kinds").set_defaults(fn=cmd_kinds)
    args = ap.parse_args(argv)
    return args.fn(args)


if __name__ == "__main__":
    raise SystemExit(main())
