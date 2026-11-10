"""
Truck Depot — Week Series: "Theodore's Truck Depot"
Grade 1 | Mathematics (place value) | Causal Arc: Pack boxes into crates of ten (count by tens)
  → the shipping label tells the cargo (tens digit = crates, ones digit = loose boxes)
  → trade 10 loose boxes for a crate (and 10 more / 10 less) → check the crates first to compare
  → Dispatch Day capstone: fill real orders, and pick amounts that make sense (5, 50, 500)

No narrator mascot: Theodore IS the dispatcher. Every passage speaks to him ("You are the
dispatcher...") and every practice sheet is a depot work order he fills.

Runs Tuesday → Saturday (no Monday this week). Manipulatives come from
scripts/generate_depot_cargo_cutouts.py — 1×10 long crates, 2×5 stack crates, 1×1 loose boxes and
the Loading Dock mat — and this script emits them alongside the packet. The crate pictures in the
packet use the same colours as the cutouts (amber tens, blue ones).

Three depot rules recur all week:
  1. Every crate holds exactly 10.
  2. Never park 10 loose boxes — trade them for a crate.
  3. Check the crates first.

Output: depot_week_series/
  depot_week.html                (student packet)
  depot_week_teacher_guide.html  (prep, answer keys, discussion guidance, misconceptions)
  depot_cargo_cutouts.html       (print on cardstock, cut before Tuesday)

Standards (Virginia SOL, verified against curriculum.db):
  Tuesday   — VA.MATH.1.1.2 (a), VA.MATH.1.1.1 (d)   (group into tens and ones; count by tens)
  Wednesday — VA.MATH.1.1.2 (a), VA.MATH.1.1.1 (b)   (write the numeral for tens and ones)
  Thursday  — VA.MATH.1.1.2 (a), VA.MATH.1.1.1 (d)   (regroup 10 ones as a ten; count by tens
              from any number); stretch: VA.MATH.2.2.1 (b) (10 more, 10 less)
  Friday    — VA.MATH.1.1.2 (b), VA.MATH.1.1.2 (c)   (compare with greater than / less than /
              equal to; order three numbers)
  Saturday  — VA.MATH.1.1.5 (a, b), VA.MATH.1.1.2 (a–c), VA.MATH.1.1.6  (capstone: reasonable
              magnitude 5 / 50 / 500; mixed place value; a story problem within 20)
"""

import os

os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import random
import sys
from pathlib import Path

sys.path.insert(0, os.path.abspath("src"))
sys.path.insert(0, os.path.abspath("scripts"))

from generate_depot_cargo_cutouts import build_html as build_cutouts_html
from worksheet_html_renderer import build_print_packet_html, get_day_palette, render_worksheet_html

# Same colours as the cardstock cutouts, so the pictures match what is on the table.
TEN_FILL, TEN_LINE = "#fde68a", "#92400e"
ONE_FILL, ONE_LINE = "#bfdbfe", "#1e3a8a"

DEPOT_CSS = """
<style>
  body { counter-reset: sheet; }
  .page { counter-increment: sheet; }
  .page::before {
    content: "THEODORE'S TRUCK DEPOT  \\00B7  DISPATCH OFFICE  \\00B7  SHEET " counter(sheet);
    display: block; font-size: 7.5pt; font-weight: bold; letter-spacing: 0.16em;
    color: #92400e; border-bottom: 2px dashed #d6a24a; padding-bottom: 4px; margin-bottom: 6px;
  }
  .dp-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 10px 12px; }
  .dp-grid.three { grid-template-columns: 1fr 1fr 1fr; }
  .dp-grid.four { grid-template-columns: 1fr 1fr 1fr 1fr; }
  .dp-card { border: 2px solid #333; border-radius: 6px; padding: 5px 8px 7px;
    break-inside: avoid; }
  .dp-no { font-size: 7.5pt; font-weight: bold; letter-spacing: 0.12em; color: #666;
    text-transform: uppercase; }
  .dp-pic { display: flex; justify-content: center; align-items: flex-end; margin: 4px 0; }
  .dp-line { font-size: 11.5pt; margin-top: 6px; line-height: 2.1; }
  .dp-blank { display: inline-block; width: 0.5in; height: 0.38in; border: 2px solid #111;
    border-radius: 4px; vertical-align: middle; margin: 0 3px; background: #fff; }
  .dp-blank.wide { width: 0.75in; }
  .dp-draw { border: 1.5px dashed #888; height: 1.4in; border-radius: 4px; margin: 4px 0; }
  .dp-label { display: inline-block; font-size: 22pt; font-weight: bold; border: 3px solid #111;
    border-radius: 6px; padding: 0 12px; background: #fff; line-height: 1.3; }
  .dp-label small { font-size: 7pt; letter-spacing: 0.1em; display: block; color: #666;
    line-height: 1.2; padding-top: 2px; }
  .dp-h { font-size: 11pt; font-weight: bold; margin: 12px 0 6px;
    border-bottom: 1px solid #bbb; padding-bottom: 2px; }
  .dp-choice { display: inline-block; border: 1.5px solid #555; border-radius: 14px;
    padding: 0 9px; margin: 0 2px; font-size: 10pt; line-height: 1.6; }
  .dp-strip { display: flex; gap: 5px; justify-content: center; margin: 6px 0; }
  .dp-strip span { width: 0.6in; height: 0.48in; border: 2px solid #111; border-radius: 4px;
    display: flex; align-items: center; justify-content: center; font-size: 14pt;
    font-weight: bold; }
  .dp-strip span.empty { background: #fffbeb; }
  .dp-rule { background: #fef3c7; border-left: 5px solid #b45309; padding: 5px 10px;
    font-size: 10pt; margin: 6px 0 10px; border-radius: 0 4px 4px 0; }
  table.dp-table { border-collapse: collapse; margin: 0 auto; }
  table.dp-table th { background: #2c2c2c; color: #fff; font-size: 10pt; padding: 4px 18px; }
  table.dp-table td { border: 1.5px solid #555; height: 0.52in; width: 1.3in; text-align: center;
    font-size: 15pt; font-weight: bold; }
  .dp-order3 { display: flex; align-items: center; gap: 6px; justify-content: center;
    font-size: 12pt; }
</style>
"""


# ── Cargo pictures ─────────────────────────────────────────────────────────


def _crate(x: float, floor: float, u: float, style: str) -> tuple[str, float]:
    """One crate of ten standing on `floor`: 'L' = 1×10 long crate, 'S' = 2×5 stack crate."""
    cols, rows = (1, 10) if style == "L" else (2, 5)
    w, h = cols * u, rows * u
    top = floor - h
    lines = "".join(
        f'<line x1="{x}" y1="{top + r * u}" x2="{x + w}" y2="{top + r * u}"/>'
        for r in range(1, rows)
    ) + "".join(
        f'<line x1="{x + c * u}" y1="{top}" x2="{x + c * u}" y2="{floor}"/>' for c in range(1, cols)
    )
    svg = (
        f'<rect x="{x}" y="{top}" width="{w}" height="{h}" fill="{TEN_FILL}"/>'
        f'<g stroke="{TEN_LINE}" stroke-width="0.6" stroke-dasharray="1.5 1.5">{lines}</g>'
        f'<rect x="{x}" y="{top}" width="{w}" height="{h}" fill="none" stroke="#111" '
        f'stroke-width="1.6"/>'
    )
    return svg, w


def _one(x: float, y: float, u: float) -> str:
    return (
        f'<rect x="{x}" y="{y}" width="{u}" height="{u}" fill="{ONE_FILL}" stroke="{ONE_LINE}" '
        f'stroke-width="1.3"/>'
    )


