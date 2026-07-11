---
name: generate-week
description: Author a themed 5-day printable lesson week offline — Claude writes all content (no OpenAI key), renders via the HTML packet engine, and emits a student packet + teacher guide. Use when asked to generate a lesson week, unit, or worksheet packet ad hoc.
---

# Generate a themed lesson week

You author every passage, question, and worksheet yourself — there is no LLM API call. Quality of
the written content is the whole product; budget most of your effort there, not on plumbing.

## 0. Required reading

Read `AGENTS.md` first. You will need:
- §3 — the worksheet-type table: **only HTML-capable kinds** (camelCase, e.g. `readingWorksheet`)
  can go in a print packet, and the `feature_matrix` items-format gotcha (HTML wants plain strings).
- §2 — the "Instructional Pair" pattern (reading page + application page).
- §4 — pedagogy: "LET'S DISCUSS" closer with `response_lines: 0`, shuffled word banks/vocabulary,
  outdoor activity in `instructions`, and a consistent narrator character introduced on Day 1.

Then skim `scripts/generate_weather_week_series.py` — the tracked canonical example of this skill's
full output, including the embedded teacher guide.

**Exact field names per kind are NOT all documented in AGENTS.md.** Before writing data dicts for a
kind you haven't used, read its render function in `src/worksheet_html_renderer.py` (e.g.
`causeEffectWorksheet` takes `pairs` with `cause`/`effect`/`effect_lines`; `treeMapWorksheet`
supports an optional `columns` layout key; `matchingWorksheet` items may be strings or
`{"text": ...}` dicts).

## 1. Inputs

- **Theme** (required) — e.g. "weather", "ancient Egypt".
- Optional: age/grade, subject, standards. Default to the established audience (Christopher,
  age 6, grade K–1) if unspecified. If asked to align to standards, look them up in
  `standards_data/` or `curriculum.db`.

## 2. Design the week (before writing code)

- A 5-day **causal arc** — each day's concept builds on the previous (e.g. Sun → tilt → seasons →
  climate → biomes). Write the arc as one line; it goes in the script docstring.
- Per day: an **instructional pair** — a `readingWorksheet` plus one application worksheet
  (featureMatrix / treeMap / causeEffect / wordSort / matching / oddOneOut / tChart / frayerModel).
  Vary the application kinds across the week. Keep feature matrices to ≤6 properties so the
  printed table stays readable.
- Friday: a capstone that synthesizes the whole arc.
- Final page: a **Parent Feedback & Teaching Notes** page (a `readingWorksheet` whose questions ask
  the parent about comprehension, curiosity, and topics to revisit).
- Annotate each day with standards IDs in the docstring when standards were given.

## 3. Write the script

Create `scripts/generate_<theme>_week_series.py`. Canonical skeleton (ruff already exempts
`scripts/*.py` from E402, so the `os.chdir` preamble is fine):

```python
"""
<Theme> — Week Series
Grade <X> | <Subject> | Causal Arc: <one line>

Standards:
  Monday — <ids>  (<concept>)
  ...
"""

import os

os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import sys
from pathlib import Path

sys.path.insert(0, os.path.abspath("src"))

from worksheet_html_renderer import build_print_packet_html, render_worksheet_html


def generate_<theme>_week_series():
    output_dir = Path("<theme>_week_series")
    output_dir.mkdir(exist_ok=True)
    pages: list[tuple[str, str]] = []

    def add(kind: str, data: dict, day_label: str) -> None:
        fragment = render_worksheet_html(kind, data, day_label)
        if fragment is None:
            raise ValueError(f"No HTML renderer for kind={kind!r}")
        pages.append((day_label, fragment))

    # MONDAY ... FRIDAY: add(...) calls, then the parent-feedback page

    html = build_print_packet_html(pages, packet_title="<Theme> Week — <subtitle>")
    (output_dir / "<theme>_week.html").write_text(html, encoding="utf-8")

    TEACHER_GUIDE = """<!DOCTYPE html>..."""  # see step 4
    (output_dir / "<theme>_week_teacher_guide.html").write_text(TEACHER_GUIDE, encoding="utf-8")

    print(f"Generated {len(pages)} pages -> {output_dir}/")
    # then print a one-line label per page (the manifest)


if __name__ == "__main__":
    generate_<theme>_week_series()
```

`scripts/generate_weather_week_series.py` is the tracked, canonical realization of this skeleton.
`scripts/reference/` (gitignored, may not exist on every machine) holds older bespoke one-offs —
skimmable if present, but not canonical.

## 4. Teacher guide — emitted by the same script

Output directories are gitignored; the script is the only tracked artifact and must reproduce the
entire week. Embed the guide as an HTML string in the script and write it alongside the packet.
Contents per day: answer key for every question/cell, guidance for the "LET'S DISCUSS" prompt,
misconceptions to watch for, and one extension activity. Model the document structure and CSS on
the teacher guide embedded in `scripts/generate_weather_week_series.py` (self-contained HTML,
day-color headings matching the packet palette).

## 5. Run and validate

```bash
venv/bin/python scripts/generate_<theme>_week_series.py
```

- Exit 0 (the `add()` helper raises on any unknown kind — an exception means a bad kind or field).
- Printed page count matches your design (typically 11: 5×2 + feedback page).
- Both HTML files exist and are non-trivially sized (packet is typically 40–60 KB).
- Read back one or two fragments from the packet HTML to spot-check content landed in the right
  fields (e.g. vocabulary in the sidebar, `response_lines: 0` rendered without write-in lines).
- Tell the user to open the packet in a browser — the print dialog opens automatically.

**No tests are required for generated weeks** — the validation above is sufficient.

## 6. Commit

Before committing, run `venv/bin/python -m ruff check --fix` and `venv/bin/python -m black` on the
script (pre-commit enforces both; f-strings without placeholders are a common miss), then re-run
the script once to confirm it still generates.

Commit the script only (outputs are gitignored), on a branch with a PR per AGENTS.md §7:
`feat: <theme> week — <arc summary>`.
