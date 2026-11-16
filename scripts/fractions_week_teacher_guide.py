#!/usr/bin/env python3
"""
Teacher guide for the "Half a Heart" fractions week.

Imported by generate_fractions_week_series.py; not meant to be run directly.
Emits fractions_week_series/fractions_week_teacher_guide.html.
"""

import os
import sys

sys.path.insert(0, os.path.abspath("src"))

from worksheet_html_renderer import build_print_packet_html, render_page  # noqa: E402


def _page(title, subtitle, rail, sections, day_label=""):
    return render_page(
        [("richText", {"sections": sections})],
        {
            "day_label": day_label,
            "title": title,
            "subtitle": subtitle,
            "rail_text": rail,
            "total_days": 0,
            "show_name_date": False,
        },
        layout="journal",
    )


# ── Overview ───────────────────────────────────────────────────────────────


def page_overview():
    return _page(
        "Half a Heart — Teacher Guide",
        "Grade 2–3 fractions · five days · narrator: Scout the wolf",
        "Overview",
        [
            {
                "heading": "The idea behind the week",
                "text": (
                    "Christopher already reads half-hearts fluently as a game mechanic. "
                    "This week does not introduce that idea — it gives it a name and "
                    "then builds on it. Expect Monday to feel easy. That is deliberate: "
                    "the week starts inside something he already knows so that Wednesday "
                    "and Thursday, which are genuinely hard, have somewhere to stand.\n\n"
                    "The arc moves region model → set model → length model. Students "
                    "who only ever meet fractions as shaded pizzas fall apart the first "
                    "time a fraction appears on a number line, so all three models appear "
                    "here, in that order."
                ),
            },
            {
                "heading": "Standards covered (Virginia SOL)",
                "rows": [
                    {"k": "Monday", "v": "2.4.a, 2.4.b — equal parts; halves, fourths, eighths"},
                    {"k": "Tuesday", "v": "2.4.a/b/c — thirds and sixths; fractions of a set"},
                    {"k": "Wednesday", "v": "3.2.c — comparing unit fractions with >, <, ="},
                    {
                        "k": "Thursday",
                        "v": "3.2.a/b/c — non-unit fractions, equivalence, number line, ≠",
                    },
                    {"k": "Friday", "v": "3.5 — add and subtract with like denominators"},
                ],
            },
            {
                "heading": "Warm-ups are not filler",
                "text": (
                    "Each day opens with a whole-number drill that secretly rehearses that "
                    "day's fraction skill. Do not skip them — the Thursday one in "
                    "particular is load-bearing."
                ),
                "rows": [
                    {"k": "Mon — half of…", "v": "primes halving before halves are named"},
                    {"k": "Tue — count by 3s/6s", "v": "primes thirds and sixths"},
                    {"k": "Wed — > and <", "v": "primes comparing, so only the inversion is new"},
                    {
                        "k": "Thu — how many more to 12",
                        "v": "primes finding “the rest” — the hardest task of the week",
                    },
                    {"k": "Fri — adding within 20", "v": "primes adding like denominators"},
                ],
            },
        ],
    )


def page_practical():
    return _page(
        "Before You Start",
        "Printing, materials and prep",
        "Setup",
        [
            {
                "heading": "Print settings — read this first",
                "text": (
                    "Print at 100% / Actual Size with “Fit to page” turned OFF. The "
                    "manipulatives are dimensioned in real inches. Browser fit-to-page "
                    "silently shrinks output by 4–6%, which is invisible on a normal "
                    "worksheet but means Monday's strips will not line up with Wednesday's. "
                    "Every kit page carries a 6-inch calibration ruler — check it against a "
                    "real ruler before any cutting.\n\n"
                    "The whole is 6 inches throughout because 6 divides evenly by 1, 2, 3, 4, "
                    "6 and 12. One third is exactly 2 inches, one fourth exactly 1.5 inches. "
                    "He can verify pieces with a ruler and get whole numbers, which makes the "
                    "kit self-checking."
                ),
            },
            {
                "heading": "Materials",
                "bullets": [
                    "Scissors, and patience for about 25 cuts across the week",
                    "Crayons or pencils: red, green, blue, yellow",
                    "A ruler",
                    "String and about 15 clothes pegs (Thursday)",
                    "6 crackers and 3 bowls (Tuesday)",
                    "Biscuits, one small and ideally one large (Wednesday)",
                    "Tape for the kit pocket (Wednesday)",
                ],
            },
        ],
    )


# ── Daily notes ────────────────────────────────────────────────────────────


