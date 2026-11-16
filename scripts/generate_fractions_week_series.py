#!/usr/bin/env python3
"""
Half a Heart — Fractions Week Series
Grade 2-3 | Mathematics | Layout: journal

Causal arc:
  Equal Parts -> Thirds & Sets -> Comparing Unit Fractions ->
  Equivalence, Non-Unit Fractions & the Number Line -> Adding and Subtracting

Narrator: Scout, a tamed wolf who follows the student home hurt on Monday and is
restored to full health by Friday. His health bar is drawn on every sheet, so the
student reads a fraction cold before any instruction, and can see the week's arc.

Standards (Virginia SOL):
  Monday    - 2.4.a/b            equal parts; halves, fourths, eighths (region model)
  Tuesday   - 2.4.a/b/c          thirds and sixths; fractions of a set
  Wednesday - 3.2.c              comparing unit fractions with >, <, =
  Thursday  - 3.2.a/b/c          non-unit fractions, equivalence, number line, not-equal
  Friday    - 3.5                add and subtract with like denominators

Design notes:
  * Every warm-up secretly rehearses that day's fraction skill in whole numbers
    (halving primes halves; "how many more to 12" primes finding "the rest").
  * Manipulatives are printed at exact physical sizes. The whole is 6 inches
    because 6 divides evenly by 1, 2, 3, 4, 6 and 12 — so most pieces land on
    whole- or half-inch ruler marks and the student can self-check with a ruler.
  * A calibration ruler appears on every manipulative page. Browser "fit to page"
    scaling silently shrinks output ~4-6%, which would stop pieces printed on
    different days from matching.

Output: fractions_week_series/fractions_week.html
        fractions_week_series/fractions_week_teacher_guide.html
"""

import os
import sys

os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.abspath("src"))

from worksheet_html_renderer import (  # noqa: E402
    build_print_packet_html,
    render_page,
)

OUT_DIR = "fractions_week_series"
NARRATOR = "Scout"

# Colouring palette — light enough to write on top of, distinct in greyscale.
RED = "#fca5a5"
GREEN = "#86efac"
BLUE = "#93c5fd"
YELLOW = "#fde68a"
PURPLE = "#d8b4fe"
ORANGE = "#fdba74"

# Scout's health across the week, in half-hearts out of 10 (5 hearts).
HEALTH = {
    "Monday": (5, "2½ / 5"),
    "Tuesday": (6, "3 / 5"),
    "Wednesday": (7, "3½ / 5"),
    "Thursday": (9, "4½ / 5"),
    "Friday": (10, "5 / 5"),
}

DAY_INDEX = {"Monday": 1, "Tuesday": 2, "Wednesday": 3, "Thursday": 4, "Friday": 5}


def meta(day, title, subtitle, rail, *, name_date=True, status=True):
    """Build the layout meta dict for one page."""
    filled, reading = HEALTH[day]
    out = {
        "day_label": day,
        "title": title,
        "subtitle": subtitle,
        "rail_text": f"{day} · {rail}",
        "day_index": DAY_INDEX[day],
        "total_days": 5,
        "show_name_date": name_date,
    }
    if status:
        out["status"] = {
            "label": "Scout's health",
            "hearts": 5,
            "filled_halves": filled,
            "reading": reading,
        }
    return out


def strip(denominator, label="", **kw):
    d = {"denominator": denominator, "label": label}
    d.update(kw)
    return d


# ═══════════════════════════════════════════════════════════════════════════
# Front matter
# ═══════════════════════════════════════════════════════════════════════════


def page_how_to():
    blocks = [
        (
            "storyPanel",
            {
                "who": "Before you start",
                "text": (
                    "This week you are going to look after a wolf named Scout.\n\n"
                    "Scout is hurt. Every day you will see his health bar at the top of "
                    "the page. Read it before you start. By Friday you should have him "
                    "back to full.\n\n"
                    "You will also build a fraction kit. Keep every piece you cut out — "
                    "you will need them all week."
                ),
            },
        ),
        (
            "noteBox",
            {
                "text": (
                    "GROWN-UPS: print this packet at 100% (Actual Size). Turn OFF "
                    '"Fit to page" or "Shrink to fit". The fraction pieces are printed at '
                    "exact sizes and will not match each other if the printer scales them. "
                    "Check the ruler below before cutting anything."
                )
            },
        ),
        ("calibrationRuler", {"inches": 6}),
        (
            "doingCard",
            {
                "label": "You will need",
                "text": (
                    "Scissors. Crayons or coloured pencils in red, green, blue and yellow. "
                    "A ruler. An envelope or zip bag for the fraction kit. Some string and "
                    "clothes pegs for Thursday."
                ),
            },
        ),
    ]
    return render_page(
        blocks,
        {
            "day_label": "",
            "title": "Half a Heart",
            "subtitle": "A week of fractions with Scout · how to use this packet",
            "rail_text": "Fractions Week",
            "total_days": 0,
            "show_name_date": False,
        },
        layout="journal",
    )


# ═══════════════════════════════════════════════════════════════════════════
# Monday — Equal Parts
# ═══════════════════════════════════════════════════════════════════════════


