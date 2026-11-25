"""Deterministic rendering of a stored WeekDoc: packet, teacher guide, parent prep sheet (M2.4).

Rendering happens on demand from stored data and never stores HTML with the child's name in it
(D3). The optional ``{{student_name}}`` token is swapped in for the name before rendering. The
name is plain text at that point: every renderer escapes it like any other text, so a name
like ``<b>`` cannot inject markup. Names the model wrote directly are escaped the same way.

Determinism: the fill-in-the-blank renderer shuffles its word bank with ``random``; each worksheet
is rendered under a seed derived from its id so repeated renders are byte-identical.
"""

from __future__ import annotations

import html
import random
import re
import sys
import zlib
from pathlib import Path
from typing import Any

try:  # package context
    from .. import worksheet_html_renderer as _r
    from ..print_fonts import font_face_css, font_stack
except ImportError:  # scripts put src/ on sys.path
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    import worksheet_html_renderer as _r  # type: ignore
    from print_fonts import font_face_css, font_stack  # type: ignore

from .models import WeekDoc

DEFAULT_NAME = "your child"
_TOKEN_RE = re.compile(r"\{\{\s*student_name\s*\}\}")
_MAX_NAME = 40

_DAY_CLASS = {"Tuesday": "tue", "Wednesday": "wed", "Thursday": "thu", "Friday": "fri"}

_GUIDE_CSS = (
    font_face_css("adult")
    + """\
    @page { size: letter; margin: 0.5in 0.6in; }
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body { font-family: """
    + font_stack("adult")
    + """; font-size: 11pt; color: #1B2433; line-height: 1.55; }
    @media screen { body { background: #b0b0b0; padding: 24px; } .page { background: white; max-width: 7.5in; margin: 0 auto 28px; padding: 0.45in 0.5in; box-shadow: 0 4px 18px rgba(0,0,0,.28); min-height: 10.3in; } }
    @media print { body { background: white; padding: 0; } .page { padding: 0; box-shadow: none; } * { -webkit-print-color-adjust: exact; print-color-adjust: exact; } }
    .page { page-break-after: always; break-after: page; }
    .page:last-child { page-break-after: avoid; break-after: avoid; }
    h1 { font-size: 18pt; color: #1d4ed8; border-bottom: 3px solid #1d4ed8; padding-bottom: 5px; margin-bottom: 12px; }
    h2 { font-size: 13pt; color: #fff; background: #1d4ed8; padding: 5px 10px; border-radius: 3px; margin: 14px 0 6px; }
    h2.tue { background: #15803d; }
    h2.wed { background: #7c3aed; }
    h2.thu { background: #c2410c; }
    h2.fri { background: #0f766e; }
    h3 { font-size: 10.5pt; font-weight: bold; color: #444; margin: 8px 0 3px; text-transform: uppercase; letter-spacing: 0.04em; }
    p, li { font-size: 10pt; margin-bottom: 5px; }
    ul { padding-left: 18px; margin-bottom: 8px; }
    .answer-box { background: #f0f4ff; border-left: 4px solid #1d4ed8; padding: 6px 10px; margin: 4px 0 10px; border-radius: 0 4px 4px 0; font-size: 10pt; }
    .answer-box.tue { background: #f0fff4; border-color: #15803d; }
    .answer-box.wed { background: #f5f0ff; border-color: #7c3aed; }
    .answer-box.thu { background: #fff7f0; border-color: #c2410c; }
    .answer-box.fri { background: #f0fff8; border-color: #0f766e; }
    .misconception { background: #fff3cd; border-left: 4px solid #d97706; padding: 6px 10px; margin: 4px 0 8px; border-radius: 0 4px 4px 0; font-size: 10pt; }
    .extension { background: #e8f5e9; border-left: 4px solid #15803d; padding: 6px 10px; margin: 4px 0 8px; border-radius: 0 4px 4px 0; font-size: 10pt; }
    .discuss { background: #fce7f3; border-left: 4px solid #9d174d; padding: 6px 10px; margin: 4px 0 8px; border-radius: 0 4px 4px 0; font-size: 10pt; }
"""
)


class RenderError(ValueError):
    """A stored week could not be rendered (never silently skipped)."""


def clean_name(name: str | None) -> str:
    """Validate a display name; None or blank falls back to a generic phrase."""
    if name is None or not name.strip():
        return DEFAULT_NAME
    name = name.strip()
    if len(name) > _MAX_NAME or any(ord(c) < 32 for c in name):
        raise RenderError("student name must be 1-40 printable characters")
    return name


def substitute_name(value: Any, name: str | None) -> Any:
    """Return ``value`` with every ``{{student_name}}`` replaced (strings, lists, dicts)."""
    return _sub(value, clean_name(name))