def page_mon_tue():
    return _page(
        "Monday & Tuesday",
        "Equal parts · thirds, sixths and sets",
        "Mon–Tue",
        [
            {
                "heading": "Monday — Equal Parts",
                "text": (
                    "Objective: the bottom number counts how many EQUAL parts the whole was "
                    "cut into.\n\n"
                    "The fold-to-discover strips come before the printed kit on purpose. If "
                    "you hand a child pre-cut perfect fourths, he never has to wrestle with "
                    "what equal means. Let him fold badly the first time."
                ),
                "bullets": [
                    "Watch for: counting pieces rather than checking they are equal.",
                    "Task 4 is the misconception check. A, B and D are genuine fourths. "
                    "C and E are each cut into exactly four pieces — but the pieces are "
                    "not equal, so they are not fourths. If he circles C or E he is "
                    "counting pieces instead of checking they match.",
                    "If he finds Monday trivial, that is expected. Do not stretch it — "
                    "Wednesday is where the week earns its keep.",
                ],
            },
            {
                "heading": "Monday answer key",
                "rows": [
                    {"k": "Task 3", "v": "8 parts; the number of parts doubles each fold"},
                    {"k": "Task 4", "v": "Circle A, B, D (all equal partitions into 4)"},
                    {"k": "Task 5", "v": "2 fourths red, 1 fourth blue, 1 fourth yellow"},
                    {"k": "Task 6", "v": "shade 1 of 2; 3 of 4; 5 of 8"},
                ],
            },
            {
                "heading": "Tuesday — Thirds, Sixths and Sets",
                "text": (
                    "Objective: not every fraction is reachable by halving, and a fraction "
                    "can describe a group rather than one object.\n\n"
                    "Let him genuinely struggle to fold a strip into thirds. The failure is "
                    "the lesson — it is why the printed kit exists. Two minutes of "
                    "fumbling here makes the printed thirds feel earned rather than arbitrary."
                ),
                "bullets": [
                    "The set model is a real conceptual jump. '1/3 of 6 chops' means split "
                    "into 3 equal groups and take one group — not 'take 3'.",
                    "Task 5 quietly previews Thursday: 2/3 and 4/6 shade to the same length. "
                    "Do not explain equivalence yet if he notices — just say 'hold that "
                    "thought until Thursday'.",
                ],
            },
            {
                "heading": "Tuesday answer key",
                "rows": [
                    {"k": "Task 2", "v": "2 chops coloured (1/3 of 6 = 2)"},
                    {"k": "Task 3", "v": "1 third red, 2 thirds blue → the rest = 2/3"},
                    {"k": "Task 4", "v": "shade 2 of 3; 4 of 6; 1 of 6"},
                    {"k": "Task 5", "v": "Yes — same size. 2/3 and 4/6 are equivalent."},
                    {"k": "Crackers", "v": "2 per bowl; then 4 per bowl"},
                ],
            },
        ],
    )


def page_wed():
    return _page(
        "Wednesday",
        "The pivot day of the week",
        "Wed",
        [
            {
                "heading": "Wednesday — Comparing Unit Fractions ⭐",
                "text": (
                    "Objective: 1/8 < 1/2 even though 8 > 2.\n\n"
                    "This is the single most common fractions misconception and the reason "
                    "the day gets a full kit build rather than a worksheet. Do not let him "
                    "answer from reasoning today — make him lay one piece on top of the "
                    "other every single time. The physical check is the lesson."
                ),
                "bullets": [
                    "If he says 1/8 is bigger, do not correct him verbally. Hand him the two "
                    "pieces and say 'show me'.",
                    "The sneaky question (1/2 of a tiny biscuit vs 1/8 of an enormous cake) "
                    "is not a trick — it is the missing precondition. Comparisons only hold "
                    "when the wholes match. Most curricula skip this and it causes real "
                    "trouble in grade 4.",
                    "Build the pocket today and label it. He needs the kit again Thursday "
                    "and Friday.",
                ],
            },
            {
                "heading": "Wednesday answer key",
                "rows": [
                    {"k": "Task 1", "v": "1/2 is bigger (larger) than 1/8"},
                    {"k": "Task 2", "v": "1/2 > 1/3 > 1/4 > 1/6 > 1/8 > 1/12"},
                    {
                        "k": "Task 3",
                        "v": "…the piece gets SMALLER — more pieces means each "
                        "one has to be smaller to still fit in the same whole",
                    },
                    {"k": "Task 4", "v": "> , > , < , < , > , >"},
                    {"k": "Task 5", "v": "4 eighths green, 2 eighths red, 2 eighths blue → 2/8"},
                    {"k": "Task 6", "v": "Either answer is fine if justified by whole size"},
                ],
            },
        ],
    )