def monday_pages():
    a = render_page(
        [
            (
                "speedMath",
                {
                    "title": "Warm-Up: Half Of",
                    "instructions": "Say them out loud. Write the answer.",
                    "timer": "2 minutes",
                    "columns": 4,
                    "problems": [
                        "half of 2",
                        "half of 4",
                        "half of 6",
                        "half of 8",
                        "half of 10",
                        "half of 12",
                        "half of 16",
                        "half of 20",
                        "2 + 2",
                        "5 + 5",
                        "8 - 4",
                        "10 - 5",
                    ],
                },
            ),
            (
                "storyPanel",
                {
                    "who": "Scout's Log",
                    "text": (
                        "A wolf followed you home through the birch forest last night. "
                        "He is grey, he limps, and he will not leave your side. You named "
                        "him Scout.\n\n"
                        "Scout is hurt. Look at his health bar at the top of this page. It "
                        "is not full. It sits at two and a half hearts.\n\n"
                        "You already know how to read that. Half a heart. Not one, not "
                        "none — half. That is a fraction, and you have been reading "
                        "fractions for a long time without anyone telling you the word.\n\n"
                        "To get Scout back to full you need to know exactly what a half is. "
                        "And a fourth. And an eighth. Let's start."
                    ),
                },
            ),
            (
                "taskList",
                {
                    "tasks": [
                        {
                            "prompt": "Take a blank strip. Fold it in half. Open it up.",
                            "detail": (
                                "Trace the crease with a pencil. How many equal parts did "
                                "you make? Each one is called ONE HALF. Write 1/2 in each part."
                            ),
                        },
                        {
                            "prompt": "Fold the same strip in half again. Open it up.",
                            "detail": (
                                "Now how many equal parts? Each one is ONE FOURTH. "
                                "Write 1/4 in each part."
                            ),
                        },
                        {
                            "prompt": "Fold it in half one more time. Open it up.",
                            "detail": (
                                "How many parts now? These are EIGHTHS. What do you notice "
                                "about the number of parts each time you fold?"
                            ),
                            "response_lines": 2,
                        },
                    ]
                },
            ),
            (
                "noteBox",
                {
                    "text": (
                        "The bottom number of a fraction tells you how many EQUAL parts the "
                        "whole was cut into. Equal is the important word."
                    )
                },
            ),
        ],
        meta(
            "Monday",
            "Scout Needs Help",
            "Equal parts, and what the bottom number means",
            "Equal Parts",
        ),
        layout="journal",
    )

    b = render_page(
        [
            (
                "taskList",
                {
                    "start_number": 4,
                    "tasks": [
                        {
                            "prompt": "Circle every shape that is cut into FOURTHS.",
                            "detail": (
                                "Careful — some of these are cut into four pieces, but "
                                "the pieces are not equal. Four pieces is not the same as "
                                "fourths."
                            ),
                            "figure": {
                                "kind": "fractionArea",
                                "data": {
                                    # 0.9in keeps all five on one row; a second row would
                                    # push this page onto a second printed sheet.
                                    "size_in": 0.9,
                                    "grids": [
                                        # A, B, D are genuine fourths. C and E have four
                                        # pieces that are deliberately unequal.
                                        {"cols": 2, "rows": 2, "caption": "A"},
                                        {"cols": 4, "rows": 1, "caption": "B"},
                                        {"cols_spec": [3, 1, 1, 1], "rows": 1, "caption": "C"},
                                        {"cols": 1, "rows": 4, "caption": "D"},
                                        {
                                            "cols_spec": [2, 1],
                                            "rows_spec": [3, 1],
                                            "caption": "E",
                                        },
                                    ],
                                },
                            },
                        },
                    ],
                },
            ),
            (
                "taskList",
                {
                    "start_number": 5,
                    "tasks": [
                        {
                            "prompt": "Colour the circle to match the key.",
                            "figure": {
                                "kind": "colorTask",
                                "data": {
                                    "figure": {
                                        "kind": "fractionCircles",
                                        "data": {
                                            "size_in": 1.6,
                                            "circles": [{"parts": 4}],
                                        },
                                    },
                                    "entries": [
                                        {"fraction": "1/2", "color_name": "red", "hex": RED},
                                        {"fraction": "1/4", "color_name": "blue", "hex": BLUE},
                                        {
                                            "fraction": "the rest",
                                            "color_name": "yellow",
                                            "hex": YELLOW,
                                        },
                                    ],
                                },
                            },
                            "detail": (
                                "How many fourths did you colour red? How many did you "
                                "colour yellow?"
                            ),
                            "response_lines": 1,
                        },
                        {
                            "prompt": "Shade the strips to show the fraction written beside them.",
                            "figure": {
                                "kind": "fractionStrips",
                                "data": {
                                    "width_in": 4.5,
                                    "strips": [
                                        strip(2, "shade 1/2"),
                                        strip(4, "shade 3/4"),
                                        strip(8, "shade 5/8"),
                                    ],
                                },
                            },
                        },
                    ],
                },
            ),
            (
                "doingCard",
                {
                    "text": (
                        "At lunch, fold a tortilla or a slice of bread into fourths before "
                        "you eat it. Are your four pieces equal? Scout says that if they are "
                        "not equal they are not fourths — they are just four pieces."
                    )
                },
            ),
        ],
        meta(
            "Monday",
            "Equal or Not?",
            "Spotting fair shares, and colouring by fraction",
            "Equal Parts",
        ),
        layout="journal",
    )

    kit = render_page(
        [
            (
                "noteBox",
                {
                    "text": (
                        "MONDAY KIT PAGE. Check the ruler first. Then cut out the four blank "
                        "strips below. Do not cut them into pieces — you are going to "
                        "FOLD these."
                    )
                },
            ),
            ("calibrationRuler", {"inches": 6}),
            (
                "fractionStrips",
                {
                    "width_in": 6.0,
                    "height_in": 0.55,
                    "show_labels": False,
                    "strips": [
                        strip(1, "fold me"),
                        strip(1, "fold me"),
                        strip(1, "fold me"),
                        strip(1, "fold me"),
                    ],
                },
            ),
            ("cutLine", {}),
            (
                "noteBox",
                {
                    "text": (
                        "Below is what your folded strips should look like when you open them "
                        "up. Do not look until you have folded yours."
                    )
                },
            ),
            (
                "fractionStrips",
                {
                    "width_in": 6.0,
                    "strips": [
                        strip(2, "halves", color=BLUE, fill_all=True),
                        strip(4, "fourths", color=PURPLE, fill_all=True),
                        strip(8, "eighths", color=GREEN, fill_all=True),
                    ],
                },
            ),
        ],
        meta(
            "Monday",
            "Fold-and-Find Strips",
            "Cut these out, then fold to discover halves, fourths and eighths",
            "Kit",
            name_date=False,
        ),
        layout="journal",
    )
    return [a, b, kit]


