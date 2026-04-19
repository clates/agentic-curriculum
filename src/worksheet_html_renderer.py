"""
worksheet_html_renderer.py

Renders worksheet content as self-contained HTML suitable for browser
printing.  Each worksheet type accepts a plain dict of data (matching the
shape validated by the corresponding Pydantic model) and returns an HTML
fragment (no <html>/<body> wrapper).

Top-level helpers:
  render_worksheet_html(kind, data, day_label) -> str | None
  build_print_packet_html(pages)               -> str   (full printable doc)

Day-colour palette — one accent per weekday so students and teachers can
instantly identify which sheets belong to which day:
  Monday    – blue   #1d4ed8 / #dbeafe
  Tuesday   – green  #15803d / #dcfce7
  Wednesday – purple #7c3aed / #ede9fe
  Thursday  – orange #c2410c / #ffedd5
  Friday    – teal   #0f766e / #ccfbf1
"""

from __future__ import annotations

import html as _html
from typing import Any

# ── Day palette ────────────────────────────────────────────────────────────

_DAY_PALETTE: dict[str, tuple[str, str]] = {
    "monday": ("#1d4ed8", "#dbeafe"),
    "tuesday": ("#15803d", "#dcfce7"),
    "wednesday": ("#7c3aed", "#ede9fe"),
    "thursday": ("#c2410c", "#ffedd5"),
    "friday": ("#0f766e", "#ccfbf1"),
}
_DEFAULT_PALETTE = ("#374151", "#f3f4f6")


def get_day_palette(day_label: str) -> tuple[str, str]:
    """Return (primary, light) hex colours for the given day label."""
    key = day_label.strip().lower().split()[0] if day_label else ""
    return _DAY_PALETTE.get(key, _DEFAULT_PALETTE)


# ── Shared CSS ─────────────────────────────────────────────────────────────

