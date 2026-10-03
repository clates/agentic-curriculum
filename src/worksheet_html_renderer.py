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
import random
from collections import Counter
import math
import os
from typing import Any

try:  # package context (tests, app): src.worksheet_html_renderer
    from .worksheets.ten_frame import TenFrameProblem
    from .worksheets.error_audit import decimal_stack_rows
except ImportError:  # top-level context (scripts run with src on sys.path)
    from worksheets.ten_frame import TenFrameProblem
    from worksheets.error_audit import decimal_stack_rows

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

  /* Error audit ("Bug Hunt") */
  .ea-badge {
    display: inline-block; border: 2px solid #333; border-radius: 10px;
    padding: 2px 14px; font-size: 10pt; font-weight: bold; margin-bottom: 8px;
  }
  .ea-card { border: 2px solid #333; border-radius: 8px; padding: 8px 12px; margin-bottom: 12px; }
  .ea-prompt { font-size: 11pt; font-weight: bold; margin-bottom: 6px; }
  .ea-art { text-align: center; margin: 6px 0; }
  .ea-specimen { border: 1px solid #999; padding: 5px 9px; font-size: 10pt; margin-bottom: 6px; }
  .ea-check { font-size: 10pt; margin: 3px 0; }
  .ea-box {
    display: inline-block; width: 12px; height: 12px;
    border: 2px solid #222; border-radius: 2px; margin-right: 8px; vertical-align: baseline;
  }
  .ea-indent { margin-left: 22px; }
  .ea-legend-label { font-size: 9.5pt; font-weight: bold; margin: 5px 0 2px; }
  .ea-redrawbox { border: 1px solid #222; min-height: 1.6in; margin: 4px 0 6px; }
  .ea-starter { text-align: center; margin: 4px 0; }
  .ea-starter svg { opacity: 0.5; }
  .ea-redrawbox.ea-with-starter { min-height: 1.1in; }
  .ea-cards-2 { display: grid; grid-template-columns: 1fr 1fr; gap: 0 14px; }
  .ea-dec-grid { border-collapse: collapse; margin: 4px 0 2px; font-family: "Courier New", monospace; font-size: 13pt; }
  .ea-dec-grid td { width: 30px; height: 34px; text-align: center; vertical-align: middle; padding: 0; }
  .ea-dec-given { font-weight: bold; }
  .ea-dec-point { font-weight: bold; }
  .ea-dec-write { border: 1.5px solid #222; border-radius: 4px; }
  .ea-dec-pad { color: #999; border: 1.5px dotted #999; border-radius: 4px; }
  .ea-dec-rule td { border-top: 2px solid #222; height: 0; }
  .ea-dec-plus { font-weight: bold; padding-right: 6px; }
  .ea-dec-caption { font-size: 9pt; color: #555; margin: 0 0 4px; }

  /* Ten-frame ("Make Ten") */
  .tf-card { border: 2px solid #333; border-radius: 8px; padding: 8px 12px; margin-bottom: 12px; }
  .tf-prompt { font-size: 11pt; font-weight: bold; margin-bottom: 4px; }
  .tf-label { font-size: 10pt; margin-bottom: 4px; }
  .tf-frames { text-align: center; margin: 6px 0 4px; }
  .tf-frames svg { margin: 0 14px; vertical-align: top; }
  .tf-proof-label { font-size: 9.5pt; font-weight: bold; margin: 5px 0 2px; }
  .tf-key { font-size: 10pt; margin: 2px 0 2px 22px; font-weight: bold; }



.venn-svg { display: block; width: 100%; max-width: 640px; margin: 6px auto; }
  .venn-circle { fill-opacity: 0.25; }
  .venn-circle-label { font-size: 20px; font-weight: 700; fill: #111827; }
  .venn-lens-label { font-size: 16px; font-weight: 700; fill: #374151; }
  .venn-item { font-size: 15px; fill: #111827; }
  .venn-wordbank {
    margin: 14px 0 6px 0; padding: 8px 10px;
    border: 2px dashed #9ca3af; border-radius: 8px;
    text-align: center; background: #f9fafb;
  }
  .venn-wordbank-title {
    font-size: 15px; font-weight: 700; letter-spacing: 0.04em;
    margin-bottom: 6px; text-transform: uppercase;
  }
  .venn-chip {
    display: inline-block; margin: 3px 6px; padding: 4px 12px;
    border: 1.5px solid #9ca3af; border-radius: 999px;
    background: #ffffff; font-size: 15px;
  }

/* Pixel copy */
  .pc-grids {
    display: flex;
    gap: 18px;
    justify-content: center;
    align-items: flex-start;
    flex-wrap: wrap;
    margin-top: 6px;
  }
  .pc-grid-box { text-align: center; }
  .pc-grid-label {
    font-size: 10pt;
    font-weight: bold;
    margin-bottom: 4px;
  }
  .pc-legend {
    margin-top: 10px;
    border: 1.5px dashed #aaa;
    border-radius: 4px;
    padding: 7px 9px;
  }
  .pc-legend-title {
    font-size: 8.5pt;
    color: #888;
    font-style: italic;
    margin-bottom: 5px;
  }
  .pc-legend-row { display: flex; flex-wrap: wrap; gap: 6px 16px; }
  .pc-legend-item {
    display: flex;
    align-items: center;
    gap: 5px;
    font-size: 9.5pt;
  }
  .pc-swatch {
    display: inline-block;
    width: 16px;
    height: 16px;
    border: 1px solid #555;
    border-radius: 3px;
  }

.seq-activity {
    font-size: 13pt;
    font-weight: bold;
    color: #1e3a8a;
    margin: 8px 0 4px;
  }
  .seq-scissors {
    font-size: 9pt;
    font-style: italic;
    color: #a0a0a0;
    margin-bottom: 10px;
  }
  .seq-cards {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 14px;
  }
  .seq-card {
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 12px;
    background: #fcfcfc;
    border: 2px dashed #646464;
    border-radius: 4px;
    min-height: 0.9in;
    page-break-inside: avoid;
    break-inside: avoid;
  }
  .seq-num {
    flex: 0 0 auto;
    width: 34px;
    height: 34px;
    border: 2px solid #3c3c3c;
    border-radius: 3px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 13pt;
    font-weight: bold;
  }
  .seq-num-answer {
    color: #c81e1e;
  }
  .seq-image {
    flex: 0 0 auto;
    width: 0.7in;
    height: 0.7in;
    object-fit: contain;
  }
  .seq-text {
    font-size: 12pt;
    font-weight: bold;
    line-height: 1.35;
  }
  @media print {
    .seq-card { -webkit-print-color-adjust: exact; print-color-adjust: exact; }
  }

.sm-day-header {
    display: flex; align-items: baseline; gap: 10px;
    padding: 5px 10px 5px 12px; border-radius: 4px 4px 0 0;
    margin-bottom: 6px; color: white;
  }
  .sm-day-header-label {
    font-size: 9pt; font-weight: bold; text-transform: uppercase;
    letter-spacing: 0.07em; opacity: 0.85;
  }
  .sm-day-header-title { font-size: 12pt; font-weight: bold; }
  .sm-title {
    font-size: 15pt; font-weight: bold; line-height: 1.2;
    padding-bottom: 4px; margin-bottom: 4px;
    border-bottom: 2.5px solid currentColor;
  }
  .sm-name-date-row {
    display: flex; justify-content: space-between;
    font-size: 10pt; margin: 6px 0 4px;
  }
  .sm-instructions {
    font-style: italic; font-size: 10.5pt; margin-bottom: 10px;
  }
  .sm-story-title {
    display: flex; align-items: flex-end; gap: 6px;
    margin: 4px 0 12px; font-size: 12pt;
  }
  .sm-story-title-line {
    flex: 1; border-bottom: 2px solid #444; height: 1.15em;
  }
  .sm-grid {
    display: grid; grid-template-columns: 1fr 1fr; gap: 12px;
  }
  .sm-box {
    border: 2px solid #646464; border-radius: 4px; overflow: hidden;
    page-break-inside: avoid; break-inside: avoid;
  }
  .sm-box-label {
    font-weight: bold; font-size: 12pt; text-align: center;
    padding: 4px 8px; border-bottom: 2px solid #646464;
  }
  .sm-box-body { padding: 6px 10px 10px; }
  .sm-prompt {
    font-style: italic; font-size: 9.5pt; color: #505050;
    margin-bottom: 6px;
  }
  .sm-line { border-bottom: 1px solid #b4b4b4; height: 24px; }
  .sm-answer {
    color: #3c3cb4; font-size: 10.5pt; white-space: pre-wrap;
    padding: 2px 0 8px;
  }

.nl-tasks { display: flex; flex-direction: column; gap: 18px; margin-top: 14px; }
  .nl-task { break-inside: avoid; page-break-inside: avoid; }
  .nl-prompt { font-style: italic; margin-bottom: 2px; }
  .nl-svg { display: block; width: 100%; height: auto; max-width: 760px; }
  .nl-svg .nl-axis { stroke: #111; stroke-width: 2.5; }
  .nl-svg .nl-tick { stroke: #111; stroke-width: 2; }
  .nl-svg .nl-label { font-size: 15px; fill: #111; text-anchor: middle; }
  .nl-svg .nl-blank { fill: none; stroke: #6b7280; stroke-width: 1.2; }
  .nl-svg .nl-mark { fill: #dc3232; }

.ld-day-header {
    display: flex; align-items: baseline; gap: 10px;
    padding: 5px 10px 5px 12px; border-radius: 4px 4px 0 0;
    margin-bottom: 6px; color: white;
  }
  .ld-day-header-label {
    font-size: 9pt; font-weight: bold; text-transform: uppercase;
    letter-spacing: 0.07em; opacity: 0.85;
  }
  .ld-day-header-title { font-size: 12pt; font-weight: bold; }
  .ld-title {
    font-size: 15pt; font-weight: bold; line-height: 1.2;
    padding-bottom: 4px; margin-bottom: 4px;
    border-bottom: 2.5px solid currentColor;
  }
  .ld-name-date-row {
    display: flex; justify-content: space-between;
    font-size: 10pt; margin: 6px 0 4px;
  }
  .ld-instructions {
    font-style: italic; font-size: 10.5pt; margin-bottom: 10px;
  }
  /* Diagram box: image or placeholder with numbered callout dots */
  .ld-diagram {
    position: relative;
    border: 2px solid #a0a0a0; border-radius: 4px;
    background: #f8f8ff;
    min-height: 3.3in; margin-bottom: 14px;
    overflow: hidden;
    page-break-inside: avoid; break-inside: avoid;
  }
  .ld-diagram img {
    display: block; max-width: 100%; max-height: 3.3in; margin: 0 auto;
  }
  .ld-diagram-placeholder {
    position: absolute; inset: 0;
    display: flex; align-items: center; justify-content: center;
    color: #b4b4b4; font-style: italic; font-size: 13pt;
  }
  .ld-callout {
    position: absolute; width: 28px; height: 28px;
    margin: -14px 0 0 -14px;
    border-radius: 50%;
    background: #6495ed; border: 2px solid #3c64c8;
    color: white; font-weight: bold; font-size: 10.5pt;
    display: flex; align-items: center; justify-content: center;
  }
  /* Word bank tile bank */
  .ld-word-bank {
    margin: 0 0 14px;
    padding: 8px 10px;
    border: 2px dashed #646464; border-radius: 6px;
    page-break-inside: avoid; break-inside: avoid;
  }
  .ld-word-bank-title {
    font-weight: bold; font-size: 11pt; margin-bottom: 6px;
  }
  .ld-word-bank-tiles {
    display: flex; flex-wrap: wrap; gap: 8px;
  }
  .ld-word-tile {
    border: 1.5px solid #646464; border-radius: 4px;
    padding: 3px 10px; font-size: 10.5pt;
    background: white;
  }
  .ld-word-tile-hint {
    display: block; font-size: 8pt; color: #707070; font-style: italic;
  }
  /* Numbered label slots */
  .ld-labels {
    display: grid; grid-template-columns: 1fr 1fr;
    column-gap: 24px; row-gap: 12px;
  }
  .ld-label-slot {
    display: flex; align-items: flex-end; gap: 4px;
    page-break-inside: avoid; break-inside: avoid;
  }
  .ld-label-number { font-size: 11pt; white-space: nowrap; }
  .ld-label-blank {
    flex: 1; border-bottom: 1.5px solid #111; height: 1.05em;
  }
  .ld-label-answer {
    flex: 1; font-size: 11pt; color: #3c3cb4;
    border-bottom: 1.5px solid #3c3cb4;
    padding-bottom: 1px;
  }

  /* Handwriting practice */
  .hw-grid { display: grid; gap: 12px 16px; margin-top: 2px; }
  .hw-cell {
    border: 1.5px solid #555;
    border-radius: 6px;
    padding: 8px 10px 10px;
    display: flex;
    flex-direction: column;
  }
  .hw-image {
    height: 0.9in;
    max-width: 100%;
    object-fit: contain;
    align-self: center;
    margin-bottom: 4px;
  }
  .hw-image-blank {
    height: 0.9in;
    border: 1.5px dashed #bbb;
    border-radius: 4px;
    align-self: center;
    width: 100%;
    margin-bottom: 4px;
  }
  .hw-trace {
    font-size: 21pt;
    font-weight: bold;
    letter-spacing: 0.22em;
    color: #c4c4c4;                 /* light trace colour */
    text-align: center;
    white-space: nowrap;
    overflow: hidden;
    border-bottom: 2px dashed #9a9a9a;   /* dashed trace underline */
    padding-bottom: 1px;
    margin-bottom: 8px;
    line-height: 1.25;
  }
  .hw-write {
    height: calc(3 * 0.4in);
    background-image: repeating-linear-gradient(
      to bottom,
      transparent 0px,
      transparent calc(0.4in - 1px),
      #777 calc(0.4in - 1px),
      #777 0.4in
    );
  }
  .hw-write.hw-bottom-rail { border-bottom: 2px solid #555; }
  .hw-sublabel {
    font-size: 9pt;
    color: #666;
    text-align: center;
    margin-top: 4px;
  }

/* Alphabet worksheet */
  .abc-centerpiece {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 18px;
    padding: 6px 0 2px;
    margin-bottom: 6px;
  }
  .abc-letter {
    font-size: 92pt;
    font-weight: bold;
    line-height: 1;
    letter-spacing: 0.04em;
  }
  .abc-image { height: 1.9in; max-width: 1.9in; object-fit: contain; }
  .abc-practice { margin-top: 8px; }
  .abc-practice-label {
    font-size: 9.5pt;
    font-weight: bold;
    color: #555;
    margin: 8px 0 3px;
  }
  /* Handwriting ruled lines: solid top, dashed midline, solid bottom */
  .abc-rule {
    position: relative;
    height: 58px;
    border-top: 2px solid #969696;
    border-bottom: 2px solid #969696;
    margin-bottom: 10px;
  }
  .abc-rule::before {
    content: "";
    position: absolute;
    left: 0; right: 0; top: 50%;
    border-top: 1px dashed #969696;
  }
  .abc-trace-row {
    display: flex;
    align-items: flex-end;
    padding: 0 14px 2px;
  }
  .abc-trace-char {
    font-size: 40pt;
    font-weight: bold;
    line-height: 1;
    margin-right: 26px;
  }
  .abc-spacing-row { padding: 0 14px; color: #777; font-size: 16pt; font-weight: bold; }
  .abc-spacing-row span { margin-right: 34px; white-space: nowrap; }
  .abc-words { margin-top: 12px; }
  .abc-words-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; }
  .abc-words-col { border: 2px solid; border-radius: 6px; padding: 7px 10px; }
  .abc-words-title {
    font-size: 11pt;
    font-weight: bold;
    text-align: center;
    border-bottom: 1px solid #bbb;
    padding-bottom: 3px;
    margin-bottom: 6px;
  }
  .abc-word {
    font-size: 13pt;
    line-height: 1.55;
    list-style: none;
    padding-left: 6px;
  }

/* Fill in the blank */
  .fib-passage { font-size: 11pt; line-height: 2.1; margin-bottom: 10px; }
  .fib-para { margin-bottom: 10px; }
  .fib-para:last-child { margin-bottom: 0; }
  .fib-gap {
    display: inline-block; min-width: 1.1in; text-align: center;
    border-bottom: 1.5px solid #444; padding: 0 6px;
    vertical-align: baseline; line-height: 1.1;
  }
  .fib-gap-num { font-size: 8pt; color: #8a8a8a; display: block; line-height: 1.4; }
  .fib-gap-filled { min-width: 1.1in; }
  .fib-answer { color: #c81e1e; font-weight: bold; font-size: 10pt; }
  .fib-word-bank { border: 1.5px dashed #aaa; border-radius: 4px; padding: 7px 9px; margin-top: 8px; }
  .fib-wb-label { font-size: 8.5pt; color: #888; font-style: italic; margin-bottom: 5px; }
  .fib-wb-tiles { display: flex; flex-wrap: wrap; gap: 5px; }
  .fib-wb-tile { border: 1px solid #555; border-radius: 3px; padding: 2px 8px; font-size: 9.5pt; background: white; }
\
  /* Two-operand math */
  .to-grid { display: grid; grid-template-columns: 1fr 1fr 1fr 1fr; gap: 14px 18px; }
  .to-problem { display: flex; align-items: flex-start; gap: 6px; font-family: 'Trebuchet MS', Arial, sans-serif; }
  .to-num { font-size: 10pt; font-weight: bold; color: #555; padding-top: 2px; flex: 0 0 18px; }
  .to-stack { text-align: right; }
  .to-row { font-size: 14pt; font-weight: bold; padding: 1px 0; letter-spacing: 0.03em; }
  .to-op { margin-right: 4px; }
  .to-underline { border-bottom: 2px solid #333; margin: 2px 0; height: 2px; }
  .to-answer-box { height: 28px; border: 1.5px solid #999; border-radius: 3px; margin-top: 2px; }
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


def _svg_clock(hour: float, minute: int, missing: str | None, starter: bool = False) -> str:
    """Inline-SVG analog clock face (prints crisply, no image assets).

    Numerals are drawn last so hands never cover them. Starter scaffolds
    push numerals inward so the 12-tick doesn't strike through "12".
    """
    import math

    r, cx, cy = 70, 80, 80
    num_inset = 32 if starter else 24
    parts = [f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="white" stroke="black" stroke-width="3"/>']
    for n in range(12):
        a = math.radians(n * 30)
        long = n % 3 == 0
        r1 = r - (12 if long else 6)
        x1, y1 = cx + r1 * math.sin(a), cy - r1 * math.cos(a)
        x2, y2 = cx + r * math.sin(a), cy - r * math.cos(a)
        parts.append(
            f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" '
            f'stroke="black" stroke-width="{3 if long else 1}"/>'
        )

    def hand(angle_deg: float, length: float, w: int) -> None:
        a = math.radians(angle_deg)
        parts.append(
            f'<line x1="{cx}" y1="{cy}" x2="{cx + length * math.sin(a):.1f}" '
            f'y2="{cy - length * math.cos(a):.1f}" stroke="black" stroke-width="{w}" '
            f'stroke-linecap="round"/>'
        )

    if missing not in ("minute", "both"):
        hand((minute % 60) / 60 * 360, r - 18, 4)
    if missing not in ("hour", "both"):
        hand((hour % 12) / 12 * 360, r - 38, 7)
    parts.append(f'<circle cx="{cx}" cy="{cy}" r="4" fill="black"/>')
    for label, n in (("12", 0), ("3", 3), ("6", 6), ("9", 9)):
        a = math.radians(n * 30)
        tx, ty = cx + (r - num_inset) * math.sin(a), cy - (r - num_inset) * math.cos(a)
        hw = 11 if len(label) == 2 else 8
        parts.append(
            f'<rect x="{tx - hw:.1f}" y="{ty - 8:.1f}" width="{hw * 2}" '
            f'height="18" fill="white"/>'
        )
        parts.append(
            f'<text x="{tx:.1f}" y="{ty + 5:.1f}" text-anchor="middle" '
            f'font-size="13" font-family="Arial">{label}</text>'
        )
    return f'<svg width="160" height="160" viewBox="0 0 160 160">{"".join(parts)}</svg>'


def _svg_dots(rows: int, cols: int) -> str:
    """Inline-SVG filled-circle array grid."""
    gap, rad = 26, 8
    w, h = cols * gap, rows * gap
    parts = []
    for rr in range(rows):
        for cc in range(cols):
            parts.append(
                f'<circle cx="{cc * gap + rad + 2}" cy="{rr * gap + rad + 2}" '
                f'r="{rad}" fill="black"/>'
            )
    return (
        f'<svg width="{w + 4}" height="{h + 4}" viewBox="0 0 {w + 4} {h + 4}">'
        f'{"".join(parts)}</svg>'
    )


def _tf_is_color(fill: str) -> bool:
    """True when *fill* is a CSS color (name or hex), not an emoji glyph."""
    fill = (fill or "black").strip()
    return fill.startswith("#") or fill.isalpha()


def _svg_ten_frame(filled: int, fill: str = "black") -> str:
    """Inline-SVG 5x2 ten-frame; first *filled* cells (row-major) are filled.

    A counter tally prints under the frame so the pair reads at a glance.
    *fill* is a CSS color (colored dot) or an emoji character (glyph in
    each filled cell).
    """
    cell, rad = 26, 8
    w, h = 5 * cell, 2 * cell
    label_h = 18
    parts = [
        f'<rect x="1.5" y="1.5" width="{w - 3}" height="{h - 3}" rx="6" '
        f'fill="white" stroke="black" stroke-width="3"/>'
    ]
    for i in range(1, 5):
        parts.append(
            f'<line x1="{i * cell}" y1="1.5" x2="{i * cell}" y2="{h - 1.5}" '
            f'stroke="black" stroke-width="1"/>'
        )
    parts.append(
        f'<line x1="1.5" y1="{cell}" x2="{w - 1.5}" y2="{cell}" '
        f'stroke="black" stroke-width="1"/>'
    )
    for rr in range(2):
        for cc in range(5):
            idx = rr * 5 + cc
            cx, cy = cc * cell + cell // 2, rr * cell + cell // 2
            if idx < filled:
                if _tf_is_color(fill):
                    parts.append(f'<circle cx="{cx}" cy="{cy}" r="{rad}" fill="{_h(fill)}"/>')
                else:
                    parts.append(
                        f'<text x="{cx}" y="{cy}" text-anchor="middle" '
                        f'dominant-baseline="central" font-size="15">{_h(fill)}</text>'
                    )
            else:
                parts.append(
                    f'<circle cx="{cx}" cy="{cy}" r="{rad}" fill="white" '
                    f'stroke="#aaa" stroke-width="1"/>'
                )
    parts.append(
        f'<text x="{w // 2}" y="{h + 13}" text-anchor="middle" font-size="12" '
        f'font-family="Arial" font-weight="bold">{filled}</text>'
    )
    return (
        f'<svg width="{w}" height="{h + label_h}" viewBox="0 0 {w} {h + label_h}">'
        f'{"".join(parts)}</svg>'
    )


def _render_ten_frame(data: dict, primary: str, light: str) -> str:
    title = data.get("title", "Make Ten!")
    day_label = data.get("day_label", "")
    problems = data.get("problems", [])
    show_answers = data.get("show_answers", False)
    equation_lines = int(data.get("equation_lines", 2))

    dh = _day_header(day_label, title, primary) if day_label else ""

    cards_html = ""
    for idx, prob in enumerate(problems, start=1):
        a = int(prob.get("addend_a", 0))
        b = int(prob.get("addend_b", 0))
        total = a + b
        head = f"{a} + {b} = {total}" if show_answers else f"{a} + {b} = ______"
        label = prob.get("label", "")
        label_html = f'<div class="tf-label">{_h(label)}</div>' if label else ""
        frames = (
            '<div class="tf-frames">'
            + _svg_ten_frame(a, prob.get("fill_a", "black"))
            + _svg_ten_frame(b, prob.get("fill_b", "black"))
            + "</div>"
        )
        if show_answers:
            # Single source of truth: the model's make-ten proof logic.
            prob_model = TenFrameProblem.from_mapping(prob)
            key_lines = "".join(
                f'<div class="tf-key">{_h(eq)}</div>'
                for eq in prob_model.proof_equations()
            )
            proof = f'<div class="tf-proof-label">Make ten:</div>{key_lines}'
        else:
            proof = (
                f'<div class="tf-proof-label">Make ten:</div>'
                + _answer_lines(equation_lines)
            )
        cards_html += (
            f'<div class="tf-card" style="border-color:{primary};">'
            f'<div class="tf-prompt">{idx}. {_h(head)}</div>'
            f"{label_html}{frames}{proof}</div>"
        )

    instructions = _h(
        data.get(
            "instructions",
            "Move counters to fill the first ten-frame to ten. "
            "Write the make-ten proof on the lines.",
        )
    )

    return f"""
{dh}
{_title_block(title, primary)}
{_name_date()}
<div class="ws-instructions">{instructions}</div>
{cards_html}
"""
def _svg_partitions(
    parts: int,
    broken: int | None = None,
    shaded=None,
    starter: bool = False,
    blank: bool = False,
) -> str:
    """Inline-SVG circle partitioned into wedges (fraction picture).

    broken: index of one mis-sized (unequal) wedge — the bug to circle.
    shaded: wedge index (or list) filled as the "shaded fraction".
    starter: draw the CORRECT equal partition shape for tracing over
    (paired with .ea-starter's 0.5 opacity).
    blank: draw a bare circle outline only — the student partitions it.
    """
    import math

    r, cx, cy = 70, 80, 80
    if blank:
        return (
            f'<svg width="160" height="160" viewBox="0 0 160 160">'
            f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="white" '
            f'stroke="black" stroke-width="3"/></svg>'
        )
    stroke = "#8a8a8a" if starter else "black"
    step = 360.0 / parts
    edges = [i * step for i in range(parts + 1)]
    if not starter and broken is not None and 0 <= broken < parts:
        d = step * 0.38
        edges[broken] -= d
        edges[broken + 1] += d
    shade = [] if starter else (
        [int(s) for s in shaded] if isinstance(shaded, (list, tuple))
        else ([int(shaded)] if shaded is not None else [])
    )
    out = []
    for i in shade:
        if not 0 <= i < parts:
            continue
        a1, a2 = math.radians(edges[i]), math.radians(edges[i + 1])
        x1, y1 = cx + r * math.sin(a1), cy - r * math.cos(a1)
        x2, y2 = cx + r * math.sin(a2), cy - r * math.cos(a2)
        large = 1 if (edges[i + 1] - edges[i]) > 180 else 0
        out.append(
            f'<path d="M {cx} {cy} L {x1:.1f} {y1:.1f} '
            f'A {r} {r} 0 {large} 1 {x2:.1f} {y2:.1f} Z" '
            f'fill="#b9b9b9" stroke="none"/>'
        )
    for a in edges[:parts]:
        aa = math.radians(a)
        out.append(
            f'<line x1="{cx}" y1="{cy}" x2="{cx + r * math.sin(aa):.1f}" '
            f'y2="{cy - r * math.cos(aa):.1f}" stroke="{stroke}" stroke-width="2"/>'
        )
    out.append(
        f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="{stroke}" '
        f'stroke-width="3"/>'
    )
    return f'<svg width="160" height="160" viewBox="0 0 160 160">{"".join(out)}</svg>'


def _html_decimal_stack(scaffold: dict, filled: bool) -> str:
    """Guided rewrite grid: decimal-aligned digit slots with helper zeroes.

    Decimal points are pre-printed in their own column; short terms carry
    faint dotted helper zeroes to trace. In key mode (*filled*) the answer
    row carries its digits.
    """
    grid = decimal_stack_rows(scaffold, filled=filled)

    def _cell(char: str, kind: str) -> str:
        if kind == "spacer":
            return "<td></td>"
        if kind == "point":
            return '<td class="ea-dec-point">.</td>'
        if kind == "pad":
            return '<td class="ea-dec-pad">0</td>'
        if kind == "write":
            return '<td class="ea-dec-write"></td>'
        return f'<td class="ea-dec-given">{_h(char)}</td>'

    def _row(cells: list, plus: bool = False) -> str:
        tds = "".join(_cell(ch, kind) for ch, kind in cells)
        prefix = '<td class="ea-dec-plus">+</td>' if plus else "<td></td>"
        return f"<tr>{prefix}{tds}</tr>"

    ncols = len(grid["terms"][0]) + 1 if grid["terms"] else 1
    terms = "".join(
        _row(cells, plus=(i == len(grid["terms"]) - 1))
        for i, cells in enumerate(grid["terms"])
    )
    rule = f'<tr class="ea-dec-rule"><td colspan="{ncols}"></td></tr>'
    answer = _row(grid["answer"])
    caption = ""
    if grid["has_pads"] and not filled:
        caption = (
            '<div class="ea-dec-caption">Gray 0s are helpers — trace them. '
            "Decimal points stay in their column.</div>"
        )
    return (
        "<div>Fix (line up the decimals):</div>"
        f'<table class="ea-dec-grid">{terms}{rule}{answer}</table>'
        f"{caption}"
    )


def _render_error_audit(data: dict, primary: str, light: str) -> str:
    title = data.get("title", "Bug Hunt")
    day_label = data.get("day_label", "")
    theme = data.get("theme_label", "Bug Hunter")
    legend = data.get("legend", [])
    specimens = data.get("specimens", [])
    fix_mode = data.get("fix_mode", "rewrite")
    verify = data.get("verify", True)
    adversarial = data.get("adversarial", False)
    show_answers = data.get("show_answers", False)
    fix_lines = int(data.get("fix_lines", 2))
    columns = int(data.get("columns", 1))

    dh = _day_header(day_label, title, primary) if day_label else ""
    legend_label = "ASSIGN SUSPECTS:" if adversarial else "SUSPECTS:"

    def art_html(art: dict | None) -> str:
        if not art:
            return ""
        if art.get("kind") == "clock":
            return (
                '<div class="ea-art">'
                + _svg_clock(
                    float(art.get("hour", 12)),
                    int(art.get("minute", 0)),
                    art.get("missing"),
                )
                + "</div>"
            )
        if art.get("kind") == "dots":
            return (
                '<div class="ea-art">'
                + _svg_dots(int(art.get("rows", 2)), int(art.get("cols", 2)))
                + "</div>"
            )
        if art.get("kind") == "partitions":
            return (
                '<div class="ea-art">'
                + _svg_partitions(
                    int(art.get("parts", 2)),
                    art.get("broken"),
                    art.get("shaded"),
                )
                + "</div>"
            )
        return ""

    cards_html = ""
    for idx, spec in enumerate(specimens, start=1):
        prompt = _h(spec.get("prompt", ""))
        lines = "".join(f"<div>{_h(ln)}</div>" for ln in spec.get("lines", []))
        if show_answers:
            stage = ""
            if spec.get("bug_location"):
                stage += f"<div><b>Bug:</b> {_h(spec['bug_location'])}</div>"
            if spec.get("diagnosis"):
                stage += f"<div><b>Diagnosis:</b> {_h(spec['diagnosis'])}</div>"
            if spec.get("fix_text") and fix_mode == "rewrite":
                stage += f"<div><b>Fix:</b> {_h(spec['fix_text'])}</div>"
            if fix_mode == "redraw":
                art = spec.get("art") or {}
                if art.get("kind") == "partitions":
                    sart = spec.get("starter_art") or {}
                    parts = int(sart.get("parts", art.get("parts", 2)))
                    stage += (
                        '<div><b>Fixed shape:</b></div><div class="ea-art">'
                        + _svg_partitions(parts)
                        + "</div>"
                    )
        else:
            stage = '<div class="ea-check"><span class="ea-box"></span>Bug circled</div>'
            if legend:
                stage += f'<div class="ea-legend-label">{_h(legend_label)}</div>'
                for entry in legend:
                    stage += (
                        '<div class="ea-check ea-indent">'
                        f'<span class="ea-box"></span>{_h(entry)}</div>'
                    )
            if fix_mode == "rewrite":
                if spec.get("fix_scaffold"):
                    stage += _html_decimal_stack(
                        spec["fix_scaffold"], filled=show_answers
                    )
                else:
                    stage += "<div>Fix:</div>" + _answer_lines(fix_lines)
            elif fix_mode == "redraw":
                art = spec.get("art") or {}
                if spec.get("blank_fix_circle") and art.get("kind") == "partitions":
                    scaffold = (
                        '<div class="ea-art">'
                        + _svg_partitions(2, blank=True)
                        + "</div>"
                    )
                    stage += (
                        "<div>Redraw it fixed — draw the lines in the circle:</div>"
                        f"{scaffold}"
                    )
                else:
                    scaffold = ""
                    if art.get("kind") == "clock":
                        scaffold = (
                            '<div class="ea-starter">'
                            + _svg_clock(12, 0, "both", starter=True)
                            + "</div>"
                        )
                    elif art.get("kind") == "partitions":
                        sart = spec.get("starter_art") or art
                        scaffold = (
                            '<div class="ea-starter">'
                            + _svg_partitions(int(sart.get("parts", 2)), starter=True)
                            + "</div>"
                        )
                    stage += f"<div>Redraw it fixed:</div>{scaffold}" + (
                        '<div class="ea-redrawbox"></div>' if not scaffold else
                        '<div class="ea-redrawbox ea-with-starter"></div>'
                    )
            if verify:
                stage += (
                    '<div class="ea-check">'
                    '<span class="ea-box"></span>Re-checked my fix</div>'
                )
        cards_html += (
            f'<div class="ea-card" style="border-color:{primary};">'
            f'<div class="ea-prompt">{idx}. {prompt}</div>'
            f"{art_html(spec.get('art'))}"
            f'<div class="ea-specimen">{lines}</div>'
            f"{stage}</div>"
        )

    instructions = _h(
        data.get(
            "instructions",
            "Something is wrong in each case. Circle the bug, "
            "diagnose it, fix it, then re-check your fix.",
        )
    )

    if columns == 2:
        cards_html = f'<div class="ea-cards-2">{cards_html}</div>'

    return f"""
{dh}
{_title_block(title, primary)}
<div class="ea-badge" style="border-color:{primary};color:{primary};">{_h(theme)}</div>
{_name_date()}
<div class="ws-instructions">{instructions}</div>
{cards_html}
"""


_VENN_CSS = """\
<style>
  .venn-diagram { text-align: center; margin: 6px 0; }
  .venn-svg { display: block; width: 100%%; max-width: 640px; margin: 0 auto; }
  .venn-wordbank { border: 1.5px dashed #aaa; border-radius: 4px; padding: 7px 9px; margin-top: 10px; }
  .venn-wordbank-title { font-size: 9pt; font-style: italic; margin-bottom: 5px; }
  .venn-chip { display: inline-block; border: 1px solid #555; border-radius: 3px; padding: 2px 8px; margin: 2px; font-size: 9.5pt; background: white; }
  .venn-circle-label { font-size: 11pt; font-weight: bold; fill: #222; }
  .venn-lens-label { font-size: 9pt; font-weight: bold; fill: #555; }
  .venn-item { font-size: 9pt; fill: #333; }
</style>"""

_NL_CSS = """\
<style>
  .nl-tasks { display: flex; flex-direction: column; gap: 18px; }
  .nl-task { }
  .nl-prompt { font-size: 10pt; margin-bottom: 4px; }
  .nl-svg { display: block; width: 100%; max-width: 780px; margin: 0 auto; }
  .nl-axis { stroke: #111; stroke-width: 2.5; }
  .nl-tick { stroke: #666; stroke-width: 1.5; }
  .nl-label { font-size: 10pt; fill: #222; text-anchor: middle; }
  .nl-blank { fill: white; stroke: #777; stroke-width: 1.5; }
  .nl-mark { }
</style>"""

_SM_CSS = """\
<style>
  .sm-title { font-size: 15pt; font-weight: bold; padding-bottom: 4px; margin-bottom: 4px; border-bottom: 2.5px solid currentColor; line-height: 1.2; }
  .sm-name-date-row { display: flex; justify-content: space-between; font-size: 10pt; margin: 6px 0 4px; }
  .sm-instructions { font-style: italic; font-size: 10.5pt; margin-bottom: 10px; }
  .sm-story-title { display: flex; align-items: flex-end; gap: 6px; margin: 4px 0 12px; font-size: 12pt; }
  .sm-story-title-line { flex: 1; border-bottom: 2px solid #444; height: 1.15em; }
  .sm-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; }
  .sm-box { border: 2px solid #646464; border-radius: 4px; overflow: hidden; page-break-inside: avoid; break-inside: avoid; }
  .sm-box-label { font-weight: bold; font-size: 12pt; text-align: center; padding: 4px 8px; border-bottom: 2px solid #646464; }
  .sm-box-body { padding: 6px 10px 10px; }
  .sm-prompt { font-style: italic; font-size: 9.5pt; color: #505050; margin-bottom: 6px; }
  .sm-line { border-bottom: 1px solid #b4b4b4; height: 24px; }
  .sm-answer { color: #3c3cb4; font-size: 10.5pt; white-space: pre-wrap; padding: 2px 0 8px; }
</style>"""

_SEQ_CSS = """\
<style>
  .seq-activity { font-size: 13pt; font-weight: bold; color: #1e3a8a; margin: 8px 0 4px; }
  .seq-scissors { font-size: 9pt; font-style: italic; color: #a0a0a0; margin-bottom: 10px; }
  .seq-cards { display: grid; grid-template-columns: 1fr 1fr; gap: 14px; }
  .seq-card { display: flex; align-items: center; gap: 10px; padding: 12px; background: #fcfcfc; border: 2px dashed #646464; border-radius: 4px; min-height: 0.9in; page-break-inside: avoid; break-inside: avoid; }
  .seq-num { flex: 0 0 auto; width: 34px; height: 34px; border: 2px solid #3c3c3c; border-radius: 3px; display: flex; align-items: center; justify-content: center; font-size: 13pt; font-weight: bold; }
  .seq-num-answer { color: #c81e1e; }
  .seq-image { flex: 0 0 auto; width: 0.7in; height: 0.7in; object-fit: contain; }
  .seq-text { font-size: 12pt; font-weight: bold; line-height: 1.35; }
  @media print { .seq-card { -webkit-print-color-adjust: exact; print-color-adjust: exact; } }
</style>"""

_LD_CSS = """\
<style>
  .ld-title { font-size: 15pt; font-weight: bold; padding-bottom: 4px; margin-bottom: 4px; border-bottom: 2.5px solid; line-height: 1.2; }
  .ld-name-date-row { display: flex; justify-content: space-between; font-size: 10pt; margin: 6px 0 4px; }
  .ld-instructions { font-style: italic; font-size: 10.5pt; margin-bottom: 10px; }
  .ld-diagram { position: relative; border: 2px solid #555; border-radius: 6px; min-height: 2.5in; margin: 8px 0 12px; overflow: hidden; }
  .ld-diagram img { width: 100%; display: block; }
  .ld-diagram-placeholder { color: #aaa; font-size: 16pt; text-align: center; padding: 1.2in 0; }
  .ld-callout { position: absolute; width: 24px; height: 24px; border-radius: 50%; background: white; border: 2px solid #222; display: flex; align-items: center; justify-content: center; font-size: 10pt; font-weight: bold; transform: translate(-50%, -50%); }
  .ld-word-bank { border-radius: 4px; padding: 7px 9px; margin: 8px 0; }
  .ld-word-bank-title { font-size: 9pt; font-weight: bold; margin-bottom: 5px; }
  .ld-word-bank-tiles { display: flex; flex-wrap: wrap; gap: 5px; }
  .ld-word-tile { border: 1.5px solid; border-radius: 3px; padding: 2px 8px; font-size: 9.5pt; background: white; white-space: nowrap; }
  .ld-word-tile-hint { font-size: 8pt; color: #888; margin-left: 4px; }
  .ld-labels { margin-top: 10px; }
  .ld-label-slot { display: flex; align-items: center; gap: 6px; margin-bottom: 5px; font-size: 10.5pt; }
  .ld-label-number { font-weight: bold; flex: 0 0 18px; text-align: right; }
  .ld-label-blank { flex: 1; border-bottom: 1.5px solid #777; height: 22px; }
  .ld-label-answer { color: #c81e1e; font-weight: bold; }
</style>"""

# Constants
_TRACE_OPACITIES = (1.0, 0.65, 0.40, 0.20)
_PC_PLACEHOLDER_PALETTE = ["#e6194b", "#3cb44b", "#ffe119", "#4363d8", "#f58231", "#911eb4"]
_PC_LEGEND_MAX = 6

def _escape_attr(text: object) -> str:
    """Escape for use inside an SVG attribute (quotes included)."""
    return _html.escape(str(text), quote=True)

def _svg_venn(
    left_label: str,
    right_label: str,
    both_label: str,
    left_items: list[str],
    right_items: list[str],
    both_items: list[str],
    primary: str,
) -> str:
    """Render the two overlapping circles as inline SVG.

    Layout: viewBox 700x430. Circles r=150 with centers (250, 230) and
    (450, 230) so the overlap is centred on x=350. Circle labels sit above
    the rims; item texts are stacked vertically inside each region, offset
    so the three columns never collide.
    """
    r = 150
    cy = 240
    left_cx, right_cx = 250, 450
    center_x = (left_cx + right_cx) // 2  # 350, centre of overlap

    line_h = 22
    fill = f"{primary}"
    stroke = f"{primary}"

    # Region label anchors: above each circle rim, overlap label at top of lens
    label_y = cy - r - 12

    # Item columns: left-only region ~x=165, overlap ~x=350, right-only ~x=535
    def item_texts(items: list[str], x: int, y_start: int) -> str:
        parts = []
        y = y_start
        for it in items:
            parts.append(
                f'<text class="venn-item" x="{x}" y="{y}" '
                f'text-anchor="middle">{_h(it)}</text>'
            )
            y += line_h
        return "".join(parts)

    left_txt = item_texts(left_items, left_cx - 85, cy - 20)
    both_txt = item_texts(both_items, center_x, cy - 20)
    right_txt = item_texts(right_items, right_cx + 85, cy - 20)

    both_label_txt = (
        f'<text class="venn-lens-label" x="{center_x}" y="{label_y + 26}" '
        f'text-anchor="middle">{_h(both_label)}</text>'
        if both_label
        else ""
    )

    return (
        '<svg class="venn-svg" viewBox="0 0 700 430" '
        'xmlns="http://www.w3.org/2000/svg" role="img" '
        f'aria-label="{_escape_attr(f"Venn diagram: {left_label} / {right_label}")}">'
        # left circle (translucent primary fill)
        f'<circle class="venn-circle venn-circle-left" cx="{left_cx}" cy="{cy}" '
        f'r="{r}" fill="{fill}" fill-opacity="0.25" stroke="{stroke}" '
        'stroke-width="2.5"/>'
        # right circle
        f'<circle class="venn-circle venn-circle-right" cx="{right_cx}" cy="{cy}" '
        f'r="{r}" fill="{fill}" fill-opacity="0.25" stroke="{stroke}" '
        'stroke-width="2.5"/>'
        # region labels
        f'<text class="venn-circle-label" x="{left_cx}" y="{label_y}" '
        f'text-anchor="middle">{_h(left_label)}</text>'
        f'<text class="venn-circle-label" x="{right_cx}" y="{label_y}" '
        f'text-anchor="middle">{_h(right_label)}</text>'
        f"{both_label_txt}"
        # pre-filled items
        f"{left_txt}{both_txt}{right_txt}"
        "</svg>"
    )

def _render_venn_diagram(data: dict, primary: str, light: str) -> str:
    """Render a vennDiagramWorksheet payload as an HTML fragment."""
    title = data.get("title", "Venn Diagram")
    instructions = data.get(
        "instructions",
        "Sort the words from the word bank into the correct section of "
        "the Venn diagram.",
    )
    left_label = data.get("left_label", "Left")
    right_label = data.get("right_label", "Right")
    both_label = data.get("both_label", "Both")
    left_items = list(data.get("left_items") or [])
    right_items = list(data.get("right_items") or [])
    both_items = list(data.get("both_items") or [])

    # Word bank: entries may be dicts with text/category, or plain strings.
    word_bank_raw = data.get("word_bank") or []
    texts: list[str] = []
    for entry in word_bank_raw:
        if isinstance(entry, dict):
            texts.append(str(entry.get("text", "")))
        elif hasattr(entry, "text"):
            texts.append(str(entry.text))
        else:
            texts.append(str(entry))
    bank_texts = [t for t in texts if t]

    # Shuffled display order (deterministic seed so print output is stable).
    display = list(bank_texts)
    random.Random(20261003).shuffle(display)

    diagram = _svg_venn(
        left_label,
        right_label,
        both_label,
        left_items,
        right_items,
        both_items,
        primary,
    )

    chips = "".join(f'<span class="venn-chip">{_h(t)}</span>' for t in display)
    wordbank = (
        f'<div class="venn-wordbank" style="border-color:{primary};">'
        f'<div class="venn-wordbank-title" style="color:{primary};">'
        "Word Bank</div>"
        f"{chips}</div>"
        if bank_texts
        else ""
    )

    header = ""
    day_label = data.get("day_label", "")
    if day_label:
        header = (
            f'<div class="ws-day" style="color:{primary};">{_h(day_label)}</div>'
        )

    return f"""\
{header}
<h2 class="ws-title" style="color:{primary};">{_h(title)}</h2>
<div class="ws-name-date">Name: __________________&nbsp;&nbsp;&nbsp;Date: __________________</div>
<div class="ws-instructions">{_h(instructions)}</div>
{_VENN_CSS}
<div class="venn-diagram">{diagram}</div>
{wordbank}
"""


def _hw_image_html(item: dict) -> str:
    """Image sprite (PIL _prepare_sprite) or a blank drawing placeholder."""
    path = item.get("image_path")
    if path:
        return f'<img class="hw-image" src="{_h(path)}" alt="{_h(item.get("text", ""))}">'
    return '<div class="hw-image-blank"></div>'

def _hw_cell(item: dict, primary: str) -> str:
    """One practice cell: picture, traceable word, ruled write lines."""
    sub = item.get("sub_label")
    sub_html = f'<div class="hw-sublabel">{_h(sub)}</div>' if sub else ""

    bottom_rail = False
    meta = item.get("metadata")
    if isinstance(meta, dict):
        bottom_rail = bool(meta.get("bottom_rail", False))
    write_cls = "hw-write hw-bottom-rail" if bottom_rail else "hw-write"

    return (
        f'<div class="hw-cell" style="border-color:{primary};">'
        f"{_hw_image_html(item)}"
        f'<div class="hw-trace">{_h(item.get("text", ""))}</div>'
        f'<div class="{write_cls}"></div>'
        f"{sub_html}"
        "</div>"
    )

def _render_handwriting(data: dict, primary: str, light: str) -> str:
    """Render a handwriting worksheet as an HTML fragment.

    Data keys (matching HandwritingWorksheet): title, instructions, items
    (list of {text, image_path, sub_label}), rows, cols, day_label.
    """
    title = data.get("title", "Handwriting Practice")
    day_label = data.get("day_label", "")
    instructions_text = data.get(
        "instructions", "Look at the picture and practice writing the word on the lines."
    )
    items = data.get("items", [])
    rows = int(data.get("rows", 4) or 4)
    cols = int(data.get("cols", 2) or 2)

    # Day header bar (omitted when no day label, matching the other renderers).
    dh = ""
    if day_label:
        dh = (
            f'<div class="day-header" style="background:{primary};">'
            f'<div class="day-header-label">{_h(day_label)}</div>'
            f'<div class="day-header-title">{_h(title)}</div>'
            "</div>"
        )

    # Grid of practice cells, capped at rows*cols like the PIL renderer.
    cells = "".join(_hw_cell(item, primary) for item in items[: rows * cols])
    grid_style = f"grid-template-columns:repeat({cols},1fr);"

    return f"""{dh}
<div class="ws-title" style="color:{primary};border-bottom-color:{primary};">{_h(title)}</div>
<div class="name-date-row">
  <span>Name:&nbsp;&nbsp;_______________________________________</span>
  <span class="short">Date:&nbsp;&nbsp;_______________</span>
</div>
<div class="ws-instructions">{_h(instructions_text)}</div>
<div class="hw-grid" style="{grid_style}">
{cells}
</div>
"""


def _pc_placeholder_colors(grid_size: int) -> list[list[str]]:
    """Deterministic diagonal-rainbow pattern for a missing/unreadable image."""
    n = max(1, int(grid_size))
    return [
        [_PC_PLACEHOLDER_PALETTE[(r + c) % len(_PC_PLACEHOLDER_PALETTE)] for c in range(n)]
        for r in range(n)
    ]

def _pc_reference_colors(image_path: str | None, grid_size: int) -> list[list[str]]:
    """Grid of hex colours sampled from *image_path* (NEAREST, like the PIL renderer).

    Falls back to a deterministic placeholder pattern when the image cannot
    be resolved or read.
    """
    n = max(1, int(grid_size))
    if image_path and os.path.exists(image_path):
        try:
            from PIL import Image  # lazy: only needed when an image resolves

            source = Image.open(image_path).convert("RGBA")
            bg = Image.new("RGBA", source.size, "WHITE")
            bg.alpha_composite(source)
            pixelated = bg.resize((n, n), Image.Resampling.NEAREST)
            px = pixelated.load()
            return [
                ["#{:02x}{:02x}{:02x}".format(*px[c, r][:3]) for c in range(n)]
                for r in range(n)
            ]
        except Exception as exc:
            import logging
            logging.getLogger(__name__).warning("pixel_copy: cannot read %s: %s", image_path, exc)
    return _pc_placeholder_colors(n)

def _svg_pixel_grid(colors: list, grid_size: int, cell_px: int) -> str:
    """Inline-SVG pixel grid.

    *colors* is a 2D list (rows of columns) of fill colours; each cell is a
    bordered rect.  An empty/None *colors* renders a blank grid of empty
    bordered cells (the copy grid the student fills in).  Cell rects are
    omitted (rendered as bare white bordered rects) only when no colour is
    supplied for them.
    """
    n = max(1, int(grid_size))
    size = max(1, int(cell_px))
    w = n * size

    # Accept None, [], or a ragged matrix — every missing cell stays blank.
    get = (
        (lambda r, c: None)
        if not colors
        else (lambda r, c: (colors[r][c] if r < len(colors) and c < len(colors[r]) else None))
    )

    parts = []
    for r in range(n):
        for c in range(n):
            fill = get(r, c)
            if fill:
                parts.append(
                    f'<rect x="{c * size}" y="{r * size}" width="{size}" height="{size}" '
                    f'fill="{_h(fill)}" stroke="#333" stroke-width="0.5"/>'
                )
            else:
                parts.append(
                    f'<rect x="{c * size}" y="{r * size}" width="{size}" height="{size}" '
                    f'fill="white" stroke="#777" stroke-width="0.5"/>'
                )
    return (
        f'<svg class="pc-grid" width="{w}" height="{w}" viewBox="0 0 {w} {w}" '
        f'shape-rendering="crispEdges">{"".join(parts)}</svg>'
    )

def _pc_cell_px(grid_size: int) -> int:
    """Cell side in px: target ~336px per grid so two fit side by side when printed."""
    n = max(1, int(grid_size))
    return max(6, min(18, 336 // n))

def _pc_legend(colors: list, primary: str, light: str) -> str:
    """Colour key showing the distinct colours used in the reference grid."""
    counts = Counter(
        cell for row in colors for cell in row if cell
    )
    if not counts:
        return ""
    swatches = "".join(
        f'<span class="pc-legend-item">'
        f'<span class="pc-swatch" style="background:{_h(color)};"></span>'
        f"Colour {i}</span>"
        for i, (color, _count) in enumerate(counts.most_common(_PC_LEGEND_MAX), start=1)
    )
    return (
        f'<div class="pc-legend">'
        f'<div class="pc-legend-title" style="color:{primary};">Colour Key — use these colours:</div>'
        f'<div class="pc-legend-row">{swatches}</div>'
        "</div>"
    )

def _render_pixel_copy(data: dict, primary: str, light: str) -> str:
    """Render a pixel copy worksheet as an HTML fragment.

    Two grids side by side: the coloured reference (left) and the blank copy
    grid (right), plus a colour legend below.  Data keys: title, instructions,
    image_path, grid_size, day_label (injected by the dispatch wrapper).
    """
    title = data.get("title", "Pixel Copy")
    day_label = data.get("day_label", "")
    instructions = data.get(
        "instructions",
        "Look at the colors on the left. Copy them to the grid on the right!",
    )
    image_path = data.get("image_path", "")
    grid_size = int(data.get("grid_size", 24) or 24)

    dh = _day_header(day_label, title, primary) if day_label else ""

    ref_colors = _pc_reference_colors(image_path, grid_size)
    cell_px = _pc_cell_px(grid_size)

    ref_svg = _svg_pixel_grid(ref_colors, grid_size, cell_px)
    blank_svg = _svg_pixel_grid([], grid_size, cell_px)

    grids = f"""
<div class="pc-grids">
  <div class="pc-grid-box">
    <div class="pc-grid-label" style="color:{primary};">Reference</div>
    {ref_svg}
  </div>
  <div class="pc-grid-box">
    <div class="pc-grid-label" style="color:{primary};">Your Copy</div>
    {blank_svg}
  </div>
</div>
{_pc_legend(ref_colors, primary, light)}
"""

    return f"""
{dh}
{_title_block(title, primary)}
{_name_date()}
<div class="ws-instructions">{_h(instructions)}</div>
{grids}
"""



def _trace_row(char: str) -> str:
    """One ruled line with four fading trace letters (PIL 'trace-a-long')."""
    chars = "".join(
        f'<span class="abc-trace-char" style="color:rgba(0,0,0,{op:.2f});">{_h(char)}</span>'
        for op in _TRACE_OPACITIES
    )
    return (
        f'<div class="abc-rule"><div class="abc-trace-row">{chars}</div></div>'
    )

def _free_line() -> str:
    """Ruled line with nothing on it — free practice."""
    return '<div class="abc-rule"></div>'

def _spacing_line(letter: str) -> str:
    """Spacing practice row of '__  __' starter blanks (PIL line 4)."""
    pairs = "".join(
        f"<span>__&nbsp;&nbsp;__</span>" for _ in range(8)
    )
    return (
        f'<div class="abc-practice-label">Write {_h(letter)} {_h(letter.lower())} '
        f"in the blanks to practice spacing:</div>"
        f'<div class="abc-spacing-row">{pairs}</div>'
    )

def _words_column(heading: str, words: list, primary: str, light: str) -> str:
    items = "".join(
        f'<div class="abc-word">&#8226;&nbsp;&nbsp;{_h(w)}</div>' for w in words
    )
    return (
        f'<div class="abc-words-col" style="border-color:{primary};background:{light};">'
        f'<div class="abc-words-title" style="color:{primary};">{_h(heading)}</div>'
        f"{items}"
        f"</div>"
    )

def _render_alphabet(data: dict, primary: str, light: str) -> str:
    """Render an alphabet worksheet fragment.

    Data keys: letter, starting_words, containing_words,
    character_image_path (optional), title, instructions, day_label.
    """
    # Factory upper-cases the letter; normalize raw data the same way (PIL parity).
    letter = str(data.get("letter", "A") or "A")[:1].upper()
    starting_words = list(data.get("starting_words", []) or [])
    containing_words = list(data.get("containing_words", []) or [])
    character_image_path = data.get("character_image_path") or ""
    title = data.get("title", "Alphabet Practice")
    day_label = data.get("day_label", "")

    dh = _day_header(day_label, title, primary) if day_label else ""

    # Centerpiece: large uppercase + lowercase pair, optional character image.
    img_html = ""
    if character_image_path:
        img_html = (
            f'<img class="abc-image" src="{_h(character_image_path)}" '
            f'alt="{_h(letter)} character">'
        )
    centerpiece = (
        f'<div class="abc-centerpiece">'
        f'<span class="abc-letter" style="color:{primary};">'
        f"{_h(letter)}{_h(letter.lower())}</span>"
        f"{img_html}"
        f"</div>"
    )

    practice = (
        f'<div class="abc-practice">'
        f'<div class="abc-practice-label">Trace and write the letter '
        f"{_h(letter)}:</div>"
        f"{_trace_row(letter)}"       # Line 1: uppercase, fading
        f"{_trace_row(letter.lower())}"  # Line 2: lowercase, fading
        f'<div class="abc-practice-label">Now write it on your own:</div>'
        f"{_free_line()}"              # Line 3: free practice
        f"{_spacing_line(letter)}"      # Line 4: spacing blanks
        f"</div>"
    )

    words = (
        f'<div class="abc-words"><div class="abc-words-grid">'
        + _words_column(
            f"Words that start with {letter}", starting_words, primary, light
        )
        + _words_column(
            f"Words that have {letter} in them", containing_words, primary, light
        )
        + "</div></div>"
    )

    instructions = _h(
        data.get("instructions", "Practice your letters and reading words!")
    )

    return f"""\
{dh}
{_title_block(title, primary)}
{_name_date()}
<div class="ws-instructions">{instructions}</div>
{centerpiece}
{practice}
{words}
"""




def _render_sequencing(data: dict, primary: str, light: str) -> str:
    """Render a sequencing worksheet as an HTML fragment.

    Args:
        data: Dict matching the SequencingWorksheet payload shape:
            title, instructions, activity_name, steps (list of
            {text, image_path?, correct_order?}), show_answers, day_label?
        primary: Primary accent colour (hex) from the day palette.
        light: Light accent colour (hex) from the day palette.

    Returns:
        HTML fragment string with ``seq-`` prefixed CSS classes.
    """
    title = data.get("title", "Put It in Order!")
    activity_name = data.get("activity_name", "Activity")
    steps = data.get("steps", []) or []
    show_answers = bool(data.get("show_answers", False))
    day_label = data.get("day_label", "")

    # Day header (matches the convention of the other HTML renderers).
    dh = ""
    if day_label:
        day = _h(day_label)
        dh = (
            f'<div class="day-header" style="background:{primary};">'
            f'<span class="day-header-label">{day}</span>'
            f'<span class="day-header-title">{_h(title)}</span></div>'
        )

    instructions = _h(
        data.get(
            "instructions",
            "Cut out each step below. Paste them in the correct order "
            "on another sheet of paper.",
        )
    )

    cards_html = ""
    for step in steps:
        if not isinstance(step, dict):
            step = {"text": step}
        text = _h(step.get("text", ""))
        correct_order = step.get("correct_order")
        image_path = step.get("image_path")

        # Number box: filled with the correct order in answer-key mode,
        # blank otherwise (mirrors the PIL renderer).
        num_inner = ""
        num_cls = "seq-num"
        if show_answers and correct_order is not None:
            num_inner = _h(str(correct_order))
            num_cls = "seq-num seq-num-answer"
        num_box = f'<div class="{num_cls}">{num_inner}</div>'

        img_html = ""
        if image_path:
            img_html = f'<img class="seq-image" src="{_h(image_path)}" alt="">'

        cards_html += (
            f'<div class="seq-card" style="border-color:{primary}44;">'
            f"{num_box}{img_html}"
            f'<div class="seq-text">{text}</div>'
            f"</div>"
        )

    cards = f'<div class="seq-cards">{cards_html}</div>' if cards_html else ""

    return f"""\
{_SEQ_CSS}
{dh}
<div class="ws-title" style="color:{primary};">{_h(title)}</div>
<div class="ws-name-date">Name: ______________________ &nbsp;&nbsp; Date: ____________</div>
<div class="ws-instructions">{instructions}</div>
<div class="seq-activity" style="color:{primary};">Activity: {_h(activity_name)}</div>
<div class="seq-scissors">&#9986; - - - - - - Cut here - - - - - - - - - - - - - - - - - - - -</div>
{cards}
"""


def _fib_segment_fields(seg: Any) -> tuple[str | None, int | None, bool]:
    """Return (text, gap, newline) for a FillBlankSegment or a plain dict."""
    if isinstance(seg, dict):
        return (
            seg.get("text"),
            int(seg["gap"]) if seg.get("gap") is not None else None,
            bool(seg.get("newline", False)),
        )
    return (getattr(seg, "text", None), getattr(seg, "gap", None), bool(getattr(seg, "newline", False)))

def _render_fill_in_the_blank(data: dict, primary: str, light: str) -> str:
    """Render a fill-in-the-blank worksheet as an HTML fragment.

    Mirrors the PIL renderer: text flows inline, each gap is an underlined
    slot with its gray "(n)" number above the line, newline segments become
    paragraph breaks, and the word bank appears as a dashed box of shuffled
    tiles below the passage. With show_answers, each gap slot carries the
    red answer text instead of the blank.
    """
    title = data.get("title", "Fill in the Blank")
    day_label = data.get("day_label", "")
    segments = data.get("segments", []) or []
    word_bank = list(data.get("word_bank", []) or [])
    answers = data.get("answers", {}) or {}
    show_answers = bool(data.get("show_answers", False))

    dh = _day_header(day_label, title, primary) if day_label else ""

    # -- Passage ------------------------------------------------------------
    para_parts: list[str] = []
    paras_html: list[str] = []
    for seg in segments:
        text, gap, newline = _fib_segment_fields(seg)
        if newline:
            paras_html.append("".join(para_parts))
            para_parts = []
        elif text is not None:
            para_parts.append(f'<span class="fib-text">{_h(text)}</span>')
        elif gap is not None:
            ans = answers.get(str(gap))
            if show_answers and ans is not None:
                para_parts.append(
                    f'<span class="fib-gap fib-gap-filled">'
                    f'<span class="fib-answer">{_h(ans)}</span></span>'
                )
            else:
                para_parts.append(
                    f'<span class="fib-gap">'
                    f'<span class="fib-gap-num">({int(gap)})</span>'
                    f"</span>"
                )
    paras_html.append("".join(para_parts))

    paras = "".join(
        f'<p class="fib-para">{body}</p>' for body in paras_html if body
    )
    passage_html = f'<div class="fib-passage">{paras}</div>'

    # -- Word bank (shuffled display order) ----------------------------------
    wb_html = ""
    if word_bank:
        shuffled = word_bank[:]
        random.shuffle(shuffled)
        tiles = "".join(f'<span class="fib-wb-tile">{_h(w)}</span>' for w in shuffled)
        wb_html = (
            f'<div class="fib-word-bank">'
            f'<div class="fib-wb-label">Word Bank — write each word in the correct blank above:</div>'
            f'<div class="fib-wb-tiles">{tiles}</div>'
            f"</div>"
        )

    instructions = _h(
        data.get("instructions", "Use the word bank to fill in the blanks.")
    )

    return f"""\
{dh}
{_title_block(title, primary)}
{_name_date()}
<div class="ws-instructions">{instructions}</div>
{passage_html}
{wb_html}
"""


def _story_title_row() -> str:
    return (
        '<div class="sm-story-title">'
        "<b>Story&nbsp;Title:</b>"
        '<div class="sm-story-title-line"></div>'
        "</div>"
    )

def _field_box(field: dict, show_answers: bool, light: str, primary: str) -> str:
    label = _h(field.get("label", ""))
    prompt = field.get("prompt") or ""
    lines = max(1, int(field.get("lines", 2)))
    value = field.get("value") or ""

    prompt_html = f'<div class="sm-prompt">{_h(prompt)}</div>' if prompt else ""

    if show_answers and value:
        body = f'<div class="sm-answer">{_h(value)}</div>'
    else:
        body = "".join('<div class="sm-line"></div>' for _ in range(lines))

    return (
        f'<div class="sm-box">'
        f'<div class="sm-box-label" style="background:{light};'
        f'border-bottom-color:{primary};color:{primary};">{label}</div>'
        f'<div class="sm-box-body">{prompt_html}{body}</div>'
        f"</div>"
    )

def _render_story_map(data: dict, primary: str, light: str) -> str:
    """Render a story map worksheet as an HTML fragment."""
    title = data.get("title", "Story Map")
    day_label = data.get("day_label", "")
    show_answers = bool(data.get("show_answers", False))
    fields = data.get("fields", [])

    dh = (
        f'<div class="sm-day-header" style="background:{primary};">'
        f'<div class="sm-day-header-label">{_h(day_label)}</div>'
        f'<div class="sm-day-header-title">{_h(title)}</div>'
        f"</div>"
        if day_label
        else ""
    )

    story_title_html = _story_title_row() if data.get("story_title_field", True) else ""

    boxes = "".join(
        _field_box(f if isinstance(f, dict) else vars(f), show_answers, light, primary)
        for f in fields
    )
    grid_html = f'<div class="sm-grid">{boxes}</div>' if boxes else ""

    instructions = _h(data.get("instructions", "Fill in each box about the story you read."))

    return f"""{_SM_CSS}
{dh}
<div class="sm-title" style="color:{primary};border-bottom-color:{primary};">{_h(title)}</div>
<div class="sm-name-date-row">
  <span>Name:&nbsp;&nbsp;_______________________________________</span>
  <span>Date:&nbsp;&nbsp;_______________</span>
</div>
<div class="sm-instructions">{instructions}</div>
{story_title_html}
{grid_html}
"""



def _fmt_num(value: float) -> str:
    """Format a tick value the same way the PIL renderer labels ticks."""
    return str(int(value)) if float(value) == int(value) else str(value)

def _task_get(task: Any, key: str, default: Any = None) -> Any:
    """Read a field from a task that is either a plain dict or a dataclass."""
    if isinstance(task, dict):
        return task.get(key, default)
    return getattr(task, key, default)

def _svg_number_line(task: Any, show_answers: bool, primary: str) -> str:
    """Render one task as an SVG number line fragment.

    Horizontal axis with arrow tips, tick marks every ``step`` from
    ``start`` to ``end`` (inclusive), numeric labels below each tick,
    blank write-in boxes for hidden positions (unless ``show_answers``),
    and filled marks above ``mark_positions`` ticks.
    """
    start = float(_task_get(task, "start", 0))
    end = float(_task_get(task, "end", 10))
    step = float(_task_get(task, "step", 1)) or 1.0
    hidden = [float(x) for x in _task_get(task, "hidden_positions", []) or []]
    marks = [float(x) for x in _task_get(task, "mark_positions", []) or []]

    # Tick values — same drift-guarded loop as the PIL renderer.
    positions: list[float] = []
    val = start
    while val <= end + step * 0.001:
        positions.append(round(val, 10))
        val += step
    if len(positions) < 2:
        return ""

    W = 760.0
    H = 88.0
    pad_x = 18.0
    line_y = 40.0
    label_y = 78.0
    mark_r = 6.0

    x1, x2 = pad_x, W - pad_x
    spacing = (x2 - x1) / (len(positions) - 1)

    parts: list[str] = [
        f'<svg class="nl-svg" viewBox="0 0 {W:.0f} {H:.0f}" '
        f'xmlns="http://www.w3.org/2000/svg" role="img" '
        f'aria-label="Number line from {_fmt_num(start)} to {_fmt_num(end)}">',
        # Axis with arrow tips on both ends.
        f'<line class="nl-axis" x1="{x1 - 8:.1f}" y1="{line_y:.1f}" '
        f'x2="{x2 + 8:.1f}" y2="{line_y:.1f}"/>',
        f'<polygon class="nl-axis" fill="#111" points="'
        f'{x2 + 14:.1f},{line_y:.1f} {x2 + 4:.1f},{line_y - 5.5:.1f} '
        f'{x2 + 4:.1f},{line_y + 5.5:.1f}"/>',
        f'<polygon class="nl-axis" fill="#111" points="'
        f'{x1 - 14:.1f},{line_y:.1f} {x1 - 4:.1f},{line_y - 5.5:.1f} '
        f'{x1 - 4:.1f},{line_y + 5.5:.1f}"/>',
    ]

    for i, pos in enumerate(positions):
        tx = x1 + i * spacing
        parts.append(
            f'<line class="nl-tick" x1="{tx:.2f}" y1="{line_y - 8:.1f}" '
            f'x2="{tx:.2f}" y2="{line_y + 8:.1f}"/>'
        )

        is_hidden = any(abs(pos - h) < 0.001 for h in hidden)
        is_marked = any(abs(pos - m) < 0.001 for m in marks)

        if is_marked:
            parts.append(
                f'<circle class="nl-mark" cx="{tx:.2f}" cy="{line_y - 20:.1f}" '
                f'r="{mark_r:.1f}" fill="{primary}"/>'
            )

        if is_hidden and not show_answers:
            # Blank write-in box instead of the number.
            box_w = 30.0
            parts.append(
                f'<rect class="nl-blank" x="{tx - box_w / 2:.2f}" y="{label_y - 22:.1f}" '
                f'width="{box_w:.1f}" height="26" rx="2"/>'
            )
        else:
            parts.append(
                f'<text class="nl-label" x="{tx:.2f}" y="{label_y:.1f}">'
                f"{_h(_fmt_num(pos))}</text>"
            )

    parts.append("</svg>")
    return "".join(parts)

def _render_number_line(data: dict, primary: str, light: str) -> str:
    """Render a number line worksheet as an HTML fragment."""
    title = data.get("title", "Number Line")
    day_label = data.get("day_label", "")
    tasks = data.get("tasks", []) or []
    show_answers = bool(data.get("show_answers", False))

    dh = _day_header(day_label, title, primary) if day_label else ""

    default_instr = (
        "Write the missing numbers on each number line."
        if show_answers
        else "Fill in the missing numbers on each number line."
    )
    instructions = _h(data.get("instructions", default_instr))

    task_html = ""
    for idx, task in enumerate(tasks, 1):
        prompt = _task_get(task, "prompt") or ""
        prompt_html = (
            f'<div class="nl-prompt"><strong>{idx}.</strong> {_h(prompt)}</div>'
        )
        svg = _svg_number_line(task, show_answers, primary)
        if not svg:
            continue
        task_html += f'<div class="nl-task">{prompt_html}{svg}</div>'

    return f"""\
{dh}
{_title_block(title, primary)}
{_name_date()}
<div class="ws-instructions">{instructions}</div>
{_NL_CSS}
<div class="nl-tasks">
{task_html}
</div>
"""


def _label_dicts(labels: list) -> list[dict]:
    """Normalize label entries (dicts or objects) to plain dicts."""
    out: list[dict] = []
    for item in labels:
        if isinstance(item, dict):
            out.append(item)
        else:
            out.append(
                {
                    "number": getattr(item, "number", None),
                    "answer": getattr(item, "answer", ""),
                    "hint": getattr(item, "hint", None),
                }
            )
    return out

def _diagram_html(labels: list[dict], image_path: str | None, primary: str) -> str:
    """Diagram box: image if provided, else placeholder, with callout dots."""
    if image_path:
        inner = f'<img src="{_h(image_path)}" alt="Diagram">'
    else:
        inner = '<div class="ld-diagram-placeholder">[ Diagram ]</div>'

    # Numbered callout circles spread across the box, mirroring the PIL layout
    n = len(labels)
    dots: list[str] = []
    for idx, lbl in enumerate(labels):
        frac = (idx + 0.5) / max(n, 1)
        left = frac * 100
        top = 35 + (idx % 2) * 30  # stagger two rows, as a percentage
        dots.append(
            f'<div class="ld-callout" style="left:{left:.2f}%;top:{top}%;"'
            f' data-number="{_h(lbl.get("number", idx + 1))}">'
            f"{_h(lbl.get('number', idx + 1))}</div>"
        )

    return (
        f'<div class="ld-diagram">{inner}{"".join(dots)}'
        f"</div>"
    )

def _word_bank_html(labels: list[dict], primary: str, light: str) -> str:
    """Shuffled tile bank of the label answers (plus optional hints)."""
    tiles = [
        {"answer": lbl.get("answer", ""), "hint": lbl.get("hint")}
        for lbl in labels
    ]
    random.shuffle(tiles)

    tile_html = "".join(
        f'<span class="ld-word-tile" style="border-color:{_h(primary)};">'
        f"{_h(t['answer'])}"
        + (
            f'<span class="ld-word-tile-hint">{_h(t["hint"])}</span>'
            if t["hint"]
            else ""
        )
        + "</span>"
        for t in tiles
    )

    return (
        f'<div class="ld-word-bank" style="background:{_h(light)};">'
        f'<div class="ld-word-bank-title" style="color:{_h(primary)};">Word Bank:</div>'
        f'<div class="ld-word-bank-tiles">{tile_html}</div>'
        f"</div>"
    )

def _label_slot(label: dict, show_answers: bool) -> str:
    """One numbered slot: '3. ______________' or the answer in answer mode."""
    number = _h(label.get("number", ""))
    if show_answers:
        body = f'<span class="ld-label-answer">{_h(label.get("answer", ""))}</span>'
    else:
        body = '<span class="ld-label-blank"></span>'
    return (
        f'<div class="ld-label-slot">'
        f'<span class="ld-label-number">{number}.</span>'
        f"{body}</div>"
    )

def _render_labeled_diagram(data: dict, primary: str, light: str) -> str:
    """Render a labeled diagram worksheet as an HTML fragment."""
    title = data.get("title", "Labeled Diagram")
    day_label = data.get("day_label", "")
    show_answers = bool(data.get("show_answers", False))
    word_bank = bool(data.get("word_bank", False))
    image_path = data.get("image_path")
    labels = _label_dicts(data.get("labels", []))

    dh = (
        f'<div class="ld-day-header" style="background:{_h(primary)};">'
        f'<div class="ld-day-header-label">{_h(day_label)}</div>'
        f'<div class="ld-day-header-title">{_h(title)}</div>'
        f"</div>"
        if day_label
        else ""
    )

    diagram = _diagram_html(labels, image_path, primary)
    bank = _word_bank_html(labels, primary, light) if word_bank else ""
    slots = "".join(_label_slot(lbl, show_answers) for lbl in labels)
    labels_html = f'<div class="ld-labels">{slots}</div>' if slots else ""

    instructions = _h(
        data.get("instructions", "Label each part of the diagram.")
    )

    return f"""{_LD_CSS}
{dh}
<div class="ld-title" style="color:{_h(primary)};border-bottom-color:{_h(primary)};">{_h(title)}</div>
<div class="ld-name-date-row">
  <span>Name:&nbsp;&nbsp;_______________________________________</span>
  <span>Date:&nbsp;&nbsp;_______________</span>
</div>
<div class="ld-instructions">{instructions}</div>
{diagram}
{bank}
{labels_html}
"""





def _render_two_operand(data: dict, primary: str, light: str) -> str:
    """Render a two-operand math worksheet as an HTML fragment.

    Vertical stacks: each problem is right-aligned digits with an
    operator line, underline, and answer box.
    """
    title = data.get("title", "Two-Operand Practice")
    day_label = data.get("day_label", "")
    problems = data.get("problems", []) or []

    dh = _day_header(day_label, title, primary) if day_label else ""

    problems_html = ""
    for i, prob in enumerate(problems, 1):
        if isinstance(prob, dict):
            a = _h(str(prob.get("operand_one", "")))
            b = _h(str(prob.get("operand_two", "")))
            op = _h(str(prob.get("operator", "+")))
        else:
            a = _h(str(getattr(prob, "operand_one", "")))
            b = _h(str(getattr(prob, "operand_two", "")))
            op_val = getattr(prob, "operator", "+")
            op = _h(str(op_val.value if hasattr(op_val, "value") else op_val))

        width = max(len(a), len(b))
        problems_html += (
            f'<div class="to-problem">'
            f'<span class="to-num">{i}.</span>'
            f'<div class="to-stack">'
            f'<div class="to-row">{a.rjust(width)}</div>'
            f'<div class="to-row"><span class="to-op">{op}</span>{b.rjust(width)}</div>'
            f'<div class="to-underline" style="width:{width * 1.2}em;"></div>'
            f'<div class="to-answer-box"></div>'
            f'</div></div>'
        )

    instructions = _h(
        data.get("instructions", "Solve each problem. Show your work if needed.")
    )

    return f"""\
{dh}
{_title_block(title, primary)}
{_name_date()}
<div class="ws-instructions">{instructions}</div>
<div class="to-grid">{problems_html}</div>
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
    "errorAuditWorksheet": _render_error_audit,
    "tenFrameWorksheet": _render_ten_frame,
    "barGraphWorksheet": _render_bar_graph,
    "pictographWorksheet": _render_pictograph,
    "vennDiagramWorksheet": _render_venn_diagram,
    "handwritingWorksheet": _render_handwriting,
    "pixelCopyWorksheet": _render_pixel_copy,
    "alphabetWorksheet": _render_alphabet,
    "sequencingWorksheet": _render_sequencing,
    "fillInBlankWorksheet": _render_fill_in_the_blank,
    "storyMapWorksheet": _render_story_map,
    "numberLineWorksheet": _render_number_line,
    "labeledDiagramWorksheet": _render_labeled_diagram,
    "twoOperandWorksheet": _render_two_operand,
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