# ═══════════════════════════════════════════════════════════════════════════
# Tuesday — Thirds, Sixths, and Sets
# ═══════════════════════════════════════════════════════════════════════════


def tuesday_pages():
    a = render_page(
        [
            (
                "speedMath",
                {
                    "title": "Warm-Up: Count by 3s and 6s",
                    "instructions": "Fill in what comes next.",
                    "timer": "2 minutes",
                    "columns": 3,
                    "problems": [
                        "3, 6, 9, ___",
                        "6, 12, 18, ___",
                        "3, 6, ___, 12",
                        "9 + 3",
                        "12 - 3",
                        "6 + 6",
                        "3 groups of 2 =",
                        "2 groups of 3 =",
                        "6 shared by 3 =",
                    ],
                },
            ),
            (
                "storyPanel",
                {
                    "who": "Scout's Log",
                    "text": (
                        "Scout slept by the fire and this morning he is hungry. Really "
                        "hungry.\n\n"
                        "There are six cooked pork chops in the chest. Scout cannot have all "
                        "six — some are for tonight and some are for the trip "
                        "tomorrow.\n\n"
                        "Yesterday you folded a strip in half, and in half again. But watch "
                        "what happens when you try to fold a strip into THREE equal parts. "
                        "Go on, try it. It is much harder. Some fractions you cannot get to "
                        "by folding in half over and over.\n\n"
                        "And here is something new: a fraction does not have to be part of "
                        "ONE thing. It can be part of a GROUP of things."
                    ),
                },
            ),
            (
                "taskList",
                {
                    "tasks": [
                        {
                            "prompt": "Try to fold a blank strip into three equal parts.",
                            "detail": (
                                "Was it harder than folding in half? Why do you think that is?"
                            ),
                            "response_lines": 2,
                        },
                        {
                            "prompt": "Here are Scout's 6 pork chops. Colour 1/3 of them red.",
                            "detail": (
                                "1/3 of a group of 6 means: split the 6 into 3 equal groups, "
                                "then take one group. How many chops did you colour?"
                            ),
                            "figure": {
                                "kind": "fractionArea",
                                "data": {
                                    "size_in": 0.62,
                                    "grids": [
                                        {"cols": 1, "rows": 1},
                                        {"cols": 1, "rows": 1},
                                        {"cols": 1, "rows": 1},
                                        {"cols": 1, "rows": 1},
                                        {"cols": 1, "rows": 1},
                                        {"cols": 1, "rows": 1},
                                    ],
                                },
                            },
                            "response_lines": 1,
                        },
                    ]
                },
            ),
        ],
        meta(
            "Tuesday", "Six Pork Chops", "Thirds, sixths, and fractions of a group", "Thirds & Sets"
        ),
        layout="journal",
    )

    b = render_page(
        [
            (
                "taskList",
                {
                    "start_number": 3,
                    "tasks": [
                        {
                            "prompt": "Colour the circle to match the key.",
                            "figure": {
                                "kind": "colorTask",
                                "data": {
                                    "figure": {
                                        "kind": "fractionCircles",
                                        "data": {"size_in": 1.6, "circles": [{"parts": 3}]},
                                    },
                                    "entries": [
                                        {"fraction": "1/3", "color_name": "red", "hex": RED},
                                        {
                                            "fraction": "the rest",
                                            "color_name": "blue",
                                            "hex": BLUE,
                                        },
                                    ],
                                },
                            },
                            "detail": "How many thirds are blue? Write the fraction.",
                            "response_lines": 1,
                        },
                        {
                            "prompt": "Shade each strip to show the fraction beside it.",
                            "figure": {
                                "kind": "fractionStrips",
                                "data": {
                                    "width_in": 4.5,
                                    "strips": [
                                        strip(3, "shade 2/3"),
                                        strip(6, "shade 4/6"),
                                        strip(6, "shade 1/6"),
                                    ],
                                },
                            },
                        },
                        {
                            "prompt": "Look at the top two strips you just shaded.",
                            "detail": (
                                "You shaded 2/3 on one and 4/6 on the other. Are the shaded "
                                "parts the same size? What does that tell you?"
                            ),
                            "response_lines": 2,
                        },
                    ],
                },
            ),
            (
                "doingCard",
                {
                    "text": (
                        "Get 6 crackers and 3 bowls. Share the crackers equally between the "
                        "bowls. How many in each bowl? Now do it again with 3 bowls and 12 "
                        "crackers. Scout wants to know if he gets more or less that way."
                    )
                },
            ),
        ],
        meta(
            "Tuesday",
            "Sharing It Out",
            "Thirds and sixths on strips, circles and in groups",
            "Thirds & Sets",
        ),
        layout="journal",
    )

    kit = render_page(
        [
            (
                "noteBox",
                {
                    "text": (
                        "TUESDAY KIT PAGE. Check the ruler. Then cut out these strips and cut "
                        "ALONG the dashed lines to make loose pieces. Add them to your kit."
                    )
                },
            ),
            ("calibrationRuler", {"inches": 6}),
            (
                "fractionStrips",
                {
                    "width_in": 6.0,
                    "height_in": 0.5,
                    "strips": [
                        strip(3, "thirds", color=GREEN, fill_all=True),
                        strip(6, "sixths", color=ORANGE, fill_all=True),
                    ],
                },
            ),
            ("cutLine", {}),
            (
                "noteBox",
                {
                    "text": (
                        "These two are REFERENCE BARS. Do not cut them into pieces — "
                        "keep them whole and lay your loose pieces on top to check them."
                    )
                },
            ),
            (
                "fractionStrips",
                {
                    "width_in": 6.0,
                    "height_in": 0.5,
                    "strips": [
                        strip(1, "one whole"),
                        strip(12, "twelfths", piece_label=""),
                    ],
                },
            ),
        ],
        meta(
            "Tuesday",
            "Thirds and Sixths",
            "Cut these out — folding will not get you thirds",
            "Kit",
            name_date=False,
        ),
        layout="journal",
    )
    return [a, b, kit]