_CSS = """\
<style>
  @page { size: letter; margin: 0.45in 0.5in; }
  * { box-sizing: border-box; margin: 0; padding: 0; }

  body {
    font-family: 'Trebuchet MS', Arial, Helvetica, sans-serif;
    font-size: 11pt;
    color: #111;
    line-height: 1.5;
  }

  /* Page structure */
  .page {
    width: 100%;
    page-break-after: always;
    break-after: page;
    padding-bottom: 0.1in;
  }
  .page:last-child { page-break-after: avoid; break-after: avoid; }

  @media screen {
    body { background: #b0b0b0; padding: 24px; }
    .page {
      background: white;
      max-width: 7.5in;
      margin: 0 auto 28px;
      padding: 0.45in 0.5in 0.35in;
      box-shadow: 0 4px 18px rgba(0,0,0,.30);
      min-height: 10.3in;
    }
  }
  @media print {
    body { background: white; padding: 0; }
    .page { padding: 0; box-shadow: none; margin: 0; }
  }

  /* Day header bar */
  .day-header {
    display: flex;
    align-items: baseline;
    gap: 10px;
    padding: 5px 10px 5px 12px;
    border-radius: 4px 4px 0 0;
    margin-bottom: 6px;
    color: white;
  }
  .day-header-label {
    font-size: 9pt;
    font-weight: bold;
    text-transform: uppercase;
    letter-spacing: 0.07em;
    opacity: 0.85;
  }
  .day-header-title { font-size: 12pt; font-weight: bold; }

  /* Title / instructions / name-date */
  .ws-title {
    font-size: 15pt;
    font-weight: bold;
    padding-bottom: 4px;
    margin-bottom: 4px;
    border-bottom: 2.5px solid currentColor;
    line-height: 1.2;
  }
  .ws-instructions {
    font-size: 9.5pt;
    color: #555;
    font-style: italic;
    margin-bottom: 8px;
  }
  .name-date-row {
    display: flex;
    gap: 16px;
    font-size: 9.5pt;
    margin-bottom: 10px;
  }
  .name-date-row span { flex: 1; border-bottom: 1px solid #444; padding-bottom: 1px; }
  .name-date-row span.short { flex: 0 0 2.2in; }

  .answer-lines { margin: 2px 0 4px; }
  .answer-line { border-bottom: 1px solid #777; height: 22px; margin-bottom: 3px; width: 100%; }

  /* Reading */
  .passage-title { font-size: 12pt; font-weight: bold; margin: 7px 0 3px; }
  .passage {
    background: #f7f7f5;
    border-left: 4px solid #aaa;
    padding: 7px 11px;
    font-size: 9.5pt;
    line-height: 1.6;
    margin-bottom: 9px;
  }
  .passage p { margin-bottom: 6px; }
  .passage p:last-child { margin-bottom: 0; }
  .questions-section h3 {
    font-size: 10pt; font-weight: bold;
    border-bottom: 1px solid #bbb; padding-bottom: 2px; margin-bottom: 6px;
  }
  .question { margin-bottom: 9px; }
  .question-prompt { font-size: 9.5pt; font-weight: bold; margin-bottom: 3px; line-height: 1.35; }
  .vocab-section { margin-top: 9px; }
  .vocab-section h3 {
    font-size: 10pt; font-weight: bold;
    border-bottom: 1px solid #bbb; padding-bottom: 2px; margin-bottom: 5px;
  }
  .vocab-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 4px 10px; }
  .vocab-item { border: 1px solid #ccc; border-radius: 3px; padding: 3px 5px; font-size: 9pt; line-height: 1.35; }
  .vocab-term { font-weight: bold; }
  .vocab-def { color: #444; }

  /* Feature matrix */
  .feature-matrix-wrapper { overflow-x: auto; margin-top: 4px; }
  table.feature-matrix { width: 100%; border-collapse: collapse; font-size: 10pt; }
  table.feature-matrix th {
    background: #2c2c2c; color: white;
    padding: 5px 8px; font-size: 9.5pt; text-align: center;
    border: 1px solid #555;
  }
  table.feature-matrix th.fm-item-col { text-align: left; min-width: 1.4in; }
  table.feature-matrix td { border: 1px solid #bbb; padding: 4px 8px; vertical-align: middle; }
  td.fm-item-cell { font-weight: bold; background: #f9f9f9; }
  td.fm-check-cell { text-align: center; font-size: 14pt; color: #666; }

  /* Tree map */
  .tm-root-row { display: flex; justify-content: center; margin-bottom: 6px; }
  .tm-root {
    border: 2.5px solid #333; border-radius: 5px;
    padding: 6px 18px; font-size: 13pt; font-weight: bold; background: #f0f4ff;
  }
  .tm-branches-grid { display: grid; gap: 8px; margin-top: 6px; }
  .tm-branch { border: 2px solid #555; border-radius: 4px; padding: 6px 8px; min-height: 80px; }
  .tm-branch-name {
    font-size: 10pt; font-weight: bold; text-align: center;
    border-bottom: 1px solid #bbb; padding-bottom: 3px; margin-bottom: 5px;
  }
  .tm-slot { font-size: 9.5pt; padding: 2px 4px; }
  .tm-slot.blank { border-bottom: 1px solid #888; margin-bottom: 3px; color: #999; }
  .tm-slot.prefilled { font-weight: bold; }

  /* Capstone tree map (word-bank variant) */
  .ctm-root-row { display: flex; justify-content: center; margin-bottom: 8px; }
  .ctm-root {
    border: 2.5px solid #333; border-radius: 5px;
    padding: 6px 20px; font-size: 13pt; font-weight: bold; background: #f0f4ff;
  }
  .ctm-branches { display: flex; gap: 12px; margin-bottom: 10px; }
  .ctm-branch { flex: 1; border: 2px solid #555; border-radius: 4px; padding: 7px 9px; min-height: 120px; }
  .ctm-branch-name {
    font-weight: bold; font-size: 10.5pt; text-align: center;
    border-bottom: 1px solid #bbb; padding-bottom: 3px; margin-bottom: 6px;
  }
  .ctm-slot { border-bottom: 1px solid #aaa; height: 24px; margin-bottom: 4px; }
  .ctm-word-bank { border: 1.5px dashed #aaa; border-radius: 4px; padding: 7px 9px; }
  .ctm-wb-label { font-size: 8.5pt; color: #888; font-style: italic; margin-bottom: 5px; }
  .ctm-wb-tiles { display: flex; flex-wrap: wrap; gap: 5px; }
  .ctm-wb-tile { border: 1px solid #555; border-radius: 3px; padding: 2px 8px; font-size: 9.5pt; background: white; }

  /* Odd one out */
  .oo-group { margin-bottom: 14px; }
  .oo-number { font-size: 9pt; font-weight: bold; color: #666; margin-bottom: 4px; }
  .oo-items-row { display: flex; gap: 8px; margin-bottom: 5px; flex-wrap: wrap; }
  .oo-item {
    border: 2px solid #555; border-radius: 20px;
    padding: 5px 14px; font-size: 10.5pt; background: #fafafa;
    cursor: pointer;
  }
  .oo-answer-row { font-size: 9pt; color: #444; }
  .oo-answer-line { border-bottom: 1px solid #888; height: 20px; margin-top: 3px; }

  /* Matching */
  .matching-row { display: flex; align-items: center; gap: 10px; margin-bottom: 9px; }
  .matching-left, .matching-right {
    flex: 1; border: 1.5px solid #444; border-radius: 4px;
    padding: 5px 9px; font-size: 10pt; background: #fafafa;
  }
  .matching-line { flex: 0 0 60px; border-bottom: 1px solid #888; height: 1px; position: relative; }
  .matching-number { font-size: 9pt; font-weight: bold; color: #666; flex: 0 0 18px; text-align: right; }
  /* Geography-style matching (lettered right column) */
  .matching-columns { display: flex; gap: 0; }
  .matching-left-col, .matching-right-col { flex: 1; }
  .matching-spacer-col { flex: 0 0 0.6in; }
  .matching-item { display: flex; align-items: baseline; gap: 6px; padding: 5px 0; font-size: 10.5pt; }
  .matching-item-num, .matching-item-letter {
    font-size: 10pt; font-weight: bold; color: #555;
    flex: 0 0 20px; text-align: right;
  }
  .matching-instructions-note { font-size: 9pt; color: #555; font-style: italic; margin-bottom: 8px; }

  /* Cause & Effect */
  .cause-effect-pair { display: flex; align-items: stretch; gap: 0; margin-bottom: 12px; }
  .ce-cause, .ce-effect { flex: 1; border: 1.5px solid #444; padding: 6px 9px; min-height: 68px; }
  .ce-cause { background: #fffbe6; border-right: none; border-radius: 5px 0 0 5px; }
  .ce-effect { background: #eaf5ea; border-left: none; border-radius: 0 5px 5px 0; }
  .ce-arrow {
    display: flex; align-items: center; padding: 0 6px; font-size: 18pt; color: #666;
    background: #f0f0f0; border-top: 1.5px solid #444; border-bottom: 1.5px solid #444; flex: 0 0 auto;
  }
  .ce-label { font-size: 7.5pt; font-weight: bold; text-transform: uppercase; color: #888; margin-bottom: 3px; letter-spacing: 0.03em; }
  .ce-text { font-size: 9.5pt; font-weight: bold; color: #222; margin-bottom: 3px; line-height: 1.3; }
  .ce-open-text { font-size: 9.5pt; color: #555; font-style: italic; }

  /* Frayer model */
  .frayer-entry { margin-bottom: 16px; }
  .frayer-word-box {
    text-align: center; font-size: 14pt; font-weight: bold;
    border: 2px solid #333; padding: 5px; background: #f0f4ff; border-bottom: none;
  }
  .frayer-grid { display: grid; grid-template-columns: 1fr 1fr; border: 2px solid #333; }
  .frayer-cell { padding: 6px 8px; min-height: 82px; font-size: 9.5pt; line-height: 1.4; }
  .frayer-cell:nth-child(1) { border-right: 1px solid #333; border-bottom: 1px solid #333; }
  .frayer-cell:nth-child(2) { border-bottom: 1px solid #333; }
  .frayer-cell:nth-child(3) { border-right: 1px solid #333; }
  .frayer-cell-label { font-size: 8pt; font-weight: bold; text-transform: uppercase; color: #777; margin-bottom: 3px; letter-spacing: 0.04em; }

  /* Word sort */
  .word-sort-categories { display: grid; gap: 8px; margin-bottom: 12px; }
  .ws-category { border: 2px solid #333; border-radius: 4px; padding: 7px 9px; min-height: 72px; }
  .ws-category-label { font-weight: bold; font-size: 10.5pt; border-bottom: 1px solid #bbb; padding-bottom: 3px; margin-bottom: 5px; }
  .ws-tile-bank { border: 1.5px dashed #aaa; border-radius: 4px; padding: 7px 9px; margin-top: 4px; }
  .ws-tile-bank-label { font-size: 8.5pt; color: #888; font-style: italic; margin-bottom: 5px; }
  .ws-tiles { display: flex; flex-wrap: wrap; gap: 5px; }
  .ws-tile { border: 1px solid #555; border-radius: 3px; padding: 2px 8px; font-size: 9.5pt; background: white; white-space: nowrap; }

  /* Writing scaffold */
  .scaffold-section { margin-bottom: 12px; }
  .scaffold-part-label { font-size: 9pt; font-weight: bold; text-transform: uppercase; color: #666; letter-spacing: 0.04em; margin-bottom: 2px; }
  .scaffold-starter { font-style: italic; color: #444; font-size: 10pt; margin-bottom: 4px; background: #f5f5f5; padding: 4px 8px; border-left: 3px solid #bbb; }

  /* T-chart */
  .t-chart-word-bank { margin-bottom: 8px; }
  .t-chart-word-bank-label { font-size: 9pt; font-weight: bold; color: #555; margin-bottom: 4px; }
  table.t-chart { width: 100%; border-collapse: collapse; font-size: 10pt; }
  table.t-chart th { background: #2c2c2c; color: white; padding: 6px 10px; font-size: 11pt; text-align: center; width: 50%; }
  table.t-chart th:first-child { border-right: 2px solid white; }
  table.t-chart td { border: 1px solid #aaa; height: 24px; padding: 0 6px; vertical-align: middle; }
  table.t-chart td:first-child { border-right: 2px solid #555; }
</style>"""

