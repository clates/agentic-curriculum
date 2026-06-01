# Trucks & Trains Math Week — Design Spec

**Date:** 2026-06-01  
**Student:** Theodore, age 4, pre-K  
**Subject:** Addition & Subtraction within 20  
**Output dir:** `trucks_trains_week_series/`  
**Script:** `scripts/generate_trucks_trains_theodore_series.py`

---

## Goals

Replace the dino-math tracing/matching format with a more challenging worksheet style:
- Word problems with countable SVG vehicle illustrations (student derives the equation)
- Standard drill problems (vertical stacked and horizontal fill-in formats)
- Number range up to 20 throughout the week
- Trucks and trains as the vehicle theme, alternating by day

---

## Week Arc

| Day | Vehicle | Operation | Number Range | Accent Color |
|-----|---------|-----------|-------------|--------------|
| Mon | Trucks 🚛 | Addition intro | within 10 | Teal `#0e7490 → #075985` |
| Tue | Trains 🚂 | Addition push | within 20 | Orange `#c2410c → #9a3412` |
| Wed | Trucks 🚛 | Subtraction intro | within 10 | Purple `#6d28d9 → #4c1d95` |
| Thu | Trains 🚂 | Subtraction push | within 20 | Forest green `#166534 → #14532d` |
| Fri | Mixed 🚛🚂 | Both ops | within 20 | Gold `#b45309 → #92400e` |

---

## Per-Day Page Structure

Each day is **one HTML page** containing two sections.

### Section A — Word Problems (2 problems)

Each problem block:
1. **Story text** — 1–2 sentences, simple vocabulary, parent reads aloud. E.g.: *"Three yellow trucks are on the road. Two more drive up. How many trucks in all?"*
2. **SVG illustration** — vehicles drawn as individual countable objects:
   - Left group: N vehicles (Group 1)
   - Center: large `+` or `−` sign in red
   - Right group: M vehicles (Group 2, slightly different shade to distinguish)
   - For groups > 8: vehicles wrap to a second row
3. **Equation blanks**: `___ + ___ = ___` (student fills all three from counting the SVG)
   - The answer blank uses a red underline to distinguish it visually

### Section B — Drills (6 problems)

Separated from Section A by a styled divider ("Now solve these!").

Grid of 6 problems — **mix of vertical and horizontal format**, distributed across the week. Within each day, verticals are grouped first (rendered in a 3-col grid), horizontals follow (rendered in a 2-col grid), separated by a thin rule. This keeps each format visually coherent rather than interleaving them.

- **Mon:** 4 vertical + 2 horizontal
- **Tue:** 3 vertical + 3 horizontal
- **Wed:** 2 vertical + 4 horizontal
- **Thu:** 4 vertical + 2 horizontal
- **Fri:** 3 vertical + 3 horizontal

**Vertical format** (3-column grid):
```
  3
+ 2
───
___
```

**Horizontal format** (2-column grid):
```
4 + 5 = ___
```

All drill answer blanks use the same red underline as word problem answers for visual consistency.

---

## SVG Vehicle Library

Pure Python functions that return SVG string snippets (no external dependencies).

### `truck_svg(x, y, body_color, scale=1.0) -> str`

Draws one truck facing right at position `(x, y)`:
- Cab: small rect at front-top
- Body: wider rect below and behind cab
- Two wheels: dark circles
- Cab window: light blue rect

Bounding box at scale=1.0: **48px wide × 38px tall** (including wheels)

### `train_car_svg(x, y, body_color, scale=1.0) -> str`

Draws one train car:
- Rectangular body with two windows
- Coupling nub at right end
- Two wheels
- Optional smokestack on first car in a group (handled by caller)

Bounding box at scale=1.0: **52px wide × 36px tall** (including wheels)

### `vehicle_group_svg(draw_fn, count, color, x0, y0, col_width, max_per_row=5) -> tuple[str, int]`

Lays out `count` vehicles using `draw_fn` inside a fixed-width column.
- Vehicles are scaled to fit `max_per_row` across `col_width` (scale computed dynamically)
- Row height = scaled vehicle height + 8px gap
- Wraps to a new row after `max_per_row` vehicles
- Returns `(svg_snippets, actual_height_used)`

**Layout math:** Fixed viewbox width of **520px**. Two vehicle columns of **210px** each, a center operator zone of **100px**. Within each 210px column, up to 5 vehicles per row fit comfortably at scale ≈ 0.85 (truck: ~41px, gap: ~5px → 5 × 46 = 230px ≤ 210 with breathing room). Groups of 6–10 use two rows; 11–20 use three or four rows. Viewbox height = `max(left_rows, right_rows) × row_height + 24px padding`.

### `word_problem_svg(left_count, left_type, right_count, right_type, operator, accent_dark, accent_light) -> str`