# ═══════════════════════════════════════════════════════════════════════════
# Wednesday — Comparing Unit Fractions
# ═══════════════════════════════════════════════════════════════════════════


def wednesday_pages():
    a = render_page(
        [
            (
                "speedMath",
                {
                    "title": "Warm-Up: Bigger or Smaller",
                    "instructions": "Write > or < between each pair.",
                    "timer": "2 minutes",
                    "columns": 4,
                    "answer_style": "box",
                    "problems": [
                        "8 ___ 3",
                        "12 ___ 20",
                        "7 ___ 7 + 1",
                        "15 ___ 9",
                        "4 + 4 ___ 10",
                        "20 - 5 ___ 14",
                        "6 ___ 2 + 3",
                        "11 ___ 11",
                    ],
                },
            ),
            (
                "storyPanel",
                {
                    "who": "Scout's Log",
                    "text": (
                        "Scout has found two food caches in the woods.\n\n"
                        "One is close by. You may take one HALF of what is inside it.\n\n"
                        "The other is a long walk away, over the hill. You may take one "
                        "EIGHTH of what is inside that one.\n\n"
                        "Scout is looking at you. Eight is a much bigger number than two. So "
                        "is an eighth a bigger piece than a half?\n\n"
                        "Get your fraction kit out. Do not guess. Put the pieces on top of "
                        "each other and look."
                    ),
                },
            ),
            (
                "taskList",
                {
                    "tasks": [
                        {
                            "prompt": "Lay your 1/8 piece on top of your 1/2 piece.",
                            "detail": "Which piece is bigger? Write it: 1/2 is ______ than 1/8.",
                            "response_lines": 1,
                        },
                        {
                            "prompt": "Now put these in order, biggest piece first.",
                            "detail": "Use your kit pieces: 1/4, 1/2, 1/8, 1/3, 1/6, 1/12",
                            "response_lines": 2,
                        },
                        {
                            "prompt": "Finish the rule.",
                            "detail": (
                                "When the bottom number gets BIGGER, the piece gets "
                                "______________. Why does that happen?"
                            ),
                            "response_lines": 2,
                        },
                    ]
                },
            ),
        ],
        meta(
            "Wednesday",
            "Two Caches",
            "The bigger the bottom number, the smaller the piece",
            "Comparing",
        ),
        layout="journal",
    )

    b = render_page(
        [
            (
                "taskList",
                {
                    "start_number": 4,
                    "tasks": [
                        {
                            "prompt": "Write > or < in each box. Use your kit to check every one.",
                            "figure": {
                                "kind": "comparePairs",
                                "data": {
                                    "columns": 3,
                                    "pairs": [
                                        {"left": "1/2", "right": "1/4"},
                                        {"left": "1/3", "right": "1/6"},
                                        {"left": "1/8", "right": "1/4"},
                                        {"left": "1/12", "right": "1/3"},
                                        {"left": "1/6", "right": "1/8"},
                                        {"left": "1/2", "right": "1/12"},
                                    ],
                                },
                            },
                        },
                        {
                            "prompt": "Colour the circle to match the key.",
                            "figure": {
                                "kind": "colorTask",
                                "data": {
                                    "figure": {
                                        "kind": "fractionCircles",
                                        "data": {"size_in": 1.6, "circles": [{"parts": 8}]},
                                    },
                                    "entries": [
                                        {"fraction": "1/2", "color_name": "green", "hex": GREEN},
                                        {"fraction": "1/4", "color_name": "red", "hex": RED},
                                        {
                                            "fraction": "the rest",
                                            "color_name": "blue",
                                            "hex": BLUE,
                                        },
                                    ],
                                },
                            },
                            "detail": "How many eighths ended up blue?",
                            "response_lines": 1,
                        },
                    ],
                },
            ),
            (
                "storyPanel",
                {
                    "who": "Careful now",
                    "text": (
                        "Scout has one more question, and it is a sneaky one.\n\n"
                        "Would you rather have HALF of a tiny biscuit, or an EIGHTH of an "
                        "enormous cake?\n\n"
                        "So when we say 1/2 is bigger than 1/8, we are only right if both "
                        "pieces came from the SAME SIZE whole. Comparing only works when the "
                        "wholes match."
                    ),
                },
            ),
            (
                "taskList",
                {
                    "start_number": 6,
                    "tasks": [
                        {
                            "prompt": "Answer Scout's sneaky question.",
                            "detail": (
                                "Which would you pick, and why? There is no wrong answer as "
                                "long as you can explain it."
                            ),
                            "response_lines": 2,
                        }
                    ],
                },
            ),
            (
                "doingCard",
                {
                    "text": (
                        "Ask a grown-up for one biscuit. Would you rather have 1/2 of it or "
                        "1/8 of it? Now ask them to show you 1/2 of a small biscuit next to "
                        "1/8 of a whole tray of biscuits. Did your answer change?"
                    )
                },
            ),
        ],
        meta(
            "Wednesday",
            "Which Is Bigger?",
            "Comparing with >, <, and why the whole matters",
            "Comparing",
        ),
        layout="journal",
    )

    kit1 = render_page(
        [
            (
                "noteBox",
                {
                    "text": (
                        "WEDNESDAY KIT PAGE 1. Check the ruler. Cut out these strips. Cut the "
                        "top three into loose pieces. Leave the bottom two whole as reference "
                        "bars."
                    )
                },
            ),
            ("calibrationRuler", {"inches": 6}),
            (
                "fractionStrips",
                {
                    "width_in": 6.0,
                    "height_in": 0.5,
                    "strips": [
                        strip(1, "1 whole", color="#f3f4f6", fill_all=True),
                        strip(2, "halves", color=BLUE, fill_all=True),
                        strip(4, "fourths", color=PURPLE, fill_all=True),
                    ],
                },
            ),
            ("cutLine", {}),
            (
                "fractionStrips",
                {
                    "width_in": 6.0,
                    "height_in": 0.5,
                    "strips": [
                        strip(8, "eighths", color="#ccfbf1", fill_all=True, piece_label=""),
                        strip(10, "tenths", color="#fce7f3", fill_all=True, piece_label=""),
                    ],
                },
            ),
        ],
        meta(
            "Wednesday",
            "The Full Kit",
            "Everything you need to compare any two fractions",
            "Kit",
            name_date=False,
        ),
        layout="journal",
    )

    kit2 = render_page(
        [
            (
                "noteBox",
                {
                    "text": (
                        "WEDNESDAY KIT PAGE 2 — the pocket. Cut around the outside of the "
                        "big rectangle. Fold up along the dotted line. Tape the two sides. Keep "
                        "all your fraction pieces in here."
                    )
                },
            ),
            (
                "fractionStrips",
                {
                    "width_in": 6.5,
                    "height_in": 1.6,
                    "show_labels": False,
                    "strips": [strip(1, "")],
                },
            ),
            (
                "noteBox",
                {"text": "↑ fold up along this line ↑"},
            ),
            (
                "fractionStrips",
                {
                    "width_in": 6.5,
                    "height_in": 2.1,
                    "show_labels": False,
                    "strips": [strip(1, "")],
                },
            ),
            (
                "doingCard",
                {
                    "label": "Label your pocket",
                    "text": (
                        "Write SCOUT'S FRACTION KIT on the front, and your name under it. "
                        "Draw Scout on it if you like. You need this kit again tomorrow and "
                        "on Friday."
                    ),
                },
            ),
        ],
        meta(
            "Wednesday",
            "A Pocket for the Kit",
            "Fold, tape, and keep every piece",
            "Kit",
            name_date=False,
        ),
        layout="journal",
    )
    return [a, b, kit1, kit2]