_HTML_WRAPPER = """\
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>{title}</title>
  {css}
</head>
<body>
{body}
</body>
</html>"""


# ── Internal helpers ───────────────────────────────────────────────────────


def _h(text: Any) -> str:
    return _html.escape(str(text))


def _name_date() -> str:
    return (
        '<div class="name-date-row">'
        "<span>Name:&nbsp;&nbsp;_______________________________________</span>"
        '<span class="short">Date:&nbsp;&nbsp;_______________</span>'
        "</div>"
    )


def _answer_lines(n: int) -> str:
    lines = "".join('<div class="answer-line"></div>' for _ in range(n))
    return f'<div class="answer-lines">{lines}</div>'


def _passage_html(text: str) -> str:
    paras = [p.strip() for p in text.split("\n\n") if p.strip()]
    inner = "".join(f"<p>{_h(p)}</p>" for p in paras)
    return f'<div class="passage">{inner}</div>'


def _day_header(day_label: str, title: str, primary: str) -> str:
    return (
        f'<div class="day-header" style="background:{primary};">'
        f'<div class="day-header-label">{_h(day_label)}</div>'
        f'<div class="day-header-title">{_h(title)}</div>'
        f"</div>"
    )


def _title_block(title: str, primary: str) -> str:
    return (
        f'<div class="ws-title" style="color:{primary};border-bottom-color:{primary};">'
        f"{_h(title)}</div>"
    )


