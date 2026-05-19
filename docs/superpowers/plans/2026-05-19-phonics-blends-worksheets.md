# Phonics Blends Worksheets Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Generate 4 print-ready HTML phonics-blend word-list worksheets (~260 words total, ≥10% with grapheme-chunk markup) for a 3-year-old to sound out.

**Architecture:** A single standalone script `scripts/generate_phonics_blends_series.py` that builds 4 HTML files in `output/phonics_blends/`, following the same pattern as existing generators (font injection, `_CSS`/`_HTML_WRAPPER` from `worksheet_html_renderer`, auto-print on load). One file per blend family (L, R, S, Final). No changes to `src/`.

**Tech Stack:** Python 3, existing `src/worksheet_html_renderer._CSS/_HTML_WRAPPER`, OpenDyslexic font via absolute `file://` path, pytest for verification.

---

### Task 1: Write failing integration test

**Files:**
- Create: `tests/test_generate_phonics_blends.py`

- [ ] **Step 1: Write the test file**

```python
# tests/test_generate_phonics_blends.py
import os
import subprocess
import pytest

OUTPUT_DIR = "output/phonics_blends"
EXPECTED_FILES = [
    "01_l_blends.html",
    "02_r_blends.html",
    "03_s_blends.html",
    "04_final_blends.html",
]


@pytest.fixture(scope="module", autouse=True)
def run_script():
    result = subprocess.run(
        ["python", "scripts/generate_phonics_blends_series.py"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, f"Script failed:\n{result.stderr}"


def test_all_files_created():
    for fname in EXPECTED_FILES:
        path = os.path.join(OUTPUT_DIR, fname)
        assert os.path.exists(path), f"Missing output file: {path}"


def test_word_count_per_file():
    for fname in EXPECTED_FILES:
        content = open(os.path.join(OUTPUT_DIR, fname)).read()
        count = content.count('class="word"')
        assert count >= 25, f"{fname}: expected >=25 words, got {count}"


def test_grapheme_chunks_present():
    for fname in EXPECTED_FILES:
        content = open(os.path.join(OUTPUT_DIR, fname)).read()
        assert 'class="blend-part"' in content, f"{fname}: missing grapheme chunks"
        chunk_count = content.count('class="blend-part"')
        word_count = content.count('class="word"')
        assert chunk_count / word_count >= 0.10, (
            f"{fname}: chunk ratio {chunk_count}/{word_count} is below 10%"
        )


def test_opendyslexic_referenced():
    for fname in EXPECTED_FILES:
        content = open(os.path.join(OUTPUT_DIR, fname)).read()
        assert "OpenDyslexic" in content, f"{fname}: OpenDyslexic font not referenced"


def test_auto_print_present():
    for fname in EXPECTED_FILES:
        content = open(os.path.join(OUTPUT_DIR, fname)).read()
        assert "window.print()" in content, f"{fname}: missing auto-print trigger"
```