# ═══════════════════════════════════════════════════════════════════════════
# Thursday — Equivalence, Non-Unit Fractions, Number Line
# ═══════════════════════════════════════════════════════════════════════════


def thursday_pages():
    a = render_page(
        [
            (
                "speedMath",
                {
                    "title": "Warm-Up: How Many More?",
                    "instructions": "How many more do you need to reach the target?",
                    "timer": "2 minutes",
                    "columns": 4,
                    "problems": [
                        "4 + ___ = 12",
                        "9 + ___ = 12",
                        "6 + ___ = 12",
                        "10 + ___ = 12",
                        "3 + ___ = 6",
                        "5 + ___ = 6",
                        "2 + ___ = 8",
                        "7 + ___ = 8",
                    ],
                },
            ),
            (
                "storyPanel",
                {
                    "who": "Scout's Log",
                    "text": (
                        "Scout is nearly well. He ate, he slept by the fire, and this morning "
                        "he chased a chicken across the whole yard — which is how you "
                        "know he feels better.\n\n"
                        "But there is one more job, and it is the trickiest yet. The food "
                        "chest has to be split three ways: some for right now, some for the "
                        "trip tomorrow, and whatever is left for the day after.\n\n"
                        "Nobody tells you how big whatever is left is. You have to work that "
                        "out yourself. That is what the whole warm-up was about."
                    ),
                },
            ),
            (
                "taskList",
                {
                    "tasks": [
                        {
                            "prompt": "Colour the circle to match the key. Work out the rest yourself.",
                            "figure": {
                                "kind": "colorTask",
                                "data": {
                                    "figure": {
                                        "kind": "fractionCircles",
                                        "data": {"size_in": 1.75, "circles": [{"parts": 6}]},
                                    },
                                    "entries": [
                                        {"fraction": "1/3", "color_name": "red", "hex": RED},
                                        {"fraction": "1/2", "color_name": "green", "hex": GREEN},
                                        {
                                            "fraction": "the rest",
                                            "color_name": "blue",
                                            "hex": BLUE,
                                        },
                                    ],
                                },
                            },
                            "detail": (
                                "How many sixths did you colour blue? Write it as a fraction. "
                                "Use your kit if you get stuck — how many sixths fit on "
                                "top of 1/3?"
                            ),
                            "response_lines": 1,
                        },
                    ]
                },
            ),
            (
                "noteBox",
                {
                    "text": (
                        "Two fractions that look different but are exactly the same size are "
                        "called EQUIVALENT. 1/2 and 3/6 are equivalent."
                    )
                },
            ),
        ],
        meta("Thursday", "What's Left Over", "Equivalence, and working out “the rest”", "The Rest"),
        layout="journal",
    )

    b = render_page(
        [
            (
                "taskList",
                {
                    "start_number": 2,
                    "tasks": [
                        {
                            "prompt": "Shade 1/2 of the top strip and 3/6 of the bottom strip.",
                            "figure": {
                                "kind": "fractionStrips",
                                "data": {
                                    "width_in": 5.0,
                                    "strips": [strip(2, ""), strip(6, "")],
                                },
                            },
                            "detail": "Are the shaded parts the same size? Write = or ≠ between them.",
                            "response_lines": 1,
                        },
                        {
                            "prompt": "Shade each square to match its caption. Two of them are equivalent.",
                            "figure": {
                                "kind": "fractionArea",
                                "data": {
                                    "size_in": 1.5,
                                    "grids": [
                                        {"cols": 2, "rows": 2, "caption": "shade 2/4"},
                                        {"cols": 4, "rows": 2, "caption": "shade 4/8"},
                                        {"cols": 3, "rows": 1, "caption": "shade 2/3"},
                                    ],
                                },
                            },
                            "detail": "Which two are equivalent? Circle them.",
                        },
                        {
                            "prompt": "Write > , < or = in each box. Same bottom number is easy — just count.",
                            "figure": {
                                "kind": "comparePairs",
                                "data": {
                                    "columns": 3,
                                    "pairs": [
                                        {"left": "3/8", "right": "5/8"},
                                        {"left": "2/6", "right": "5/6"},
                                        {"left": "7/8", "right": "3/8"},
                                        {"left": "4/6", "right": "4/6"},
                                        {"left": "1/2", "right": "4/8"},
                                        {"left": "2/3", "right": "1/3"},
                                    ],
                                },
                            },
                        },
                    ],
                },
            ),
        ],
        meta("Thursday", "Same Size, Different Name", "Equivalence and comparing", "The Rest"),
        layout="journal",
    )

    c = render_page(
        [
            (
                "storyPanel",
                {
                    "who": "A fraction is a number",
                    "text": (
                        "Everything you have coloured this week has been a PICTURE of a "
                        "fraction. But a fraction is not only a picture. It is a number, and "
                        "every number has its own place on a line.\n\n"
                        "1/2 is not just a shape cut in half. It is a number that sits exactly "
                        "halfway between 0 and 1."
                    ),
                },
            ),
            (
                "taskList",
                {
                    "start_number": 5,
                    "tasks": [
                        {
                            "prompt": "Mark 3/4 on this line with an X.",
                            "figure": {
                                "kind": "fractionNumberLine",
                                "data": {
                                    "width_in": 5.4,
                                    "lines": [{"denominator": 4}],
                                },
                            },
                        },
                        {
                            "prompt": "Mark 1/2 on this line with an X.",
                            "detail": "Careful — this line is cut into sixths, not halves.",
                            "figure": {
                                "kind": "fractionNumberLine",
                                "data": {
                                    "width_in": 5.4,
                                    "lines": [{"denominator": 6, "show_labels": False}],
                                },
                            },
                        },
                        {
                            "prompt": "Mark 2/8 AND 1/4 on this line. What do you notice?",
                            "figure": {
                                "kind": "fractionNumberLine",
                                "data": {
                                    "width_in": 5.4,
                                    "lines": [{"denominator": 8}],
                                },
                            },
                            "response_lines": 2,
                        },
                    ],
                },
            ),
            (
                "doingCard",
                {
                    "text": (
                        "Hang a string across the room. Peg the 0 card at one end and the 1 "
                        "card at the other. Now peg every fraction card where you think it "
                        "goes. Check 1/2 with your fraction strip — is it exactly in the "
                        "middle? Which cards ended up on top of each other?"
                    )
                },
            ),
        ],
        meta("Thursday", "Fractions on a Line", "Where does a fraction actually live?", "The Rest"),
        layout="journal",
    )

    kit = render_page(
        [
            (
                "noteBox",
                {
                    "text": (
                        "THURSDAY KIT PAGE. Cut out these cards for the string number line. "
                        "Keep them in your pocket afterwards."
                    )
                },
            ),
            (
                "cutCards",
                {
                    "columns": 5,
                    "cards": [
                        "0",
                        "1/4",
                        "1/2",
                        "3/4",
                        "1",
                        "1/6",
                        "1/3",
                        "2/3",
                        "5/6",
                        "2/2",
                        "1/8",
                        "3/8",
                        "5/8",
                        "7/8",
                        "4/4",
                    ],
                },
            ),
            (
                "noteBox",
                {
                    "text": (
                        "Three of these cards are all worth the same. Can you find them before "
                        "you peg them up?"
                    )
                },
            ),
            (
                "fractionNumberLine",
                {
                    "width_in": 6.0,
                    "lines": [
                        {
                            "denominator": 8,
                            "prompt": "Practice line — eighths, all labelled for you.",
                        }
                    ],
                },
            ),
        ],
        meta(
            "Thursday",
            "Number Line Cards",
            "Cut out and peg onto the string",
            "Kit",
            name_date=False,
        ),
        layout="journal",
    )
    return [a, b, c, kit]


