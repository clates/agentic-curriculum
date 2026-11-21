#!/usr/bin/env python3
"""Sports-reporter week: one brief, many models, blind printable comparison.

Brief: the Sports Reporter Week of PR #99 (a K-1 child keeps a reporter's notebook about real
games). Each model gets the SAME brief and the real facts from that PR, authors a full WeekDoc
through the repo's plan -> week pipeline (kind menu, structured output, bounded repair), and the
output is printed as: the week plan, Monday, Tuesday (plus a Mon/Tue answer key), one feedback
sheet per model. Packets are labelled with blind letter codes; KEY.md maps codes to models.

    run     call the models (spends money; cost is logged, never capped)
    render  PDFs, KEY.md, blind combined packet (free)

Every call is metered to a JSONL ledger. The cap is effectively off (--max-usd defaults huge).
Repairs: at most ``--max-repairs`` (default 4) per stage before the model is marked a bust.
"""

from __future__ import annotations

import argparse
import html
import json
import random
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import quality_check as qc  # noqa: E402
from quality_check import (  # noqa: E402
    AuthoredWeek,
    BudgetStop,
    WeekPlan,
    kind_block,
    kind_menu,
    make_client,
    real_provider,
    run_stage,
    sample_data,
)

from src.weekdoc import load_week  # noqa: E402
from src.weekdoc.render import render_packet, render_teacher_guide  # noqa: E402

MODELS = {
    "hy4": "tencent/hy4",
    "deepseek-v4-flash": "~deepseek/deepseek-v4-flash-latest",
    "glm-5.3-flash": "z-ai/glm-5.3-flash",
    "gpt-6-luna": "openai/gpt-6-luna",
    "glm-5.3": "z-ai/glm-5.3",
    "qwen3.8-flash": "qwen/qwen3.8-flash",
    "muse-ember": "meta/muse-ember",
}

# Vendor-published sampling settings (looked up 2026-11-21). temperature None = send none and let the
# provider default apply (nothing published, or the API only accepts it with reasoning off).
# top_p / top_k go out in the request body only where the vendor publishes them.
SAMPLING: dict[str, dict[str, Any]] = {
    "hy4": {"temperature": 0.9, "top_p": 1.0, "src": "Hy4 Preview model card (HF)"},
    "deepseek-v4-flash": {"temperature": 1.0, "top_p": 1.0, "src": "DeepSeek V4 Flash 0731 notes"},
    "glm-5.3-flash": {"temperature": 1.0, "top_p": 0.95, "src": "docs.z.ai GLM-5.3-Flash guide"},
    "glm-5.3": {
        "temperature": 1.0,
        "top_p": 0.95,
        "src": "third-party docs (same family as Flash)",
    },
    "qwen3.8-flash": {
        "temperature": 1.0,
        "top_p": 0.95,
        "top_k": 20,
        "src": "Qwen3.8-Flash-Next card, thinking mode (match uncertain)",
    },
    "gpt-6-luna": {
        "temperature": None,
        "src": "none published; temperature only valid with reasoning off",
    },
    "muse-ember": {"temperature": None, "src": "none found"},
}


class SamplingProvider:
    """Overrides temperature (author AND repair calls) and adds top_p/top_k per model."""

    def __init__(self, inner: Any, by_model: dict[str, dict[str, Any]]) -> None:
        self._inner = inner
        self._by_model = by_model

    def __getattr__(self, name: str) -> Any:
        return getattr(self._inner, name)

    def complete(self, request: Any) -> Any:
        from dataclasses import replace

        cfg = self._by_model.get(request.model)
        if cfg is None:
            return self._inner.complete(request)
        extra = {**request.extra_body, **{k: cfg[k] for k in ("top_p", "top_k") if k in cfg}}
        return self._inner.complete(
            replace(request, temperature=cfg.get("temperature"), extra_body=extra)
        )