Composes a full `<svg>` element for one word problem:
- Viewbox: `0 0 520 H` where H is computed from row wrapping (min 80px)
- Background: `#f8fafc` tinted rect
- Left group at x=5 via `vehicle_group_svg` — uses `accent_dark` color
- Operator sign (`+` or `−`) centered in the 100px middle zone, 28pt bold red `#dc2626`
- Right group at x=315 via `vehicle_group_svg` — uses `accent_light` color (a fixed lighter hex, specified per day, not computed)
- `width="100%"` so it scales to page width

Vehicle types: `"truck"` | `"train"`

**Per-day accent colors:**

| Day | `accent_dark` (left group) | `accent_light` (right group) |
|-----|---------------------------|------------------------------|
| Mon | `#0e7490` (teal) | `#22d3ee` (cyan) |
| Tue | `#c2410c` (orange) | `#fb923c` (peach) |
| Wed | `#6d28d9` (purple) | `#a78bfa` (lavender) |
| Thu | `#166534` (green) | `#4ade80` (lime) |
| Fri | alternates Mon/Thu colors per problem | same |

---

## Page Renderers

### `render_word_problem(number, story, svg_html, operator) -> str`

Returns HTML for one word problem block:
- Problem number + story text
- SVG element
- Equation blank row

### `render_drill_vertical(a, b, operator) -> str`

Returns HTML for one vertical drill problem card.

### `render_drill_horizontal(a, b, operator) -> str`

Returns HTML for one horizontal drill problem card.

### `render_day_page(day_label, title, accent, word_problems, drills) -> str`

Assembles a full day page:
- Day header
- Two word problem blocks
- Divider
- 6-problem drill grid (accepts a list of pre-rendered drill HTML strings)

### `build_week_ahead() -> str`

Week-ahead planning guide with 5-day card layout, materials list, and "Say this to start" callout per day. Follows same CSS/structure as `cars_trucks_week_series/00_week_ahead.html`.

---

## CSS

Self-contained — same OpenDyslexic CSS block as `generate_cars_trucks_theodore_series.py`, extended with:

```css
/* Word problem block */
.wp-block { border, rounded, padding }
.wp-story  { bold, 13pt }
.wp-svg-wrap { width: 100%, margin }
.wp-equation { flex row, 16pt bold, answer line in red }

/* Drill grid */
.drill-grid-3col { grid 3 cols }
.drill-grid-2col { grid 2 cols }
.drill-vertical   { card, centered, stacked operands }
.drill-horizontal { card, flex row, inline equation }
.drill-answer-line { red underline, 32px wide }
```

---

## Word Problem Bank

### Monday — Trucks, Addition within 10

1. *Three yellow trucks are on the road. Two more drive up. How many trucks in all?* `3 + 2 = 5`
2. *One big truck is at the gas station. Four more pull in. How many trucks are there now?* `1 + 4 = 5`

### Tuesday — Trains, Addition within 20

1. *Seven blue train cars sit on the track. Six more roll in. How many cars are on the track?* `7 + 6 = 13`
2. *Nine green train cars are at the depot. Eight more arrive. How many cars in all?* `9 + 8 = 17`

### Wednesday — Trucks, Subtraction within 10

1. *Eight red trucks are parked at the yard. Three trucks drive away. How many are left?* `8 − 3 = 5`
2. *Seven blue trucks are at the loading dock. Four leave. How many stay?* `7 − 4 = 3`

### Thursday — Trains, Subtraction within 20

1. *Fifteen train cars are on the track. Six roll away to the station. How many are left?* `15 − 6 = 9`
2. *Twelve orange train cars are at the depot. Five get sent away. How many remain?* `12 − 5 = 7`

### Friday — Mixed, within 20

1. *Six trucks are on the highway. Seven more join them. How many trucks are driving?* `6 + 7 = 13`
2. *Fourteen train cars are coupled together. Five get uncoupled. How many are left?* `14 − 5 = 9`

---

## Drill Problem Bank

### Monday — Addition within 10 (4 vertical, 2 horizontal)
Vertical: `3+2`, `5+4`, `6+1`, `4+3`  
Horizontal: `2+7=___`, `1+8=___`

### Tuesday — Addition within 20 (3 vertical, 3 horizontal)
Vertical: `8+5`, `9+6`, `7+8`  
Horizontal: `6+9=___`, `8+7=___`, `9+9=___`

### Wednesday — Subtraction within 10 (2 vertical, 4 horizontal)
Vertical: `9−4`, `8−3`  
Horizontal: `7−2=___`, `6−1=___`, `10−4=___`, `9−5=___`

### Thursday — Subtraction within 20 (4 vertical, 2 horizontal)
Vertical: `15−7`, `13−6`, `18−9`, `16−8`  
Horizontal: `14−5=___`, `17−9=___`

### Friday — Mixed within 20 (3 vertical, 3 horizontal)
Vertical: `8+6`, `15−7`, `9+8`  
Horizontal: `13−6=___`, `7+9=___`, `16−8=___`

---

## File Output

```
trucks_trains_week_series/
  00_week_ahead.html
  01_monday.html
  02_tuesday.html
  03_wednesday.html
  04_thursday.html
  05_friday.html
```

## Run Command

```bash
venv/bin/python3 scripts/generate_trucks_trains_theodore_series.py
```