# ── Worksheet render functions ─────────────────────────────────────────────


def _render_reading(data: dict, primary: str, light: str) -> str:
    title = data.get("title", "Reading Comprehension")
    day_label = data.get("day_label", "")
    questions = data.get("questions", [])
    vocab = data.get("vocabulary", [])

    dh = _day_header(day_label, title, primary) if day_label else ""

    q_html = ""
    for i, q in enumerate(questions, 1):
        lines = q.get("response_lines", 2) if isinstance(q, dict) else 2
        prompt = q.get("prompt", "") if isinstance(q, dict) else str(q)
        q_html += (
            f'<div class="question">'
            f'<div class="question-prompt">{i}. {_h(prompt)}</div>'
            f"{_answer_lines(lines)}"
            f"</div>"
        )

    v_html = ""
    if vocab:
        items_html = ""
        for v in vocab:
            term = v.get("term", "") if isinstance(v, dict) else str(v)
            defn = v.get("definition", "") if isinstance(v, dict) else ""
            items_html += (
                f'<div class="vocab-item">'
                f'<span class="vocab-term">{_h(term)}:</span> '
                f'<span class="vocab-def">{_h(defn)}</span>'
                f"</div>"
            )
        v_html = (
            f'<div class="vocab-section"><h3>Words to Know</h3>'
            f'<div class="vocab-grid">{items_html}</div></div>'
        )

    qs_html = ""
    if questions:
        qs_html = f'<div class="questions-section">' f"<h3>Questions</h3>{q_html}</div>"

    instructions = _h(data.get("instructions", "Read the passage, then answer the questions."))
    passage_title = _h(data.get("passage_title", ""))

    return f"""
{dh}
{_title_block(title, primary)}
{_name_date()}
<div class="ws-instructions">{instructions}</div>
<div class="passage-title">{passage_title}</div>
{_passage_html(data.get("passage", ""))}
{qs_html}
{v_html}
"""


