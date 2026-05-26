# Phonics Blends Worksheets — Design Spec

**Date:** 2026-05-19
**Status:** Approved

## Summary

A standalone Python script that generates 4 print-ready HTML worksheet files covering phonics blends. Intended for a 3-year-old learning to sound out words. No interactive activities — each page is a word list to read aloud, with a subset of words broken into grapheme chunks to scaffold sounding-out.

## Output Files

All files written to `output/phonics_blends/`:

| File | Blend Family | Blends Covered | Target Word Count |
|------|-------------|----------------|-------------------|
| `01_l_blends.html` | L-blends | bl, cl, fl, gl, pl, sl | ~60 |
| `02_r_blends.html` | R-blends | br, cr, dr, fr, gr, pr, tr | ~70 |
| `03_s_blends.html` | S-blends | sc, sk, sm, sn, sp, st, sw | ~70 |
| `04_final_blends.html` | Final blends | nd, nt, st, sk, lk, mp | ~60 |

**Total: ~260 words. At least 10% (~26) displayed with grapheme chunks.**

## Page Layout

Each HTML file follows the existing project pattern:

- **Font:** OpenDyslexic (primary), Trebuchet MS / Arial fallback
- **Font size:** 20pt for words, 13pt for sub-headers
- **Page size:** US Letter, 0.45in top/bottom margins, 0.5in left/right margins
- **Auto-print:** `window.addEventListener("load", () => window.print())` trigger
- **Color scheme:** One accent color per blend family, drawn from the existing day palette:
  - L-blends → Blue (`#1d4ed8` / `#dbeafe`)
  - R-blends → Green (`#15803d` / `#dcfce7`)
  - S-blends → Purple (`#7c3aed` / `#ede9fe`)
  - Final blends → Orange (`#c2410c` / `#ffedd5`)

**Page structure (top to bottom):**
1. Full-width color header bar — blend family name (e.g., "L-Blends") + subtitle listing the blends covered (e.g., "bl · cl · fl · gl · pl · sl")
2. For each blend in the family: a sub-header (e.g., "bl words") followed by its word list
3. Words displayed in a 3-column CSS grid
4. Name line + date line at the bottom of each page (standard across all worksheets)

## Grapheme Chunk Format

Approximately 2–3 words per blend section are shown with the blend chunk visually separated:

```
bl · ue       cr · ab       st · op
```

- The blend letters are rendered in the page's accent color, bold weight
- The separator `·` (U+00B7 middle dot) is in a muted gray
- The remainder of the word is normal weight, black
- Regular (non-chunked) words are displayed as plain text at the same size

Chunked words are chosen to be short and decodable (CVC+blend structure preferred), e.g. `bl·ot`, `cr·ab`, `st·op` rather than complex vowel patterns.

## Script Structure

**File:** `scripts/generate_phonics_blends_series.py`

Follows the pattern of existing generators (e.g., `generate_mancala_math_series.py`):

1. Embed OpenDyslexic `@font-face` CSS block at the top of the script
2. Define word lists per blend as Python dicts — `{blend: [words]}` — with a separate dict marking which words get grapheme-chunk display and where the split point is
3. For each blend family, call a `_build_page_html(family_name, blends_dict, palette)` helper that assembles the full HTML document
4. Write each file to `output/phonics_blends/`
5. Print confirmation for each file written

## Word Selection Constraints

- All words must be real, common English words a 3-year-old would recognise or can be sounded out
- Prefer CVC or CCVC structure (short vowels) for accessibility
- Avoid multi-syllable words except where the blend is very clear (e.g., "blanket")
- Final blends: ensure words are monosyllabic where possible (hand, mint, desk)

## Out of Scope

- No images or picture matching
- No tracing lines or write-in activities
- No integration with the FastAPI backend or database
- No frontend UI changes