- [ ] **Step 2: Run tests to confirm they fail (script doesn't exist yet)**

```bash
pytest tests/test_generate_phonics_blends.py -v
```

Expected: FAIL — `AssertionError: Script failed` or `FileNotFoundError` because `scripts/generate_phonics_blends_series.py` does not exist yet.

- [ ] **Step 3: Commit the test**

```bash
git add tests/test_generate_phonics_blends.py
git commit -m "test: add failing integration tests for phonics blends generator"
```

---

### Task 2: Implement the generator script

**Files:**
- Create: `scripts/generate_phonics_blends_series.py`

- [ ] **Step 1: Create the script with all word data and HTML builder**

Create `scripts/generate_phonics_blends_series.py` with the following complete contents:

```python
"""
generate_phonics_blends_series.py

Phonics blends word-list worksheets for a 3-year-old.
Covers L-blends, R-blends, S-blends, and final blends.
~20% of words shown with grapheme-chunk markup to scaffold sounding-out.

Output: output/phonics_blends/  (4 HTML files, one per blend family)

Run from project root:
  python scripts/generate_phonics_blends_series.py
"""

import html as _html
import os
import sys

os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.abspath("src"))

from worksheet_html_renderer import _CSS, _HTML_WRAPPER  # noqa: E402

# ── Font injection ──────────────────────────────────────────────────────────

_FONT_FACE = """\
  @font-face {
    font-family: 'OpenDyslexic';
    src: local('OpenDyslexic'),
         url('file:///home/clates/.local/share/fonts/opendyslexic/OpenDyslexic-Regular.otf') format('opentype');
    font-weight: normal;
    font-style: normal;
  }
  @font-face {
    font-family: 'OpenDyslexic';
    src: local('OpenDyslexic Bold'),
         url('file:///home/clates/.local/share/fonts/opendyslexic/OpenDyslexic-Bold.otf') format('opentype');
    font-weight: bold;
    font-style: normal;
  }
"""

# ── Word data ───────────────────────────────────────────────────────────────
# Each blend entry: blend prefix/suffix, 10 words, 2 words to show chunked.
# For initial blends (final=False): split after len(blend) chars → bl·ue
# For final blends (final=True):   split before last len(blend) chars → ha·nd

FAMILIES = [
    {
        "filename": "01_l_blends.html",
        "title": "L-Blends",
        "subtitle": "bl · cl · fl · gl · pl · sl",
        "accent": "#1d4ed8",
        "bg": "#dbeafe",
        "final": False,
        "blends": [
            {
                "blend": "bl",
                "words": ["blue", "black", "blob", "blot", "blab", "blip", "blaze", "block", "blow", "blend"],
                "chunks": ["blot", "blob"],
            },
            {
                "blend": "cl",
                "words": ["clap", "clay", "clip", "clock", "clown", "club", "clean", "clog", "cluck", "clan"],
                "chunks": ["clap", "clip"],
            },
            {
                "blend": "fl",
                "words": ["flag", "flat", "flip", "flock", "fly", "flap", "flab", "flit", "fled", "flog"],
                "chunks": ["flip", "flit"],
            },
            {
                "blend": "gl",
                "words": ["glad", "glass", "glide", "glow", "glue", "glob", "glen", "glum", "glint", "glee"],
                "chunks": ["glad", "glob"],
            },
            {
                "blend": "pl",
                "words": ["plan", "play", "plop", "plug", "plus", "plum", "plot", "plod", "plank", "pluck"],
                "chunks": ["plop", "plug"],
            },
            {
                "blend": "sl",
                "words": ["slap", "slam", "slip", "slob", "slug", "sled", "slim", "slot", "slid", "slop"],
                "chunks": ["slap", "slid"],
            },
        ],
    },
    {
        "filename": "02_r_blends.html",
        "title": "R-Blends",
        "subtitle": "br · cr · dr · fr · gr · pr · tr",
        "accent": "#15803d",
        "bg": "#dcfce7",
        "final": False,
        "blends": [
            {
                "blend": "br",
                "words": ["brag", "brick", "brush", "brown", "bring", "brim", "bred", "brat", "brisk", "brew"],
                "chunks": ["brat", "brim"],
            },
            {
                "blend": "cr",
                "words": ["crab", "crack", "crop", "crow", "crush", "crib", "crisp", "cram", "crest", "crag"],
                "chunks": ["crab", "cram"],
            },
            {
                "blend": "dr",
                "words": ["drag", "drip", "drop", "drum", "drub", "drab", "drift", "drill", "dress", "drew"],
                "chunks": ["drip", "drop"],
            },
            {
                "blend": "fr",
                "words": ["frog", "frost", "from", "fresh", "fry", "frill", "fret", "frisk", "frock", "franc"],
                "chunks": ["frog", "fret"],
            },
            {
                "blend": "gr",
                "words": ["grab", "grass", "gray", "grin", "grip", "grub", "grit", "gram", "grim", "grew"],
                "chunks": ["grin", "grub"],
            },
            {
                "blend": "pr",
                "words": ["press", "prim", "prop", "prod", "prom", "prank", "prep", "prig", "prism", "prone"],
                "chunks": ["prim", "prop"],
            },
            {
                "blend": "tr",
                "words": ["trap", "tree", "trip", "trot", "truck", "trim", "track", "tram", "trek", "trick"],
                "chunks": ["trip", "trot"],
            },
        ],
    },
    {
        "filename": "03_s_blends.html",
        "title": "S-Blends",
        "subtitle": "sc · sk · sm · sn · sp · st · sw",
        "accent": "#7c3aed",
        "bg": "#ede9fe",
        "final": False,
        "blends": [
            {
                "blend": "sc",
                "words": ["scam", "scat", "scab", "scar", "scan", "scoff", "scold", "scone", "scope", "scorn"],
                "chunks": ["scam", "scab"],
            },
            {
                "blend": "sk",
                "words": ["skip", "skill", "skin", "sky", "skim", "skid", "skull", "sketch", "skunk", "skit"],
                "chunks": ["skip", "skid"],
            },
            {
                "blend": "sm",
                "words": ["small", "smash", "smell", "smile", "smoke", "smock", "smug", "smart", "smear", "smirk"],
                "chunks": ["smug", "smash"],
            },
            {
                "blend": "sn",
                "words": ["snag", "snap", "sniff", "snob", "snow", "snug", "sneak", "snore", "snip", "snarl"],
                "chunks": ["snap", "snip"],
            },
            {
                "blend": "sp",
                "words": ["span", "spin", "spit", "spot", "spur", "spell", "spill", "spoke", "sport", "speck"],
                "chunks": ["spin", "spot"],
            },
            {
                "blend": "st",
                "words": ["stop", "step", "stem", "star", "stir", "stamp", "stone", "store", "stab", "stuck"],
                "chunks": ["stop", "stem"],
            },
            {
                "blend": "sw",
                "words": ["swap", "swim", "swing", "sweet", "swept", "swell", "swift", "swab", "swipe", "swam"],
                "chunks": ["swim", "swam"],
            },
        ],
    },
    {
        "filename": "04_final_blends.html",
        "title": "Final Blends",
        "subtitle": "nd · nt · st · sk · lk · mp",
        "accent": "#c2410c",
        "bg": "#ffedd5",
        "final": True,
        "blends": [
            {
                "blend": "nd",
                "words": ["hand", "band", "wind", "bond", "bend", "find", "land", "mind", "sand", "end"],
                "chunks": ["hand", "bend"],
            },
            {
                "blend": "nt",
                "words": ["mint", "hint", "rent", "hunt", "tent", "dent", "pant", "punt", "font", "rant"],
                "chunks": ["mint", "tent"],
            },
            {
                "blend": "st",
                "words": ["best", "fast", "list", "most", "past", "rest", "dust", "fist", "mist", "last"],
                "chunks": ["best", "fast"],
            },
            {
                "blend": "sk",
                "words": ["ask", "desk", "dusk", "husk", "mask", "risk", "task", "brisk", "flask", "disk"],
                "chunks": ["desk", "mask"],
            },
            {
                "blend": "lk",
                "words": ["bulk", "hulk", "milk", "silk", "sulk", "talk", "walk", "elk", "folk", "yolk"],
                "chunks": ["milk", "bulk"],
            },
            {
                "blend": "mp",
                "words": ["bump", "camp", "damp", "dump", "jump", "lamp", "limp", "pump", "ramp", "hemp"],
                "chunks": ["jump", "bump"],
            },
        ],
    },
]

# ── HTML helpers ────────────────────────────────────────────────────────────


def _word_html(word: str, blend: str, is_final: bool, accent: str, is_chunk: bool) -> str:
    w = _html.escape(word)
    if not is_chunk:
        return f'<span class="word">{w}</span>'
    n = len(blend)
    if is_final:
        root = _html.escape(word[:-n])
        blend_part = _html.escape(word[-n:])
        return (
            f'<span class="word">'
            f'<span class="rest">{root}</span>'
            f'<span class="sep">·</span>'
            f'<span class="blend-part" style="color:{accent};font-weight:bold">{blend_part}</span>'
            f'</span>'
        )
    blend_part = _html.escape(word[:n])
    rest = _html.escape(word[n:])
    return (
        f'<span class="word">'
        f'<span class="blend-part" style="color:{accent};font-weight:bold">{blend_part}</span>'
        f'<span class="sep">·</span>'
        f'<span class="rest">{rest}</span>'
        f'</span>'
    )


def _build_family_page(family: dict) -> str:
    accent = family["accent"]
    bg = family["bg"]
    is_final = family["final"]

    css = _CSS.replace("<style>", f"<style>\n{_FONT_FACE}")
    css = css.replace(
        "font-family: 'Trebuchet MS', Arial, Helvetica, sans-serif;",
        "font-family: 'OpenDyslexic', 'Trebuchet MS', Arial, sans-serif;",
    )
    css = css.replace("font-size: 11pt;", "font-size: 13pt;")

    extra_css = f"""
    .family-header {{
      background: {accent};
      color: white;
      padding: 10px 16px;
      border-radius: 4px;
      margin-bottom: 18px;
    }}
    .family-header h1 {{
      font-size: 22pt;
      margin: 0 0 2px 0;
      font-weight: bold;
    }}
    .family-header .subtitle {{
      font-size: 13pt;
      opacity: 0.9;
      letter-spacing: 2px;
    }}
    .blend-section {{
      margin-bottom: 14px;
    }}
    .blend-subhead {{
      font-size: 11pt;
      font-weight: bold;
      color: {accent};
      text-transform: uppercase;
      letter-spacing: 1px;
      margin-bottom: 6px;
      border-bottom: 2px solid {bg};
      padding-bottom: 2px;
    }}
    .word-grid {{
      display: grid;
      grid-template-columns: repeat(3, 1fr);
      gap: 4px 12px;
    }}
    .word {{
      font-size: 20pt;
      line-height: 1.5;
      display: inline-block;
    }}
    .sep {{
      color: #9ca3af;
      font-size: 0.75em;
    }}
    .name-line {{
      margin-top: 20px;
      border-top: 1px solid #d1d5db;
      padding-top: 10px;
      display: flex;
      gap: 40px;
      font-size: 10pt;
      color: #6b7280;
    }}
    .name-field {{
      border-bottom: 1px solid #374151;
      min-width: 160px;
      display: inline-block;
    }}
"""
    css = css.replace("</style>", extra_css + "  </style>")

    sections = []
    for blend_info in family["blends"]:
        blend = blend_info["blend"]
        chunk_set = set(blend_info["chunks"])
        words_html = "\n      ".join(
            _word_html(w, blend, is_final, accent, w in chunk_set)
            for w in blend_info["words"]
        )
        sections.append(
            f'  <div class="blend-section">\n'
            f'    <div class="blend-subhead">{_html.escape(blend)} words</div>\n'
            f'    <div class="word-grid">\n      {words_html}\n    </div>\n'
            f'  </div>'
        )

    body = (
        '<div class="page">\n'
        f'  <div class="family-header">\n'
        f'    <h1>{_html.escape(family["title"])}</h1>\n'
        f'    <div class="subtitle">{_html.escape(family["subtitle"])}</div>\n'
        f'  </div>\n'
        + "\n".join(sections)
        + '\n  <div class="name-line">'
        + '\n    <span>Name: <span class="name-field">'
        + " " * 20
        + "</span></span>"
        + '\n    <span>Date: <span class="name-field">'
        + " " * 20
        + "</span></span>"
        + "\n  </div>"
        + "\n</div>"
        + '\n<script>window.addEventListener("load", () => window.print());</script>'
    )

    return _HTML_WRAPPER.format(
        title=_html.escape(family["title"]),
        css=css,
        body=body,
    )


# ── Entry point ─────────────────────────────────────────────────────────────


def main() -> None:
    out_dir = os.path.join("output", "phonics_blends")
    os.makedirs(out_dir, exist_ok=True)
    for family in FAMILIES:
        html = _build_family_page(family)
        path = os.path.join(out_dir, family["filename"])
        with open(path, "w", encoding="utf-8") as f:
            f.write(html)
        print(f"Wrote {path}")


if __name__ == "__main__":
    main()
```

- [ ] **Step 2: Run the script manually to check it executes without errors**

```bash
python scripts/generate_phonics_blends_series.py
```

Expected output:
```
Wrote output/phonics_blends/01_l_blends.html
Wrote output/phonics_blends/02_r_blends.html
Wrote output/phonics_blends/03_s_blends.html
Wrote output/phonics_blends/04_final_blends.html
```

If it errors, fix before proceeding.

---

### Task 3: Run tests, verify, and commit

- [ ] **Step 1: Run the full test suite**

```bash
pytest tests/test_generate_phonics_blends.py -v
```

Expected: All 5 tests PASS.
- `test_all_files_created` — 4 files exist
- `test_word_count_per_file` — ≥25 `class="word"` per file
- `test_grapheme_chunks_present` — ≥10% chunk ratio per file
- `test_opendyslexic_referenced` — font referenced in every file
- `test_auto_print_present` — `window.print()` in every file

If any test fails, fix the script and re-run.

- [ ] **Step 2: Spot-check one file visually (optional but recommended)**

```bash
# Open in browser to verify layout looks correct
xdg-open output/phonics_blends/01_l_blends.html
```

Verify: OpenDyslexic font loads, words display in 3-column grid at large size, grapheme-chunked words show blend in accent color with `·` separator, header bar correct color.

- [ ] **Step 3: Commit everything**

```bash
git add scripts/generate_phonics_blends_series.py tests/test_generate_phonics_blends.py output/phonics_blends/
git commit -m "feat: add phonics blends word-list worksheet generator

260 words across 4 blend families (L, R, S, Final).
~20% of words displayed with grapheme-chunk markup.
OpenDyslexic font, letter-size, auto-print on load."
```