def _render_feature_matrix(data: dict, primary: str, light: str) -> str:
    title = data.get("title", "Feature Matrix")
    day_label = data.get("day_label", "")
    items = data.get("items", [])
    properties = data.get("properties", [])

    dh = _day_header(day_label, title, primary) if day_label else ""

    headers = f'<th class="fm-item-col" style="background:{primary};">Name</th>'
    for prop in properties:
        headers += f'<th style="background:{primary};">{_h(prop)}</th>'

    rows = ""
    for item in items:
        cells = f'<td class="fm-item-cell">{_h(item)}</td>'
        for _ in properties:
            cells += '<td class="fm-check-cell">&#9744;</td>'
        rows += f"<tr>{cells}</tr>"

    instructions = _h(data.get("instructions", "Check the box if the statement is true."))

    return f"""
{dh}
{_title_block(title, primary)}
{_name_date()}
<div class="ws-instructions">{instructions}</div>
<div class="feature-matrix-wrapper">
<table class="feature-matrix">
  <thead><tr>{headers}</tr></thead>
  <tbody>{rows}</tbody>
</table>
</div>
"""


def _render_tree_map(data: dict, primary: str, light: str) -> str:
    title = data.get("title", "Tree Map")
    day_label = data.get("day_label", "")
    root_label = data.get("root_label", "")
    branches = data.get("branches", [])
    cols = data.get("columns", min(len(branches), 4) or 4)
    word_bank = data.get("word_bank", [])

    dh = _day_header(day_label, title, primary) if day_label else ""

    branches_html = ""
    for branch in branches:
        name = (
            branch.get("name", branch.get("label", "")) if isinstance(branch, dict) else str(branch)
        )
        prefilled = branch.get("prefilled", []) if isinstance(branch, dict) else []
        # Support both blank_count and slot_count field names
        blank_count = (
            branch.get("blank_count", branch.get("slot_count", 1))
            if isinstance(branch, dict)
            else 1
        )

        slots_html = ""
        for item in prefilled:
            slots_html += f'<div class="tm-slot prefilled">{_h(item)}</div>'
        for _ in range(blank_count):
            slots_html += '<div class="tm-slot blank">_______________</div>'

        branches_html += (
            f'<div class="tm-branch" style="border-color:{primary};">'
            f'<div class="tm-branch-name" style="color:{primary};">{_h(name)}</div>'
            f"{slots_html}"
            f"</div>"
        )

    wb_html = ""
    if word_bank:
        tiles = "".join(f'<span class="ctm-wb-tile">{_h(w)}</span>' for w in word_bank)
        wb_html = (
            f'<div class="ctm-word-bank" style="margin-top:10px;">'
            f'<div class="ctm-wb-label">Word Bank — write each word in the correct branch above:</div>'
            f'<div class="ctm-wb-tiles">{tiles}</div>'
            f"</div>"
        )

    instructions = _h(data.get("instructions", "Fill in the tree map."))

    return f"""
{dh}
{_title_block(title, primary)}
{_name_date()}
<div class="ws-instructions">{instructions}</div>
<div class="tm-root-row">
  <div class="tm-root" style="border-color:{primary};color:{primary};">{_h(root_label)}</div>
</div>
<div class="tm-branches-grid" style="grid-template-columns:repeat({cols},1fr);">
{branches_html}
</div>
{wb_html}
"""


