"""
worksheet_layouts.py

Page-chrome layouts for printable worksheet packets.

A *layout* owns the furniture around a worksheet — the header, rails, progress
indicators, name/date row — but never the worksheet content itself.  Content is
rendered by ``worksheet_html_renderer`` and handed to a layout as an opaque HTML
string, so the two stay decoupled and no circular import is possible.

Adding a new layout:
  1. Write a ``_render_<name>_page(inner, meta, primary, light) -> str``.
  2. Write its CSS as a ``<style>`` string.
  3. Register a ``Layout`` in ``LAYOUTS``.

``classic`` is the historical look and is the default everywhere, so existing
packets render byte-identically unless a caller opts into another layout.

Layout ``meta`` keys (all optional unless noted):
  day_label     str   "Monday" — also drives the day colour palette
  title         str   main sheet title (journal: shown once, large)
  subtitle      str   italic line under the title
  rail_text     str   vertical spine text (journal; defaults to day_label)
  day_index     int   1-based position in the week, for progress pips
  total_days    int   pips to draw (default 5)
  status        dict  {"label", "hearts", "filled_halves", "reading"} health strip
  show_name_date bool draw the Name/Date rule (default True)
"""

from __future__ import annotations

import html as _html
from dataclasses import dataclass
from typing import Any, Callable

# ── Journal layout CSS ─────────────────────────────────────────────────────

JOURNAL_CSS = """\
<style>
  /* ── Journal layout ─────────────────────────────────────────────────── */
  .jr-sheet { display: flex; gap: 0.16in; }
  .jr-rail { flex: 0 0 0.26in; border-radius: 3px; position: relative; }
  .jr-rail-text {
    writing-mode: vertical-rl; transform: rotate(180deg);
    color: #fff; font-size: 8pt; font-weight: bold; letter-spacing: 0.16em;
    text-transform: uppercase; padding: 8px 0; width: 100%; text-align: center;
  }
  .jr-body { flex: 1; min-width: 0; }

  .jr-masthead { display: flex; align-items: flex-start; gap: 10px; margin-bottom: 3px; }
  .jr-mast-left { flex: 1; min-width: 0; }
  .jr-chip {
    display: inline-block; border-radius: 999px; padding: 1px 10px;
    font-size: 7.5pt; font-weight: bold; letter-spacing: 0.1em;
    text-transform: uppercase; color: #fff; margin-bottom: 3px;
  }
  .jr-title { font-size: 16pt; font-weight: bold; line-height: 1.12; }
  .jr-sub { font-size: 9pt; color: #666; font-style: italic; margin-top: 1px; }
  .jr-rule { height: 0; border-top: 2.5px solid; margin: 5px 0 2px; }
  .jr-rule-thin { height: 0; border-top: 1px solid; opacity: 0.45; margin-bottom: 9px; }

  .jr-pips { display: flex; gap: 4px; padding-top: 3px; }
  .jr-pip { width: 9px; height: 9px; border-radius: 50%; border: 1.5px solid; }

  .jr-status {
    display: flex; align-items: center; gap: 9px;
    border: 1.5px solid #d4d4d4; border-radius: 5px;
    padding: 5px 9px; margin-bottom: 9px; background: #fcfcfb;
    break-inside: avoid;
  }
  .jr-status-label {
    font-size: 8pt; color: #666; text-transform: uppercase;
    letter-spacing: 0.07em; flex: 0 0 auto;
  }
  .jr-hbar { display: flex; gap: 2px; flex: 1; }
  .jr-hbar .jr-h { flex: 1 1 0; height: 0.19in; border: 1.25px solid #7f1d1d; display: flex; }
  .jr-hbar .jr-h span { flex: 1 1 0; border-right: 1px dotted #7f1d1d; }
  .jr-hbar .jr-h span:last-child { border-right: none; }
  .jr-hbar .jr-h span.on { background: #fca5a5; }
  .jr-status-read { font-size: 9.5pt; font-weight: bold; flex: 0 0 auto; }

  .jr-meta { display: flex; gap: 16px; font-size: 8.5pt; color: #888; margin-bottom: 9px; }
  .jr-meta span { flex: 1; border-bottom: 1px solid #ccc; padding-bottom: 1px; }
  .jr-meta span.short { flex: 0 0 1.9in; }
</style>"""