STUDENT = {
    "first_name": "Christopher",
    "age": 6,
    "grade": "Kindergarten-Grade 1",
    "reading_level": "early reader (K-1)",
    "interests": ["baseball", "football"],
    "parent_note": (
        "Wants real sports, real events, no fantasy framing. He keeps a reporter's notebook all "
        "week, so each day adds a short entry built from sentence starters; keep the daily "
        "writing load light. Light math (sums and differences within 10-20, measuring with "
        "non-standard units, a pictograph) tied to the sports."
    ),
}

TOPIC = (
    "Sports Reporter Week. Causal arc: learn a sport's rules -> report on a real game -> learn "
    "another sport's rules -> report on a second real game -> compare both stories -> assemble "
    "the finished newspaper column. Narrator: the child himself as 'Rookie Reporter "
    "{{student_name}}', keeping a running reporter's notebook."
)

REAL_EVENTS = """\
REAL EVENTS (the ONLY facts you may use; never invent scores, players, dates or stats):
- The child's own first baseball game of the season. You know no details: the page must be a
  template with blanks/sentence starters so the parent and child fill in the specifics together.
- NFL, Sept 13, 2026: Buffalo Bills 36, Houston Texans 31. A back-and-forth game. Josh Allen threw
  a 34-yard game-winning touchdown pass to Joshua Palmer with 1:36 remaining.
- NFL, Sept 13, 2026: Las Vegas Raiders 27, Miami Dolphins 13. The Raiders never trailed. They
  opened with a 16-play, 93-yard drive that took 8:58. Kirk Cousins threw 3 touchdown passes;
  Ashton Jeanty ran for 102 yards and 2 touchdowns.
"""

PACING = (
    "Shape of a good week (follow it): each day has a reading page that teaches that day's sport "
    "rule or play, a writing-scaffold page that builds ONE short notebook entry (about 1.5 "
    "paragraphs, from sentence starters), and a varied application worksheet (matching, t-chart, "
    "bar graph, feature matrix, pictograph, ...). Thursday compares the two NFL games (fact vs "
    "opinion, point margin). Friday assembles the four entries into a finished newspaper column "
    "and an oral retell. About 2 hours of work a day."
)

STANDARD_IDS = [
    "VA.ENGLISH.K.k.c.2.a",
    "VA.ENGLISH.1.1.w.1.a",
    "VA.MATH.K.k.6",
    "VA.ENGLISH.1.1.ri.1.a",
    "VA.MATH.1.1.6",
    "VA.MATH.1.1.10",
    "VA.ENGLISH.1.1.ri.3.a",
    "VA.ENGLISH.1.1.w.1.c",
    "VA.ENGLISH.K.k.w.1.a",
    "VA.ENGLISH.K.k.rl.1.c",
    "VA.MATH.K.k.11",
]

DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]


def sports_rules() -> str:
    """The shared hard rules, re-pointed from a grade-2 science week to a K-1 sports week."""
    rules = qc.RULES
    swaps = [
        (
            "frames a brief hands-on (indoors or outdoors)\n   before/during/after activity tied "
            "to that day's idea",
            "frames a brief active warm-up (a throw, a count, a pose, a mini-game) tied to that "
            "day's idea",
        ),
        ("before the science content", "before the lesson"),
        ("readable at grade 2", "readable by a 6-year-old at Kindergarten-Grade 1 level"),
        ("define science words in context", "define sport words in context"),
    ]
    for old, new in swaps:
        if old not in rules:
            raise SystemExit(f"rules text changed; cannot re-point: {old[:40]!r}")
        rules = rules.replace(old, new)
    return (
        rules
        + "14. Real events only: use ONLY the REAL EVENTS facts. Where a detail is unknown (the "
        "child's own game), use blanks and sentence starters, never invented specifics.\n"
        "15. The child's name never appears literally anywhere; use {{student_name}}.\n"
    )


def build_common(standards: list[dict]) -> str:
    student = (
        "STUDENT (the only personal data you get):\n"
        + json.dumps(STUDENT)
        + f"\n\nTOPIC: {TOPIC}\n\n{REAL_EVENTS}\n{PACING}\n\nSTANDARDS (use ONLY these ids):\n"
        + "\n".join(f"- {s['standard_id']}: {s['description']}" for s in standards)
    )
    return "\n\n".join([student, qc.reference_structure(), sports_rules()])