def _render_odd_one_out(data: dict, primary: str, light: str) -> str:
    title = data.get("title", "Odd One Out")
    day_label = data.get("day_label", "")
    rows = data.get("rows", [])

    dh = _day_header(day_label, title, primary) if day_label else ""

    rows_html = ""
    for i, row in enumerate(rows, 1):
        items = row.get("items", []) if isinstance(row, dict) else list(row)
        items_html = "".join(
            f'<div class="oo-item" style="border-color:{primary};">{_h(it)}</div>' for it in items
        )
        reasoning_lines = row.get("reasoning_lines", 1) if isinstance(row, dict) else 1
        rows_html += (
            f'<div class="oo-group">'
            f'<div class="oo-number">Row {i}</div>'
            f'<div class="oo-items-row">{items_html}</div>'
            f'<div class="oo-answer-row">Circle the one that does NOT belong.&nbsp; Why?'
            f"{_answer_lines(reasoning_lines)}"
            f"</div></div>"
        )

    instructions = _h(
        data.get("instructions", "Circle the one that does NOT belong. Tell a grown-up why!")
    )

    return f"""
{dh}
{_title_block(title, primary)}
{_name_date()}
<div class="ws-instructions">{instructions}</div>
{rows_html}
"""


def _render_matching(data: dict, primary: str, light: str) -> str:
    title = data.get("title", "Matching")
    day_label = data.get("day_label", "")
    left_items = data.get("left_items", [])
    right_items = data.get("right_items", [])

    dh = _day_header(day_label, title, primary) if day_label else ""

    rows_html = ""
    for i, (left, right) in enumerate(zip(left_items, right_items, strict=False), 1):
        ltext = left if isinstance(left, str) else left.get("text", "")
        rtext = right if isinstance(right, str) else right.get("text", "")
        rows_html += (
            f'<div class="matching-row">'
            f'<div class="matching-number">{i}.</div>'
            f'<div class="matching-left">{_h(ltext)}</div>'
            f'<div class="matching-line"></div>'
            f'<div class="matching-right">{_h(rtext)}</div>'
            f"</div>"
        )

    instructions = _h(
        data.get(
            "instructions", "Draw a line from each item on the left to its match on the right."
        )
    )

    return f"""
{dh}
{_title_block(title, primary)}
{_name_date()}
<div class="ws-instructions">{instructions}</div>
{rows_html}
"""


def _render_cause_effect(data: dict, primary: str, light: str) -> str:
    title = data.get("title", "Cause and Effect")
    day_label = data.get("day_label", "")
    pairs = data.get("pairs", [])

    dh = _day_header(day_label, title, primary) if day_label else ""

    pairs_html = ""
    for pair in pairs:
        cause = _h(pair.get("cause", ""))
        effect = pair.get("effect", "")
        effect_lines = pair.get("effect_lines", 2)

        cause_html = f'<div class="ce-label">Cause</div>' f'<div class="ce-text">{cause}</div>'
        if effect:
            effect_body = (
                f'<div class="ce-label">Effect</div>' f'<div class="ce-text">{_h(effect)}</div>'
            )
        else:
            effect_body = '<div class="ce-label">Effect (write your answer)</div>' + _answer_lines(
                effect_lines
            )

        pairs_html += (
            f'<div class="cause-effect-pair">'
            f'<div class="ce-cause">{cause_html}</div>'
            f'<div class="ce-arrow">&#8594;</div>'
            f'<div class="ce-effect">{effect_body}</div>'
            f"</div>"
        )

    instructions = _h(data.get("instructions", "Read each cause. Write or identify the effect."))

    return f"""
{dh}
{_title_block(title, primary)}
{_name_date()}
<div class="ws-instructions">{instructions}</div>
{pairs_html}
"""