def _sub(value: Any, display: str) -> Any:
    if isinstance(value, str):
        return _TOKEN_RE.sub(lambda _m: display, value)
    if isinstance(value, dict):
        return {k: _sub(v, display) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [_sub(v, display) for v in value]
    return value


def _prepared(week: WeekDoc, name: str | None) -> dict[str, Any]:
    return substitute_name(week.model_dump(mode="json", by_alias=True), name)


# ── Student packet ──────────────────────────────────────────────────────────


def _render_worksheet(kind: str, data: dict[str, Any], day: str, ws_id: str) -> str:
    state = random.getstate()
    random.seed(zlib.crc32(ws_id.encode()))
    try:
        fragment = _r.render_worksheet_html(kind, data, day)
    finally:
        random.setstate(state)
    if not fragment or not fragment.strip():
        raise RenderError(f"worksheet {ws_id!r} ({kind}) rendered nothing")
    return fragment


def render_packet(week: WeekDoc, student_name: str | None = None) -> str:
    doc = _prepared(week, student_name)
    pages = [
        (day["day"], _render_worksheet(ws["kind"], ws["data"], day["day"], ws["id"]))
        for day in doc["days"]
        for ws in day["worksheets"]
    ]
    return _r.build_print_packet_html(pages, packet_title=doc["packet_title"])


# ── Parent prep sheet ───────────────────────────────────────────────────────


def render_prep_sheet(week: WeekDoc, student_name: str | None = None) -> str:
    doc = _prepared(week, student_name)
    order = [d["day"] for d in doc["days"]]
    checks = sorted(doc["prep_checks"], key=lambda c: order.index(c["day"]))
    fragment = _r.render_worksheet_html(
        "prepCheckList",
        {
            "title": f"Parent Prep Sheet: {doc['title']}",
            "instructions": "Run each check, then tick Got it, Shaky or Missed.",
            "checks": checks,
        },
        "",
    )
    return _r.build_print_packet_html(
        [("", fragment)], packet_title=f"Prep Sheet: {doc['title']}", audience="adult"
    )


# ── Teacher guide ───────────────────────────────────────────────────────────

_ENTITY_RE = re.compile(r"(&#?\w+;)")


def _text(raw: str) -> str:
    """Escape guide text, keeping HTML entities (&rarr;) and **bold** / *italic* markup."""
    parts = _ENTITY_RE.split(raw)
    escaped = "".join(p if i % 2 else html.escape(p, quote=False) for i, p in enumerate(parts))
    escaped = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", escaped)
    return re.sub(r"(?<!\*)\*(?!\s)(.+?)(?<!\s)\*(?!\*)", r"<em>\1</em>", escaped)


def _meta_line(pairs: list[list[str]]) -> str:
    out = ""
    for i, (label, value) in enumerate(pairs):
        if i:
            out += " &nbsp;|&nbsp;" + ("\n  " if i % 2 == 0 else " ")
        out += f"<strong>{_text(label)}:</strong> {_text(value)}"
    return f"  <p>{out}</p>"


def render_teacher_guide(week: WeekDoc, student_name: str | None = None) -> str:
    g = _prepared(week, student_name)["teacher_guide"]
    pages: list[list[str]] = []
    for i, day in enumerate(g["days"]):
        if i == 0 or day["page_break_before"]:
            pages.append([])
        cls = _DAY_CLASS.get(day["day"], "")
        h2_cls = f' class="{cls}"' if cls else ""
        lines = [f"  <h2{h2_cls}>{_text(day['day'])} — {_text(day['title'])}</h2>"]
        for block in day["blocks"]:
            if block["heading"] is not None:
                lines.append(f"  <h3>{_text(block['heading'])}</h3>")
                continue
            div_cls = block["style"]
            if div_cls == "answer":
                div_cls = "answer-box" + (f" {cls}" if cls else "")
            lines.append(f'  <div class="{div_cls}">')
            lines += [f"    <p>{_text(p)}</p>" for p in block["paragraphs"]]
            lines.append("  </div>")
        pages[-1].append("\n".join(lines))

    head = [f"  <h1>{_text(g['title'])}</h1>"]
    if g["meta"]:
        head.append(_meta_line(g["meta"]))
    if g["arc"]:
        head.append(f"  <p><strong>Causal Arc:</strong> {_text(g['arc'])}</p>")
    pages[0].insert(0, "\n".join(head))

    summary = g["summary"]
    if summary:  # its heading takes the last day's colour
        last_cls = _DAY_CLASS.get(g["days"][-1]["day"], "")
        h2_cls = f' class="{last_cls}"' if last_cls else ""
        items = "\n".join(f"    <li>{_text(it)}</li>" for it in summary["items"])
        parts = [
            '  <hr style="margin: 18px 0; border-color: #ccc;">',
            f"  <h2{h2_cls}>{_text(summary['heading'])}</h2>",
            f"  <p>{_text(summary['intro'])}</p>",
            f'  <ol style="padding-left: 20px; font-size: 10pt; line-height: 2;">\n{items}\n  </ol>',
        ]
        if summary["closing"]:
            parts.append(f'  <p style="margin-top: 10px;">{_text(summary["closing"])}</p>')
        pages[-1].append("\n".join(parts))

    body = "\n\n".join('<div class="page">\n' + "\n\n".join(page) + "\n</div>" for page in pages)
    title = _text(g["html_title"] or g["title"])
    return (
        '<!DOCTYPE html>\n<html lang="en">\n<head>\n  <meta charset="UTF-8">\n'
        f"  <title>{title}</title>\n  <style>\n{_GUIDE_CSS}  </style>\n</head>\n<body>\n\n"
        f"{body}\n\n</body>\n</html>"
    )