# ═══════════════════════════════════════════════════════════════════════════
# Friday — Adding and Subtracting + Capstone
# ═══════════════════════════════════════════════════════════════════════════


def friday_pages():
    a = render_page(
        [
            (
                "speedMath",
                {
                    "title": "Warm-Up: Add and Take Away",
                    "instructions": "Quick as you can.",
                    "timer": "2 minutes",
                    "columns": 4,
                    "problems": [
                        "3 + 2",
                        "5 + 3",
                        "7 - 4",
                        "8 - 5",
                        "4 + 4",
                        "6 + 5",
                        "12 - 7",
                        "10 - 6",
                        "3 + 2 + 1",
                        "9 - 3 - 2",
                        "5 + 5 + 2",
                        "11 - 5",
                    ],
                },
            ),
            (
                "storyPanel",
                {
                    "who": "Scout's Log",
                    "text": (
                        "Scout is well. His bar is full — five whole hearts. Look at the "
                        "top of the page.\n\n"
                        "Today you are both going out. Down through the birch forest, past the "
                        "two caches, over the hill and home again before dark.\n\n"
                        "Things are going to happen out there. Scout will take some damage and "
                        "he will find some food. You need to keep track of his health the "
                        "whole way, in eighths.\n\n"
                        "One last thing before you go. When you add 3/8 and 2/8 you get 5/8. "
                        "You add the COUNT of pieces. The pieces do not change size. The "
                        "bottom number stays put."
                    ),
                },
            ),
            (
                "taskList",
                {
                    "tasks": [
                        {
                            "prompt": "Work these out. Use your kit pieces if you need them.",
                            "figure": {
                                "kind": "speedMath",
                                "data": {
                                    "title": "",
                                    "columns": 2,
                                    "problems": [
                                        "3/8 + 2/8 =",
                                        "1/6 + 4/6 =",
                                        "5/8 − 2/8 =",
                                        "5/6 − 3/6 =",
                                        "2/8 + 5/8 =",
                                        "6/6 − 2/6 =",
                                    ],
                                },
                            },
                        },
                        {
                            "prompt": "Scout says the answer to 3/8 + 2/8 is 5/16. Is he right?",
                            "detail": (
                                "Use your strips to check. What did Scout do wrong? Explain it "
                                "to him."
                            ),
                            "response_lines": 3,
                        },
                    ]
                },
            ),
        ],
        meta(
            "Friday",
            "The Journey",
            "Adding and subtracting when the bottom numbers match",
            "Adding",
        ),
        layout="journal",
    )

    b = render_page(
        [
            (
                "storyPanel",
                {
                    "who": "The Journey — keep score",
                    "text": (
                        "Scout starts with 8/8 of his health. Shade each bar to show his "
                        "health after each thing that happens. The first one is done for you."
                    ),
                },
            ),
            (
                "taskList",
                {
                    "tasks": [
                        {
                            "prompt": "START: Scout is at full health, 8/8.",
                            "figure": {
                                "kind": "heartBar",
                                "data": {
                                    "hearts": 4,
                                    "filled_halves": 8,
                                    "width_in": 3.2,
                                    "caption": "8/8 — done for you",
                                },
                            },
                        },
                        {
                            "prompt": "A skeleton hits Scout. He loses 2/8. Shade what is left.",
                            "figure": {
                                "kind": "heartBar",
                                "data": {
                                    "hearts": 4,
                                    "filled_halves": 0,
                                    "width_in": 3.2,
                                    "caption": "____ / 8",
                                },
                            },
                        },
                        {
                            "prompt": "He falls off a ledge and loses another 3/8. Shade what is left.",
                            "figure": {
                                "kind": "heartBar",
                                "data": {
                                    "hearts": 4,
                                    "filled_halves": 0,
                                    "width_in": 3.2,
                                    "caption": "____ / 8",
                                },
                            },
                        },
                        {
                            "prompt": "You feed him. He gains back 4/8. Shade what he has now.",
                            "figure": {
                                "kind": "heartBar",
                                "data": {
                                    "hearts": 4,
                                    "filled_halves": 0,
                                    "width_in": 3.2,
                                    "caption": "____ / 8",
                                },
                            },
                        },
                        {
                            "prompt": "Home safe. He sleeps and gains 2/8 more. Shade his final health.",
                            "figure": {
                                "kind": "heartBar",
                                "data": {
                                    "hearts": 4,
                                    "filled_halves": 0,
                                    "width_in": 3.2,
                                    "caption": "____ / 8",
                                },
                            },
                        },
                        {
                            "prompt": "Did Scout make it home without his bar reaching zero?",
                            "detail": "What was the lowest his health got on the whole trip?",
                            "response_lines": 2,
                        },
                    ]
                },
            ),
        ],
        meta(
            "Friday",
            "Keeping Scout Alive",
            "A running total, in eighths, all the way home",
            "Adding",
        ),
        layout="journal",
    )

    capstone = render_page(
        [
            (
                "noteBox",
                {
                    "text": (
                        "SHOW WHAT YOU KNOW. No kit for this page if you can manage without "
                        "it — but it is not cheating to use it."
                    )
                },
            ),
            (
                "taskList",
                {
                    "tasks": [
                        {
                            "prompt": "Write the fraction shaded under each square.",
                            "figure": {
                                "kind": "fractionArea",
                                "data": {
                                    "size_in": 1.1,
                                    "grids": [
                                        {"cols": 2, "rows": 2, "shaded": [0], "caption": "______"},
                                        {
                                            "cols": 3,
                                            "rows": 1,
                                            "shaded": [0, 1],
                                            "caption": "______",
                                        },
                                        {
                                            "cols": 4,
                                            "rows": 2,
                                            "shaded": [0, 1, 2, 4, 5, 6],
                                            "caption": "______",
                                        },
                                        {
                                            "cols": 3,
                                            "rows": 2,
                                            "shaded": [0, 1, 3],
                                            "caption": "______",
                                        },
                                    ],
                                },
                            },
                        },
                        {
                            "prompt": "Put a ring round the BIGGEST fraction in each row.",
                            "figure": {
                                "kind": "richText",
                                "data": {
                                    "sections": [
                                        {
                                            "bullets": [
                                                "1/2   ·   1/8   ·   1/4",
                                                "2/6   ·   5/6   ·   1/6",
                                                "3/4   ·   1/4   ·   4/4",
                                            ]
                                        }
                                    ]
                                },
                            },
                        },
                        {
                            "prompt": "Colour to match the key. Work out the rest.",
                            "figure": {
                                "kind": "colorTask",
                                "data": {
                                    "figure": {
                                        "kind": "fractionCircles",
                                        "data": {"size_in": 1.6, "circles": [{"parts": 8}]},
                                    },
                                    "entries": [
                                        {"fraction": "1/4", "color_name": "red", "hex": RED},
                                        {"fraction": "1/2", "color_name": "yellow", "hex": YELLOW},
                                        {
                                            "fraction": "the rest",
                                            "color_name": "green",
                                            "hex": GREEN,
                                        },
                                    ],
                                },
                            },
                            "response_lines": 1,
                        },
                        {
                            "prompt": "Tell Scout the rule in your own words.",
                            "detail": (
                                "Why is 1/8 smaller than 1/2, even though 8 is bigger than 2?"
                            ),
                            "response_lines": 2,
                        },
                    ]
                },
            ),
        ],
        meta("Friday", "Show What You Know", "Friday capstone", "Capstone"),
        layout="journal",
    )
    return [a, b, capstone]