def _render_frayer_model(data: dict, primary: str, light: str) -> str:
    title = data.get("title", "Frayer Model")
    day_label = data.get("day_label", "")
    entries = data.get("entries", [])
    quad_labels = data.get(
        "quadrant_labels", ["Definition", "Characteristics", "Examples", "Non-Examples"]
    )

    dh = _day_header(day_label, title, primary) if day_label else ""

    entries_html = ""
    for entry in entries:
        word = _h(entry.get("word", ""))
        quads = entry.get("quadrants", {})

        cells_html = ""
        for label in quad_labels:
            content = quads.get(label, "")
            if isinstance(content, list):
                content_html = "<ul style='padding-left:14px;margin:0;'>"
                for item in content:
                    content_html += f"<li>{_h(item)}</li>"
                content_html += "</ul>"
            elif content:
                content_html = _h(content)
            else:
                content_html = _answer_lines(3)

            cells_html += (
                f'<div class="frayer-cell">'
                f'<div class="frayer-cell-label">{_h(label)}</div>'
                f"{content_html}"
                f"</div>"
            )

        entries_html += (
            f'<div class="frayer-entry">'
            f'<div class="frayer-word-box" style="background:{light};border-color:{primary};">{word}</div>'
            f'<div class="frayer-grid" style="border-color:{primary};">{cells_html}</div>'
            f"</div>"
        )

    instructions = _h(data.get("instructions", "Fill in each section of the Frayer Model."))

    return f"""
{dh}
{_title_block(title, primary)}
{_name_date()}
<div class="ws-instructions">{instructions}</div>
{entries_html}
"""


def _render_word_sort(data: dict, primary: str, light: str) -> str:
    title = data.get("title", "Word Sort")
    day_label = data.get("day_label", "")
    categories = data.get("categories", [])
    tiles = data.get("tiles", [])
    col_count = data.get("columns", len(categories) or 1)

    dh = _day_header(day_label, title, primary) if day_label else ""

    cats_html = ""
    for cat in categories:
        label = cat.get("label", cat) if isinstance(cat, dict) else str(cat)
        cats_html += (
            f'<div class="ws-category" style="border-color:{primary};">'
            f'<div class="ws-category-label" style="color:{primary};">{_h(label)}</div>'
            f"</div>"
        )

    tiles_html = "".join(
        f'<span class="ws-tile">{_h(t if isinstance(t, str) else t.get("word", ""))}</span>'
        for t in tiles
    )

    instructions = _h(data.get("instructions", "Cut or write each word into the correct category."))
    col_style = f"grid-template-columns:repeat({col_count},1fr);"

    return f"""
{dh}
{_title_block(title, primary)}
{_name_date()}
<div class="ws-instructions">{instructions}</div>
<div class="word-sort-categories" style="{col_style}">
{cats_html}
</div>
<div class="ws-tile-bank">
  <div class="ws-tile-bank-label">Word Bank — write each word in the correct box above:</div>
  <div class="ws-tiles">{tiles_html}</div>
</div>
"""


def _render_writing_scaffold(data: dict, primary: str, light: str) -> str:
    title = data.get("title", "Writing Scaffold")
    day_label = data.get("day_label", "")
    topic = data.get("topic", "")
    sections = data.get("sections", [])

    dh = _day_header(day_label, title, primary) if day_label else ""

    topic_html = ""
    if topic:
        topic_html = f'<div style="font-size:11pt;font-weight:bold;margin-bottom:8px;color:{primary};">Topic: {_h(topic)}</div>'

    secs_html = ""
    for sec in sections:
        label = sec.get("label", "") if isinstance(sec, dict) else str(sec)
        starter = sec.get("starter", "") if isinstance(sec, dict) else ""
        lines = sec.get("lines", 3) if isinstance(sec, dict) else 3

        starter_html = ""
        if starter:
            starter_html = f'<div class="scaffold-starter">{_h(starter)}</div>'

        secs_html += (
            f'<div class="scaffold-section">'
            f'<div class="scaffold-part-label" style="color:{primary};">{_h(label)}</div>'
            f"{starter_html}"
            f"{_answer_lines(lines)}"
            f"</div>"
        )

    instructions = _h(data.get("instructions", "Use the sections below to organize your writing."))

    return f"""
{dh}
{_title_block(title, primary)}
{_name_date()}
<div class="ws-instructions">{instructions}</div>
{topic_html}
{secs_html}
"""