def completeness_problem(week: AuthoredWeek) -> str | None:
    """The completeness gate: things the schema allows but a printable week cannot lack."""
    problems = []
    if [d.day for d in week.days] != DAYS:
        problems.append("days must be exactly Monday..Friday in order")
    for d in week.days:
        if len(d.worksheets) < 2:
            problems.append(f"{d.day} has fewer than 2 worksheets")
    if len(week.prep_checks) < 8:
        problems.append(f"only {len(week.prep_checks)} prep checks (need about 10)")
    guide_days = [g.day for g in week.teacher_guide.days]
    if guide_days != DAYS:
        problems.append("teacher_guide must have one entry for each of Monday..Friday")
    for g in week.teacher_guide.days:
        styles = {getattr(b, "style", None) for b in g.blocks}
        for need in ("answer", "misconception", "extension", "discuss"):
            if need not in styles:
                problems.append(f"teacher_guide {g.day} lacks a {need} callout")
    if "christopher" in json.dumps(week.model_dump(mode="json", by_alias=True)).lower():
        problems.append("the child's name appears literally; use {{student_name}}")
    return "; ".join(problems[:6]) or None


def _ladder(max_out: int) -> list[tuple[str | None, int]]:
    """(structured mode, max_tokens) attempts. The first rung asks for the model's own maximum
    output (nothing of ours caps it); later rungs fall down only on request-level provider errors.
    """
    return [
        (None, max_out),
        ("json_object", max_out),
        ("json_object", max_out // 2),
        ("json_object", 16000),
    ]


def model_max_output(out_dir: Path, model_id: str) -> int:
    """The model's advertised max completion tokens from OpenRouter's list (cached in work/)."""
    data = json.loads((out_dir / "work" / "models_list.json").read_text())["data"]
    for m in data:
        if m["id"] == model_id:
            return int((m.get("top_provider") or {}).get("max_completion_tokens") or 32000)
    return 32000


def _stage_with_ladder(
    model_id, provider, label, messages, model_cls, repairs, check, notes, max_out
):
    for rung, (mode, tokens) in enumerate(_ladder(max_out)):
        client = make_client(model_id, provider, max_tokens=tokens, structured=mode)
        client._env["LLM_TIMEOUT_S_AUTHOR"] = "1500"
        client._env["LLM_TIMEOUT_S_REPAIR"] = "1500"
        client._env["LLM_MAX_ATTEMPTS"] = "3"
        res = run_stage(client, provider, label, messages, model_cls, repairs, check)
        provider_error = (
            not res["valid"]
            and res["calls"] == 0
            and res["final_error"]
            and not str(res["final_error"]).startswith("BUDGET")
        )
        if not provider_error:
            if rung:
                notes.append(f"{label}: needed fallback rung {rung} (mode={mode}, tokens={tokens})")
            return res
        notes.append(f"{label}: rung {rung} (mode={mode}, tokens={tokens}) -> {res['final_error']}")
    return res


def author(
    model_id: str, provider, common: str, samples: dict, max_repairs: int, max_out: int
) -> dict:
    notes: list[str] = []
    rec: dict[str, Any] = {"model": model_id, "mode": "menu", "notes": notes, "stages": {}}
    stages = []
    plan_prompt = (
        f"{common}\n\nKIND MENU (the only kinds that exist; one line each):\n{kind_menu()}\n\n"
        'TASK STEP 1 of 2: plan the week. Return JSON {"narrator": str, "arc": str, "days": '
        '[{"day", "title", "standards": [ids], "worksheets": [{"id", "kind", "focus"}]}]} '
        "covering Monday..Friday, 2-3 worksheets per day, choosing kinds from the menu that suit "
        "a K-1 sports reporter week. Use a varied but sensible set of kinds (not every kind). "
        "Do not write worksheet content yet."
    )
    s1 = _stage_with_ladder(
        model_id,
        provider,
        f"{model_id}|sports|plan",
        [{"role": "system", "content": qc.SYSTEM}, {"role": "user", "content": plan_prompt}],
        WeekPlan,
        max_repairs,
        None,
        notes,
        max_out,
    )
    stages.append(s1)
    rec["stages"]["plan"] = {k: v for k, v in s1.items() if k not in ("parsed", "raw_texts")}
    rec["plan_raw"] = s1["raw_texts"]
    rec["plan"] = s1["parsed"]
    if not s1["valid"]:
        rec.update(valid=False, week=None, final_error=f"plan stage failed: {s1['final_error']}")
        return qc._finish(rec, stages)
    plan = WeekPlan.model_validate(s1["parsed"])
    catalog = "\n\n".join(kind_block(k, samples) for k in plan.kinds())
    week_prompt = (
        f"{common}\n\nYOUR PLAN FROM STEP 1 (follow it):\n{json.dumps(s1['parsed'])}\n\n"
        f"SCHEMAS for the kinds in your plan:\n{catalog}\n\n"
        "TASK STEP 2 of 2: write the complete WeekDoc JSON following your plan: title, "
        "packet_title (use {{student_name}} for the child), theme, subject, grade_band 'K-1', "
        "narrator, arc, days (with worksheets and answers), prep_checks, teacher_guide."
    )
    s2 = _stage_with_ladder(
        model_id,
        provider,
        f"{model_id}|sports|week",
        [{"role": "system", "content": qc.SYSTEM}, {"role": "user", "content": week_prompt}],
        AuthoredWeek,
        max_repairs,
        completeness_problem,
        notes,
        max_out,
    )
    stages.append(s2)
    rec["stages"]["week"] = {k: v for k, v in s2.items() if k not in ("parsed", "raw_texts")}
    rec["week_raw"] = s2["raw_texts"]
    rec.update(valid=s2["valid"], final_error=s2["final_error"], week=s2["parsed"])
    return qc._finish(rec, stages)


def cmd_run(args: argparse.Namespace) -> int:
    out = Path(args.out)
    work = out / "work"
    work.mkdir(parents=True, exist_ok=True)
    db = qc.ensure_db(out)
    standards = qc.standards_from_db(db, STANDARD_IDS)
    common = build_common(standards)
    (work / "prompt_common.txt").write_text(common)
    samples = sample_data()
    provider = real_provider(out, args.max_usd)
    if args.sampling == "recommended":
        provider = SamplingProvider(provider, {MODELS[k]: v for k, v in SAMPLING.items()})
    keys = [k.strip() for k in args.models.split(",")] if args.models else list(MODELS)

    def one(key: str) -> tuple[str, dict]:
        path = work / f"run_{key}.json"
        if path.exists() and not args.redo:
            return key, json.loads(path.read_text())
        print(f"== start {key} {MODELS[key]}", flush=True)
        try:
            rec = author(
                MODELS[key],
                provider,
                common,
                samples,
                args.max_repairs,
                model_max_output(out, MODELS[key]),
            )
        except BudgetStop as exc:
            rec = {"model": MODELS[key], "valid": False, "final_error": f"BUDGET STOP: {exc}"}
        except Exception as exc:  # one model's crash must not stop the others
            rec = {
                "model": MODELS[key],
                "valid": False,
                "final_error": f"{type(exc).__name__}: {exc}",
            }
        rec["key"] = key
        rec["sampling"] = (
            {"mode": "forced", "author_temperature": 0.5, "repair_temperature": 0.0}
            if args.sampling == "forced"
            else {"mode": "recommended", **SAMPLING[key]}
        )
        path.write_text(json.dumps(rec, indent=1, ensure_ascii=False))
        print(
            f"== done {key} valid={rec['valid']} repairs={rec.get('repair_rounds')} "
            f"cost=${rec.get('cost_usd', 0):.4f} wall={rec.get('wall_s')}s "
            f"{(rec.get('final_error') or '')[:200]}",
            flush=True,
        )
        return key, rec

    with ThreadPoolExecutor(max_workers=len(keys)) as pool:
        list(pool.map(one, keys))
    print(f"TOTAL SPENT ${provider.spent():.4f}")
    return 0


# ── rendering ──────────────────────────────────────────────────────────────────────────────────

FACT_PROBES = {
    "Bills 36-31": ("36", "31"),
    "Josh Allen": ("allen",),
    "Joshua Palmer / 34-yard": ("palmer", "34"),
    "1:36 left": ("1:36",),
    "Raiders 27-13": ("27", "13"),
    "16-play / 93-yard drive": ("16", "93"),
    "Cousins": ("cousins",),
    "Jeanty": ("jeanty",),
}

SPORTS_CRITERIA = [
    ("Right level for a 6-year-old (K-1)", "too hard / too babyish", "just right"),
    ("Clear instructions", "confusing", "clear without help"),
    ("Real facts used accurately", "invented or wrong", "faithful to the facts"),
    ("Reporter's-notebook voice and arc", "disconnected", "feels like one story"),
    ("Writing load", "too much", "light and doable"),
    ("Usefulness of activities", "busywork", "worth doing"),
    ("Layout / printability", "cut off, cramped", "clean page"),
]


def feedback_html(code: str, title: str) -> str:
    rows = ""
    for name, lo, hi in SPORTS_CRITERIA:
        circ = "".join(f'<span class="circ">{i}</span>' for i in range(1, 6))
        rows += (
            f"<tr><td style='width:32%'><b>{name}</b></td><td style='width:16%'>{lo}</td>"
            f"<td style='width:32%;text-align:center'>{circ}</td><td>{hi}</td></tr>"
        )
    body = (
        f"<h1>Feedback: Packet {html.escape(code)}</h1>"
        f"<div>{html.escape(title)} &nbsp;|&nbsp; Reviewer: ____________ &nbsp; Date: ________</div>"
        "<h2>Circle one number per row (1 = poor, 5 = great)</h2>"
        f"<table>{rows}</table>"
        "<h2>Plan page: does the week arc make sense?</h2>"
        + qc._lines(2)
        + "<h2>Monday: best / worst thing about it</h2>"
        + qc._lines(2)
        + "<h2>Tuesday: best / worst thing about it</h2>"
        + qc._lines(2)
        + "<h2>Wrong or confusing answer-key entries</h2>"
        + qc._lines(2)
        + "<h2>Would you print this week for Christopher?  yes / with edits / no &nbsp; Why?</h2>"
        + qc._lines(3)
    )
    return qc._page_doc(body, f"Feedback {code}")


def plan_page_html(code: str, week: dict, plan: dict | None) -> str:
    sub = lambda t: str(t).replace("{{student_name}}", "Christopher")  # noqa: E731
    body = f"<h1>Packet {html.escape(code)}: week plan</h1>"
    body += f"<h2>{html.escape(sub(week['title']))}</h2>"
    body += f"<p><b>Narrator:</b> {html.escape(sub(week['narrator']))}</p>"
    body += f"<p><b>Arc:</b> {html.escape(sub(week['arc']))}</p>"
    focus = {}
    for d in (plan or {}).get("days", []):
        for w in d["worksheets"]:
            focus[w["id"]] = w["focus"]
    rows = ""
    for d in week["days"]:
        ws = "".join(
            f"<div><code>{html.escape(w['kind'])}</code> &mdash; "
            f"{html.escape(sub(focus.get(w['id'], w.get('title', '') or '')))}</div>"
            for w in d["worksheets"]
        )
        rows += (
            f"<tr><td style='width:14%'><b>{d['day']}</b></td>"
            f"<td style='width:26%'>{html.escape(sub(d['title']))}</td><td>{ws}</td>"
            f"<td style='width:18%;font-size:7.5pt'>{html.escape(', '.join(d['standards']))}</td></tr>"
        )
    body += f"<table><tr><th>Day</th><th>Title</th><th>Worksheets (kind: focus)</th><th>Standards</th></tr>{rows}</table>"
    body += (
        f"<p>Prep checks: {len(week['prep_checks'])}. "
        "Only Monday and Tuesday are printed in this packet.</p>"
    )
    return qc._page_doc(
        body,
        f"Plan {code}",
        extra_css="code{font-size:7.5pt;background:#eee;padding:0 3px} td,th{font-size:8pt;padding:3px 5px} body{line-height:1.25} h1{font-size:18pt} h2{font-size:12pt}",
        page_css="@page { size: letter; margin: 0.35in 0.45in; }",
    )


def fact_usage(week: dict) -> dict[str, bool]:
    text = json.dumps(week, ensure_ascii=False).lower()
    return {k: all(p in text for p in probes) for k, probes in FACT_PROBES.items()}


def cmd_render(args: argparse.Namespace) -> int:
    from pypdf import PdfReader, PdfWriter

    out = Path(args.out)
    work = out / "work"
    recs = {
        k: json.loads((work / f"run_{k}.json").read_text())
        for k in MODELS
        if (work / f"run_{k}.json").exists()
    }
    rng = random.Random(20261121)
    order = list(recs)
    rng.shuffle(order)
    codes = {k: args.code_prefix + "ABCDEFGH"[i] for i, k in enumerate(order)}
    key_rows = []
    parts: list[Path] = []
    tmp = out / "tmp"
    tmp.mkdir(exist_ok=True)
    db = qc.ensure_db(out)
    with qc.Pdfer() as pdfer:
        cover = qc._page_doc(
            "<h1>Sports Reporter Week: blind comparison</h1>"
            f"<p><b>{html.escape(args.note or 'Same settings for every model.')}</b></p>"
            "<p>Each packet: week plan, Monday, Tuesday, feedback sheet. "
            "Model names are in KEY.md; open it after marking.</p>",
            "cover",
        )
        pdfer.pdf(cover, tmp / "cover.pdf")
        parts.append(tmp / "cover.pdf")
        for k in sorted(order, key=lambda k: codes[k]):
            rec, code = recs[k], codes[k]
            folder = out / f"packet-{code}"
            folder.mkdir(exist_ok=True)
            row = {
                "code": code,
                "key": k,
                "model": rec["model"],
                "valid": rec["valid"],
                "cost_usd": rec.get("cost_usd"),
                "repair_rounds": rec.get("repair_rounds"),
                "calls": rec.get("calls"),
                "wall_s": rec.get("wall_s"),
                "tokens": f"{rec.get('prompt_tokens')}/{rec.get('completion_tokens')}",
                "notes": rec.get("notes"),
                "final_error": rec.get("final_error"),
                "stopped": rec.get("stopped", False),
                "sampling": rec.get("sampling"),
            }
            slim = {kk: v for kk, v in rec.items() if kk not in ("week_raw", "plan_raw", "week")}
            (folder / "run_record.json").write_text(json.dumps(slim, indent=1))
            for tag in ("week_raw", "plan_raw"):
                for i, t in enumerate(rec.get(tag, [])):
                    (folder / "attempts").mkdir(exist_ok=True)
                    (folder / "attempts" / f"{tag[:-4]}_call{i}.txt").write_text(t)
            if rec["valid"]:
                wk = rec["week"]
                (folder / "week.json").write_text(json.dumps(wk, indent=1, ensure_ascii=False))
                row["facts_used"] = fact_usage(wk)
                try:
                    row["checks"] = qc.analyze_week(wk, db, STANDARD_IDS)
                except Exception as exc:
                    row["checks_error"] = str(exc)
                week = load_week(wk)
                two = week.model_copy(update={"days": week.days[:2]})
                gd = week.teacher_guide
                two_guide = week.model_copy(
                    update={
                        "days": week.days[:2],
                        "teacher_guide": gd.model_copy(update={"days": gd.days[:2]}),
                    }
                )
                sheets = {
                    "plan": plan_page_html(code, wk, rec.get("plan")),
                    "mon_tue": render_packet(two, "Christopher"),
                    "mon_tue_answer_key": render_teacher_guide(two_guide, "Christopher"),
                    "feedback": feedback_html(code, wk["title"]),
                }
                row["pages"] = {}
                for name, doc in sheets.items():
                    row["pages"][name] = pdfer.pdf(doc, folder / f"{name}.pdf")
                    (folder / f"{name}.html").write_text(doc)
                div = qc._page_doc(
                    f"<h1>Packet {code}</h1><p>Week plan, Monday, Tuesday, then the feedback sheet.</p>",
                    "d",
                )
                pdfer.pdf(div, tmp / f"div_{code}.pdf")
                parts += [tmp / f"div_{code}.pdf"] + [
                    folder / f"{n}.pdf" for n in ("plan", "mon_tue", "feedback")
                ]
            else:
                div = qc._page_doc(
                    f"<h1>Packet {code}</h1><p><b>No valid week produced</b> (bust after repairs, or stopped early: see KEY.md).</p>",
                    "d",
                )
                pdfer.pdf(div, tmp / f"div_{code}.pdf")
                parts.append(tmp / f"div_{code}.pdf")
            key_rows.append(row)
    writer = PdfWriter()
    for part in parts:
        for pg in PdfReader(str(part)).pages:
            writer.add_page(pg)
    with (out / "sports_blind_packet.pdf").open("wb") as fh:
        writer.write(fh)
    (out / "KEY.json").write_text(json.dumps(key_rows, indent=1, ensure_ascii=False))
    lines = [
        "# KEY (open after marking)",
        "",
        "| code | model | valid | repairs | calls | cost | wall s | tokens in/out |",
        "|---|---|---|---|---|---|---|---|",
    ]
    for r in key_rows:
        lines.append(
            f"| {r['code']} | {r['model']} | {r['valid']} | {r['repair_rounds']} | {r['calls']} | ${(r['cost_usd'] or 0):.4f} | {r['wall_s']} | {r['tokens']} |"
        )
    lines += ["", f"Total: ${sum((r['cost_usd'] or 0) for r in key_rows):.4f}", ""]
    for r in key_rows:
        lines.append(f"## {r['code']} {r['model']}")
        lines.append(f"- sampling: {json.dumps(r.get('sampling'))}")
        if not r["valid"]:
            lines.append(("STOPPED: " if r.get("stopped") else "BUST: ") + str(r["final_error"]))
        if r.get("notes"):
            lines += [f"- {n}" for n in r["notes"]]
        if r.get("facts_used"):
            lines.append(
                "- facts used: "
                + ", ".join(f"{k}={'yes' if v else 'NO'}" for k, v in r["facts_used"].items())
            )
        c = r.get("checks")
        if c:
            lines.append(
                f"- {c['worksheets']} worksheets, {c['distinct_kinds']} kinds, answer coverage {c['answer_coverage']}, prep checks {c['prep_checks']}, reading level {c['reading_level']}"
            )
        lines.append("")
    (out / "KEY.md").write_text("\n".join(lines))
    import shutil

    shutil.rmtree(tmp)
    print("\n".join(lines))
    return 0


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawTextHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    for name in ("run", "render"):
        p = sub.add_parser(name)
        p.add_argument("--out", required=True)
        if name == "run":
            p.add_argument("--models", help="comma list of keys; default all")
            p.add_argument("--max-repairs", type=int, default=4)
            p.add_argument("--max-usd", type=float, default=1e9)
            p.add_argument("--redo", action="store_true")
            p.add_argument(
                "--sampling",
                choices=["forced", "recommended"],
                default="forced",
                help="forced = harness defaults (0.5 author / 0.0 repair); "
                "recommended = each vendor's published settings",
            )
        else:
            p.add_argument("--code-prefix", default="")
            p.add_argument("--note", default="")
    args = ap.parse_args(argv)
    return {"run": cmd_run, "render": cmd_render}[args.cmd](args)


if __name__ == "__main__":
    raise SystemExit(main())