# ═══════════════════════════════════════════════════════════════════════════
# Parent feedback
# ═══════════════════════════════════════════════════════════════════════════


def page_feedback():
    return render_page(
        [
            (
                "noteBox",
                {
                    "text": (
                        "For the grown-up. Fill this in after Friday and keep it — it "
                        "decides what next week looks like."
                    )
                },
            ),
            (
                "taskList",
                {
                    "tasks": [
                        {
                            "prompt": "Which days felt too easy?",
                            "response_lines": 2,
                        },
                        {
                            "prompt": "Which days were a real struggle?",
                            "response_lines": 2,
                        },
                        {
                            "prompt": "Did he get the Wednesday idea — bigger bottom number, smaller piece?",
                            "detail": "Circle one:   not yet   /   with the kit   /   without the kit",
                            "response_lines": 1,
                        },
                        {
                            "prompt": "Could he work out “the rest” on Thursday without help?",
                            "detail": "Circle one:   not yet   /   with a hint   /   on his own",
                            "response_lines": 1,
                        },
                        {
                            "prompt": "Was the amount of work per day about right?",
                            "detail": "Circle one:   too little   /   about right   /   too much",
                            "response_lines": 1,
                        },
                        {
                            "prompt": "Anything he particularly liked or hated?",
                            "response_lines": 3,
                        },
                    ]
                },
            ),
        ],
        {
            "day_label": "",
            "title": "How Did the Week Go?",
            "subtitle": "Parent feedback — one page, takes two minutes",
            "rail_text": "Feedback",
            "total_days": 0,
            "show_name_date": False,
        },
        layout="journal",
    )


# ═══════════════════════════════════════════════════════════════════════════
# Assembly
# ═══════════════════════════════════════════════════════════════════════════


def build_student_packet():
    pages = [("", page_how_to())]
    for day, builder in (
        ("Monday", monday_pages),
        ("Tuesday", tuesday_pages),
        ("Wednesday", wednesday_pages),
        ("Thursday", thursday_pages),
        ("Friday", friday_pages),
    ):
        pages.extend((day, frag) for frag in builder())
    pages.append(("", page_feedback()))
    return build_print_packet_html(pages, "Half a Heart — Fractions Week", layout="journal")


def main():
    os.makedirs(OUT_DIR, exist_ok=True)

    student_path = os.path.join(OUT_DIR, "fractions_week.html")
    with open(student_path, "w", encoding="utf-8") as fh:
        fh.write(build_student_packet())
    print(f"Wrote {student_path}")

    from fractions_week_teacher_guide import build_teacher_guide  # noqa: E402

    guide_path = os.path.join(OUT_DIR, "fractions_week_teacher_guide.html")
    with open(guide_path, "w", encoding="utf-8") as fh:
        fh.write(build_teacher_guide())
    print(f"Wrote {guide_path}")


if __name__ == "__main__":
    main()