def _render_t_chart(data: dict, primary: str, light: str) -> str:
    title = data.get("title", "T-Chart")
    day_label = data.get("day_label", "")
    columns = data.get("columns", ["Column A", "Column B"])
    row_count = data.get("row_count", 8)
    word_bank = data.get("word_bank", [])

    dh = _day_header(day_label, title, primary) if day_label else ""

    wb_html = ""
    if word_bank:
        tiles = "".join(f'<span class="ws-tile">{_h(w)}</span>' for w in word_bank)
        wb_html = (
            f'<div class="t-chart-word-bank">'
            f'<div class="t-chart-word-bank-label">Word Bank:</div>'
            f'<div class="ws-tiles" style="margin-top:4px;">{tiles}</div>'
            f"</div>"
        )

    col_headers = "".join(f'<th style="background:{primary};">{_h(c)}</th>' for c in columns)
    rows = "".join(
        "<tr>" + "".join("<td></td>" for _ in columns) + "</tr>" for _ in range(row_count)
    )

    instructions = _h(data.get("instructions", "Fill in the T-Chart."))

    return f"""
{dh}
{_title_block(title, primary)}
{_name_date()}
<div class="ws-instructions">{instructions}</div>
{wb_html}
<table class="t-chart">
  <thead><tr>{col_headers}</tr></thead>
  <tbody>{rows}</tbody>
</table>
"""


# ── Dispatch table ─────────────────────────────────────────────────────────

_RENDERERS = {
    "readingWorksheet": _render_reading,
    "featureMatrixWorksheet": _render_feature_matrix,
    "treeMapWorksheet": _render_tree_map,
    "oddOneOutWorksheet": _render_odd_one_out,
    "matchingWorksheet": _render_matching,
    "causeEffectWorksheet": _render_cause_effect,
    "frayerModelWorksheet": _render_frayer_model,
    "wordSortWorksheet": _render_word_sort,
    "writingScaffoldWorksheet": _render_writing_scaffold,
    "tChartWorksheet": _render_t_chart,
}

#: Worksheet kinds that have an HTML renderer.
HTML_SUPPORTED_KINDS: frozenset[str] = frozenset(_RENDERERS)


def render_worksheet_html(kind: str, data: dict, day_label: str = "") -> str | None:
    """Return an HTML fragment for *kind* populated with *data*, or None if unsupported."""
    renderer = _RENDERERS.get(kind)
    if renderer is None:
        return None
    primary, light = get_day_palette(day_label)
    # Inject day_label so renderers can include the header
    enriched = {**data, "day_label": day_label}
    return renderer(enriched, primary, light)


def build_print_packet_html(
    pages: list[tuple[str, str]],
    packet_title: str = "Weekly Worksheets",
) -> str:
    """
    Assemble a full printable HTML document from a list of (day_label, html_fragment) tuples.

    Opens the browser print dialog automatically when loaded.
    """
    page_divs = []
    for i, (_day_label, fragment) in enumerate(pages):
        is_last = i == len(pages) - 1
        cls = "page last-page" if is_last else "page"
        page_divs.append(f'<div class="{cls}">{fragment}</div>')

    body = "\n".join(page_divs)
    # Auto-trigger print dialog; close tab after printing if opened as popup
    body += '\n<script>window.addEventListener("load", () => window.print());</script>'

    return _HTML_WRAPPER.format(title=_h(packet_title), css=_CSS, body=body)
