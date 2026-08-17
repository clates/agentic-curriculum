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
import os
import sys
from typing import Any

try:
    from .worksheet_layouts import get_layout
except ImportError:  # Fallback when executed outside package context
    CURRENT_DIR = os.path.dirname(__file__)
    if CURRENT_DIR not in sys.path:
        sys.path.insert(0, CURRENT_DIR)
    from worksheet_layouts import get_layout  # type: ignore

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
    * { -webkit-print-color-adjust: exact; print-color-adjust: exact; }
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

  /* Bar graph */
  .bg-wrap { margin-top: 8px; }
  .bg-flex { display: flex; align-items: stretch; }
  .bg-ytitle {
    flex: 0 0 0.24in; writing-mode: vertical-rl; transform: rotate(180deg);
    text-align: center; font-size: 8.5pt; font-weight: bold; color: #444;
  }
  .bg-ticks { flex: 0 0 0.48in; position: relative; }
  .bg-tick { position: absolute; right: 5px; transform: translateY(-50%); font-size: 8.5pt; color: #555; }
  .bg-plot { flex: 1; position: relative; border-left: 2px solid #333; border-bottom: 2px solid #333; }
  .bg-gridline { position: absolute; left: 0; right: 0; border-top: 1px solid #dcdcdc; }
  .bg-lanes { position: absolute; inset: 0; display: flex; }
  .bg-lane { flex: 1; border-right: 1px solid #ededed; display: flex; align-items: flex-end; justify-content: center; }
  .bg-lane:last-child { border-right: none; }
  .bg-bar { width: 58%; border: 1.5px solid #333; border-bottom: none; position: relative; }
  .bg-bar-val { position: absolute; top: -15px; left: -20px; right: -20px; text-align: center; font-size: 8.5pt; font-weight: bold; color: #222; }
  .bg-xrow { display: flex; }
  .bg-xspacer { flex: 0 0 0.72in; }
  .bg-xlabels { flex: 1; display: flex; }
  .bg-xlabel { flex: 1; text-align: center; font-size: 9pt; font-weight: bold; padding-top: 4px; line-height: 1.15; }
  .bg-xtitle { flex: 1; text-align: center; font-size: 8.5pt; font-weight: bold; color: #444; margin-top: 2px; }

  /* Pictograph */
  .pg-key {
    display: inline-block; font-size: 10pt; font-weight: bold;
    padding: 4px 10px; border-radius: 4px; margin: 4px 0 10px;
  }
  .pg-row { display: flex; align-items: center; border-bottom: 1px solid #ddd; padding: 6px 0; min-height: 34px; }
  .pg-label { flex: 0 0 1.7in; font-weight: bold; font-size: 10pt; padding-right: 8px; }
  .pg-symbols { flex: 1; display: flex; flex-wrap: wrap; align-items: center; gap: 4px; font-size: 15pt; line-height: 1; }
  .pg-cell { width: 22px; height: 22px; border: 1px dashed #bbb; border-radius: 3px; }

  /* Graph interpretation questions (shared by bar graph + pictograph) */
  .graph-questions { margin-top: 12px; }
  .graph-questions h3 {
    font-size: 10pt; font-weight: bold;
    border-bottom: 1px solid #bbb; padding-bottom: 2px; margin-bottom: 6px;
  }
</style>"""

# ── Content-block CSS ──────────────────────────────────────────────────────
# Blocks are layout-agnostic: they render the same in `classic` and `journal`.
# Appended to every packet; rules are namespaced so nothing here can affect the
# historical worksheet types above.

_BLOCK_CSS = """\
<style>
  /* Story panel */
  .fx-story {
    position: relative; border-radius: 5px; padding: 9px 12px 9px 34px;
    font-size: 10pt; line-height: 1.6; margin-bottom: 10px;
    background: #fdfbf6; border: 1.5px solid #e6dcc8; border-left-width: 5px;
    break-inside: avoid;
  }
  .fx-story::before {
    content: "\\1F43E"; position: absolute; left: 9px; top: 8px;
    font-size: 13pt; opacity: 0.65;
  }
  .fx-story .fx-who {
    font-weight: bold; font-size: 8.5pt; text-transform: uppercase;
    letter-spacing: 0.09em; color: #8a7a55; display: block; margin-bottom: 3px;
  }
  .fx-story p { margin-bottom: 6px; }
  .fx-story p:last-child { margin-bottom: 0; }

  /* Hands-on card */
  .fx-doing {
    border: 2px dashed #b9b9b9; border-radius: 6px;
    padding: 8px 11px 8px 34px; position: relative; background: #fafafa;
    font-size: 9.5pt; margin-bottom: 10px; break-inside: avoid;
  }
  .fx-doing::before {
    content: "\\270B"; position: absolute; left: 10px; top: 7px;
    font-size: 13pt; opacity: 0.6;
  }
  .fx-doing-label {
    font-size: 8pt; font-weight: bold; text-transform: uppercase;
    letter-spacing: 0.09em; color: #666; display: block; margin-bottom: 2px;
  }

  /* Note / teacher aside */
  .fx-note {
    border-left: 4px solid #cbd5e1; background: #f8fafc;
    padding: 6px 10px; font-size: 9pt; color: #475569;
    margin-bottom: 9px; border-radius: 0 4px 4px 0;
  }

  /* Numbered tasks */
  .fx-task { display: flex; gap: 9px; margin-bottom: 11px; break-inside: avoid; }
  .fx-badge {
    flex: 0 0 0.26in; height: 0.26in; border-radius: 50%; color: #fff;
    font-size: 9.5pt; font-weight: bold; display: flex;
    align-items: center; justify-content: center; margin-top: 1px;
  }
  .fx-task-body { flex: 1; min-width: 0; }
  .fx-task-prompt { font-size: 10pt; font-weight: bold; margin-bottom: 4px; line-height: 1.35; }
  .fx-task-detail { font-size: 9.5pt; color: #444; margin-bottom: 4px; }

  /* Warm-up / speed math */
  .fx-drill { margin-bottom: 11px; break-inside: avoid; }
  .fx-drill-head {
    display: flex; align-items: baseline; gap: 8px;
    border-bottom: 1.5px solid; padding-bottom: 2px; margin-bottom: 6px;
  }
  .fx-drill-title { font-size: 11pt; font-weight: bold; }
  .fx-drill-inst { font-size: 8.5pt; color: #666; font-style: italic; flex: 1; }
  .fx-timer {
    border: 1.5px solid #999; border-radius: 4px; padding: 1px 8px;
    font-size: 8pt; color: #555; white-space: nowrap;
  }
  .fx-drill-grid { display: grid; gap: 7px 12px; }
  .fx-drill-item {
    display: flex; align-items: baseline; gap: 5px;
    font-size: 10.5pt; padding: 3px 0;
  }
  .fx-drill-num { font-size: 8pt; color: #999; flex: 0 0 auto; min-width: 0.15in; }
  .fx-drill-q { flex: 0 1 auto; white-space: nowrap; }
  .fx-drill-blank {
    flex: 1 1 0.45in; min-width: 0.35in; border-bottom: 1.5px solid #777; height: 0.19in;
  }
  .fx-drill-box {
    flex: 0 0 0.42in; height: 0.3in; border: 1.5px solid #777; border-radius: 3px;
  }

  /* Comparison pairs */
  .fx-cmp-grid { display: grid; gap: 10px 18px; margin-bottom: 10px; }
  .fx-cmp {
    display: flex; align-items: center; gap: 7px;
    border-bottom: 1px solid #e8e8e8; padding-bottom: 5px;
  }
  .fx-cmp-side {
    flex: 1; text-align: center; font-size: 11.5pt; font-weight: bold;
  }
  .fx-cmp-box {
    flex: 0 0 0.36in; height: 0.28in; border: 1.5px solid #777; border-radius: 3px;
  }

  /* Fraction strips */
  .fx-strips { margin-bottom: 10px; }
  .fx-strip-row { display: flex; align-items: center; gap: 8px; margin-bottom: 0.09in; }
  .fx-strip-label { font-size: 8.5pt; color: #555; flex: 0 0 0.85in; text-align: right; }
  .fx-strip { display: flex; border: 1.5px solid #111; break-inside: avoid; }
  .fx-strip > span {
    flex: 1 1 0; border-right: 1px dashed #444;
    display: flex; align-items: center; justify-content: center;
    font-size: 8.5pt; font-weight: bold;
  }
  .fx-strip > span:last-child { border-right: none; }

  /* Fraction circles */
  .fx-circles { display: flex; flex-wrap: wrap; gap: 0.26in; margin-bottom: 8px; }
  .fx-circle-cell { text-align: center; }
  .fx-circle { border-radius: 50%; border: 1.75px solid #111; }
  .fx-caption { font-size: 8.5pt; color: #555; margin-top: 3px; }

  /* Area-model grids */
  .fx-areas { display: flex; flex-wrap: wrap; gap: 0.18in; margin-bottom: 8px; }
  .fx-area { display: grid; border: 1.75px solid #111; }
  .fx-area div { border: 0.5px solid #777; }

  /* Number line */
  .fx-nl-wrap { margin-bottom: 12px; break-inside: avoid; }
  .fx-nl-prompt { font-size: 9.5pt; margin-bottom: 14px; }
  .fx-nl { position: relative; border-top: 2px solid #111; height: 0.42in; display: flex; }
  .fx-nl-tick { flex: 1 1 0; position: relative; }
  .fx-nl-tick::before {
    content: ""; position: absolute; left: 0; top: 0;
    width: 1.5px; height: 0.15in; background: #111;
  }
  .fx-nl-tick:last-child::after {
    content: ""; position: absolute; right: 0; top: 0;
    width: 1.5px; height: 0.15in; background: #111;
  }
  .fx-nl-lab {
    position: absolute; top: 0.17in; left: 0; transform: translateX(-50%);
    font-size: 8.5pt; white-space: nowrap;
  }
  .fx-nl-lab.end { left: auto; right: 0; transform: translateX(50%); }

  /* Heart bar */
  .fx-hearts { display: flex; gap: 0.04in; margin-bottom: 6px; }
  .fx-heart { flex: 1 1 0; border: 1.5px solid #7f1d1d; display: flex; }
  .fx-heart span { flex: 1 1 0; border-right: 1px dotted #7f1d1d; }
  .fx-heart span:last-child { border-right: none; }
  .fx-heart span.on { background: #fca5a5; }

  /* Colour key */
  .fx-key { font-size: 9.5pt; line-height: 1.85; }
  .fx-sw {
    display: inline-block; width: 11px; height: 11px; border: 1px solid #444;
    vertical-align: -1px; margin-right: 5px;
  }
  .fx-row { display: flex; gap: 0.3in; align-items: center; margin: 6px 0 2px; flex-wrap: wrap; }

  /* Calibration ruler */
  .fx-ruler { height: 0.42in; border: 1.5px solid #111; display: flex; margin-bottom: 3px; }
  .fx-ruler div {
    flex: 1 1 0; border-right: 1px solid #111; font-size: 7.5pt;
    display: flex; align-items: flex-end; justify-content: flex-end; padding-right: 2px;
  }
  .fx-ruler div:last-child { border-right: none; }

  /* Cut-out cards */
  .fx-cards { display: grid; gap: 6px; margin-bottom: 8px; }
  .fx-card {
    border: 1.5px dashed #666; border-radius: 4px; padding: 8px 4px;
    text-align: center; font-size: 12pt; font-weight: bold; background: #fff;
  }

  /* Rich text sections (teacher guides, answer keys) */
  .fx-rt { margin-bottom: 11px; break-inside: avoid; }
  .fx-rt-head {
    font-size: 11pt; font-weight: bold; border-bottom: 1.5px solid;
    padding-bottom: 2px; margin-bottom: 5px;
  }
  .fx-rt p { font-size: 9.5pt; line-height: 1.55; margin-bottom: 5px; }
  .fx-rt ul { margin: 0 0 5px 18px; }
  .fx-rt li { font-size: 9.5pt; line-height: 1.5; margin-bottom: 2px; }
  .fx-rt-table { border-collapse: collapse; width: 100%; margin-bottom: 4px; }
  .fx-rt-table th {
    text-align: left; vertical-align: top; font-size: 9pt; font-weight: bold;
    padding: 3px 8px 3px 0; width: 1.5in; border-bottom: 1px solid #e5e5e5;
  }
  .fx-rt-table td {
    font-size: 9.5pt; padding: 3px 0; border-bottom: 1px solid #e5e5e5;
  }

  /* Cut line */
  .fx-cutline { border-top: 2px dashed #aaa; margin: 12px 0; position: relative; height: 0; }
  .fx-cutline::before {
    content: "\\2702"; position: absolute; left: 0; top: -9px;
    background: #fff; padding-right: 5px; font-size: 11pt; color: #999;
  }
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


def _graph_questions(questions: list) -> str:
    """Render a numbered question block (with answer lines) below a graph."""
    if not questions:
        return ""
    q_html = ""
    for i, q in enumerate(questions, 1):
        lines = q.get("response_lines", 1) if isinstance(q, dict) else 1
        prompt = q.get("prompt", "") if isinstance(q, dict) else str(q)
        q_html += (
            f'<div class="question">'
            f'<div class="question-prompt">{i}. {_h(prompt)}</div>'
            f"{_answer_lines(lines)}"
            f"</div>"
        )
    return f'<div class="graph-questions"><h3>Read the Graph</h3>{q_html}</div>'


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


def _render_bar_graph(data: dict, primary: str, light: str) -> str:
    """Render a bar graph.

    Two modes, chosen by whether ``values`` is supplied:
      * ``values`` omitted / None  -> a blank grid the student fills in (colours the bars).
      * ``values`` given           -> pre-filled coloured bars for the student to *read*.

    Data keys: title, instructions, categories (list[str]), values (list[int|float]|None),
    y_max, y_step, x_label, y_label, height_in, show_values (bool), questions (list).
    """
    title = data.get("title", "Bar Graph")
    day_label = data.get("day_label", "")
    categories = data.get("categories", [])
    values = data.get("values")
    y_max = data.get("y_max", 10) or 10
    y_step = data.get("y_step", 1) or 1
    x_label = data.get("x_label", "")
    y_label = data.get("y_label", "")
    height_in = data.get("height_in", 2.5)
    show_values = data.get("show_values", False)
    questions = data.get("questions", [])

    dh = _day_header(day_label, title, primary) if day_label else ""

    steps = max(1, round(y_max / y_step))

    # Horizontal gridlines + y-axis tick labels, aligned by percentage from the top.
    gridlines_html = ""
    ticks_html = ""
    for i in range(steps + 1):
        value = round(i * y_step, 4)
        value_label = int(value) if float(value).is_integer() else value
        top_pct = (1 - (value / y_max)) * 100
        gridlines_html += f'<div class="bg-gridline" style="top:{top_pct:.4f}%;"></div>'
        ticks_html += f'<div class="bg-tick" style="top:{top_pct:.4f}%;">{value_label}</div>'

    # Bars, one lane per category.
    lanes_html = ""
    for idx in range(len(categories)):
        bar = ""
        if values is not None and idx < len(values) and values[idx] is not None:
            v = values[idx]
            h_pct = max(0.0, min(100.0, (v / y_max) * 100))
            v_disp = int(v) if float(v).is_integer() else v
            val_lbl = f'<span class="bg-bar-val">{_h(v_disp)}</span>' if show_values else ""
            bar = (
                f'<div class="bg-bar" style="height:{h_pct:.4f}%;'
                f'background:{light};border-color:{primary};">{val_lbl}</div>'
            )
        lanes_html += f'<div class="bg-lane">{bar}</div>'

    xlabels_html = "".join(f'<div class="bg-xlabel">{_h(c)}</div>' for c in categories)

    ytitle_html = f'<div class="bg-ytitle">{_h(y_label)}</div>'
    xtitle_html = (
        f'<div class="bg-xrow"><div class="bg-xspacer"></div>'
        f'<div class="bg-xtitle">{_h(x_label)}</div></div>'
        if x_label
        else ""
    )

    default_instr = (
        "Read the bars to answer the questions."
        if values is not None
        else "Colour in a bar for each group to show how many you counted."
    )
    instructions = _h(data.get("instructions", default_instr))

    return f"""
{dh}
{_title_block(title, primary)}
{_name_date()}
<div class="ws-instructions">{instructions}</div>
<div class="bg-wrap">
  <div class="bg-flex">
    {ytitle_html}
    <div class="bg-ticks">{ticks_html}</div>
    <div class="bg-plot" style="height:{height_in}in;">
      {gridlines_html}
      <div class="bg-lanes">{lanes_html}</div>
    </div>
  </div>
  <div class="bg-xrow"><div class="bg-xspacer"></div><div class="bg-xlabels">{xlabels_html}</div></div>
  {xtitle_html}
</div>
{_graph_questions(questions)}
"""


def _render_pictograph(data: dict, primary: str, light: str) -> str:
    """Render a pictograph (picture graph).

    Two modes per row, chosen by whether ``symbols`` is supplied:
      * blank -> a strip of empty cells for the student to draw symbols in.
      * given -> that many symbol icons drawn for the student to *read*.

    Data keys: title, instructions, symbol (emoji/char), per_symbol (int), unit_label,
    rows (list of {label, symbols}), blank (bool, force all rows blank), max_symbols (int
    width of blank strips), questions (list).
    """
    title = data.get("title", "Pictograph")
    day_label = data.get("day_label", "")
    symbol = data.get("symbol", "⭐")
    per_symbol = data.get("per_symbol", 1)
    unit_label = data.get("unit_label", "")
    rows = data.get("rows", [])
    blank = data.get("blank", False)
    max_symbols = data.get("max_symbols", 10)
    questions = data.get("questions", [])

    dh = _day_header(day_label, title, primary) if day_label else ""

    per_disp = int(per_symbol) if float(per_symbol).is_integer() else per_symbol
    key_text = f"Key:  each {symbol} = {per_disp}"
    if unit_label:
        key_text += f" {unit_label}"
    key_html = (
        f'<div class="pg-key" style="background:{light};color:{primary};">{_h(key_text)}</div>'
    )

    rows_html = ""
    for row in rows:
        label = row.get("label", "") if isinstance(row, dict) else str(row)
        count = row.get("symbols") if isinstance(row, dict) else None
        if blank or count is None:
            cells = "".join('<span class="pg-cell"></span>' for _ in range(max_symbols))
            symbols_html = cells
        else:
            symbols_html = "".join(_h(symbol) for _ in range(int(count)))
        rows_html += (
            f'<div class="pg-row">'
            f'<div class="pg-label">{_h(label)}</div>'
            f'<div class="pg-symbols">{symbols_html}</div>'
            f"</div>"
        )

    default_instr = (
        "Draw the right number of pictures in each row to match the key."
        if blank
        else "Count the pictures in each row. Remember the key!"
    )
    instructions = _h(data.get("instructions", default_instr))

    return f"""
{dh}
{_title_block(title, primary)}
{_name_date()}
<div class="ws-instructions">{instructions}</div>
{key_html}
<div class="pg-table">{rows_html}</div>
{_graph_questions(questions)}
"""


# ── Content blocks (layout-agnostic) ───────────────────────────────────────
#
# These are composable page fragments rather than whole worksheets: a journal
# page is assembled from several of them.  They carry no day header of their
# own — the layout supplies that.


def _render_story_panel(data: dict, primary: str, light: str) -> str:
    """Narrative panel — the recurring-character beat that opens each day."""
    who = data.get("who", "")
    text = data.get("text", "")
    paras = [p.strip() for p in text.split("\n\n") if p.strip()]
    who_html = f'<span class="fx-who">{_h(who)}</span>' if who else ""
    body = "".join(f"<p>{_h(p)}</p>" for p in paras)
    return f'<div class="fx-story">{who_html}{body}</div>'


def _render_doing_card(data: dict, primary: str, light: str) -> str:
    """Hands-on / outdoor activity, styled so it reads as not-desk-work."""
    label = data.get("label", "Go and do")
    text = data.get("text", "")
    return (
        f'<div class="fx-doing"><span class="fx-doing-label">{_h(label)}</span>' f"{_h(text)}</div>"
    )


def _render_note_box(data: dict, primary: str, light: str) -> str:
    return f'<div class="fx-note">{_h(data.get("text", ""))}</div>'


def _render_cut_line(data: dict, primary: str, light: str) -> str:
    return '<div class="fx-cutline"></div>'


def _render_task_list(data: dict, primary: str, light: str) -> str:
    """Numbered tasks. Each task may embed a figure block via ``figure``."""
    tasks = data.get("tasks", [])
    start = int(data.get("start_number", 1))
    out = []
    for i, task in enumerate(tasks, start):
        prompt = task.get("prompt", "")
        detail = task.get("detail", "")
        detail_html = f'<div class="fx-task-detail">{_h(detail)}</div>' if detail else ""

        fig_html = ""
        figure = task.get("figure")
        if figure:
            fig_html = _render_block(figure.get("kind", ""), figure.get("data", {}), primary, light)

        answer = ""
        if task.get("response_lines"):
            answer = _answer_lines(int(task["response_lines"]))

        out.append(
            f'<div class="fx-task">'
            f'<div class="fx-badge" style="background:{primary};">{i}</div>'
            f'<div class="fx-task-body">'
            f'<div class="fx-task-prompt">{_h(prompt)}</div>'
            f"{detail_html}{fig_html}{answer}"
            f"</div></div>"
        )
    return "".join(out)


def _render_speed_math(data: dict, primary: str, light: str) -> str:
    """
    Warm-up / speed drill: a dense grid of short problems with answer slots.

    ``title`` defaults to empty so the block doubles as a bare problem grid inside
    a numbered task; pass one explicitly for a standalone warm-up.
    """
    title = data.get("title", "")
    instructions = data.get("instructions", "")
    problems = data.get("problems", [])
    columns = int(data.get("columns", 4))
    answer_style = data.get("answer_style", "blank")  # "blank" | "box"
    timer = data.get("timer", "")

    timer_html = f'<div class="fx-timer">{_h(timer)}</div>' if timer else ""
    inst_html = f'<div class="fx-drill-inst">{_h(instructions)}</div>' if instructions else ""
    slot_cls = "fx-drill-box" if answer_style == "box" else "fx-drill-blank"

    # Head is suppressed entirely when unlabelled, so the block can be reused as a
    # bare problem grid inside a numbered task without printing an empty rule.
    head_html = ""
    if title or instructions or timer:
        head_html = (
            f'<div class="fx-drill-head" style="border-color:{primary};">'
            f'<div class="fx-drill-title" style="color:{primary};">{_h(title)}</div>'
            f"{inst_html}{timer_html}</div>"
        )

    items = []
    for i, prob in enumerate(problems, 1):
        text = prob.get("q", "") if isinstance(prob, dict) else str(prob)
        items.append(
            f'<div class="fx-drill-item">'
            f'<span class="fx-drill-num">{i}.</span>'
            f'<span class="fx-drill-q">{_h(text)}</span>'
            f'<span class="{slot_cls}"></span>'
            f"</div>"
        )

    return (
        f'<div class="fx-drill">{head_html}'
        f'<div class="fx-drill-grid" style="grid-template-columns:repeat({columns},1fr);">'
        f'{"".join(items)}</div></div>'
    )


def _render_fraction_strips(data: dict, primary: str, light: str) -> str:
    """
    Fraction strip kit.  Equal division is done by ``flex: 1 1 0`` so the
    browser splits the strip exactly — no arithmetic, no rounding drift.
    """
    strips = data.get("strips", [])
    width_in = float(data.get("width_in", 6.0))
    height_in = float(data.get("height_in", 0.44))
    show_labels = data.get("show_labels", True)

    rows = []
    for strip in strips:
        denom = int(strip.get("denominator", 1))
        label = strip.get("label", "")
        shade = set(strip.get("shade", []))
        color = strip.get("color", "")
        piece_label = strip.get("piece_label")
        if piece_label is None:
            piece_label = f"1/{denom}" if show_labels and denom <= 8 else ""

        cells = []
        for idx in range(denom):
            bg = ""
            if idx in shade and color:
                bg = f"background:{color};"
            elif color and strip.get("fill_all"):
                bg = f"background:{color};"
            cells.append(f'<span style="{bg}">{_h(piece_label)}</span>')

        label_html = f'<div class="fx-strip-label">{_h(label)}</div>' if label else ""
        rows.append(
            f'<div class="fx-strip-row">{label_html}'
            f'<div class="fx-strip" style="width:{width_in}in;height:{height_in}in;">'
            f'{"".join(cells)}</div></div>'
        )
    return f'<div class="fx-strips">{"".join(rows)}</div>'


def _render_fraction_circles(data: dict, primary: str, light: str) -> str:
    """Circles divided into equal wedges via conic-gradient (360/n degree stops)."""
    circles = data.get("circles", [])
    size_in = float(data.get("size_in", 1.5))

    cells = []
    for circ in circles:
        parts = max(1, int(circ.get("parts", 1)))
        caption = circ.get("caption", "")
        shaded = int(circ.get("shaded", 0))
        shade_color = circ.get("shade_color", "#dbeafe")

        wedge = 360.0 / parts
        spokes = f"repeating-conic-gradient(#111 0 0.7deg, transparent 0.7deg {wedge:g}deg)"
        if shaded > 0:
            stop = wedge * shaded
            fill = f"conic-gradient({shade_color} 0 {stop:g}deg, #fff {stop:g}deg 360deg)"
        else:
            fill = "conic-gradient(#fff 0 360deg)"

        cap = f'<div class="fx-caption">{_h(caption)}</div>' if caption else ""
        cells.append(
            f'<div class="fx-circle-cell">'
            f'<div class="fx-circle" style="width:{size_in}in;height:{size_in}in;'
            f'background:{spokes},{fill};"></div>{cap}</div>'
        )
    return f'<div class="fx-circles">{"".join(cells)}</div>'


def _render_fraction_area(data: dict, primary: str, light: str) -> str:
    """
    Area/region models — a square partitioned by CSS grid.

    ``cols``/``rows`` give an equal partition.  ``cols_spec``/``rows_spec`` take a
    list of relative weights instead (e.g. ``[3, 1, 1, 1]``) to produce a shape cut
    into the right *number* of parts that are deliberately **not** equal — the
    distractors needed to test whether a student is checking for equal parts rather
    than just counting pieces.
    """
    grids = data.get("grids", [])
    size_in = float(data.get("size_in", 1.9))

    cells = []
    for grid in grids:
        cols_spec = grid.get("cols_spec")
        rows_spec = grid.get("rows_spec")
        cols = max(1, int(grid.get("cols", 2)))
        rows = max(1, int(grid.get("rows", 2)))

        if cols_spec:
            col_css = " ".join(f"{float(w):g}fr" for w in cols_spec)
            cols = len(cols_spec)
        else:
            col_css = f"repeat({cols},1fr)"
        if rows_spec:
            row_css = " ".join(f"{float(w):g}fr" for w in rows_spec)
            rows = len(rows_spec)
        else:
            row_css = f"repeat({rows},1fr)"

        shaded = set(grid.get("shaded", []))
        color = grid.get("shade_color", "#ede9fe")
        caption = grid.get("caption", "")

        squares = "".join(
            f'<div style="background:{color};"></div>' if i in shaded else "<div></div>"
            for i in range(cols * rows)
        )
        cap = f'<div class="fx-caption">{_h(caption)}</div>' if caption else ""
        cells.append(
            f"<div>"
            f'<div class="fx-area" style="width:{size_in}in;height:{size_in}in;'
            f"grid-template-columns:{col_css};"
            f'grid-template-rows:{row_css};">{squares}</div>{cap}</div>'
        )
    return f'<div class="fx-areas">{"".join(cells)}</div>'


def _render_fraction_number_line(data: dict, primary: str, light: str) -> str:
    """0-to-1 number lines partitioned into equal fractional steps."""
    lines = data.get("lines", [])
    width_in = float(data.get("width_in", 6.0))

    out = []
    for line in lines:
        denom = max(1, int(line.get("denominator", 2)))
        prompt = line.get("prompt", "")
        show_labels = line.get("show_labels", True)
        end_label = line.get("end_label", "1")
        start_label = line.get("start_label", "0")

        ticks = []
        for i in range(denom):
            lab = ""
            if show_labels:
                text = start_label if i == 0 else f"{i}/{denom}"
                lab = f'<div class="fx-nl-lab">{_h(text)}</div>'
            end = ""
            if i == denom - 1 and show_labels:
                end = f'<div class="fx-nl-lab end">{_h(end_label)}</div>'
            ticks.append(f'<div class="fx-nl-tick">{lab}{end}</div>')

        prompt_html = f'<div class="fx-nl-prompt">{_h(prompt)}</div>' if prompt else ""
        out.append(
            f'<div class="fx-nl-wrap">{prompt_html}'
            f'<div class="fx-nl" style="width:{width_in}in;">{"".join(ticks)}</div></div>'
        )
    return "".join(out)


def _render_heart_bar(data: dict, primary: str, light: str) -> str:
    """Themed half-unit bar: N hearts, each split in two."""
    hearts = int(data.get("hearts", 5))
    filled = int(data.get("filled_halves", 0))
    width_in = float(data.get("width_in", 5.0))
    height_in = float(data.get("height_in", 0.4))
    caption = data.get("caption", "")

    cells = []
    for i in range(hearts):
        left = "on" if filled >= i * 2 + 1 else ""
        right = "on" if filled >= i * 2 + 2 else ""
        cells.append(
            f'<div class="fx-heart" style="height:{height_in}in;">'
            f'<span class="{left}"></span><span class="{right}"></span></div>'
        )
    cap = f'<div class="fx-caption">{_h(caption)}</div>' if caption else ""
    return f'<div class="fx-hearts" style="width:{width_in}in;">{"".join(cells)}</div>{cap}'


def _render_color_key(data: dict, primary: str, light: str) -> str:
    """Colour-by-fraction key: swatch + fraction + colour name."""
    entries = data.get("entries", [])
    rows = []
    for entry in entries:
        frac = entry.get("fraction", "")
        name = entry.get("color_name", "")
        hexv = entry.get("hex", "#ffffff")
        rows.append(
            f'<div><span class="fx-sw" style="background:{hexv};"></span>'
            f"<b>{_h(frac)}</b> &rarr; {_h(name)}</div>"
        )
    return f'<div class="fx-key">{"".join(rows)}</div>'


def _render_color_task(data: dict, primary: str, light: str) -> str:
    """A figure plus its colour key, side by side."""
    figure = data.get("figure", {})
    fig_html = _render_block(figure.get("kind", ""), figure.get("data", {}), primary, light)
    key_html = _render_color_key({"entries": data.get("entries", [])}, primary, light)
    return f'<div class="fx-row">{fig_html}{key_html}</div>'


def _render_calibration_ruler(data: dict, primary: str, light: str) -> str:
    """Printed ruler for verifying the page printed at 100% scale."""
    inches = int(data.get("inches", 6))
    note = data.get(
        "note",
        "Check this against a real ruler. If it is not exactly "
        f"{inches} inches long, reprint at 100% (Actual Size) with "
        '"Fit to page" turned OFF — otherwise the pieces will not match.',
    )
    ticks = "".join(f"<div>{i}</div>" for i in range(1, inches + 1))
    return (
        f'<div class="fx-ruler" style="width:{inches}in;">{ticks}</div>'
        f'<div class="fx-note">{_h(note)}</div>'
    )


def _render_compare_pairs(data: dict, primary: str, light: str) -> str:
    """
    Grid of ``left [ ] right`` comparison prompts.

    Written as a real grid rather than a run-on text line so the pairs stay
    visually separate — a string like "3/8 ___ 5/8   2/6 ___ 5/6" collapses its
    whitespace in HTML and reads as one continuous blob.
    """
    pairs = data.get("pairs", [])
    columns = int(data.get("columns", 3))
    items = []
    for pair in pairs:
        left = pair.get("left", "") if isinstance(pair, dict) else str(pair)
        right = pair.get("right", "") if isinstance(pair, dict) else ""
        items.append(
            f'<div class="fx-cmp">'
            f'<span class="fx-cmp-side">{_h(left)}</span>'
            f'<span class="fx-cmp-box"></span>'
            f'<span class="fx-cmp-side">{_h(right)}</span>'
            f"</div>"
        )
    return (
        f'<div class="fx-cmp-grid" style="grid-template-columns:repeat({columns},1fr);">'
        f'{"".join(items)}</div>'
    )


def _render_rich_text(data: dict, primary: str, light: str) -> str:
    """
    Headed prose sections with optional bullets and key/value rows — the
    workhorse block for teacher guides and answer keys.
    """
    sections = data.get("sections", [])
    out = []
    for sec in sections:
        heading = sec.get("heading", "")
        text = sec.get("text", "")
        bullets = sec.get("bullets", [])
        rows = sec.get("rows", [])

        head_html = ""
        if heading:
            head_html = (
                f'<div class="fx-rt-head" style="color:{primary};'
                f'border-color:{primary};">{_h(heading)}</div>'
            )

        body = ""
        for para in (p.strip() for p in text.split("\n\n")):
            if para:
                body += f"<p>{_h(para)}</p>"
        if bullets:
            items = "".join(f"<li>{_h(b)}</li>" for b in bullets)
            body += f"<ul>{items}</ul>"
        if rows:
            trs = "".join(
                f"<tr><th>{_h(r.get('k', ''))}</th><td>{_h(r.get('v', ''))}</td></tr>" for r in rows
            )
            body += f'<table class="fx-rt-table">{trs}</table>'

        out.append(f'<div class="fx-rt">{head_html}{body}</div>')
    return "".join(out)


def _render_cut_cards(data: dict, primary: str, light: str) -> str:
    """Grid of cut-apart cards (number-line pegs, fraction cards)."""
    cards = data.get("cards", [])
    cols = int(data.get("columns", 6))
    tiles = "".join(f'<div class="fx-card">{_h(c)}</div>' for c in cards)
    return (
        f'<div class="fx-cards" style="grid-template-columns:repeat({cols},1fr);">' f"{tiles}</div>"
    )


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
    "barGraphWorksheet": _render_bar_graph,
    "pictographWorksheet": _render_pictograph,
    # Composable content blocks (see "Content blocks" above)
    "storyPanel": _render_story_panel,
    "doingCard": _render_doing_card,
    "noteBox": _render_note_box,
    "cutLine": _render_cut_line,
    "taskList": _render_task_list,
    "speedMath": _render_speed_math,
    "fractionStrips": _render_fraction_strips,
    "fractionCircles": _render_fraction_circles,
    "fractionArea": _render_fraction_area,
    "fractionNumberLine": _render_fraction_number_line,
    "heartBar": _render_heart_bar,
    "colorKey": _render_color_key,
    "colorTask": _render_color_task,
    "calibrationRuler": _render_calibration_ruler,
    "cutCards": _render_cut_cards,
    "richText": _render_rich_text,
    "comparePairs": _render_compare_pairs,
}

#: Worksheet kinds that have an HTML renderer.
HTML_SUPPORTED_KINDS: frozenset[str] = frozenset(_RENDERERS)


def _render_block(kind: str, data: dict, primary: str, light: str) -> str:
    """Render one block by kind, returning '' for unknown kinds."""
    renderer = _RENDERERS.get(kind)
    if renderer is None:
        return ""
    return renderer(data, primary, light)


def render_worksheet_html(kind: str, data: dict, day_label: str = "") -> str | None:
    """Return an HTML fragment for *kind* populated with *data*, or None if unsupported."""
    renderer = _RENDERERS.get(kind)
    if renderer is None:
        return None
    primary, light = get_day_palette(day_label)
    # Inject day_label so renderers can include the header
    enriched = {**data, "day_label": day_label}
    return renderer(enriched, primary, light)


def render_page(
    blocks: list[tuple[str, dict]],
    meta: dict | None = None,
    layout: str = "classic",
) -> str:
    """
    Render a sequence of ``(kind, data)`` blocks into one page fragment, wrapped
    in the named layout's chrome.

    ``meta`` carries layout-level page data (title, subtitle, day_index, status);
    see ``worksheet_layouts`` for the recognised keys.  Unknown block kinds are
    skipped rather than raising, so a typo degrades to a missing block instead of
    a failed run.
    """
    meta = dict(meta or {})
    day_label = meta.get("day_label", "")
    primary, light = get_day_palette(day_label)
    inner = "".join(_render_block(kind, data, primary, light) for kind, data in blocks)
    return get_layout(layout).render_page(inner, meta, primary, light)


def build_print_packet_html(
    pages: list[tuple[str, str]],
    packet_title: str = "Weekly Worksheets",
    layout: str = "classic",
) -> str:
    """
    Assemble a full printable HTML document from a list of (day_label, html_fragment) tuples.

    ``layout`` selects the page-chrome stylesheet to include alongside the base
    CSS.  Block CSS is always included; it is namespaced under ``.fx-`` so it
    cannot affect the historical worksheet types.

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

    css = _CSS + "\n" + _BLOCK_CSS
    layout_css = get_layout(layout).css
    if layout_css:
        css += "\n" + layout_css

    return _HTML_WRAPPER.format(title=_h(packet_title), css=css, body=body)