def page_thu():
    return _page(
        "Thursday",
        "The hardest task of the week",
        "Thu",
        [
            {
                "heading": "Thursday — Equivalence, Non-Unit Fractions, Number Line",
                "text": (
                    "Objective: 3/8 vs 5/8 (count the pieces), 2/4 = 1/2 = 4/8 "
                    "(equivalence), and a fraction is a number with a position — not "
                    "only a shaded picture.\n\n"
                    "Task 1 is the hardest thing in the week. He must work out that 1/3 + "
                    "1/2 = 5/6, so 'the rest' is 1/6. The warm-up primed exactly this. If he "
                    "stalls, do not give the answer — ask 'how many sixths fit on top of "
                    "your 1/3 piece?'"
                ),
                "bullets": [
                    "Expected route: 1/3 = 2/6, 1/2 = 3/6, so 5 of 6 are used and 1 is left.",
                    "The clothesline is worth the setup time. Discovering that 1/2 sits "
                    "exactly in the middle, and that 2/2, 4/4 and 1 all land on the same "
                    "peg, is the moment fractions stop being pictures.",
                    "Line 5 has no printed labels on purpose — he has to work out where "
                    "1/2 falls among sixths (between the 3rd and 4th tick).",
                ],
            },
            {
                "heading": "Thursday answer key",
                "rows": [
                    {"k": "Task 1", "v": "2/6 red, 3/6 green, 1/6 blue — the rest is 1/6"},
                    {"k": "Task 2", "v": "Same size → = (1/2 = 3/6)"},
                    {"k": "Task 3", "v": "2/4 and 4/8 are equivalent; 2/3 is not"},
                    {"k": "Task 4", "v": "< , < , > , = , = , >"},
                    {"k": "Line 4", "v": "X on the 3rd tick of 4"},
                    {"k": "Line 5", "v": "X exactly halfway — on the 3rd tick of 6"},
                    {"k": "Cards", "v": "1, 2/2 and 4/4 all peg at the same place"},
                ],
            },
        ],
    )


def page_fri():
    return _page(
        "Friday & After",
        "Adding, the capstone, and where to go next",
        "Fri",
        [
            {
                "heading": "Friday — Adding and Subtracting",
                "text": (
                    "Objective: with like denominators you add the COUNT of pieces; the "
                    "piece size does not change.\n\n"
                    "Task 2 deliberately puts the classic error in Scout's mouth — "
                    "3/8 + 2/8 = 5/16 — and asks Christopher to correct him. Explaining "
                    "why it is wrong is worth more than getting it right silently, and it "
                    "gives you a clean read on whether the concept landed."
                ),
                "bullets": [
                    "If he cannot explain Scout's error, have him lay out 3 eighth-pieces "
                    "and 2 eighth-pieces. Ask: did the pieces get smaller when we pushed "
                    "them together? No — so the bottom number cannot change.",
                    "The journey page is a running total. If he loses track, let him shade "
                    "each bar from the previous bar rather than recomputing from 8/8.",
                ],
            },
            {
                "heading": "Friday answer key",
                "rows": [
                    {"k": "Task 1", "v": "5/8 · 5/6 · 3/8 · 2/6"},
                    {
                        "k": "Task 2",
                        "v": "Scout is wrong. He added the bottom numbers too. The pieces "
                        "are still eighths — only how many you have changed. 5/8.",
                    },
                    {"k": "Journey", "v": "8/8 → 6/8 → 3/8 → 7/8 → 9/8 (full, 8/8)"},
                    {"k": "Lowest point", "v": "3/8"},
                    {"k": "Capstone 1", "v": "1/4 · 2/3 · 6/8 · 3/6"},
                    {"k": "Capstone 2", "v": "1/2 · 5/6 · 4/4"},
                    {"k": "Capstone 3", "v": "2/8 red, 4/8 yellow, 2/8 green"},
                ],
            },
            {
                "heading": "A note on the journey totals",
                "text": (
                    "Step 4 lands on 9/8, which is more than a whole. The bar only holds "
                    "8/8, so his health caps at full — exactly as it would in game. If "
                    "he notices and objects, that is a genuinely good observation: he has "
                    "spotted an improper fraction on his own. Name it for him and leave it "
                    "there; mixed numbers are next term's problem."
                ),
            },
            {
                "heading": "Where to go next",
                "bullets": [
                    "If Wednesday and Thursday were solid: unlike denominators, and "
                    "fractions greater than one (SOL 3.2, 3.5 extended).",
                    "If Thursday was a struggle: another week on equivalence alone, "
                    "using the same kit — do not move on.",
                    "Either way the kit is reusable. Keep the pocket.",
                    "Held in reserve from planning: “T-Minus” (place value to six digits "
                    "and rounding, SOL 3.1) and a repeat sound/vibrations science week.",
                ],
            },
            {
                "heading": "Please fill in the feedback page",
                "text": (
                    "The last page of the student packet is a two-minute parent feedback "
                    "sheet. There is currently no completed-packet feedback recorded at all, "
                    "which is why this week had to be planned from standards rather than "
                    "from what he has actually mastered. One filled-in sheet changes that."
                ),
            },
        ],
    )


def build_teacher_guide():
    pages = [
        ("", page_overview()),
        ("", page_practical()),
        ("Monday", page_mon_tue()),
        ("Wednesday", page_wed()),
        ("Thursday", page_thu()),
        ("Friday", page_fri()),
    ]
    return build_print_packet_html(pages, "Half a Heart — Teacher Guide", layout="journal")