# ── Helpers ────────────────────────────────────────────────────────────────


def _h(text: Any) -> str:
    return _html.escape(str(text))


def _pips(day_index: int, total_days: int, primary: str) -> str:
    if not day_index or not total_days:
        return ""
    dots = []
    for i in range(1, total_days + 1):
        fill = f"background:{primary};" if i <= day_index else ""
        dots.append(f'<div class="jr-pip" style="border-color:{primary};{fill}"></div>')
    return f'<div class="jr-pips">{"".join(dots)}</div>'


def _status_strip(status: dict) -> str:
    """Render the running health/progress strip. ``filled_halves`` counts half-units."""
    if not status:
        return ""
    hearts = int(status.get("hearts", 5))
    filled = int(status.get("filled_halves", 0))
    label = status.get("label", "")
    reading = status.get("reading", "")

    cells = []
    for i in range(hearts):
        left = "on" if filled >= i * 2 + 1 else ""
        right = "on" if filled >= i * 2 + 2 else ""
        cells.append(
            f'<div class="jr-h"><span class="{left}"></span><span class="{right}"></span></div>'
        )

    label_html = f'<div class="jr-status-label">{_h(label)}</div>' if label else ""
    read_html = f'<div class="jr-status-read">{_h(reading)}</div>' if reading else ""
    return (
        f'<div class="jr-status">{label_html}'
        f'<div class="jr-hbar">{"".join(cells)}</div>{read_html}</div>'
    )


def _name_date_row() -> str:
    return (
        '<div class="jr-meta"><span class="short">Name</span>'
        '<span class="short">Date</span></div>'
    )


# ── Layout renderers ───────────────────────────────────────────────────────


def _render_classic_page(inner: str, meta: dict, primary: str, light: str) -> str:
    """Classic layout: worksheet renderers already emit their own header/title."""
    return inner


def _render_journal_page(inner: str, meta: dict, primary: str, light: str) -> str:
    day_label = meta.get("day_label", "")
    title = meta.get("title", "")
    subtitle = meta.get("subtitle", "")
    rail_text = meta.get("rail_text") or day_label
    day_index = int(meta.get("day_index", 0) or 0)
    total_days = int(meta.get("total_days", 5) or 0)
    status = meta.get("status") or {}
    show_name_date = meta.get("show_name_date", True)

    chip = ""
    if day_index and total_days:
        chip = (
            f'<span class="jr-chip" style="background:{primary};">'
            f"Day {day_index} of {total_days}</span>"
        )
    elif day_label:
        chip = f'<span class="jr-chip" style="background:{primary};">{_h(day_label)}</span>'

    sub_html = f'<div class="jr-sub">{_h(subtitle)}</div>' if subtitle else ""
    title_html = f'<div class="jr-title">{_h(title)}</div>' if title else ""

    masthead = (
        f'<div class="jr-masthead">'
        f'<div class="jr-mast-left">{chip}{title_html}{sub_html}</div>'
        f"{_pips(day_index, total_days, primary)}"
        f"</div>"
        f'<div class="jr-rule" style="border-color:{primary};"></div>'
        f'<div class="jr-rule-thin" style="border-color:{primary};"></div>'
    )

    rail = (
        f'<div class="jr-rail" style="background:{primary};">'
        f'<div class="jr-rail-text">{_h(rail_text)}</div></div>'
    )

    body = masthead
    if show_name_date:
        body += _name_date_row()
    body += _status_strip(status)
    body += inner

    return f'<div class="jr-sheet">{rail}<div class="jr-body">{body}</div></div>'


# ── Registry ───────────────────────────────────────────────────────────────


@dataclass(frozen=True)
class Layout:
    """A page-chrome layout: extra CSS plus a page wrapper."""

    name: str
    css: str
    render_page: Callable[[str, dict, str, str], str]


LAYOUTS: dict[str, Layout] = {
    "classic": Layout("classic", "", _render_classic_page),
    "journal": Layout("journal", JOURNAL_CSS, _render_journal_page),
}

#: Layout names available to callers.
LAYOUT_NAMES: frozenset[str] = frozenset(LAYOUTS)


def get_layout(name: str | None) -> Layout:
    """Return the named layout, falling back to ``classic`` for None/unknown names."""
    if not name:
        return LAYOUTS["classic"]
    return LAYOUTS.get(name, LAYOUTS["classic"])