def cargo_svg(tens: int, ones: int, u: float = 11, styles: str = "L") -> str:
    """Crates left to right, then loose boxes stacked from the floor up in columns of 5."""
    gap, pad = 4, 3
    floor = (10 * u if tens else 5 * u) + pad
    parts, x = [], pad
    for i in range(tens):
        svg, w = _crate(x, floor, u, styles[i % len(styles)])
        parts.append(svg)
        x += w + gap
    if tens and ones:
        x += 8
    for i in range(ones):
        col, row = divmod(i, 5)
        parts.append(_one(x + col * (u + 2), floor - (row + 1) * (u + 1), u))
    if ones:
        x += ((ones - 1) // 5 + 1) * (u + 2)
    width = max(x + pad, 20)
    return (
        f'<svg width="{width}" height="{floor + pad}" viewBox="0 0 {width} {floor + pad}" '
        f'xmlns="http://www.w3.org/2000/svg">{"".join(parts)}</svg>'
    )


def scatter_svg(n: int, seed: int, cols: int = 9, rows: int = 5) -> str:
    """n loose boxes tumbled off a truck: a jittered, rotated grid so nothing overlaps."""
    rng = random.Random(seed)
    u, cell, pad = 17, 33, 6
    slots = rng.sample(range(cols * rows), n)
    parts = []
    for s in slots:
        r, c = divmod(s, cols)
        x = pad + c * cell + rng.uniform(0, cell - u - 6)
        y = pad + r * cell + rng.uniform(0, cell - u - 6)
        angle = rng.uniform(-18, 18)
        parts.append(
            f'<g transform="rotate({angle:.1f} {x + u / 2:.1f} {y + u / 2:.1f})">'
            f"{_one(round(x, 1), round(y, 1), u)}</g>"
        )
    w, h = pad * 2 + cols * cell, pad * 2 + rows * cell
    return (
        f'<svg width="{w}" height="{h}" viewBox="0 0 {w} {h}" '
        f'xmlns="http://www.w3.org/2000/svg">{"".join(parts)}</svg>'
    )


# ── Page building blocks ───────────────────────────────────────────────────

BLANK = '<span class="dp-blank"></span>'
WIDE = '<span class="dp-blank wide"></span>'


def choices(*words: str) -> str:
    return " ".join(f'<span class="dp-choice">{w}</span>' for w in words)


def card(no: str, body: str) -> str:
    return f'<div class="dp-card"><div class="dp-no">{no}</div>{body}</div>'


def pic(svg: str) -> str:
    return f'<div class="dp-pic">{svg}</div>'


def label(text: object) -> str:
    return f'<div class="dp-label"><small>SHIPPING LABEL</small>{text}</div>'


def strip(cells: list[object]) -> str:
    """A count-by strip; None cells are empty boxes to fill in."""
    inner = "".join(
        '<span class="empty"></span>' if c is None else f"<span>{c}</span>" for c in cells
    )
    return f'<div class="dp-strip">{inner}</div>'


def custom_page(day: str, title: str, instructions: str, body: str) -> str:
    primary, _ = get_day_palette(day)
    return f"""
<div class="day-header" style="background:{primary};">
  <div class="day-header-label">{day}</div><div class="day-header-title">{title}</div>
</div>
<div class="ws-title" style="color:{primary};border-bottom-color:{primary};">{title}</div>
<div class="name-date-row"><span>Dispatcher:&nbsp;&nbsp;___________________________</span>
<span class="short">Date:&nbsp;&nbsp;_______________</span></div>
<div class="ws-instructions">{instructions}</div>
{body}
"""


def generate_depot_week_series():
    output_dir = Path("depot_week_series")
    output_dir.mkdir(exist_ok=True)
    pages: list[tuple[str, str]] = []

    def add(kind: str, data: dict, day_label: str) -> None:
        fragment = render_worksheet_html(kind, data, day_label)
        if fragment is None:
            raise ValueError(f"No HTML renderer for kind={kind!r}")
        pages.append((day_label, fragment))

    def add_custom(day: str, title: str, instructions: str, body: str) -> None:
        pages.append((day, custom_page(day, title, instructions, body)))

    # =========================================================================
    # TUESDAY — Crates of Ten
    # Standards: VA.MATH.1.1.2 (a), VA.MATH.1.1.1 (d) — group into tens; count by tens
    # =========================================================================

    add(
        "readingWorksheet",
        {
            "title": "Tuesday: Welcome, Dispatcher!",
            "passage_title": "Theodore's Truck Depot Opens",
            "instructions": (
                "Hands-on first (30 min): The Big Delivery! Dump 40–60 small things on the table "
                '— LEGO bricks, dry pasta, toy cars. Ask Theodore "How many?" and let him start '
                "counting one by one. Then show him the depot way: pack groups of 10 into cups or "
                "zip bags (crates). Count the crates by tens — 10, 20, 30 — then count on the "
                "loose ones. Which way was easier? Last, open the cargo cutouts: lay 10 loose "
                "boxes on a long crate, then on a stack crate. Same size — both are 10!"
            ),
            "passage": (
                "You are the dispatcher at Theodore's Truck Depot. Trucks bring boxes in, and "
                "trucks take boxes out. Your job is to know how many boxes are on every truck.\n\n"
                "Counting boxes one at a time is slow. If someone bumps you at box 27, you have "
                "to start all over again!\n\n"
                "So the depot has a rule: pack the boxes into crates. Every crate holds exactly "
                "10 boxes. Not 9. Not 11. Always 10.\n\n"
                "Now counting is fast. Count the crates by tens: 10, 20, 30. Then count the loose "
                "boxes on: 31, 32. Three crates and two loose boxes is 32 boxes.\n\n"
                "The depot has two kinds of crates. A long crate is 1 box wide and 10 boxes long. "
                "A stack crate is 2 rows of 5. They look different, but they both hold 10 boxes."
            ),
            "questions": [
                {"prompt": "How many boxes are in one crate?", "response_lines": 1},
                {"prompt": "Count by tens. How many boxes are in 4 crates?", "response_lines": 1},
                {
                    "prompt": "A truck has 2 crates and 5 loose boxes. How many boxes is that?",
                    "response_lines": 1,
                },
                {
                    "prompt": "Why does the depot pack boxes into crates?",
                    "response_lines": 2,
                },
                {
                    "prompt": (
                        "LET'S DISCUSS: A new worker says, \"The long crate holds more boxes. "
                        "It's longer!\" Is that right? How could you prove it with your cutouts?"
                    ),
                    "response_lines": 0,
                },
            ],
            "vocabulary": [
                {"term": "loose box", "definition": "one box that is not packed in a crate yet"},
                {"term": "dispatcher", "definition": "the boss who keeps track of every box"},
                {"term": "count by tens", "definition": "10, 20, 30, 40 … one number per crate"},
                {"term": "crate", "definition": "holds exactly 10 boxes — always 10"},
            ],
        },
        "Tuesday",
    )

    tue_scatter = [(14, 101), (20, 102), (26, 103), (33, 104)]
    add_custom(
        "Tuesday",
        "Pack the Crates",
        "Boxes fell off the truck! Circle groups of 10 to pack them into crates. Cross off each box "
        "as you count it so you never count a box twice. Then fill in the work order.",
        '<div class="dp-rule"><b>Depot Rule 1:</b> every crate holds exactly 10.</div>'
        + '<div class="dp-grid">'
        + "".join(
            card(
                f"Work order {i}",
                pic(scatter_svg(n, seed))
                + f'<div class="dp-line">{BLANK} crates and {BLANK} loose boxes<br>'
                f"That is {WIDE} boxes.</div>",
            )
            for i, (n, seed) in enumerate(tue_scatter, 1)
        )
        + "</div>",
    )

    tue_tens = [(2, "L"), (5, "L"), (8, "LS"), (10, "L")]
    tue_strip = [0, 10, None, 30, None, 50, None, None, 80, None, 100]
    tue_mixed = [(2, 4, "L"), (4, 7, "S"), (1, 6, "L")]
    add_custom(
        "Tuesday",
        "Count the Crates by Tens",
        "Touch each crate and count by tens: 10, 20, 30… Then count on the loose boxes by ones.",
        '<div class="dp-h">A. Crates only — how many boxes?</div><div class="dp-grid four">'
        + "".join(
            card(
                chr(64 + i),
                pic(cargo_svg(t, 0, u=8.5, styles=s)) + f'<div class="dp-line">{WIDE} boxes</div>',
            )
            for i, (t, s) in enumerate(tue_tens, 1)
        )
        + "</div>"
        + '<div class="dp-h">B. Fill in the missing numbers. Count by tens!</div>'
        + strip(tue_strip)
        + '<div class="dp-h">C. Crates AND loose boxes — count the crates by tens, then count '
        "on.</div>"
        + '<div class="dp-grid three">'
        + "".join(
            card(
                chr(67 + i),
                pic(cargo_svg(t, o, u=10, styles=s))
                + f'<div class="dp-line">{BLANK} crates {BLANK} loose<br>= {WIDE} boxes</div>',
            )
            for i, (t, o, s) in enumerate(tue_mixed, 1)
        )
        + "</div>",
    )

    # =========================================================================
    # WEDNESDAY — The Label Tells the Cargo
    # Standards: VA.MATH.1.1.2 (a), VA.MATH.1.1.1 (b) — tens and ones; write the numeral
    # =========================================================================

    wed_cards = [34, 52, 17, 60, 8, 45, 71, 26]
    add(
        "readingWorksheet",
        {
            "title": "Wednesday: The Label Tells the Cargo",
            "passage_title": "Reading a Shipping Label",
            "instructions": (
                "Hands-on first (30 min): Fill the Orders! Write these work orders on index cards: "
                + ", ".join(map(str, wed_cards))
                + ". Shuffle them. Theodore draws a card, loads the Loading Dock mat (crates in "
                'the TENS bay, loose boxes in the ONES bay) and reads it back to you: "3 tens '
                'and 4 ones is 34." You check it. Then switch jobs: you load the dock, and '
                "Theodore writes the shipping label."
            ),
            "passage": (
                "Every truck that leaves the depot gets a shipping label. The label is a number, "
                "and the number tells you exactly what is on the truck.\n\n"
                "Look at the label 34. The 3 is in the tens place. It means 3 crates. The 4 is in "
                "the ones place. It means 4 loose boxes. So 34 is 3 tens and 4 ones. That is "
                "30 + 4.\n\n"
                "The order of the digits matters! The label 43 means 4 crates and 3 loose boxes. "
                "34 and 43 use the same digits, but they are different trucks.\n\n"
                "What about the label 50? That truck has 5 crates and 0 loose boxes. The 0 is "
                "important. It holds the ones place, so the 5 stays in the tens place. Without "
                "the 0, the label would say 5 — just five loose boxes!"
            ),
            "questions": [
                {
                    "prompt": "Look at the label 52. How many crates? How many loose boxes?",
                    "response_lines": 1,
                },
                {
                    "prompt": "A truck has 6 crates and 1 loose box. What does its label say?",
                    "response_lines": 1,
                },
                {
                    "prompt": "Which digit tells you the crates — the left one or the right one?",
                    "response_lines": 1,
                },
                {"prompt": "What does the 0 in 70 tell you?", "response_lines": 1},
                {
                    "prompt": (
                        "LET'S DISCUSS: A truck has 1 crate and 0 loose boxes. What is its label? "
                        "What about 1 crate and 7 loose boxes? What do you notice?"
                    ),
                    "response_lines": 0,
                },
            ],
            "vocabulary": [
                {"term": "ones place", "definition": "the right digit — it counts loose boxes"},
                {
                    "term": "shipping label",
                    "definition": "the number that tells what is on a truck",
                },
                {"term": "digit", "definition": "one of the number symbols 0 to 9"},
                {"term": "zero", "definition": "holds a place when there are none"},
                {"term": "tens place", "definition": "the left digit — it counts crates"},
            ],
        },
        "Wednesday",
    )

    wed_read = [(3, 4, "L"), (1, 6, "S"), (5, 0, "L"), (4, 3, "LS"), (0, 8, "L"), (7, 2, "S")]
    add_custom(
        "Wednesday",
        "Read the Truck, Write the Label",
        "Count the crates (tens) and the loose boxes (ones). Then write the shipping label.",
        '<div class="dp-grid">'
        + "".join(
            card(
                f"Truck {i}",
                pic(cargo_svg(t, o, u=11, styles=s))
                + f'<div class="dp-line">{BLANK} tens and {BLANK} ones &nbsp; Label: {WIDE}</div>',
            )
            for i, (t, o, s) in enumerate(wed_read, 1)
        )
        + "</div>",
    )

    wed_orders = [25, 41, 13, 60, 38, 9]
    add_custom(
        "Wednesday",
        "Fill the Work Orders",
        "Draw the cargo for each label: a long stick | for each crate and a small square □ for each "
        "loose box. Then fill in the blanks.",
        '<div class="dp-grid">'
        + "".join(
            card(
                f"Order {i}",
                label(n)
                + '<div class="dp-draw" style="height:0.85in"></div>'
                + f'<div class="dp-line">{BLANK} tens and {BLANK} ones<br>'
                f"{WIDE} + {BLANK} = {n}</div>",
            )
            for i, n in enumerate(wed_orders, 1)
        )
        + "</div>",
    )

    # =========================================================================
    # THURSDAY — Trade Day
    # Standards: VA.MATH.1.1.2 (a), VA.MATH.1.1.1 (d); stretch VA.MATH.2.2.1 (b)
    # =========================================================================

    add(
        "readingWorksheet",
        {
            "title": "Thursday: Trade Day",
            "passage_title": "Never Park 10 Loose Boxes",
            "instructions": (
                "Hands-on first (30 min): The Trading Game! Start with an empty Loading Dock mat "
                "and a warehouse pile of crates and loose boxes. Take turns rolling a die and "
                "adding that many loose boxes to your dock. The moment you have 10 loose boxes, "
                'shout "TRADE!" and swap them for 1 crate. Say your total after every turn '
                '("2 tens and 3 ones — 23!"). First dispatcher to 5 crates (50) wins. Two dice '
                "make it faster."
            ),
            "passage": (
                "The depot has a second rule: never park 10 loose boxes. Ten loose boxes take up "
                "too much room. As soon as you have 10, pack them into a crate. That is called a "
                "trade: 10 ones for 1 ten.\n\n"
                "A truck pulls in with 2 crates and 13 loose boxes. That is messy! Pack 10 of the "
                "loose boxes into a new crate. Now the truck has 3 crates and 3 loose boxes. The "
                "label is 33. Nothing got lost. It is the same 33 boxes, just packed better.\n\n"
                "Remember the Ten Stop? 8 + 5 is 8 loose boxes and 5 more. Pack 10 into a crate, "
                "and 3 are left over. 1 ten and 3 ones is 13.\n\n"
                "When a truck brings 1 more crate, the depot has 10 more boxes. Only the tens "
                "digit changes: 34 becomes 44. When a crate leaves, there are 10 fewer: 34 "
                "becomes 24."
            ),
            "questions": [
                {
                    "prompt": "How many loose boxes do you trade for one crate?",
                    "response_lines": 1,
                },
                {
                    "prompt": "A truck has 1 crate and 12 loose boxes. After the trade, what is "
                    "the label?",
                    "response_lines": 1,
                },
                {"prompt": "What is 10 more than 34?", "response_lines": 1},
                {
                    "prompt": "When a crate leaves, which digit changes — tens or ones?",
                    "response_lines": 1,
                },
                {
                    "prompt": (
                        "LET'S DISCUSS: A truck has 4 crates and 0 loose boxes. A customer wants "
                        "just 3 boxes. How can the dispatcher give them 3 boxes?"
                    ),
                    "response_lines": 0,
                },
            ],
            "vocabulary": [
                {"term": "10 less", "definition": "one fewer crate — the tens digit goes down 1"},
                {"term": "unpack", "definition": "open a crate into 10 loose boxes"},
                {"term": "trade", "definition": "swap 10 loose boxes for 1 crate"},
                {"term": "10 more", "definition": "one more crate — the tens digit goes up 1"},
            ],
        },
        "Thursday",
    )

    thu_trade = [(2, 12), (1, 15), (4, 10), (3, 11), (0, 14)]
    thu_trade_text = (5, 16)
    trade_line = (
        f'<div class="dp-line">Trade! Now {BLANK} crates {BLANK} loose<br>Label: {WIDE}</div>'
    )
    add_custom(
        "Thursday",
        "Trade It In",
        "Someone parked 10 or more loose boxes! Circle 10 loose boxes and trade them for a crate. "
        "Use your cutouts if it helps. Then write the new work order.",
        '<div class="dp-rule"><b>Depot Rule 2:</b> never park 10 loose boxes — trade them for a '
        "crate.</div>"
        + '<div class="dp-grid">'
        + "".join(
            card(
                f"Truck {i} &nbsp;·&nbsp; {t} crate{'' if t == 1 else 's'}, {o} loose boxes",
                pic(cargo_svg(t, o, u=10)) + trade_line,
            )
            for i, (t, o) in enumerate(thu_trade, 1)
        )
        + card(
            "Truck 6 &nbsp;·&nbsp; no picture!",
            f'<div class="dp-line" style="font-size:13pt;margin:8px 0 18px;">'
            f"{thu_trade_text[0]} crates and {thu_trade_text[1]} loose boxes</div>" + trade_line,
        )
        + "</div>",
    )

    thu_table = [34, 57, 20, 18, 65, 89, 40]
    thu_strips = [
        [3, 13, None, 33, None, None, 63, None, None],
        [6, 16, 26, None, None, None, None, None, None],
    ]
    thu_story = [
        ("The depot has 26 boxes. 1 crate arrives. Then 2 more crates arrive. How many boxes now?"),
        ("A truck has 71 boxes. 3 crates leave. How many boxes are left?"),
    ]
    add_custom(
        "Thursday",
        "10 More, 10 Less",
        "A crate arriving is 10 more. A crate leaving is 10 less. Only the tens digit changes!",
        '<div class="dp-h">A. Fill in the delivery log.</div>'
        + '<table class="dp-table"><tr><th>10 less (a crate leaves)</th><th>Truck</th>'
        "<th>10 more (a crate arrives)</th></tr>"
        + "".join(
            f"<tr><td></td><td style='background:{TEN_FILL}'>{n}</td><td></td></tr>"
            for n in thu_table
        )
        + "</table>"
        + '<div class="dp-h">B. Crate parade — count by tens, starting anywhere!</div>'
        + "".join(strip(s) for s in thu_strips)
        + '<div class="dp-h">C. Delivery stories</div>'
        + '<div class="dp-grid">'
        + "".join(
            card(
                f"Story {i}",
                f'<div style="font-size:10.5pt">{s}</div>'
                f'<div class="dp-line">{WIDE} boxes</div>',
            )
            for i, s in enumerate(thu_story, 1)
        )
        + "</div>",
    )

    # =========================================================================
    # FRIDAY — Which Truck Has More?
    # Standards: VA.MATH.1.1.2 (b), VA.MATH.1.1.2 (c) — compare; order three numbers
    # =========================================================================

    add(
        "readingWorksheet",
        {
            "title": "Friday: Which Truck Has More?",
            "passage_title": "Check the Crates First",
            "instructions": (
                "Hands-on first (30 min): Truck Showdown! Each player gets a toy truck (or a "
                "plate). Roll one die for crates and one die for loose boxes, and load that cargo "
                "next to your truck. Line the crates up side by side to compare. Whoever has more "
                'boxes says "My truck is greater than yours!" Play 6 rounds. Then add a third '
                "truck and line all three up from least to greatest."
            ),
            "passage": (
                "Two trucks pull up to the depot at the same time. Which one has more boxes? A "
                "smart dispatcher follows rule 3: check the crates first.\n\n"
                "Truck A has 4 crates. Truck B has 2 crates. Truck A has more boxes — even if "
                "Truck B has a pile of loose boxes! Here is why. After a trade, a truck never has "
                "more than 9 loose boxes. And 9 loose boxes is still less than one crate. So more "
                "crates always wins.\n\n"
                "If the crates are a tie, compare the loose boxes. 36 and 32 both have 3 crates. "
                "6 loose boxes is more than 2, so 36 is greater than 32.\n\n"
                "When two trucks carry the same number of boxes, the numbers are equal to each "
                "other. 25 is equal to 25.\n\n"
                "To line up three trucks from least to greatest, find the truck with the fewest "
                "boxes first. It goes at the front of the line."
            ),
            "questions": [
                {
                    "prompt": "When you compare two trucks, what do you check first?",
                    "response_lines": 1,
                },
                {"prompt": "Which is greater, 41 or 29?", "response_lines": 1},
                {
                    "prompt": "53 and 58 have the same number of crates. Which one is less?",
                    "response_lines": 1,
                },
                {
                    "prompt": "Put these in order from least to greatest: 62, 26, 44",
                    "response_lines": 1,
                },
                {
                    "prompt": (
                        "LET'S DISCUSS: Truck A has 3 crates. Truck B has 2 crates and 9 loose "
                        "boxes. Truck B has more things to carry. Does it have more boxes?"
                    ),
                    "response_lines": 0,
                },
            ],
            "vocabulary": [
                {"term": "equal to", "definition": "the same number of boxes"},
                {"term": "least", "definition": "the smallest number in the group"},
                {"term": "greater than", "definition": "more boxes"},
                {"term": "greatest", "definition": "the biggest number in the group"},
                {"term": "less than", "definition": "fewer boxes"},
            ],
        },
        "Friday",
    )

    # (truck A, truck B) as (tens, ones); the last three pairs are numbers only.
    fri_pics = [((3, 1), (2, 8)), ((4, 5), (4, 2)), ((5, 0), (4, 10))]
    fri_nums = [(76, 67), (19, 91), (59, 60)]
    compare_line = (
        f'<div class="dp-line" style="line-height:1.8">Truck A is {choices("greater than")} '
        f'{choices("less than")} {choices("equal to")} Truck B</div>'
    )
    add_custom(
        "Friday",
        "Truck Showdown",
        "Write each truck's label. Then circle greater than, less than, or equal to.",
        '<div class="dp-rule"><b>Depot Rule 3:</b> check the crates first.</div>'
        + "".join(
            card(
                f"Showdown {i}",
                '<div style="display:flex;justify-content:space-around;align-items:flex-end">'
                + "".join(
                    f'<div style="text-align:center">{pic(cargo_svg(t, o, u=7.5))}'
                    f"<b>Truck {side}</b> {WIDE}</div>"
                    for side, (t, o) in zip("AB", pair, strict=True)
                )
                + "</div>"
                + compare_line,
            )
            for i, pair in enumerate(fri_pics, 1)
        )
        + '<div class="dp-h">No pictures — check the crates in your head!</div>'
        + "".join(
            f'<div class="dp-line" style="line-height:2.4"><b>{a}</b> is '
            f'{choices("greater than", "less than", "equal to")} <b>{b}</b></div>'
            for a, b in fri_nums
        ),
    )

    fri_order = [
        ("least to greatest", [34, 43, 30]),
        ("greatest to least", [72, 27, 70]),
        ("least to greatest", [15, 51, 50]),
        ("greatest to least", [88, 81, 18]),
    ]
    fri_digits = [(4, 7), (3, 9), (5, 8)]
    add_custom(
        "Friday",
        "Line Up the Trucks",
        "Three trucks are waiting at the gate. Line them up in the order the sign says.",
        '<div class="dp-grid">'
        + "".join(
            card(
                f"Gate {i} &nbsp;·&nbsp; {how.upper()}",
                f'<div style="text-align:center;font-size:15pt;font-weight:bold;margin:4px 0">'
                f'{" &nbsp; ".join(map(str, nums))}</div>'
                f'<div class="dp-order3">{WIDE}&rarr;{WIDE}&rarr;{WIDE}</div>',
            )
            for i, (how, nums) in enumerate(fri_order, 1)
        )
        + "</div>"
        + '<div class="dp-h">Build a label! Use both digits once.</div>'
        + '<div class="dp-grid three">'
        + "".join(
            card(
                f"Digits {a} and {b}",
                f'<div class="dp-line">Greatest label: {WIDE}<br>Least label: {WIDE}</div>',
            )
            for a, b in fri_digits
        )
        + "</div>",
    )

    # =========================================================================
    # SATURDAY — Dispatch Day (capstone)
    # Standards: VA.MATH.1.1.5 (a, b), VA.MATH.1.1.2 (a–c), VA.MATH.1.1.6
    # =========================================================================

    add(
        "readingWorksheet",
        {
            "title": "Saturday: Dispatch Day",
            "passage_title": "Big Orders, Small Orders",
            "instructions": (
                "Hands-on first (40 min, outside): Open the depot! Chalk a giant Loading Dock on "
                "the driveway with a TENS bay and a ONES bay. Collect sticks: a bundle of 10 "
                "sticks with a rubber band is a crate, and a single stick is a loose box. You are "
                'the customer. Call out orders ("I need 46 boxes!"). Theodore loads the chalk '
                "dock, writes the label in chalk, and delivers it by toy truck or wagon. Include "
                "one order that needs a trade, and one where you ask which of two loads is bigger."
            ),
            "passage": (
                "Today you run the whole depot. Orders are coming in from all over town!\n\n"
                "A good dispatcher knows what makes sense. A pickup truck is small. It might "
                "carry 5 boxes. A big box truck can carry 50 boxes — that is 5 crates. A long "
                "freight train can carry 500 boxes!\n\n"
                "5, 50, and 500 all start with a 5, but they are very different amounts. Ten "
                "crates is 100 boxes. That fills a whole pallet. 500 boxes is 5 full pallets.\n\n"
                "When an order comes in, think first: is this a small order, a medium order, or a "
                "giant order? Then pack it, crates first. Write the label. Check it by counting by "
                "tens, then counting on by ones.\n\n"
                "Remember the three depot rules: every crate holds 10, never park 10 loose boxes, "
                "and check the crates first."
            ),
            "questions": [
                {
                    "prompt": "Which makes sense for a pickup truck: 5, 50, or 500 boxes?",
                    "response_lines": 1,
                },
                {"prompt": "How many boxes are in 10 crates?", "response_lines": 1},
                {
                    "prompt": "An order for 63 boxes comes in. How many crates and loose boxes "
                    "do you pack?",
                    "response_lines": 1,
                },
                {
                    "prompt": "Which depot rule helps you compare two trucks?",
                    "response_lines": 1,
                },
                {
                    "prompt": (
                        "LET'S DISCUSS: A customer orders 500 boxes and wants them all in one "
                        "pickup truck. What should the dispatcher say? How many trips might it "
                        "take?"
                    ),
                    "response_lines": 0,
                },
            ],
            "vocabulary": [
                {"term": "pallet", "definition": "10 crates — 100 boxes"},
                {"term": "makes sense", "definition": "fits the real world"},
                {"term": "order", "definition": "a customer asking for some boxes"},
                {"term": "deliver", "definition": "drive the boxes to the customer"},
            ],
        },
        "Saturday",
    )

    sat_read = (5, 7)
    sat_pack = 48
    sat_trade = (3, 14)
    sat_more = 62
    sat_compare = (39, 41)
    sat_story = (14, 6)
    add_custom(
        "Saturday",
        "The Dispatch Board",
        "Six orders came in this morning. Fill every one — then you're done for the week, "
        "Dispatcher!",
        '<div class="dp-grid">'
        + card(
            "Order 1 · read it",
            pic(cargo_svg(*sat_read, u=9, styles="LS"))
            + f'<div class="dp-line">{BLANK} tens {BLANK} ones &nbsp; Label: {WIDE}</div>',
        )
        + card(
            "Order 2 · pack it",
            label(sat_pack)
            + '<div class="dp-draw" style="height:0.9in"></div>'
            + f'<div class="dp-line">{BLANK} crates and {BLANK} loose boxes</div>',
        )
        + card(
            "Order 3 · trade it",
            f'<div style="font-size:11pt;margin-top:4px">A truck has <b>{sat_trade[0]} crates '
            f"and {sat_trade[1]} loose boxes</b>. Follow rule 2!</div>"
            f'<div class="dp-line">{BLANK} crates {BLANK} loose &nbsp; Label: {WIDE}</div>',
        )
        + card(
            "Order 4 · ten more",
            f'<div style="font-size:11pt;margin-top:4px">The depot has <b>{sat_more}</b> boxes. '
            f"One more crate arrives.</div>"
            f'<div class="dp-line">Now the depot has {WIDE} boxes.</div>',
        )
        + card(
            "Order 5 · compare",
            f'<div style="font-size:11pt;margin-top:4px">The red truck has <b>{sat_compare[0]}</b>'
            f" boxes. The blue truck has <b>{sat_compare[1]}</b> boxes.</div>"
            f'<div class="dp-line">Circle the truck with MORE: {choices("red", "blue")}</div>',
        )
        + card(
            "Order 6 · story",
            f'<div style="font-size:11pt;margin-top:4px">A truck has 1 crate and '
            f"{sat_story[0] - 10} loose boxes. The driver adds {sat_story[1]} more loose boxes. "
            f"How many boxes now?</div>"
            f'<div class="dp-line">{sat_story[0]} + {sat_story[1]} = {WIDE}<br>'
            f"Trade! {BLANK} crates {BLANK} loose</div>",
        )
        + "</div>",
    )

    sat_sense = [
        ("Boxes in a bike basket", [3, 30, 300], 3),
        ("Kids on a school bus", [4, 40, 400], 40),
        ("Boxes on a long freight train", [5, 50, 500], 500),
        ("Wheels on a pickup truck", [4, 40, 400], 4),
        ("Boxes in a big box truck (5 crates)", [5, 50, 500], 50),
    ]
    add_custom(
        "Saturday",
        "What Makes Sense?",
        "Think first: is it a small, medium, or giant amount? Circle the number that makes sense.",
        "".join(
            f'<div class="dp-line" style="line-height:2.5;border-bottom:1px solid #ddd">'
            f"<b>{i}.</b> {what}: &nbsp; {choices(*map(str, opts))}</div>"
            for i, (what, opts, _) in enumerate(sat_sense, 1)
        )
        + '<div class="dp-rule" style="margin-top:12px">Tell a grown-up WHY you picked your answer '
        "for number 3. What would 5 boxes on a freight train look like?</div>"
        + '<div class="dp-h">Your own work order</div>'
        + card(
            "Written by Dispatcher Theodore",
            '<div class="dp-line">My label: <span class="dp-blank wide"></span> &nbsp; '
            f"{BLANK} tens and {BLANK} ones</div>"
            '<div class="dp-draw" style="height:1.7in"></div>'
            '<div style="font-size:9pt;color:#555">Draw the cargo. Then load it on the Loading '
            "Dock mat and have a grown-up check it.</div>",
        ),
    )

    # =========================================================================
    # PARENT FEEDBACK & TEACHING NOTES
    # =========================================================================

    add(
        "readingWorksheet",
        {
            "title": "Parent Feedback & Teaching Notes",
            "instructions": "For the parent/teacher — fill in at the end of the week.",
            "passage_title": "Truck Depot Week Reflection",
            "passage": (
                "This week Theodore ran a truck depot instead of following a narrator. He packed "
                "boxes into crates of ten, read and wrote two-digit labels as tens and ones, "
                "traded 10 ones for a ten, found 10 more and 10 less, compared and ordered "
                "numbers by checking the crates first, and judged which amounts make sense. Use "
                "these notes to plan next week — including whether the dispatcher role landed "
                "better than Kip did."
            ),
            "vocabulary": [
                {
                    "term": "Key Misconception to Watch",
                    "definition": (
                        'Writing the trade without trading: 2 crates and 13 loose → "213". '
                        "Did this show up?"
                    ),
                },
                {
                    "term": "Strongest Concept This Week",
                    "definition": "(Fill in — which depot job clicked best?)",
                },
                {
                    "term": "Next Week's Hook",
                    "definition": (
                        "Adding at the depot: 34 + 23 as crates + crates and loose + loose, "
                        "then trades when the loose boxes overflow."
                    ),
                },
            ],
            "questions": [
                {
                    "prompt": (
                        "Overall comfort with tens and ones (1 = struggled throughout, "
                        "5 = confident and quick):"
                    ),
                    "response_lines": 1,
                },
                {
                    "prompt": "Did being the dispatcher work as a hook? What did he say or do "
                    "that showed it?",
                    "response_lines": 2,
                },
                {
                    "prompt": "Which manipulative did he reach for — long crates, stack crates, "
                    "or drawing sticks and squares?",
                    "response_lines": 1,
                },
                {
                    "prompt": "Could he compare two numbers without the cutouts by Friday?",
                    "response_lines": 2,
                },
                {"prompt": "Skills to revisit next week:", "response_lines": 2},
            ],
        },
        "Saturday",
    )

    html = build_print_packet_html(pages, packet_title="Truck Depot Week — Math for Theodore")
    html = html.replace("</head>", DEPOT_CSS + "</head>", 1)
    out_path = output_dir / "depot_week.html"
    out_path.write_text(html, encoding="utf-8")

    cutouts_path = output_dir / "depot_cargo_cutouts.html"
    cutouts_path.write_text(build_cutouts_html(), encoding="utf-8")

    # ── Answer keys, computed from the same data the pages were built from ────

    def li(items: list[str]) -> str:
        return "".join(f"<li>{x}</li>" for x in items)

    def crates(n: int) -> str:
        return f"{n} crate" if n == 1 else f"{n} crates"

    def to(t: int, o: int) -> str:
        return f"{t} ten{'' if t == 1 else 's'} and {o} ones = {10 * t + o}"

    def relation(a: int, b: int) -> str:
        return "greater than" if a > b else "less than" if a < b else "equal to"

    def digits(n: int) -> str:
        return f"{n // 10} ten{'' if n // 10 == 1 else 's'} and {n % 10} ones; {n // 10 * 10} + {n % 10} = {n}"

    trade_all = thu_trade + [thu_trade_text]
    keys = {
        "TUE_SCATTER": li([f"{crates(n // 10)} and {n % 10} loose = {n}" for n, _ in tue_scatter]),
        "TUE_TENS": li([f"{t} crates = {10 * t} boxes" for t, _ in tue_tens]),
        "TUE_STRIP": ", ".join(str(10 * i) for i, c in enumerate(tue_strip) if c is None),
        "TUE_MIXED": li([to(t, o) for t, o, _ in tue_mixed]),
        "WED_READ": li([to(t, o) for t, o, _ in wed_read]),
        "WED_ORDERS": li([digits(n) for n in wed_orders]),
        "THU_TRADE": li(
            [
                f"{crates(t)} + {o} loose &rarr; {crates(t + o // 10)} and {o % 10} loose = "
                f"{10 * t + o}"
                for t, o in trade_all
            ]
        ),
        "THU_TABLE": li([f"{n - 10} &larr; {n} &rarr; {n + 10}" for n in thu_table]),
        "THU_STRIPS": li(
            [", ".join(str(s[0] + 10 * i) for i in range(len(s))) for s in thu_strips]
        ),
        "FRI_PICS": li(
            [
                f"A = {10 * a[0] + a[1]}, B = {10 * b[0] + b[1]}: A is "
                f"{relation(10 * a[0] + a[1], 10 * b[0] + b[1])} B"
                for a, b in fri_pics
            ]
        ),
        "FRI_NUMS": li([f"{a} is {relation(a, b)} {b}" for a, b in fri_nums]),
        "FRI_ORDER": li(
            [
                f"{how}: " + " &rarr; ".join(map(str, sorted(nums, reverse="greatest to" in how)))
                for how, nums in fri_order
            ]
        ),
        "FRI_DIGITS": li(
            [
                f"{a} and {b}: greatest {max(a, b)}{min(a, b)}, least {min(a, b)}{max(a, b)}"
                for a, b in fri_digits
            ]
        ),
        "SAT_SENSE": li([f"{what}: {ans}" for what, _, ans in sat_sense]),
    }
    assert all(10 * t + o <= 99 for t, o in trade_all)
    assert sum(sat_story) == 20

    TEACHER_GUIDE = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>Truck Depot Week — Teacher Guide</title>
  <style>
    @page { size: letter; margin: 0.5in 0.6in; }
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body { font-family: 'Trebuchet MS', Arial, sans-serif; font-size: 11pt; color: #111; line-height: 1.55; }
    @media screen { body { background: #b0b0b0; padding: 24px; } .page { background: white; max-width: 7.5in; margin: 0 auto 28px; padding: 0.45in 0.5in; box-shadow: 0 4px 18px rgba(0,0,0,.28); min-height: 10.3in; } }
    @media print { body { background: white; padding: 0; } .page { padding: 0; box-shadow: none; } * { -webkit-print-color-adjust: exact; print-color-adjust: exact; } }
    .page { page-break-after: always; break-after: page; }
    .page:last-child { page-break-after: avoid; break-after: avoid; }
    h1 { font-size: 18pt; color: #b45309; border-bottom: 3px solid #b45309; padding-bottom: 5px; margin-bottom: 12px; }
    h2 { font-size: 13pt; color: #fff; background: #15803d; padding: 5px 10px; border-radius: 3px; margin: 14px 0 6px; }
    h2.wed { background: #7c3aed; }
    h2.thu { background: #c2410c; }
    h2.fri { background: #0f766e; }
    h2.sat { background: #b45309; }
    h2.prep { background: #374151; }
    h3 { font-size: 10.5pt; font-weight: bold; color: #444; margin: 8px 0 3px; text-transform: uppercase; letter-spacing: 0.04em; }
    p, li { font-size: 10pt; margin-bottom: 5px; }
    ul, ol { padding-left: 18px; margin-bottom: 8px; }
    .answer-box { background: #f0fff4; border-left: 4px solid #15803d; padding: 6px 10px; margin: 4px 0 10px; border-radius: 0 4px 4px 0; font-size: 10pt; }
    .answer-box ol, .answer-box ul { margin-bottom: 0; }
    .answer-box.wed { background: #f5f0ff; border-color: #7c3aed; }
    .answer-box.thu { background: #fff7f0; border-color: #c2410c; }
    .answer-box.fri { background: #f0fff8; border-color: #0f766e; }
    .answer-box.sat { background: #fffbeb; border-color: #b45309; }
    .misconception { background: #fff3cd; border-left: 4px solid #d97706; padding: 6px 10px; margin: 4px 0 8px; border-radius: 0 4px 4px 0; font-size: 10pt; }
    .extension { background: #e8f5e9; border-left: 4px solid #15803d; padding: 6px 10px; margin: 4px 0 8px; border-radius: 0 4px 4px 0; font-size: 10pt; }
    .discuss { background: #fce7f3; border-left: 4px solid #9d174d; padding: 6px 10px; margin: 4px 0 8px; border-radius: 0 4px 4px 0; font-size: 10pt; }
  </style>
</head>
<body>

<div class="page">
  <h1>Truck Depot Week — Teacher / Parent Guide</h1>
  <p><strong>Subject:</strong> Math — place value, tens and ones &nbsp;|&nbsp;
  <strong>Audience:</strong> Theodore, Grade 1 &nbsp;|&nbsp; <strong>Days:</strong> Tuesday &ndash; Saturday</p>
  <p><strong>Arc:</strong> pack crates of ten &rarr; the label tells the cargo &rarr; trade 10 ones for a ten
  &rarr; check the crates first to compare &rarr; Dispatch Day capstone</p>
  <p><strong>The hook:</strong> no mascot this week. Theodore <em>is</em> the dispatcher &mdash; every
  passage talks to him, every practice page is a work order he fills, and you play the customer.
  Lean into it: call him "Dispatcher," hand him orders on index cards, let him sign off sheets.</p>

  <h3>The three depot rules (say them every day)</h3>
  <ol>
    <li><strong>Every crate holds exactly 10.</strong></li>
    <li><strong>Never park 10 loose boxes</strong> &mdash; trade them for a crate.</li>
    <li><strong>Check the crates first</strong> when you compare.</li>
  </ol>

  <h2 class="prep">Prep before Tuesday (~30 min)</h2>
  <ul>
    <li><strong>Print <code>depot_cargo_cutouts.html</code> on cardstock</strong> at 100% scale
    ("Actual size", not "Fit to page"). Four pages: 16 long crates, 18 stack crates, 180 loose
    boxes, and the Loading Dock mat.</li>
    <li><strong>Cut the loose boxes yourself</strong> (straight lines &mdash; a paper trimmer makes it
    fast). Leave a few long crates for Theodore to cut on Tuesday; they're easy straight cuts.</li>
    <li>Keep the pieces in two containers labelled CRATES and LOOSE BOXES &mdash; the "warehouse."</li>
    <li>Gather: 40&ndash;60 small objects and cups or zip bags (Tue), 8 index cards (Wed), a die
    or two (Thu, Fri), two toy trucks (Fri), sidewalk chalk, sticks and rubber bands (Sat).</li>
  </ul>
  <p><strong>Day shape (~90 min):</strong> hands-on game first (30&ndash;40 min), then the briefing
  page read together, then the two work-order pages. The cutouts and dock mat stay on the table for
  every page &mdash; building it before writing it is the whole point.</p>

  <h2>Tuesday — Crates of Ten</h2>
  <h3>Answer Key — Briefing Questions</h3>
  <div class="answer-box">
    <p><strong>Q1:</strong> 10. <strong>Q2:</strong> 40 (10, 20, 30, 40). <strong>Q3:</strong> 25.
    <strong>Q4:</strong> Counting one at a time is slow and easy to lose track; crates let you count by tens.</p>
  </div>
  <h3>Pack the Crates</h3>
  <div class="answer-box"><ol>{{TUE_SCATTER}}</ol></div>
  <h3>Count the Crates by Tens</h3>
  <div class="answer-box">
    <p><strong>A:</strong></p><ol>{{TUE_TENS}}</ol>
    <p><strong>B (missing):</strong> {{TUE_STRIP}}</p>
    <p><strong>C:</strong></p><ol>{{TUE_MIXED}}</ol>
    <p><em>A&ndash;D: 10 crates is 100 &mdash; enjoy the "a hundred!" moment; Saturday comes back to it.</em></p>
  </div>
  <h3>LET'S DISCUSS Guidance</h3>
  <div class="discuss">
    <p><em>"The long crate holds more?"</em> No &mdash; lay 10 loose boxes on each one: they cover both
    exactly. Different shape, same amount. This is the first taste of "a ten is a ten no matter how
    it's arranged" (the stack crate is a full ten frame).</p>
  </div>
  <h3>Misconceptions to Watch</h3>
  <div class="misconception">
    <p><strong>Counting a crate as 1:</strong> "4 crates and 3 loose is 7." Fix: touch each crate and
    say "10, 20, 30, 40," then switch voices for the loose boxes: "41, 42, 43."</p>
  </div>
  <h3>Extension Activity</h3>
  <div class="extension">
    <p>Crate hunt: would an egg carton work as a depot crate? (No &mdash; it holds 12!) Find things
    at home that really come in tens: fingers, toes, a 10-pack of crayons.</p>
  </div>

  <h2 class="wed">Wednesday — The Label Tells the Cargo</h2>
  <h3>Answer Key — Briefing Questions</h3>
  <div class="answer-box wed">
    <p><strong>Q1:</strong> 5 crates, 2 loose boxes. <strong>Q2:</strong> 61. <strong>Q3:</strong> The
    left one (tens place). <strong>Q4:</strong> There are no loose boxes; the 0 holds the ones place
    so the 7 means 7 tens.</p>
  </div>
  <h3>Read the Truck, Write the Label</h3>
  <div class="answer-box wed"><ol>{{WED_READ}}</ol></div>
  <h3>Fill the Work Orders</h3>
  <div class="answer-box wed"><ol>{{WED_ORDERS}}</ol>
  <p><em>Order 6 is the trap: 9 is 0 tens and 9 ones &mdash; no crates to draw.</em></p></div>
  <h3>LET'S DISCUSS Guidance</h3>
  <div class="discuss">
    <p>1 crate and 0 loose is <strong>10</strong>; 1 crate and 7 loose is <strong>17</strong>. Every
    teen number is one crate plus some loose boxes. That's why "ten" has a 1 and a 0, and why
    "seven-teen" is 17, not 71 &mdash; the word says the ones first, but the label writes the crate first.</p>
  </div>
  <h3>Misconceptions to Watch</h3>
  <div class="misconception">
    <p><strong>Teen reversals:</strong> writing 61 for sixteen because he hears "six" first.
    <strong>Dropping the zero:</strong> writing 5 for 5 crates. Ask him to load his written label on the
    dock mat &mdash; the mismatch shows itself.</p>
  </div>
  <h3>Extension Activity</h3>
  <div class="extension">
    <p>Label hunt on a walk or drive: speed limit signs, house numbers, page numbers. For each, ask
    "How many crates? How many loose boxes?"</p>
  </div>
</div>

<div class="page">
  <h2 class="thu">Thursday — Trade Day</h2>
  <h3>Answer Key — Briefing Questions</h3>
  <div class="answer-box thu">
    <p><strong>Q1:</strong> 10. <strong>Q2:</strong> 22 (2 crates, 2 loose). <strong>Q3:</strong> 44.
    <strong>Q4:</strong> The tens digit.</p>
  </div>
  <h3>Trade It In</h3>
  <div class="answer-box thu"><ol>{{THU_TRADE}}</ol>
  <p><em>Truck 3 (4 crates, 10 loose) trades to exactly 5 crates and 0 loose &mdash; label 50.</em></p></div>
  <h3>10 More, 10 Less</h3>
  <div class="answer-box thu">
    <p><strong>A (10 less &larr; truck &rarr; 10 more):</strong></p><ol>{{THU_TABLE}}</ol>
    <p><strong>B:</strong></p><ol>{{THU_STRIPS}}</ol>
    <p><strong>C:</strong> Story 1: 56 boxes (26 &rarr; 36 &rarr; 46 &rarr; 56). Story 2: 41 boxes
    (71 &rarr; 61 &rarr; 51 &rarr; 41).</p>
  </div>
  <h3>LET'S DISCUSS Guidance</h3>
  <div class="discuss">
    <p><em>"4 crates and no loose boxes, but the customer wants 3?"</em> Unpack a crate! Now it's 3
    crates and 10 loose; hand over 3 and 3 crates and 7 loose (37) remain. Trading works both
    directions &mdash; this is the seed of subtraction with regrouping. Act it out with the cutouts.</p>
  </div>
  <h3>Misconceptions to Watch</h3>
  <div class="misconception">
    <p><strong>"213":</strong> writing 2 crates and 13 loose as 213, or trading but forgetting to take
    the 10 loose boxes away. Fix: physically swap on the dock &mdash; 10 boxes go back to the
    warehouse, 1 crate comes out. On 10 more/10 less, watch for him changing the ones digit (34 + 10
    = 35).</p>
  </div>
  <h3>Extension Activity</h3>
  <div class="extension">
    <p>Play the Trading Game to 100 with two dice. When he gets 10 crates, trade them for a "pallet"
    (a sheet of paper under them) &mdash; a first look at the hundreds place.</p>
  </div>

  <h2 class="fri">Friday — Which Truck Has More?</h2>
  <h3>Answer Key — Briefing Questions</h3>
  <div class="answer-box fri">
    <p><strong>Q1:</strong> The crates (tens). <strong>Q2:</strong> 41. <strong>Q3:</strong> 53.
    <strong>Q4:</strong> 26, 44, 62.</p>
  </div>
  <h3>Truck Showdown</h3>
  <div class="answer-box fri"><ol>{{FRI_PICS}}</ol><ul>{{FRI_NUMS}}</ul>
  <p><em>Showdown 1 is the "more pieces" trap (Truck B has 10 pieces to Truck A's 4, but fewer
  boxes). Showdown 3 broke rule 2 &mdash; trade Truck B's 10 loose and it's 5 crates, equal to A.</em></p></div>
  <h3>Line Up the Trucks</h3>
  <div class="answer-box fri"><ol>{{FRI_ORDER}}</ol><ul>{{FRI_DIGITS}}</ul></div>
  <h3>LET'S DISCUSS Guidance</h3>
  <div class="discuss">
    <p>Truck A has 30 boxes; Truck B has 29 &mdash; Truck A has more, even though B has 11 pieces
    and A has 3. Build both: B is only 1 box away from another crate. "Check the crates first" works
    because 9 loose boxes can never beat a crate.</p>
  </div>
  <h3>Misconceptions to Watch</h3>
  <div class="misconception">
    <p><strong>Comparing the ones digit:</strong> "29 is bigger than 31 because 9 is bigger than 1."
    Or comparing by how many pieces/how much space. Always back to rule 3: crates first.</p>
  </div>
  <h3>Extension Activity</h3>
  <div class="extension">
    <p>Label War: deal two-digit number cards; each player flips one, and the greater label takes
    both. Say the sentence each time: "52 is greater than 47."</p>
  </div>
</div>

<div class="page">
  <h2 class="sat">Saturday — Dispatch Day (Capstone)</h2>
  <h3>Answer Key — Briefing Questions</h3>
  <div class="answer-box sat">
    <p><strong>Q1:</strong> 5. <strong>Q2:</strong> 100. <strong>Q3:</strong> 6 crates and 3 loose
    boxes. <strong>Q4:</strong> Rule 3 &mdash; check the crates first.</p>
  </div>
  <h3>The Dispatch Board</h3>
  <div class="answer-box sat"><ol>
    <li>5 tens 7 ones; label 57</li>
    <li>48: 4 crates and 8 loose boxes (drawing: 4 sticks, 8 squares)</li>
    <li>3 crates + 14 loose &rarr; 4 crates and 4 loose; label 44</li>
    <li>72</li>
    <li>Blue (41 has 4 crates; 39 has only 3)</li>
    <li>14 + 6 = 20; trade &rarr; 2 crates and 0 loose (the Ten Stop again: 4 + 6 fills a crate)</li>
  </ol></div>
  <h3>What Makes Sense?</h3>
  <div class="answer-box sat"><ol>{{SAT_SENSE}}</ol>
  <p><em>Accept a well-argued different answer on the school bus (a small bus might seat about
  20). The goal is the reasoning (1.1.5b), not the exact number.</em></p></div>
  <h3>LET'S DISCUSS Guidance</h3>
  <div class="discuss">
    <p>The dispatcher should say "That won't fit!" If a pickup carries about 5 boxes, 500 boxes is
    100 trips. He won't compute that &mdash; but "lots and lots of trips" or "send the freight train"
    is exactly the sense of magnitude we want.</p>
  </div>
  <h3>Misconceptions to Watch</h3>
  <div class="misconception">
    <p>Treating 5, 50 and 500 as "about the same" because they all show a 5. Build 5 and 50 with the
    cutouts side by side, and point out that 500 wouldn't fit on the table.</p>
  </div>
  <h3>Extension Activity</h3>
  <div class="extension">
    <p>Toy-car inventory: bundle his real toy cars (or LEGO, or crayons) into groups of ten with
    cups or rubber bands, write the depot label for his whole collection, and post it on his door.</p>
  </div>
</div>

</body>
</html>"""
    for name, value in keys.items():
        TEACHER_GUIDE = TEACHER_GUIDE.replace("{{" + name + "}}", value)
    assert "{{" not in TEACHER_GUIDE
    guide_path = output_dir / "depot_week_teacher_guide.html"
    guide_path.write_text(TEACHER_GUIDE, encoding="utf-8")

    print(f"Generated {len(pages)} pages -> {output_dir}/")
    labels = [
        "Tue p1 — Briefing: Welcome, Dispatcher!",
        "Tue p2 — Work order: Pack the Crates",
        "Tue p3 — Work order: Count the Crates by Tens",
        "Wed p1 — Briefing: The Label Tells the Cargo",
        "Wed p2 — Work order: Read the Truck, Write the Label",
        "Wed p3 — Work order: Fill the Work Orders",
        "Thu p1 — Briefing: Trade Day",
        "Thu p2 — Work order: Trade It In",
        "Thu p3 — Work order: 10 More, 10 Less",
        "Fri p1 — Briefing: Which Truck Has More?",
        "Fri p2 — Work order: Truck Showdown",
        "Fri p3 — Work order: Line Up the Trucks",
        "Sat p1 — Briefing: Dispatch Day (Capstone)",
        "Sat p2 — Work order: The Dispatch Board",
        "Sat p3 — Work order: What Makes Sense?",
        "         Parent Feedback & Teaching Notes",
    ]
    for line in labels:
        print(f"  {line}")
    print(f"Teacher guide -> {guide_path}")
    print(f"Cutouts       -> {cutouts_path}")


if __name__ == "__main__":
    generate_depot_week_series()
