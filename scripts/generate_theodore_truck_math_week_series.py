#!/usr/bin/env python3
"""
Theodore's Truck & Car Math Week — Week Series
Age 3 (pre-K) | Mathematics | Layout: journal

Developmental note: curriculum.db has no pre-K grade level (youngest is K), so this
week is developmentally-targeted rather than standards-aligned — see AGENTS.md's
existing "Ages 3-4" carve-out for the same reasoning applied to phonics.

Causal arc (concrete -> symbolic, each day building on the last):
  Counting groups 1:1 -> Joining groups (addition) -> Groups shrinking (subtraction)
  -> Comparing two groups (>/<) -> Mixed review & a build-your-own-rig capstone

Every problem stays pictorially countable — real vehicle emoji stand in for objects,
never a bare abstract equation. Numbers run 0-10, but addends/subtrahends are kept
small enough that a 3-year-old can literally count every icon on the page.

Each day is four short activities rather than one long sitting (~50-60 minutes total,
best run as several 10-15 minute chunks across the day): teach/model, independent
practice, a paired reference/matching page, and a distinct hands-on or game-based
activity (scavenger hunt, dice game, acted-out story problems, or a block-stacking
game) that gets Theodore off the page and moving.

Narrator: Duke the Truck Dog, a good ol' dog who rides shotgun in a different real
truck or car every day. Introduced Monday. (Named separately from the student's own
nickname "Theo" on purpose, to avoid confusing the two.)

Real logos: each day features one real, current vehicle-make logo (Ford, Chevrolet,
Peterbilt, Freightliner, International) as a small badge — sourced from Wikimedia
Commons (licensing-checked), embedded as base64 data URIs below so this script fully
reproduces the week offline with no network dependency. Personal, non-commercial,
non-distributed home use.

Output: theodore_truck_math_week_series/theodore_truck_math_week.html
        theodore_truck_math_week_series/theodore_truck_math_week_teacher_guide.html
"""

import os
import sys

os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.abspath("src"))

from worksheet_html_renderer import (  # noqa: E402
    build_print_packet_html,
    render_page,
    render_worksheet_html,
)

OUT_DIR = "theodore_truck_math_week_series"
NARRATOR = "Duke the Truck Dog"
DAY_INDEX = {"Monday": 1, "Tuesday": 2, "Wednesday": 3, "Thursday": 4, "Friday": 5}


def logo_badge(make: str, kicker: str) -> tuple[str, dict]:
    """A logoBadge block for today's featured real vehicle make."""
    return (
        "logoBadge",
        {"src": LOGOS[make], "alt": f"{make} logo", "caption": f"{kicker}: {make.upper()}"},
    )


def meta(day, title, subtitle, rail, *, name_date=True):
    return {
        "day_label": day,
        "title": title,
        "subtitle": subtitle,
        "rail_text": f"{day} · {rail}",
        "day_index": DAY_INDEX[day],
        "total_days": 5,
        "show_name_date": name_date,
    }


# ═══════════════════════════════════════════════════════════════════════════
# Monday — Counting 0-10 (Peterbilt)
# ═══════════════════════════════════════════════════════════════════════════


def monday_pages():
    a = render_page(
        [
            logo_badge("Peterbilt", "Today's Truck"),
            (
                "storyPanel",
                {
                    "who": NARRATOR,
                    "text": (
                        "Woof! I'm Duke, and I ride along in a different truck every day this "
                        "week! Today my friend is driving a shiny red PETERBILT rig.\n\n"
                        "Before we go anywhere, let's count the trucks we see. Ready? Point to "
                        "each one and count out loud!"
                    ),
                },
            ),
            (
                "taskList",
                {
                    "tasks": [
                        {"prompt": "🚛🚛", "detail": "Count together out loud: 1... 2!"},
                        {
                            "prompt": "🚛🚛🚛🚛🚛",
                            "detail": "Point to each rig as you count: 1, 2, 3, 4, 5!",
                        },
                        {
                            "prompt": "🚛🚛🚛🚛🚛🚛🚛🚛",
                            "detail": "This is a big group! Count slowly all the way to 8.",
                        },
                    ]
                },
            ),
            (
                "doingCard",
                {
                    "label": "Go and do",
                    "text": (
                        "Line up your toy trucks and cars in a row. Touch each one and count "
                        "out loud together. Can you count all the way to ten?"
                    ),
                },
            ),
        ],
        meta("Monday", "Count the Rigs!", "Learning to count groups, 0 to 10", "Counting"),
        layout="journal",
    )

    b = render_page(
        [
            (
                "speedMath",
                {
                    "title": "Count and Write",
                    "instructions": "How many trucks? Count them, then write the number in the box.",
                    "answer_style": "box",
                    "columns": 2,
                    "problems": [
                        {"q": "🚛"},
                        {"q": "🚛🚛🚛"},
                        {"q": "🚛🚛🚛🚛"},
                        {"q": "🚛🚛🚛🚛🚛🚛"},
                        {"q": "🚛🚛🚛🚛🚛🚛🚛"},
                        {"q": "🚛🚛🚛🚛🚛🚛🚛🚛🚛🚛"},
                    ],
                },
            ),
            (
                "noteBox",
                {
                    "text": (
                        "Nice counting! Tomorrow Duke rides along in a FORD, and we'll learn "
                        "about ADDING trucks together."
                    )
                },
            ),
        ],
        meta(
            "Monday",
            "Monday: You Try!",
            "Independent counting practice",
            "Counting",
            name_date=False,
        ),
        layout="journal",
    )

    c = render_worksheet_html(
        "matchingWorksheet",
        {
            "title": "Match the Number!",
            "instructions": "Read the number. Count the trucks next to it — do they match?",
            "left_items": ["2", "4", "5", "8", "9"],
            "right_items": [
                "🚛🚛",
                "🚛🚛🚛🚛",
                "🚛🚛🚛🚛🚛",
                "🚛🚛🚛🚛🚛🚛🚛🚛",
                "🚛🚛🚛🚛🚛🚛🚛🚛🚛",
            ],
        },
        day_label="Monday",
    )

    d = render_page(
        [
            (
                "noteBox",
                {
                    "text": (
                        "Grab a grown-up and go on a real truck-and-car hunt — around your "
                        "house, in your driveway, or on a walk. Count each kind you find."
                    )
                },
            ),
            (
                "taskList",
                {
                    "tasks": [
                        {
                            "prompt": "How many toy trucks can you find in your toy box?",
                            "response_lines": 1,
                        },
                        {
                            "prompt": "How many real cars are parked near your home?",
                            "response_lines": 1,
                        },
                        {
                            "prompt": (
                                "Watch outside for 2 minutes. How many trucks or vans go by?"
                            ),
                            "response_lines": 1,
                        },
                        {
                            "prompt": "How many wheels does your favorite toy truck have?",
                            "response_lines": 1,
                        },
                    ]
                },
            ),
            (
                "doingCard",
                {
                    "label": "Bonus",
                    "text": (
                        "Find one BIG truck and one SMALL car. Point to each — which one do "
                        "you think is heavier?"
                    ),
                },
            ),
        ],
        meta(
            "Monday",
            "Truck & Car Scavenger Hunt",
            "A real-world counting adventure",
            "Counting",
            name_date=False,
        ),
        layout="journal",
    )
    return [a, b, c, d]


# ═══════════════════════════════════════════════════════════════════════════
# Tuesday — Addition (Ford)
# ═══════════════════════════════════════════════════════════════════════════


def tuesday_pages():
    a = render_page(
        [
            logo_badge("Ford", "Today's Truck"),
            (
                "storyPanel",
                {
                    "who": NARRATOR,
                    "text": (
                        "Today I'm riding in a blue FORD pickup! We're picking up friends "
                        "along the way — every time we pick up more, our group gets bigger.\n\n"
                        "That's called ADDING. The '+' sign means 'and more.'"
                    ),
                },
            ),
            (
                "noteBox",
                {
                    "text": (
                        "ADDING means putting two groups together to make one bigger group. "
                        "Count everything together to find the total."
                    )
                },
            ),
            (
                "taskList",
                {
                    "tasks": [
                        {
                            "prompt": "🛻🛻 + 🛻 = ?",
                            "detail": "2 trucks and 1 more truck. Count them all: 1, 2, 3. 2 + 1 = 3!",
                        },
                        {
                            "prompt": "🛻🛻🛻 + 🛻🛻 = ?",
                            "detail": "3 trucks and 2 more. Count them all: 1, 2, 3, 4, 5. 3 + 2 = 5!",
                        },
                        {
                            "prompt": "🛻🛻🛻🛻 + 🛻🛻🛻 = ?",
                            "detail": "4 trucks and 3 more. Count everything together. 4 + 3 = 7!",
                        },
                    ]
                },
            ),
            (
                "doingCard",
                {
                    "label": "Go and do",
                    "text": (
                        "Line up 2 toy trucks. Add 3 more toy trucks to the line. Count the "
                        "whole new group together — how many are there now?"
                    ),
                },
            ),
        ],
        meta("Tuesday", "Add the Trucks!", "Joining two groups together", "Addition"),
        layout="journal",
    )

    b = render_page(
        [
            (
                "speedMath",
                {
                    "title": "Add and Write",
                    "instructions": "Count all the trucks. Write the total in the box.",
                    "answer_style": "box",
                    "columns": 2,
                    "problems": [
                        {"q": "🛻 + 🛻🛻 = ?"},
                        {"q": "🛻🛻 + 🛻🛻 = ?"},
                        {"q": "🛻🛻🛻 + 🛻🛻 = ?"},
                        {"q": "🛻🛻🛻🛻 + 🛻🛻 = ?"},
                        {"q": "🛻🛻🛻🛻🛻 + 🛻🛻 = ?"},
                        {"q": "🛻🛻🛻🛻🛻🛻 + 🛻🛻🛻🛻 = ?"},
                    ],
                },
            ),
            (
                "noteBox",
                {
                    "text": (
                        "Great adding! Tomorrow Duke rides in an INTERNATIONAL truck, and "
                        "we'll learn what happens when trucks drive away."
                    )
                },
            ),
        ],
        meta(
            "Tuesday",
            "Tuesday: You Try!",
            "Independent addition practice",
            "Addition",
            name_date=False,
        ),
        layout="journal",
    )

    c = render_worksheet_html(
        "matchingWorksheet",
        {
            "title": "Match the Total!",
            "instructions": "Read the number. Does it match the total when you add the trucks?",
            "left_items": ["3", "4", "6", "7", "9"],
            "right_items": [
                "🛻 + 🛻🛻",
                "🛻🛻🛻 + 🛻",
                "🛻🛻🛻 + 🛻🛻🛻",
                "🛻🛻🛻🛻 + 🛻🛻🛻",
                "🛻🛻🛻🛻🛻 + 🛻🛻🛻🛻",
            ],
        },
        day_label="Tuesday",
    )

    d = render_page(
        [
            (
                "noteBox",
                {
                    "text": (
                        "You'll need 2 dice (or make number cards 1-6 and pick two at random). "
                        "Roll both, then add the dots together!"
                    )
                },
            ),
            (
                "taskList",
                {
                    "tasks": [
                        {
                            "prompt": f"Round {n}",
                            "detail": "Roll two dice. Count all the dots. Write the total.",
                            "response_lines": 1,
                        }
                        for n in range(1, 6)
                    ]
                },
            ),
            (
                "doingCard",
                {
                    "label": "No dice?",
                    "text": (
                        "Use two stacks of blocks instead — stack any number 1 to 6 in each, "
                        "then count them together."
                    ),
                },
            ),
        ],
        meta(
            "Tuesday",
            "Roll and Add!",
            "A dice game for addition practice",
            "Addition",
            name_date=False,
        ),
        layout="journal",
    )
    return [a, b, c, d]


# ═══════════════════════════════════════════════════════════════════════════
# Wednesday — Subtraction (International)
# ═══════════════════════════════════════════════════════════════════════════


def wednesday_pages():
    a = render_page(
        [
            logo_badge("International", "Today's Truck"),
            (
                "storyPanel",
                {
                    "who": NARRATOR,
                    "text": (
                        "Today I'm watching trucks at a busy truck stop with an INTERNATIONAL "
                        "rig! Trucks keep arriving... and then some of them drive away.\n\n"
                        "That's called SUBTRACTING. The '−' sign means 'take away.'"
                    ),
                },
            ),
            (
                "noteBox",
                {
                    "text": (
                        "SUBTRACTING means some go away, and we count how many are left. "
                        "Cross them out in your mind, then count what remains."
                    )
                },
            ),
            (
                "taskList",
                {
                    "tasks": [
                        {
                            "prompt": "🚚🚚🚚 − 🚚 = ?",
                            "detail": "3 trucks. 1 drives away. How many are left? 3 − 1 = 2!",
                        },
                        {
                            "prompt": "🚚🚚🚚🚚🚚 − 🚚🚚 = ?",
                            "detail": "5 trucks. 2 drive away. How many are left? 5 − 2 = 3!",
                        },
                        {
                            "prompt": "🚚🚚🚚🚚🚚🚚🚚 − 🚚🚚🚚 = ?",
                            "detail": "7 trucks. 3 drive away. How many are left? 7 − 3 = 4!",
                        },
                    ]
                },
            ),
            (
                "doingCard",
                {
                    "label": "Go and do",
                    "text": (
                        "Line up 5 toy trucks. Drive 2 of them away to another room. Count "
                        "out loud how many are left in the line."
                    ),
                },
            ),
        ],
        meta("Wednesday", "Trucks Drive Away!", "Some go away — how many are left?", "Subtraction"),
        layout="journal",
    )

    b = render_page(
        [
            (
                "speedMath",
                {
                    "title": "Take Away and Write",
                    "instructions": "Cross out the ones that drive away. Write how many are left.",
                    "answer_style": "box",
                    "columns": 2,
                    "problems": [
                        {"q": "🚚🚚🚚🚚 − 🚚 = ?"},
                        {"q": "🚚🚚🚚🚚🚚 − 🚚🚚 = ?"},
                        {"q": "🚚🚚🚚🚚🚚🚚 − 🚚🚚 = ?"},
                        {"q": "🚚🚚🚚🚚🚚🚚🚚🚚 − 🚚🚚🚚 = ?"},
                        {"q": "🚚🚚🚚🚚🚚🚚🚚🚚🚚 − 🚚🚚🚚🚚 = ?"},
                        {"q": "🚚🚚🚚🚚🚚🚚🚚🚚🚚🚚 − 🚚🚚🚚🚚 = ?"},
                    ],
                },
            ),
            (
                "noteBox",
                {
                    "text": (
                        "Great job! Tomorrow Duke rides in a CHEVROLET, and we'll learn how "
                        "to tell which group has MORE and which has FEWER."
                    )
                },
            ),
        ],
        meta(
            "Wednesday",
            "Wednesday: You Try!",
            "Independent subtraction practice",
            "Subtraction",
            name_date=False,
        ),
        layout="journal",
    )

    c = render_worksheet_html(
        "matchingWorksheet",
        {
            "title": "Match What's Left!",
            "instructions": "Read the number. Does it match how many trucks are left?",
            "left_items": ["3", "4", "5", "6", "7"],
            "right_items": [
                "🚚🚚🚚🚚 − 🚚",
                "🚚🚚🚚🚚🚚🚚 − 🚚🚚",
                "🚚🚚🚚🚚🚚🚚🚚 − 🚚🚚",
                "🚚🚚🚚🚚🚚🚚🚚🚚🚚 − 🚚🚚🚚",
                "🚚🚚🚚🚚🚚🚚🚚🚚🚚🚚 − 🚚🚚🚚",
            ],
        },
        day_label="Wednesday",
    )

    d = render_page(
        [
            (
                "noteBox",
                {
                    "text": (
                        "Act these out with toy trucks if you have them! Listen to each story, "
                        "then figure out how many are left."
                    )
                },
            ),
            (
                "taskList",
                {
                    "tasks": [
                        {
                            "prompt": (
                                "5 trucks are parked at the truck stop. 2 drive away to make a "
                                "delivery. How many are left?"
                            ),
                            "response_lines": 1,
                        },
                        {
                            "prompt": (
                                "8 cars are in the parking lot. 3 drive away to go home. How "
                                "many are left?"
                            ),
                            "response_lines": 1,
                        },
                        {
                            "prompt": (
                                "6 rigs are lined up for gas. 1 drives away, all filled up. How "
                                "many are left?"
                            ),
                            "response_lines": 1,
                        },
                        {
                            "prompt": (
                                "9 trucks are waiting at a red light. 4 turn and drive away. "
                                "How many are still waiting?"
                            ),
                            "response_lines": 1,
                        },
                    ]
                },
            ),
            (
                "doingCard",
                {
                    "label": "Your turn",
                    "text": "Make up your own truck stop story! Ask a grown-up to write it down.",
                },
            ),
        ],
        meta(
            "Wednesday",
            "Truck Stop Story Problems",
            "Acting out subtraction with stories",
            "Subtraction",
            name_date=False,
        ),
        layout="journal",
    )
    return [a, b, c, d]


# ═══════════════════════════════════════════════════════════════════════════
# Thursday — Comparing > and < (Chevrolet)
# ═══════════════════════════════════════════════════════════════════════════


def thursday_pages():
    a = render_page(
        [
            logo_badge("Chevrolet", "Today's Car"),
            (
                "storyPanel",
                {
                    "who": NARRATOR,
                    "text": (
                        "Today I'm riding in a CHEVROLET! We drove past two parking lots — "
                        "one had lots of cars, and one had just a few.\n\n"
                        "Let's learn how to compare two groups: which has MORE, and which has "
                        "FEWER?"
                    ),
                },
            ),
            (
                "noteBox",
                {
                    "text": (
                        "Picture a hungry alligator mouth between two groups. The alligator "
                        "always opens wide toward the BIGGER group, because he wants to eat "
                        "more! '>' means 'greater than' (more). '<' means 'less than' (fewer)."
                    )
                },
            ),
            (
                "comparePairs",
                {
                    "columns": 1,
                    "pairs": [
                        {"left": "🚗🚗🚗🚗🚗🚗🚗 (7)", "right": "🚗🚗🚗 (3)"},
                        {"left": "🚗🚗 (2)", "right": "🚗🚗🚗🚗🚗 (5)"},
                        {"left": "🚗🚗🚗🚗 (4)", "right": "🚗🚗🚗🚗🚗🚗🚗🚗🚗 (9)"},
                    ],
                },
            ),
            (
                "doingCard",
                {
                    "label": "Go and do",
                    "text": (
                        "Make two rows of toy cars — one row with more, one with fewer. Open "
                        "your hand like an alligator mouth and point it toward the row with "
                        "MORE cars."
                    ),
                },
            ),
        ],
        meta("Thursday", "More or Fewer?", "Comparing two groups with > and <", "Comparing"),
        layout="journal",
    )

    b = render_page(
        [
            (
                "noteBox",
                {
                    "text": (
                        "Count each side. Decide which group is bigger. Write > if the left "
                        "side has more, or < if the left side has fewer."
                    )
                },
            ),
            (
                "comparePairs",
                {
                    "columns": 2,
                    "pairs": [
                        {"left": "🚗🚗🚗🚗🚗 (5)", "right": "🚗🚗 (2)"},
                        {"left": "🚗🚗🚗 (3)", "right": "🚗🚗🚗🚗🚗🚗🚗🚗 (8)"},
                        {"left": "🚛🚛🚛🚛🚛🚛🚛🚛🚛 (9)", "right": "🚛🚛🚛🚛 (4)"},
                        {"left": "🚗🚗🚗🚗🚗🚗 (6)", "right": "🚗 (1)"},
                        {"left": "🚛🚛 (2)", "right": "🚛🚛🚛🚛🚛🚛🚛 (7)"},
                        {"left": "🚗🚗🚗🚗🚗🚗🚗🚗🚗🚗 (10)", "right": "🚗🚗🚗🚗 (4)"},
                    ],
                },
            ),
            (
                "noteBox",
                {
                    "text": (
                        "Nice comparing! Tomorrow is Friday — a big mixed review with Duke's "
                        "FREIGHTLINER, and you get to build your own rig!"
                    )
                },
            ),
        ],
        meta(
            "Thursday",
            "Thursday: You Try!",
            "Independent comparing practice",
            "Comparing",
            name_date=False,
        ),
        layout="journal",
    )

    c = render_page(
        [
            (
                "noteBox",
                {
                    "text": (
                        "Build two towers out of blocks, one for each round. Compare! Which "
                        "tower is taller — the one with more blocks?"
                    )
                },
            ),
            (
                "taskList",
                {
                    "tasks": [
                        {
                            "prompt": f"Round {n}",
                            "detail": (
                                "Build two towers. Count the blocks in each. Which has more? "
                                "Write > or <."
                            ),
                            "response_lines": 1,
                        }
                        for n in range(1, 6)
                    ]
                },
            ),
            (
                "doingCard",
                {
                    "label": "Extra fun",
                    "text": (
                        "Try it with stuffed animals lined up in two groups instead of blocks!"
                    ),
                },
            ),
        ],
        meta(
            "Thursday",
            "Tower Battle!",
            "A block-stacking comparing game",
            "Comparing",
            name_date=False,
        ),
        layout="journal",
    )

    d = render_page(
        [
            (
                "noteBox",
                {
                    "text": (
                        "More practice! Count each side. Write > if the left side has more, "
                        "or < if the left side has fewer."
                    )
                },
            ),
            (
                "comparePairs",
                {
                    "columns": 2,
                    "pairs": [
                        {"left": "🛻🛻🛻🛻🛻🛻🛻 (7)", "right": "🛻🛻 (2)"},
                        {"left": "🚚 (1)", "right": "🚚🚚🚚🚚🚚🚚 (6)"},
                        {"left": "🚗🚗🚗🚗🚗🚗🚗🚗 (8)", "right": "🚗🚗🚗 (3)"},
                        {"left": "🚛🚛 (2)", "right": "🚛🚛🚛🚛🚛 (5)"},
                        {"left": "🛻🛻🛻🛻🛻🛻🛻🛻🛻 (9)", "right": "🛻🛻🛻🛻 (4)"},
                        {"left": "🚗🚗🚗 (3)", "right": "🚗🚗🚗🚗🚗🚗🚗🚗🚗🚗 (10)"},
                        {"left": "🚚🚚🚚🚚🚚 (5)", "right": "🚚🚚 (2)"},
                        {"left": "🚛🚛 (2)", "right": "🚛🚛🚛🚛🚛🚛🚛🚛 (8)"},
                    ],
                },
            ),
        ],
        meta(
            "Thursday",
            "Thursday: More Practice!",
            "Extra comparing reps",
            "Comparing",
            name_date=False,
        ),
        layout="journal",
    )
    return [a, b, c, d]


# ═══════════════════════════════════════════════════════════════════════════
# Friday — Mixed Review + Capstone (Freightliner)
# ═══════════════════════════════════════════════════════════════════════════


def friday_pages():
    a = render_page(
        [
            logo_badge("Freightliner", "Today's Truck"),
            (
                "storyPanel",
                {
                    "who": NARRATOR,
                    "text": (
                        "It's Friday — Duke's Big Rig Rally! This week we rode in a PETERBILT, "
                        "a FORD, an INTERNATIONAL, a CHEVROLET, and today a green FREIGHTLINER.\n\n"
                        "Let's remember everything we learned: counting, adding, taking away, "
                        "and comparing!"
                    ),
                },
            ),
            (
                "taskList",
                {
                    "tasks": [
                        {"prompt": "🚛🚛🚛🚛🚛🚛", "detail": "Count together: how many rigs?"},
                        {
                            "prompt": "🚗🚗🚗 + 🚗🚗 = ?",
                            "detail": "Add the cars together. How many in all?",
                        },
                        {
                            "prompt": "🚚🚚🚚🚚🚚🚚 − 🚚🚚 = ?",
                            "detail": "Some trucks drive away. How many are left?",
                        },
                        {
                            "prompt": "🚛🚛🚛🚛🚛🚛🚛🚛 vs. 🚛🚛",
                            "detail": "Which group is bigger? Point your alligator mouth at it!",
                        },
                    ]
                },
            ),
            (
                "doingCard",
                {
                    "label": "Build your own rig!",
                    "text": (
                        "Grab crayons or blocks. Build or draw your very own big rig. Give it "
                        "exactly 8 wheels. Count them out loud one at a time when you're done!"
                    ),
                },
            ),
        ],
        meta("Friday", "Big Rig Rally!", "Mixed review + build your own rig", "Review"),
        layout="journal",
    )

    b = render_page(
        [
            (
                "speedMath",
                {
                    "title": "Mixed Review",
                    "instructions": "Count, add, subtract, or compare. Write the answer in each box.",
                    "answer_style": "box",
                    "columns": 2,
                    "problems": [
                        {"q": "🚛🚛🚛🚛🚛🚛🚛 = ?"},
                        {"q": "🚗🚗🚗🚗 + 🚗🚗 = ?"},
                        {"q": "🛻🛻🛻🛻🛻🛻🛻🛻 + 🛻🛻 = ?"},
                        {"q": "🚚🚚🚚🚚🚚🚚🚚🚚 − 🚚🚚🚚 = ?"},
                        {"q": "🚛🚛🚛🚛🚛🚛🚛🚛🚛🚛 − 🚛🚛🚛🚛 = ?"},
                        {"q": "🚗🚗🚗🚗🚗🚗🚗🚗🚗 − 🚗🚗🚗 = ?"},
                    ],
                },
            ),
            (
                "comparePairs",
                {
                    "columns": 2,
                    "pairs": [
                        {"left": "🚛🚛🚛🚛🚛🚛🚛🚛 (8)", "right": "🚛🚛🚛 (3)"},
                        {"left": "🚗🚗 (2)", "right": "🚗🚗🚗🚗🚗🚗 (6)"},
                    ],
                },
            ),
            (
                "noteBox",
                {
                    "text": (
                        "You did it! Woof woof — Duke is so proud of you, Theodore. Great "
                        "counting, adding, subtracting, and comparing all week long!"
                    )
                },
            ),
        ],
        meta("Friday", "Friday: You Try!", "Independent mixed review", "Review", name_date=False),
        layout="journal",
    )

    c = render_worksheet_html(
        "matchingWorksheet",
        {
            "title": "Big Rig Review Match",
            "instructions": "Read the number. Does it match the answer next to it?",
            "left_items": ["4", "5", "6", "7", "8"],
            "right_items": [
                "🚛🚛🚛🚛🚛🚛🚛🚛🚛🚛 − 🚛🚛🚛🚛🚛🚛",
                "🚗🚗 + 🚗🚗🚗",
                "🚛🚛🚛🚛🚛🚛",
                "🚚🚚🚚🚚🚚🚚🚚🚚🚚 − 🚚🚚",
                "🛻🛻🛻🛻 + 🛻🛻🛻🛻",
            ],
        },
        day_label="Friday",
    )

    d = render_page(
        [
            (
                "noteBox",
                {
                    "text": (
                        "Go for a walk, a drive, or just look out the window for 5 minutes. "
                        "Every time you see a vehicle, make a tally mark below."
                    )
                },
            ),
            (
                "taskList",
                {
                    "tasks": [
                        {"prompt": "Trucks (🚛 🚚 🛻)", "response_lines": 1},
                        {"prompt": "Cars (🚗)", "response_lines": 1},
                        {
                            "prompt": "Other (buses, motorcycles, anything else!)",
                            "response_lines": 1,
                        },
                        {"prompt": "Did you see more TRUCKS or more CARS?", "response_lines": 1},
                        {
                            "prompt": "Write it with > or <: Trucks ___ Cars",
                            "response_lines": 1,
                        },
                    ]
                },
            ),
            (
                "doingCard",
                {
                    "label": "From Duke",
                    "text": (
                        "Woof! You counted, added, subtracted, and compared trucks and cars "
                        "all week long. What a great rig rally, Theodore!"
                    ),
                },
            ),
        ],
        meta(
            "Friday",
            "Vehicle Hunt Field Trip",
            "The whole week, out in the real world",
            "Review",
            name_date=False,
        ),
        layout="journal",
    )
    return [a, b, c, d]


# ═══════════════════════════════════════════════════════════════════════════
# Parent feedback page
# ═══════════════════════════════════════════════════════════════════════════


def parent_feedback_page():
    return render_worksheet_html(
        "readingWorksheet",
        {
            "title": "For the Grown-Up: Feedback & Notes",
            "passage_title": "How Did This Week Go?",
            "instructions": "No reading for Theodore here — this page is for you.",
            "passage": (
                "This week stayed deliberately concrete: every count, sum, difference, and "
                "comparison was carried by a picture (vehicle emoji) rather than a bare "
                "equation, since symbolic math this early is usually ahead of a typical "
                "3-year-old's development. Independent pencil work was kept short and "
                "large-target (write-the-number boxes), while the teaching and modeling "
                "happened out loud with you, plus a short hands-on toy-truck activity each "
                "day. Your notes below help pace next week."
            ),
            "questions": [
                {
                    "prompt": "Which day or activity did Theodore enjoy most?",
                    "response_lines": 2,
                },
                {
                    "prompt": (
                        "Was counting/adding/subtracting up to 10 a good fit, or should next "
                        "week stay smaller (within 5) or stretch further?"
                    ),
                    "response_lines": 2,
                },
                {
                    "prompt": (
                        "Did the alligator-mouth idea for > and < make sense to him, or would "
                        "another trick land better?"
                    ),
                    "response_lines": 2,
                },
                {
                    "prompt": "Any other vehicle makes he'd love to see featured next time?",
                    "response_lines": 2,
                },
            ],
        },
        day_label="",
    )


# ═══════════════════════════════════════════════════════════════════════════
# Teacher guide
# ═══════════════════════════════════════════════════════════════════════════

TEACHER_GUIDE = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>Theodore's Truck &amp; Car Math Week — Teacher Guide</title>
  <style>
    @page { size: letter; margin: 0.5in 0.6in; }
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body { font-family: 'Trebuchet MS', Arial, sans-serif; font-size: 11pt; color: #111; line-height: 1.55; }
    @media screen { body { background: #b0b0b0; padding: 24px; } .page { background: white; max-width: 7.5in; margin: 0 auto 28px; padding: 0.45in 0.5in; box-shadow: 0 4px 18px rgba(0,0,0,.28); min-height: 10.3in; } }
    @media print { body { background: white; padding: 0; } .page { padding: 0; box-shadow: none; } * { -webkit-print-color-adjust: exact; print-color-adjust: exact; } }
    .page { page-break-after: always; break-after: page; }
    .page:last-child { page-break-after: avoid; break-after: avoid; }
    h1 { font-size: 18pt; color: #b91c1c; border-bottom: 3px solid #b91c1c; padding-bottom: 5px; margin-bottom: 12px; }
    h2 { font-size: 13pt; color: #fff; background: #b91c1c; padding: 5px 10px; border-radius: 3px; margin: 14px 0 6px; }
    h2.tue { background: #1d4ed8; }
    h2.wed { background: #0f766e; }
    h2.thu { background: #a16207; }
    h2.fri { background: #15803d; }
    h3 { font-size: 10.5pt; font-weight: bold; color: #444; margin: 8px 0 3px; text-transform: uppercase; letter-spacing: 0.04em; }
    p, li { font-size: 10pt; margin-bottom: 5px; }
    ul { padding-left: 18px; margin-bottom: 8px; }
    .answer-box { background: #fef2f2; border-left: 4px solid #b91c1c; padding: 6px 10px; margin: 4px 0 10px; border-radius: 0 4px 4px 0; font-size: 10pt; }
    .answer-box.tue { background: #eff6ff; border-color: #1d4ed8; }
    .answer-box.wed { background: #f0fdfa; border-color: #0f766e; }
    .answer-box.thu { background: #fffbeb; border-color: #a16207; }
    .answer-box.fri { background: #f0fdf4; border-color: #15803d; }
    .talk { background: #f5f3ff; border-left: 4px solid #6d28d9; padding: 6px 10px; margin: 4px 0 8px; border-radius: 0 4px 4px 0; font-size: 10pt; }
    .doing { background: #fafafa; border-left: 4px solid #6b7280; padding: 6px 10px; margin: 4px 0 8px; border-radius: 0 4px 4px 0; font-size: 10pt; }
    .watch { background: #fff3cd; border-left: 4px solid #d97706; padding: 6px 10px; margin: 4px 0 8px; border-radius: 0 4px 4px 0; font-size: 10pt; }
  </style>
</head>
<body>

<div class="page">
  <h1>Theodore's Truck &amp; Car Math Week — Parent Guide</h1>
  <p><strong>Theme:</strong> Trucks &amp; Cars &nbsp;|&nbsp; <strong>Audience:</strong> Theodore, age 3
  &nbsp;|&nbsp; <strong>Narrator:</strong> Duke the Truck Dog</p>
  <p><strong>Arc:</strong> Counting groups &rarr; Adding groups &rarr; Groups shrinking (subtracting)
  &rarr; Comparing two groups (&gt;/&lt;) &rarr; Mixed review &amp; build-your-own-rig capstone</p>
  <p><strong>How to run each day (~50-60 minutes, in short chunks):</strong> Read the story panel
  together, talk through the worked examples out loud (Page 1 is a shared/oral activity — no
  writing pressure), do the hands-on activity with real toy trucks, then let Theodore attempt the
  short independent "You Try!" page (Page 2). Page 3 is a quick paired reference/matching page —
  read each number, then verify it against the picture next to it. Page 4 is a distinct game or
  real-world activity that gets him off the page for the back half of the hour. None of this needs
  to happen back-to-back; four 10-15 minute chunks across the day works at least as well as one
  long sitting, probably better at this age. Number range is 0-10, but every problem is pictured —
  he should never need to work with a bare digit-only equation this week.</p>

  <h2>Monday — Count the Rigs! (Peterbilt)</h2>
  <h3>Answer Key — Count and Write</h3>
  <div class="answer-box">
    <p>1, 3, 4, 6, 7, 10</p>
  </div>
  <h3>Talking Points</h3>
  <div class="talk">
    <p>Point to each truck as you say the number — this is "one-to-one correspondence," the
    foundation skill under all of this week's math. If he loses count, that's normal; restart
    from 1 rather than correcting mid-count.</p>
  </div>
  <h3>Watch For</h3>
  <div class="watch">
    <p>Kids this age often "count" by rattling off numbers without pointing to each item (or
    double-tap one item). Gently slow him down and re-point rather than just supplying the
    answer.</p>
  </div>
  <h3>Page 3 Answer Key — Match the Number!</h3>
  <div class="answer-box">
    <p>2 &rarr; 2 trucks, 4 &rarr; 4 trucks, 5 &rarr; 5 trucks, 8 &rarr; 8 trucks, 9 &rarr; 9
    trucks. Every row already matches — the activity is reading the number and verifying the
    count, not solving a puzzle.</p>
  </div>
  <h3>Page 4 — Truck &amp; Car Scavenger Hunt</h3>
  <div class="doing">
    <p>Fully open-ended — there's no fixed answer key, the counts depend on what you actually
    have around the house. If you're short on real traffic to watch, toy trucks and a "count the
    wheels on every vehicle in the toy box" substitute work just as well.</p>
  </div>

  <h2 class="tue">Tuesday — Add the Trucks! (Ford)</h2>
  <h3>Answer Key — Add and Write</h3>
  <div class="answer-box tue">
    <p>3, 4, 5, 6, 7, 10</p>
  </div>
  <h3>Talking Points</h3>
  <div class="talk">
    <p>Frame addition as "putting groups together," not as a memorized fact. Have him physically
    slide two little piles of toy trucks together before counting the new total — the motion
    matters as much as the number.</p>
  </div>
  <h3>Extension</h3>
  <div class="doing">
    <p>Once he's comfortable, try it the other way: start with one big pile, split it into two
    smaller piles, and ask "how many in each part?" — this previews subtraction as the inverse.</p>
  </div>
  <h3>Page 3 Answer Key — Match the Total!</h3>
  <div class="answer-box tue">
    <p>3 &rarr; 1+2, 4 &rarr; 3+1, 6 &rarr; 3+3, 7 &rarr; 4+3, 9 &rarr; 5+4. Same "verify, don't
    solve" format as Monday's Page 3.</p>
  </div>
  <h3>Page 4 — Roll and Add!</h3>
  <div class="doing">
    <p>Answers vary by dice roll — that's the point, it's genuine practice with random numbers
    instead of a fixed worksheet. If a roll produces a sum above 10, that's fine; just count all
    the dots together as usual rather than skipping the round.</p>
  </div>

  <h2 class="wed">Wednesday — Trucks Drive Away! (International)</h2>
  <h3>Answer Key — Take Away and Write</h3>
  <div class="answer-box wed">
    <p>3, 3, 4, 5, 5, 6</p>
  </div>
  <h3>Talking Points</h3>
  <div class="talk">
    <p>"Driving away" is a friendlier frame than "taking away" for a truck-loving 3-year-old —
    lean into it. Physically moving toy trucks out of the room (rather than just turning them
    over) makes the "some are gone now" concept concrete.</p>
  </div>
  <h3>Watch For</h3>
  <div class="watch">
    <p>Subtraction is usually harder than addition at this age because the starting group
    disappears from view. If he struggles, keep the "driven away" trucks visible but set apart
    (not hidden) until he's ready for the harder version.</p>
  </div>
  <h3>Page 3 Answer Key — Match What's Left!</h3>
  <div class="answer-box wed">
    <p>3 &rarr; 4−1, 4 &rarr; 6−2, 5 &rarr; 7−2, 6 &rarr; 9−3, 7 &rarr; 10−3.</p>
  </div>
  <h3>Page 4 Answer Key — Truck Stop Story Problems</h3>
  <div class="answer-box wed">
    <p>5 − 2 = 3 trucks. 8 − 3 = 5 cars. 6 − 1 = 5 rigs. 9 − 4 = 5 trucks still waiting.</p>
  </div>

  <h2 class="thu">Thursday — More or Fewer? (Chevrolet)</h2>
  <h3>Answer Key — Comparing Practice</h3>
  <div class="answer-box thu">
    <p>&gt;, &lt;, &lt;, &gt;, &lt;, &gt;</p>
    <p>(Left side compared to right side, in order down the page.)</p>
  </div>
  <h3>Talking Points</h3>
  <div class="talk">
    <p>Lead with "which has more?" every single time before naming the symbol — the concrete
    judgment (more/fewer) should always come before the abstract mark. The alligator-mouth trick
    is optional scaffolding; if another mental image clicks better for him, use that instead.</p>
  </div>
  <h3>Extension</h3>
  <div class="doing">
    <p>Two real snack piles (crackers, grapes) work just as well as toy trucks for this skill,
    and add a nice "you get to eat the difference" payoff.</p>
  </div>
  <h3>Page 3 — Tower Battle!</h3>
  <div class="doing">
    <p>Answers vary by build, same as Tuesday's dice game — the skill being rehearsed is the
    comparison judgment and writing the correct symbol, not a fixed count.</p>
  </div>
  <h3>Page 4 Answer Key — More Practice!</h3>
  <div class="answer-box thu">
    <p>&gt;, &lt;, &gt;, &lt;, &gt;, &lt;, &gt;, &lt;</p>
    <p>(Left side compared to right side, in order down the page.)</p>
  </div>

  <h2 class="fri">Friday — Big Rig Rally! (Freightliner)</h2>
  <h3>Answer Key — Mixed Review</h3>
  <div class="answer-box fri">
    <p>7, 6, 10, 5, 6, 6</p>
  </div>
  <h3>Answer Key — Comparing (bottom of page)</h3>
  <div class="answer-box fri">
    <p>&gt;, &lt;</p>
  </div>
  <h3>Capstone — Build Your Own Rig</h3>
  <div class="doing">
    <p>Blocks, crayons, or even cut paper wheels all work. The only requirement is exactly 8
    wheels, counted out loud one at a time at the end — this is the week's skills (counting,
    care with a target number) wrapped in a creative, low-pressure finish.</p>
  </div>
  <h3>Page 3 Answer Key — Big Rig Review Match</h3>
  <div class="answer-box fri">
    <p>4 &rarr; 10−6, 5 &rarr; 2+3, 6 &rarr; count of 6, 7 &rarr; 9−2, 8 &rarr; 4+4. One item per
    skill from the whole week, in the same "verify the pairing" format as the other days.</p>
  </div>
  <h3>Page 4 — Vehicle Hunt Field Trip</h3>
  <div class="doing">
    <p>Open-ended, same as Monday's scavenger hunt — this is the week's closing real-world tie-in.
    If you can't get out for a walk or drive, watching out a window for 5 minutes works fine.</p>
  </div>

  <h3>Looking ahead</h3>
  <div class="talk">
    <p>Use the Parent Feedback page at the end of the packet to note what clicked and what
    didn't — especially whether "within 10" was the right stretch, since that's the single
    biggest lever for how next week should be paced.</p>
  </div>
</div>

</body>
</html>"""


def generate_theodore_truck_math_week_series():
    from pathlib import Path

    output_dir = Path(OUT_DIR)
    output_dir.mkdir(exist_ok=True)

    pages: list[tuple[str, str]] = []
    for day_pages in (
        monday_pages(),
        tuesday_pages(),
        wednesday_pages(),
        thursday_pages(),
        friday_pages(),
    ):
        for html in day_pages:
            pages.append((f"page-{len(pages)}", html))
    pages.append(("parent-feedback", parent_feedback_page()))

    html = build_print_packet_html(
        pages,
        packet_title="Theodore's Truck & Car Math Week",
        layout="journal",
    )
    (output_dir / "theodore_truck_math_week.html").write_text(html, encoding="utf-8")
    (output_dir / "theodore_truck_math_week_teacher_guide.html").write_text(
        TEACHER_GUIDE, encoding="utf-8"
    )

    print(f"Generated {len(pages)} pages -> {output_dir}/")
    labels = [
        "Mon: Count the Rigs!",
        "Mon: You Try!",
        "Mon: Match the Number!",
        "Mon: Truck & Car Scavenger Hunt",
        "Tue: Add the Trucks!",
        "Tue: You Try!",
        "Tue: Match the Total!",
        "Tue: Roll and Add!",
        "Wed: Trucks Drive Away!",
        "Wed: You Try!",
        "Wed: Match What's Left!",
        "Wed: Truck Stop Story Problems",
        "Thu: More or Fewer?",
        "Thu: You Try!",
        "Thu: Tower Battle!",
        "Thu: More Practice!",
        "Fri: Big Rig Rally!",
        "Fri: You Try!",
        "Fri: Big Rig Review Match",
        "Fri: Vehicle Hunt Field Trip",
        "Parent Feedback & Notes",
    ]
    for label in labels:
        print(f"  - {label}")


# ─────────────────────────────────────────────────────────────────────────────
# Real vehicle-make logos, embedded as base64 SVG data URIs.
# Source: Wikimedia Commons, current/on-vehicle versions, licensing-checked.
#   Ford         -> https://commons.wikimedia.org/wiki/File:Ford_Motor_Company_Logo.svg
#   Chevrolet    -> https://commons.wikimedia.org/wiki/File:Chevrolet-logo.svg
#   Peterbilt    -> https://commons.wikimedia.org/wiki/File:Peterbilt_logo.svg
#   Freightliner -> https://commons.wikimedia.org/wiki/File:Freightliner_logo.svg
#   International-> https://commons.wikimedia.org/wiki/File:International_Motors_Logo,_October_2024.svg
# ─────────────────────────────────────────────────────────────────────────────

_LOGO_FORD_B64 = "PD94bWwgdmVyc2lvbj0iMS4wIiBlbmNvZGluZz0idXRmLTgiPz4KPCEtLSBHZW5lcmF0b3I6IEFkb2JlIElsbHVzdHJhdG9yIDIyLjEuMCwgU1ZHIEV4cG9ydCBQbHVnLUluIC4gU1ZHIFZlcnNpb246IDYuMDAgQnVpbGQgMCkgIC0tPgo8c3ZnIHZlcnNpb249IjEuMSIKCSBpZD0ic3ZnNjA5NiIgeG1sbnM6Y2M9Imh0dHA6Ly9jcmVhdGl2ZWNvbW1vbnMub3JnL25zIyIgeG1sbnM6ZGM9Imh0dHA6Ly9wdXJsLm9yZy9kYy9lbGVtZW50cy8xLjEvIiB4bWxuczpyZGY9Imh0dHA6Ly93d3cudzMub3JnLzE5OTkvMDIvMjItcmRmLXN5bnRheC1ucyMiIHhtbG5zOnN2Zz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciCgkgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIiB4bWxuczp4bGluaz0iaHR0cDovL3d3dy53My5vcmcvMTk5OS94bGluayIgeD0iMHB4IiB5PSIwcHgiIHZpZXdCb3g9IjAgMCAzMDAgMTEyLjUiCgkgc3R5bGU9ImVuYWJsZS1iYWNrZ3JvdW5kOm5ldyAwIDAgMzAwIDExMi41OyIgeG1sOnNwYWNlPSJwcmVzZXJ2ZSI+CjxzdHlsZSB0eXBlPSJ0ZXh0L2NzcyI+Cgkuc3Qwe2ZpbGw6I0QzRDJEMjt9Cgkuc3Qxe2ZpbGw6dXJsKCNwYXRoMzU1OF8xXyk7fQoJLnN0MntmaWxsOnVybCgjcGF0aDM1ODBfMV8pO30KCS5zdDN7ZmlsbDp1cmwoI3BhdGgzNjAyXzFfKTt9Cgkuc3Q0e2ZpbGw6dXJsKCNwYXRoMzYyNF8xXyk7fQoJLnN0NXtmaWxsOnVybCgjcGF0aDM2NDZfMV8pO30KCS5zdDZ7ZmlsbDp1cmwoI3BhdGgzNjY4XzFfKTt9Cgkuc3Q3e2ZpbGw6dXJsKCNwYXRoMzY5MF8xXyk7fQoJLnN0OHtmaWxsOnVybCgjcGF0aDM3NDJfMV8pO30KCS5zdDl7ZmlsbDp1cmwoI3BhdGgzNzY0XzFfKTt9Cgkuc3QxMHtmaWxsOnVybCgjcGF0aDM3ODZfMV8pO30KCS5zdDExe2ZpbGw6dXJsKCNwYXRoMzgwOF8xXyk7fQoJLnN0MTJ7ZmlsbDp1cmwoI3BhdGgzODMwXzFfKTt9Cgkuc3QxM3tmaWxsOnVybCgjcGF0aDM4NTJfMV8pO30KCS5zdDE0e2ZpbGw6dXJsKCNwYXRoMzg3NF8xXyk7fQoJLnN0MTV7ZmlsbDp1cmwoI3BhdGgzODk2XzFfKTt9Cgkuc3QxNntmaWxsOnVybCgjcGF0aDM5MThfMV8pO30KCS5zdDE3e2ZpbGw6dXJsKCNwYXRoMzk0MF8xXyk7fQoJLnN0MTh7ZmlsbDp1cmwoI3BhdGgzOTYyXzFfKTt9Cgkuc3QxOXtmaWxsOnVybCgjcGF0aDM5ODRfMV8pO30KCS5zdDIwe2ZpbGw6dXJsKCNwYXRoNDAwNl8xXyk7fQoJLnN0MjF7ZmlsbDp1cmwoI3BhdGg0MDI4XzFfKTt9Cgkuc3QyMntmaWxsOnVybCgjcGF0aDQwNTBfMV8pO30KCS5zdDIze2ZpbGw6dXJsKCNwYXRoNDA3Ml8xXyk7fQoJLnN0MjR7ZmlsbDp1cmwoI3BhdGg0MDk0XzFfKTt9Cgkuc3QyNXtmaWxsOiM0RjRDNEQ7fQoJLnN0MjZ7ZmlsbDp1cmwoI3BhdGg0MTMwXzFfKTt9Cgkuc3QyN3tmaWxsOnVybCgjcGF0aDQxNTRfMV8pO30KCS5zdDI4e2ZpbGw6dXJsKCNwYXRoNDE4MF8xXyk7fQoJLnN0Mjl7ZmlsbDp1cmwoI3BhdGg0MjA2XzFfKTt9Cgkuc3QzMHtmaWxsOnVybCgjcGF0aDQyMzJfMV8pO30KPC9zdHlsZT4KPHBhdGggaWQ9InBhdGgzNTMyIiBjbGFzcz0ic3QwIiBkPSJNMjk5LjEsNTEuOWMwLjEsMC4zLDAuMSwwLjUsMC4xLDAuOEMyOTkuMiw1Mi40LDI5OS4xLDUyLjIsMjk5LjEsNTEuOSBNMTUwLDAKCUM2Ni43LDAsMCwyNSwwLDU2LjJjMCwzMS4xLDY3LjMsNTYuMiwxNTAsNTYuMmM4Mi43LDAsMTUwLTI1LjIsMTUwLTU2LjJDMzAwLDI1LjIsMjMyLjcsMCwxNTAsMCIvPgo8cmFkaWFsR3JhZGllbnQgaWQ9InBhdGgzNTU4XzFfIiBjeD0iLTgwNy43NTM3IiBjeT0iNTk2LjIzODMiIHI9IjEiIGdyYWRpZW50VHJhbnNmb3JtPSJtYXRyaXgoNjQ3LjY1NTQgMCAwIC02MzEuNTMwNSA1MjMyOTQuOTM3NSAzNzcxNjMuMDkzOCkiIGdyYWRpZW50VW5pdHM9InVzZXJTcGFjZU9uVXNlIj4KCTxzdG9wICBvZmZzZXQ9IjAiIHN0eWxlPSJzdG9wLWNvbG9yOiMwMDA1MEQiLz4KCTxzdG9wICBvZmZzZXQ9IjAuNyIgc3R5bGU9InN0b3AtY29sb3I6IzA1MTEyNSIvPgoJPHN0b3AgIG9mZnNldD0iMC45MDQ1IiBzdHlsZT0ic3RvcC1jb2xvcjojMTczRTdFIi8+Cgk8c3RvcCAgb2Zmc2V0PSIwLjk1NSIgc3R5bGU9InN0b3AtY29sb3I6IzRDQTlFMyIvPgoJPHN0b3AgIG9mZnNldD0iMSIgc3R5bGU9InN0b3AtY29sb3I6IzRDQTlFMyIvPgo8L3JhZGlhbEdyYWRpZW50Pgo8cGF0aCBpZD0icGF0aDM1NTgiIGNsYXNzPSJzdDEiIGQ9Ik0yLjMsNTYuMmMwLDI5LjgsNjYuMSw1NCwxNDcuNyw1NGwwLDBjODEuNiwwLDE0Ny43LTI0LjEsMTQ3LjctNTRsMCwwYzAtMjkuOC02Ni4xLTU0LTE0Ny43LTU0CglsMCwwQzY4LjQsMi4yLDIuMywyNi40LDIuMyw1Ni4yIi8+CjxsaW5lYXJHcmFkaWVudCBpZD0icGF0aDM1ODBfMV8iIGdyYWRpZW50VW5pdHM9InVzZXJTcGFjZU9uVXNlIiB4MT0iLTgxMy4yMDcyIiB5MT0iNTg5Ljk0MDkiIHgyPSItODEyLjIwNzIiIHkyPSI1ODkuOTQwOSIgZ3JhZGllbnRUcmFuc2Zvcm09Im1hdHJpeCgwIC0xMTQuMzIwMiAtMTE0LjMyMDIgMCA2NzU5MS45MTQxIC05Mjg1Mi4yODEyKSI+Cgk8c3RvcCAgb2Zmc2V0PSIwIiBzdHlsZT0ic3RvcC1jb2xvcjojMDgxNDJFIi8+Cgk8c3RvcCAgb2Zmc2V0PSIwLjgwOSIgc3R5bGU9InN0b3AtY29sb3I6IzE3MzI2RSIvPgoJPHN0b3AgIG9mZnNldD0iMSIgc3R5bGU9InN0b3AtY29sb3I6IzBENjlBOSIvPgo8L2xpbmVhckdyYWRpZW50Pgo8cGF0aCBpZD0icGF0aDM1ODAiIGNsYXNzPSJzdDIiIGQ9Ik0xMy40LDU2LjJjMCwyLDAuNCw0LDEuMiw2bDAsMGMtMC4zLTEuMy0wLjUtMi42LTAuNS0zLjlsMCwwYzAtMjQuNyw2MS4xLTQ0LjcsMTM2LjYtNDQuN2wwLDAKCWM2OS40LDAsMTI2LjcsMTYuOSwxMzUuNCwzOC45bDAsMGMtNS44LTIzLjEtNjQuNS00MS4yLTEzNi4xLTQxLjJsMCwwQzc0LjYsMTEuMiwxMy40LDMxLjQsMTMuNCw1Ni4yIi8+CjxsaW5lYXJHcmFkaWVudCBpZD0icGF0aDM2MDJfMV8iIGdyYWRpZW50VW5pdHM9InVzZXJTcGFjZU9uVXNlIiB4MT0iLTgxMy4yMDY4IiB5MT0iNTg5Ljk0MTUiIHgyPSItODEyLjIwNjgiIHkyPSI1ODkuOTQxNSIgZ3JhZGllbnRUcmFuc2Zvcm09Im1hdHJpeCgwIC0xMTQuMzMwNiAtMTE0LjMzMDYgMCA2NzU5OS45Njg4IC05Mjg2MC42Nzk3KSI+Cgk8c3RvcCAgb2Zmc2V0PSIwIiBzdHlsZT0ic3RvcC1jb2xvcjojMDgxNDJFIi8+Cgk8c3RvcCAgb2Zmc2V0PSIwLjgwOSIgc3R5bGU9InN0b3AtY29sb3I6IzE3MzI2RSIvPgoJPHN0b3AgIG9mZnNldD0iMSIgc3R5bGU9InN0b3AtY29sb3I6IzBENjlBOSIvPgo8L2xpbmVhckdyYWRpZW50Pgo8cGF0aCBpZD0icGF0aDM2MDIiIGNsYXNzPSJzdDMiIGQ9Ik0yOTEuNSw1Ni4yYzAsMjcuMi02My40LDQ5LjMtMTQxLjUsNDkuM2wwLDBDODAuNCwxMDUuNSwyMi42LDg4LDEwLjcsNjVsMCwwCgljOS4xLDI0LDY4LjQsNDIuNSwxNDAuMyw0Mi41bDAsMGM3OC4yLDAsMTQxLjUtMjEuOSwxNDEuNS00OC44bDAsMGMwLTIuNy0wLjctNS40LTEuOS04bDAsMEMyOTEuMiw1Mi40LDI5MS41LDU0LjMsMjkxLjUsNTYuMiIvPgo8bGluZWFyR3JhZGllbnQgaWQ9InBhdGgzNjI0XzFfIiBncmFkaWVudFVuaXRzPSJ1c2VyU3BhY2VPblVzZSIgeDE9Ii04MTUuMDcyMSIgeTE9IjU4Ni44MTE4IiB4Mj0iLTgxNC4wNzIxIiB5Mj0iNTg2LjgxMTgiIGdyYWRpZW50VHJhbnNmb3JtPSJtYXRyaXgoMCAtNzkuMjEgLTc5LjIxIDAgNDY2NTYuOTg0NCAtNjQ0NjcuNzg1MikiPgoJPHN0b3AgIG9mZnNldD0iMCIgc3R5bGU9InN0b3AtY29sb3I6IzA4MTQyRSIvPgoJPHN0b3AgIG9mZnNldD0iMC44MDkiIHN0eWxlPSJzdG9wLWNvbG9yOiMxNzMyNkUiLz4KCTxzdG9wICBvZmZzZXQ9IjEiIHN0eWxlPSJzdG9wLWNvbG9yOiMwRDY5QTkiLz4KPC9saW5lYXJHcmFkaWVudD4KPHBhdGggaWQ9InBhdGgzNjI0IiBjbGFzcz0ic3Q0IiBkPSJNMTc2LjQsNjFjLTMuMiwzLjMtMy40LDcuNi0xLjMsOS41bDAsMGMwLjcsMC43LDEuNiwxLDIuNSwxLjFsMCwwYy0xLjQtMS43LTItNS4xLTAuMy03LjdsMCwwCgljLTAuMy0wLjgtMC40LTEuNy0wLjItMi42bDAsMGMwLTAuMi0wLjEtMC40LTAuMy0wLjRsMCwwQzE3Ni42LDYwLjgsMTc2LjUsNjAuOSwxNzYuNCw2MSIvPgo8bGluZWFyR3JhZGllbnQgaWQ9InBhdGgzNjQ2XzFfIiBncmFkaWVudFVuaXRzPSJ1c2VyU3BhY2VPblVzZSIgeDE9Ii04MTQuOTkyMyIgeTE9IjU4Ni45NDU5IiB4Mj0iLTgxMy45OTIzIiB5Mj0iNTg2Ljk0NTkiIGdyYWRpZW50VHJhbnNmb3JtPSJtYXRyaXgoMCAtODAuMjY1NiAtODAuMjY1NiAwIDQ3MzIxLjAyMzQgLTY1MzIxLjQyOTcpIj4KCTxzdG9wICBvZmZzZXQ9IjAiIHN0eWxlPSJzdG9wLWNvbG9yOiMwODE0MkUiLz4KCTxzdG9wICBvZmZzZXQ9IjAuODA5IiBzdHlsZT0ic3RvcC1jb2xvcjojMTczMjZFIi8+Cgk8c3RvcCAgb2Zmc2V0PSIxIiBzdHlsZT0ic3RvcC1jb2xvcjojMEQ2OUE5Ii8+CjwvbGluZWFyR3JhZGllbnQ+CjxwYXRoIGlkPSJwYXRoMzY0NiIgY2xhc3M9InN0NSIgZD0iTTIwOS4xLDY4YzAsMC41LDAuMiwxLjQsMC4zLDIuMWwwLDBjMC4yLTAuMywwLjMtMC42LDAuNS0xbDAsMGMwLjEtMC4zLDAuMS0wLjMtMC4xLTAuNGwwLDAKCWMtMC4zLTAuMS0wLjctMC40LTAuNy0wLjZsMCwwQzIwOSw2OC4xLDIwOSw2OC4xLDIwOS4xLDY4TDIwOS4xLDY4TDIwOS4xLDY4TDIwOS4xLDY4eiIvPgo8bGluZWFyR3JhZGllbnQgaWQ9InBhdGgzNjY4XzFfIiBncmFkaWVudFVuaXRzPSJ1c2VyU3BhY2VPblVzZSIgeDE9Ii04MTUuNTQxNCIgeTE9IjU4Ni4wMjQ1IiB4Mj0iLTgxNC41NDE0IiB5Mj0iNTg2LjAyNDUiIGdyYWRpZW50VHJhbnNmb3JtPSJtYXRyaXgoMCAtNzMuNTI3NyAtNzMuNTI3NyAwIDQzMzAzLjQzMzYgLTU5ODczLjYwMTYpIj4KCTxzdG9wICBvZmZzZXQ9IjAiIHN0eWxlPSJzdG9wLWNvbG9yOiMwODE0MkUiLz4KCTxzdG9wICBvZmZzZXQ9IjAuODA5IiBzdHlsZT0ic3RvcC1jb2xvcjojMTczMjZFIi8+Cgk8c3RvcCAgb2Zmc2V0PSIxIiBzdHlsZT0ic3RvcC1jb2xvcjojMEQ2OUE5Ii8+CjwvbGluZWFyR3JhZGllbnQ+CjxwYXRoIGlkPSJwYXRoMzY2OCIgY2xhc3M9InN0NiIgZD0iTTIxMi45LDU3LjJjMS4xLDEsMS43LDIuMiwxLjgsMy40bDAsMGMwLDAuNSwwLjUsMC42LDAuOCwwLjFsMCwwYzAuMS0wLjEsMC4yLTAuMywwLjMtMC41bDAsMAoJYy0wLjEtMC4xLTAuMi0wLjItMC4zLTAuNGwwLDBDMjE1LjEsNTkuMywyMTQsNTguMiwyMTIuOSw1Ny4yTDIxMi45LDU3LjJ6Ii8+CjxsaW5lYXJHcmFkaWVudCBpZD0icGF0aDM2OTBfMV8iIGdyYWRpZW50VW5pdHM9InVzZXJTcGFjZU9uVXNlIiB4MT0iLTgxNS4zMjgzIiB5MT0iNTg2LjM4MjEiIHgyPSItODE0LjMyODMiIHkyPSI1ODYuMzgyMSIgZ3JhZGllbnRUcmFuc2Zvcm09Im1hdHJpeCgwIC03Ni4wMDM4IC03Ni4wMDM4IDAgNDQ3MzcuNDE4IC02MTg3NS43MTA5KSI+Cgk8c3RvcCAgb2Zmc2V0PSIwIiBzdHlsZT0ic3RvcC1jb2xvcjojMDgxNDJFIi8+Cgk8c3RvcCAgb2Zmc2V0PSIwLjgwOSIgc3R5bGU9InN0b3AtY29sb3I6IzE3MzI2RSIvPgoJPHN0b3AgIG9mZnNldD0iMSIgc3R5bGU9InN0b3AtY29sb3I6IzBENjlBOSIvPgo8L2xpbmVhckdyYWRpZW50Pgo8cGF0aCBpZD0icGF0aDM2OTAiIGNsYXNzPSJzdDciIGQ9Ik0xNjksNTUuMmMwLjgsMS4yLDEuMiwyLjgsMS4yLDQuOWwwLDBjMCwwLjUsMC40LDAuNSwwLjYsMC4xbDAsMGMwLjEtMC4yLDAuMy0wLjQsMC40LTAuNmwwLDAKCUMxNzAuNyw1Ny43LDE2OS43LDU1LjksMTY5LDU1LjJ6Ii8+CjxsaW5lYXJHcmFkaWVudCBpZD0icGF0aDM3NDJfMV8iIGdyYWRpZW50VW5pdHM9InVzZXJTcGFjZU9uVXNlIiB4MT0iLTgxNS4wMDIiIHkxPSI1ODYuOTI5NyIgeDI9Ii04MTQuMDAyIiB5Mj0iNTg2LjkyOTciIGdyYWRpZW50VHJhbnNmb3JtPSJtYXRyaXgoMCAtODAuMTM2NSAtODAuMTM2NSAwIDQ3MjM2LjQzNzUgLTY1MjE3LjAyNzMpIj4KCTxzdG9wICBvZmZzZXQ9IjAiIHN0eWxlPSJzdG9wLWNvbG9yOiMwODE0MkUiLz4KCTxzdG9wICBvZmZzZXQ9IjAuODA5IiBzdHlsZT0ic3RvcC1jb2xvcjojMTczMjZFIi8+Cgk8c3RvcCAgb2Zmc2V0PSIxIiBzdHlsZT0ic3RvcC1jb2xvcjojMEQ2OUE5Ii8+CjwvbGluZWFyR3JhZGllbnQ+CjxwYXRoIGlkPSJwYXRoMzc0MiIgY2xhc3M9InN0OCIgZD0iTTE5OC4zLDY2LjJjLTMsMy42LTQuNiw3LjMtNC42LDEwLjlsMCwwYzAsMS4zLDAuNSwyLjksMS42LDMuNGwwLDBjMC40LDAuMiwwLjcsMC4zLDEuMSwwLjRsMCwwCgljLTAuMS0wLjUtMC4yLTEtMC4yLTEuNGwwLDBjMC0zLjcsMS4xLTcuNCw0LjEtMTEuMWwwLDBjMy42LTQuNCw3LjQtNi42LDEwLTUuNGwwLDBjLTAuMS0xLTAuNi0xLjgtMS43LTIuM2wwLDAKCWMtMC41LTAuMi0xLTAuMy0xLjYtMC4zbDAsMEMyMDQuNCw2MC40LDIwMS4yLDYyLjYsMTk4LjMsNjYuMiIvPgo8bGluZWFyR3JhZGllbnQgaWQ9InBhdGgzNzY0XzFfIiBncmFkaWVudFVuaXRzPSJ1c2VyU3BhY2VPblVzZSIgeDE9Ii04MTUuMDAzMiIgeTE9IjU4Ni45Mjc2IiB4Mj0iLTgxNC4wMDMyIiB5Mj0iNTg2LjkyNzYiIGdyYWRpZW50VHJhbnNmb3JtPSJtYXRyaXgoMCAtODAuMTE5NSAtODAuMTE5NSAwIDQ3MTU2Ljk3MjcgLTY1MjAzLjMyODEpIj4KCTxzdG9wICBvZmZzZXQ9IjAiIHN0eWxlPSJzdG9wLWNvbG9yOiMwODE0MkUiLz4KCTxzdG9wICBvZmZzZXQ9IjAuODA5IiBzdHlsZT0ic3RvcC1jb2xvcjojMTczMjZFIi8+Cgk8c3RvcCAgb2Zmc2V0PSIxIiBzdHlsZT0ic3RvcC1jb2xvcjojMEQ2OUE5Ii8+CjwvbGluZWFyR3JhZGllbnQ+CjxwYXRoIGlkPSJwYXRoMzc2NCIgY2xhc3M9InN0OSIgZD0iTTEzOC45LDU4LjVjLTQsMS41LTgsMy45LTEwLjgsNy42bDAsMGMtMy4yLDQuMi00LDkuMy0xLjksMTIuM2wwLDBjMC41LDAuNywxLjEsMS4yLDEuOCwxLjVsMCwwCgljLTEuMS0zLjUtMC4zLTguMiwyLjQtMTEuOGwwLDBjMi44LTMuNyw1LjktNS4xLDkuNC02LjdsMCwwYzAuNS0wLjIsMC41LTAuNSwwLjQtMC45bDAsMGMtMC4yLTAuNy0wLjYtMi41LTAuOC0yLjlsMCwwbDAsMAoJQzEzOS41LDU4LjEsMTM5LjQsNTguNCwxMzguOSw1OC41Ii8+CjxsaW5lYXJHcmFkaWVudCBpZD0icGF0aDM3ODZfMV8iIGdyYWRpZW50VW5pdHM9InVzZXJTcGFjZU9uVXNlIiB4MT0iLTgxNS4wNDQ2IiB5MT0iNTg2Ljg1ODIiIHgyPSItODE0LjA0NDYiIHkyPSI1ODYuODU4MiIgZ3JhZGllbnRUcmFuc2Zvcm09Im1hdHJpeCgwIC03OS41NzE3IC03OS41NzE3IDAgNDY4NjQuNTYyNSAtNjQ3NjAuMTU2MikiPgoJPHN0b3AgIG9mZnNldD0iMCIgc3R5bGU9InN0b3AtY29sb3I6IzA4MTQyRSIvPgoJPHN0b3AgIG9mZnNldD0iMC44MDkiIHN0eWxlPSJzdG9wLWNvbG9yOiMxNzMyNkUiLz4KCTxzdG9wICBvZmZzZXQ9IjEiIHN0eWxlPSJzdG9wLWNvbG9yOiMwRDY5QTkiLz4KPC9saW5lYXJHcmFkaWVudD4KPHBhdGggaWQ9InBhdGgzNzg2IiBjbGFzcz0ic3QxMCIgZD0iTTE2OC45LDY5LjhjLTMuNyw1LjctNy4yLDExLjItMTAuOSwxN2wwLDBjLTAuMiwwLjMtMC40LDAuNC0wLjcsMC41bDAsMGMtMi4zLDAtNC44LDAtNy4zLDAKCWwwLDBjLTAuMywwLTAuNC0wLjEtMC41LTAuM2wwLDBjMC4yLDAuOSwwLjUsMi41LDAuNiwyLjlsMCwwYzAuMSwwLjMsMC4zLDAuNCwwLjUsMC40bDAsMGMyLjcsMCw2LDAsOC4zLDBsMCwwCgljMC4zLDAsMC42LTAuMiwwLjctMC41bDAsMGMzLjQtNS4zLDctMTEsMTAuNC0xNi4zbDAsMGMwLjgsMi43LDEuMSwzLjksMi42LDUuMmwwLDBjMS40LDEuMywyLjcsMS42LDQuNywxLjZsMCwwCgljMS44LDAsMy41LTAuNyw1LjYtMS42bDAsMGMwLjgtMC4zLDEuNC0wLjcsMi0xLjFsMCwwYzAtMSwwLjEtMiwwLjMtMi45bDAsMGMwLTAuMS0wLjEtMC43LTAuNi0wLjRsMCwwYy0xLDAuNy0yLjIsMS40LTMuOCwybDAsMAoJYy0xLjksMC43LTIuOCwxLTQuNiwxbDAsMGMtMi4yLDAtNC4yLTEtNS42LTMuMmwwLDBjLTAuOC0xLjItMS4xLTMtMS4yLTQuM2wwLDBjMC0wLjEtMC4xLTAuMi0wLjItMC4ybDAsMAoJQzE2OS4xLDY5LjcsMTY5LDY5LjcsMTY4LjksNjkuOCIvPgo8bGluZWFyR3JhZGllbnQgaWQ9InBhdGgzODA4XzFfIiBncmFkaWVudFVuaXRzPSJ1c2VyU3BhY2VPblVzZSIgeDE9Ii04MTUuMDAwNiIgeTE9IjU4Ni45MzIxIiB4Mj0iLTgxNC4wMDA2IiB5Mj0iNTg2LjkzMjEiIGdyYWRpZW50VHJhbnNmb3JtPSJtYXRyaXgoMCAtODAuMTU0OCAtODAuMTU0OCAwIDQ3MjU1LjAzOTEgLTY1MjMxLjg1NTUpIj4KCTxzdG9wICBvZmZzZXQ9IjAiIHN0eWxlPSJzdG9wLWNvbG9yOiMwODE0MkUiLz4KCTxzdG9wICBvZmZzZXQ9IjAuODA5IiBzdHlsZT0ic3RvcC1jb2xvcjojMTczMjZFIi8+Cgk8c3RvcCAgb2Zmc2V0PSIxIiBzdHlsZT0ic3RvcC1jb2xvcjojMEQ2OUE5Ii8+CjwvbGluZWFyR3JhZGllbnQ+CjxwYXRoIGlkPSJwYXRoMzgwOCIgY2xhc3M9InN0MTEiIGQ9Ik0yMzMuMyw3Mi44Yy0zLjYsNC40LTcuNSw4LjUtMTEuMywxMS40bDAsMGMtNS45LDQuNi0xMS43LDUuNy0xNC42LDIuOGwwLDAKCWMtMS4xLTEuMS0xLjctMi42LTEuNy00bDAsMGMwLTAuNy0wLjQtMC43LTAuNy0wLjRsMCwwYy0zLjUsMy40LTkuNSw3LjItMTUsNC41bDAsMGMtMi43LTEuNC00LjItMy45LTQuOC02LjdsMCwwCgljMC4zLDIsMC44LDQuOSwxLjcsNi43bDAsMGMwLjYsMS4yLDIsMi42LDIuOSwzbDAsMGM0LjksMi40LDExLjgtMC4zLDE2LjMtNC42bDAsMGMwLTAuMSwwLjEtMC4xLDAuMS0wLjFsMCwwCgljMC4yLDAuOCwwLjUsMS43LDAuNSwxLjhsMCwwYzAuMywxLDAuOCwxLjksMS4yLDIuNGwwLDBjMy4xLDMuNSw5LjUsMS45LDE2LjMtMy4zbDAsMGMzLjgtMi45LDYuNi01LjgsMTAtOS44bDAsMAoJYzAuMS0wLjIsMC4xLTAuNCwwLjEtMC44bDAsMGMtMC4yLTAuOS0wLjUtMi40LTAuNy0zLjJsMCwwQzIzMy40LDcyLjUsMjMzLjQsNzIuNywyMzMuMyw3Mi44IE0xODUuMSw4MC4yYzAsMC4xLDAsMC4yLDAsMC4ybDAsMAoJQzE4NS4xLDgwLjQsMTg1LjEsODAuMywxODUuMSw4MC4yTDE4NS4xLDgwLjJDMTg1LjEsODAuMywxODUuMSw4MC4yLDE4NS4xLDgwLjJMMTg1LjEsODAuMnoiLz4KPGxpbmVhckdyYWRpZW50IGlkPSJwYXRoMzgzMF8xXyIgZ3JhZGllbnRVbml0cz0idXNlclNwYWNlT25Vc2UiIHgxPSItODE0Ljk5NjgiIHkxPSI1ODYuOTM4NCIgeDI9Ii04MTMuOTk2OCIgeTI9IjU4Ni45Mzg0IiBncmFkaWVudFRyYW5zZm9ybT0ibWF0cml4KDAgLTgwLjIwNTcgLTgwLjIwNTcgMCA0NzI1OC4yNDYxIC02NTI3Mi45OTYxKSI+Cgk8c3RvcCAgb2Zmc2V0PSIwIiBzdHlsZT0ic3RvcC1jb2xvcjojMDgxNDJFIi8+Cgk8c3RvcCAgb2Zmc2V0PSIwLjgwOSIgc3R5bGU9InN0b3AtY29sb3I6IzE3MzI2RSIvPgoJPHN0b3AgIG9mZnNldD0iMSIgc3R5bGU9InN0b3AtY29sb3I6IzBENjlBOSIvPgo8L2xpbmVhckdyYWRpZW50Pgo8cGF0aCBpZD0icGF0aDM4MzAiIGNsYXNzPSJzdDEyIiBkPSJNMTg2LjgsNjAuN2MtMC4zLDIuMi0xLjUsNC4xLTMuNSw1LjFsMCwwYy0xLjcsMC44LTMuNywwLjctNS4xLTAuNmwwLDBjLTAuNC0wLjQtMC43LTAuOS0xLTEuNAoJbDAsMGMwLjQsMS42LDAuNywyLjgsMS4xLDMuNWwwLDBjMS4zLDIsMy42LDIuNSw2LjEsMS4xbDAsMGMxLjgtMSwzLjQtMy4xLDMuMi02LjRsMCwwYy0wLjEtMS43LTAuNi0zLjQtMS40LTQuOGwwLDAKCUMxODYuOCw1OC4zLDE4Nyw1OS41LDE4Ni44LDYwLjciLz4KPGxpbmVhckdyYWRpZW50IGlkPSJwYXRoMzg1Ml8xXyIgZ3JhZGllbnRVbml0cz0idXNlclNwYWNlT25Vc2UiIHgxPSItODE1LjAwMjEiIHkxPSI1ODYuOTI5NSIgeDI9Ii04MTQuMDAyMSIgeTI9IjU4Ni45Mjk1IiBncmFkaWVudFRyYW5zZm9ybT0ibWF0cml4KDAgLTgwLjEzNTEgLTgwLjEzNTEgMCA0NzI1OS44MjgxIC02NTIxNS45NTMxKSI+Cgk8c3RvcCAgb2Zmc2V0PSIwIiBzdHlsZT0ic3RvcC1jb2xvcjojMDgxNDJFIi8+Cgk8c3RvcCAgb2Zmc2V0PSIwLjgwOSIgc3R5bGU9InN0b3AtY29sb3I6IzE3MzI2RSIvPgoJPHN0b3AgIG9mZnNldD0iMSIgc3R5bGU9InN0b3AtY29sb3I6IzBENjlBOSIvPgo8L2xpbmVhckdyYWRpZW50Pgo8cGF0aCBpZD0icGF0aDM4NTIiIGNsYXNzPSJzdDEzIiBkPSJNMjM4LjEsNDAuMWMtMS4xLDItMjMuMSwzNS40LTI0LjUsMzguOWwwLDBjLTAuNCwxLjEtMC41LDEuOSwwLDIuNWwwLDAKCWMwLjUsMC42LDEuMSwwLjgsMS45LDAuOGwwLDBjMC4xLTAuNCwwLjItMC45LDAuNC0xLjRsMCwwYzEuNC0zLjUsMjItMzQuNywyMy4xLTM2LjdsMCwwYzAuMS0wLjIsMC4xLTAuNCwwLTAuNWwwLDAKCWMtMC4xLTAuMy0wLjgtMy42LTAuOC0zLjlsMCwwQzIzOC4yLDM5LjksMjM4LjIsNDAsMjM4LjEsNDAuMSIvPgo8bGluZWFyR3JhZGllbnQgaWQ9InBhdGgzODc0XzFfIiBncmFkaWVudFVuaXRzPSJ1c2VyU3BhY2VPblVzZSIgeDE9Ii04MTUuMTQzOSIgeTE9IjU4Ni42OTE2IiB4Mj0iLTgxNC4xNDM5IiB5Mj0iNTg2LjY5MTYiIGdyYWRpZW50VHJhbnNmb3JtPSJtYXRyaXgoMCAtNzguMjg1NyAtNzguMjg1NyAwIDQ2MDc4LjMxNjQgLTYzNzIwLjYyMTEpIj4KCTxzdG9wICBvZmZzZXQ9IjAiIHN0eWxlPSJzdG9wLWNvbG9yOiMwODE0MkUiLz4KCTxzdG9wICBvZmZzZXQ9IjAuODA5IiBzdHlsZT0ic3RvcC1jb2xvcjojMTczMjZFIi8+Cgk8c3RvcCAgb2Zmc2V0PSIxIiBzdHlsZT0ic3RvcC1jb2xvcjojMEQ2OUE5Ii8+CjwvbGluZWFyR3JhZGllbnQ+CjxwYXRoIGlkPSJwYXRoMzg3NCIgY2xhc3M9InN0MTQiIGQ9Ik0xNDYuOSw1NS43YzAuMSwwLjEsMC4xLDAuMSwwLjIsMC4ybDAsMGMxLjMsMiwyLDQuNywyLjEsNy42bDAsMGMwLjEsMC42LDAuMywwLjYsMC42LDAuM2wwLDAKCWMwLjMtMC4zLDAuNS0wLjYsMC44LTAuOGwwLDBjLTAuNC0xLjUtMS0yLjktMS42LTQuMmwwLDBDMTQ4LjgsNTguMiwxNDcuOCw1Ni41LDE0Ni45LDU1Ljd6Ii8+CjxsaW5lYXJHcmFkaWVudCBpZD0icGF0aDM4OTZfMV8iIGdyYWRpZW50VW5pdHM9InVzZXJTcGFjZU9uVXNlIiB4MT0iLTgxNS4wNDI3IiB5MT0iNTg2Ljg2MTMiIHgyPSItODE0LjA0MjciIHkyPSI1ODYuODYxMyIgZ3JhZGllbnRUcmFuc2Zvcm09Im1hdHJpeCgwIC03OS41OTYzIC03OS41OTYzIDAgNDY4NDguMjQyMiAtNjQ3ODAuMDU0NykiPgoJPHN0b3AgIG9mZnNldD0iMCIgc3R5bGU9InN0b3AtY29sb3I6IzA4MTQyRSIvPgoJPHN0b3AgIG9mZnNldD0iMC44MDkiIHN0eWxlPSJzdG9wLWNvbG9yOiMxNzMyNkUiLz4KCTxzdG9wICBvZmZzZXQ9IjEiIHN0eWxlPSJzdG9wLWNvbG9yOiMwRDY5QTkiLz4KPC9saW5lYXJHcmFkaWVudD4KPHBhdGggaWQ9InBhdGgzODk2IiBjbGFzcz0ic3QxNSIgZD0iTTE1OC4xLDYyLjNjLTQuNywzLjYtOC43LDkuMi0xMC43LDExLjdsMCwwYy0xLjIsMS41LTIuMywzLjYtNS40LDdsMCwwCgljLTQuOSw1LjMtMTEuNCw4LjQtMTcuNiw2LjJsMCwwYy0zLjQtMS4xLTUuOS0zLjktNi44LTcuM2wwLDBjLTAuMi0wLjctMC42LTAuOC0wLjktMC40bDAsMGMtMSwxLjMtMy4xLDMuMS00LjgsNC4zbDAsMAoJYy0wLjIsMC4xLTAuNywwLjQtMS4xLDAuMmwwLDBjLTAuNC0wLjItMS42LTItMS45LTIuNWwwLDBjMC0wLjEtMC4xLTAuMS0wLjEtMC4ybDAsMHYwYzAuNCwyLjIsMC41LDIuNSwxLjEsMy41bDAsMAoJYzAuNywxLjEsMS40LDEuOSwxLjUsMmwwLDBjMC40LDAuMiwwLjgsMCwxLTAuMWwwLDBjMS4zLTAuNywzLjktMi43LDUuMS00LjFsMCwwYzAuMy0wLjMsMC43LTAuMSwwLjgsMC4ybDAsMAoJYzAuNSwxLjUsMS4yLDIuNiwxLjksMy45bDAsMGMwLjgsMS40LDIuNSwyLjgsNC43LDMuNGwwLDBjMi44LDAuOCw1LjksMC45LDkuOS0wLjZsMCwwYzMuMi0xLjIsNi42LTMuNyw5LjItNi42bDAsMAoJYzMuMS0zLjQsNC4yLTUuNSw1LjQtN2wwLDBjMi0yLjUsNS4yLTYuOSw5LjYtMTAuN2wwLDBjMS41LTEuMywzLjItMi4yLDQuMy0xLjhsMCwwYzAuNi0xLjYsMC4zLTIuNS0wLjMtM2wwLDAKCWMtMC4yLTAuMS0wLjUtMC4yLTAuOC0wLjJsMCwwQzE2MSw2MC40LDE1OS41LDYxLjMsMTU4LjEsNjIuMyIvPgo8bGluZWFyR3JhZGllbnQgaWQ9InBhdGgzOTE4XzFfIiBncmFkaWVudFVuaXRzPSJ1c2VyU3BhY2VPblVzZSIgeDE9Ii04MTUuMDAyMyIgeTE9IjU4Ni45MjkxIiB4Mj0iLTgxNC4wMDIzIiB5Mj0iNTg2LjkyOTEiIGdyYWRpZW50VHJhbnNmb3JtPSJtYXRyaXgoMCAtODAuMTMxNiAtODAuMTMxNiAwIDQ3MTA3LjM5ODQgLTY1MjEzLjEyMTEpIj4KCTxzdG9wICBvZmZzZXQ9IjAiIHN0eWxlPSJzdG9wLWNvbG9yOiMwODE0MkUiLz4KCTxzdG9wICBvZmZzZXQ9IjAuODA5IiBzdHlsZT0ic3RvcC1jb2xvcjojMTczMjZFIi8+Cgk8c3RvcCAgb2Zmc2V0PSIxIiBzdHlsZT0ic3RvcC1jb2xvcjojMEQ2OUE5Ii8+CjwvbGluZWFyR3JhZGllbnQ+CjxwYXRoIGlkPSJwYXRoMzkxOCIgY2xhc3M9InN0MTYiIGQ9Ik03OS4zLDU3LjhjLTIuNywxLjQtNS45LDMuNy03LjUsNi45bDAsMGMtMS4zLDIuNi0xLjUsNS43LDAuNCw4LjdsMCwwYzAuMiwwLjIsMC4zLDAuNSwwLjUsMC43CglsMCwwYy0wLjYtMi41LDAuMS01LjEsMS03LjFsMCwwYzEuNi0zLjIsMy44LTQuNyw2LTYuMWwwLDBjMC45LTAuNiwxLjQtMS4yLDAuOC0yLjdsMCwwYy0wLjItMC40LTAuMy0xLjItMC40LTEuOWwwLDAKCUM4MC4yLDU2LjksNzkuOSw1Ny41LDc5LjMsNTcuOCIvPgo8bGluZWFyR3JhZGllbnQgaWQ9InBhdGgzOTQwXzFfIiBncmFkaWVudFVuaXRzPSJ1c2VyU3BhY2VPblVzZSIgeDE9Ii04MTUuMDAzNiIgeTE9IjU4Ni45MjY5IiB4Mj0iLTgxNC4wMDM2IiB5Mj0iNTg2LjkyNjkiIGdyYWRpZW50VHJhbnNmb3JtPSJtYXRyaXgoMCAtODAuMTE0NSAtODAuMTE0NSAwIDQ3MTMzLjAyNzMgLTY1MTk5LjI1KSI+Cgk8c3RvcCAgb2Zmc2V0PSIwIiBzdHlsZT0ic3RvcC1jb2xvcjojMDgxNDJFIi8+Cgk8c3RvcCAgb2Zmc2V0PSIwLjgwOSIgc3R5bGU9InN0b3AtY29sb3I6IzE3MzI2RSIvPgoJPHN0b3AgIG9mZnNldD0iMSIgc3R5bGU9InN0b3AtY29sb3I6IzBENjlBOSIvPgo8L2xpbmVhckdyYWRpZW50Pgo8cGF0aCBpZD0icGF0aDM5NDAiIGNsYXNzPSJzdDE3IiBkPSJNOTkuNCwyNS45Yy03LjcsMi45LTExLjEsOS05LjUsMTMuMWwwLDBjMC4zLDAuOCwwLjgsMS40LDEuNSwxLjhsMCwwCgljLTAuNS0zLjgsMi4zLTkuOSw5LjctMTIuNGwwLDBjOS43LTMuMiwyMC41LTEuMiwyOS4yLDAuN2wwLDBjMS4yLTAuOCwyLjMtMS4zLDMuMy0xLjlsMCwwYzAuNS0wLjMtMC4xLTAuNi0wLjItMC42bDAsMAoJYy02LjktMS4zLTE0LjEtMi45LTIxLjEtMi45bDAsMEMxMDcuOSwyMy43LDEwMy42LDI0LjMsOTkuNCwyNS45Ii8+CjxsaW5lYXJHcmFkaWVudCBpZD0icGF0aDM5NjJfMV8iIGdyYWRpZW50VW5pdHM9InVzZXJTcGFjZU9uVXNlIiB4MT0iLTgxNS4wMDIxIiB5MT0iNTg2LjkyOTQiIHgyPSItODE0LjAwMjEiIHkyPSI1ODYuOTI5NCIgZ3JhZGllbnRUcmFuc2Zvcm09Im1hdHJpeCgwIC04MC4xMzQ0IC04MC4xMzQ0IDAgNDcxMzQuNDc2NiAtNjUyMTUuMzY3MikiPgoJPHN0b3AgIG9mZnNldD0iMCIgc3R5bGU9InN0b3AtY29sb3I6IzA4MTQyRSIvPgoJPHN0b3AgIG9mZnNldD0iMC44MDkiIHN0eWxlPSJzdG9wLWNvbG9yOiMxNzMyNkUiLz4KCTxzdG9wICBvZmZzZXQ9IjEiIHN0eWxlPSJzdG9wLWNvbG9yOiMwRDY5QTkiLz4KPC9saW5lYXJHcmFkaWVudD4KPHBhdGggaWQ9InBhdGgzOTYyIiBjbGFzcz0ic3QxOCIgZD0iTTEzMS43LDQ4LjhjLTMuNSwwLjItOC45LDAuNy0xMi42LDEuMmwwLDBjLTAuOSwwLjEtMSwwLjMtMS4yLDAuNmwwLDAKCWMtNS45LDkuNy0xMi4xLDIwLjEtMTksMjcuMWwwLDBjLTcuNCw3LjUtMTMuNSw5LjUtMjAsOS41bDAsMGMtNy41LDAuMS0xNC4yLTQuMi0xNS45LTExLjdsMCwwYzAuOSw0LjIsMy42LDkuMiw2LjcsMTEuNGwwLDAKCWMzLjIsMi4yLDYuMywzLDkuOSwzbDAsMGM3LjQsMC4xLDE0LjItMi45LDIxLjQtMTAuMmwwLDBjNi45LTcsMTIuOS0xNi44LDE4LjctMjYuNWwwLDBjMC4yLTAuMywwLjQtMC41LDEuNC0wLjZsMCwwCgljMy43LTAuNSw3LTAuNywxMC4zLTFsMCwwYzEtMC4xLDEuNy0wLjIsMi4xLDAuMmwwLDBjMS4yLDEuMiwyLjUsMi4zLDMuNSwyLjhsMCwwYzAuNiwwLDEuMSwwLjEsMS41LDAuNWwwLDBjMC40LTAuMSwwLjctMC4zLDEtMC41CglsMCwwYzAuNC0wLjQsMC40LTAuOSwwLjQtMS4zbDAsMGMtMC4xLTAuOC0wLjQtMi40LTAuNi0yLjhsMCwwYzAuMiwwLjMsMC4xLDAuOC0wLjMsMS4ybDAsMGMtMC4zLDAuMy0wLjcsMC42LTEuMiwwLjZsMCwwCgljLTAuNCwwLTAuNy0wLjItMS4yLTAuNGwwLDBjLTEuMS0wLjYtMi41LTEuNi0zLjQtMi43bDAsMGMtMC4yLTAuMy0wLjQtMC40LTAuOC0wLjRsMCwwQzEzMiw0OC43LDEzMS45LDQ4LjgsMTMxLjcsNDguOCIvPgo8bGluZWFyR3JhZGllbnQgaWQ9InBhdGgzOTg0XzFfIiBncmFkaWVudFVuaXRzPSJ1c2VyU3BhY2VPblVzZSIgeDE9Ii04MTQuOTk5MSIgeTE9IjU4Ni45MzQ0IiB4Mj0iLTgxMy45OTkxIiB5Mj0iNTg2LjkzNDQiIGdyYWRpZW50VHJhbnNmb3JtPSJtYXRyaXgoMCAtODAuMTc0NiAtODAuMTc0NiAwIDQ3MTYwLjM1OTQgLTY1MjQ3LjgzOTgpIj4KCTxzdG9wICBvZmZzZXQ9IjAiIHN0eWxlPSJzdG9wLWNvbG9yOiMwODE0MkUiLz4KCTxzdG9wICBvZmZzZXQ9IjAuODA5IiBzdHlsZT0ic3RvcC1jb2xvcjojMTczMjZFIi8+Cgk8c3RvcCAgb2Zmc2V0PSIxIiBzdHlsZT0ic3RvcC1jb2xvcjojMEQ2OUE5Ii8+CjwvbGluZWFyR3JhZGllbnQ+CjxwYXRoIGlkPSJwYXRoMzk4NCIgY2xhc3M9InN0MTkiIGQ9Ik05OS45LDU0LjZjLTAuOCwwLjYtMiwwLjUtMi41LTAuM2wwLDBjLTAuMi0wLjMtMC4zLTAuNi0wLjMtMC44bDAsMGMtMC4xLDEuMywwLjQsMy4xLDAuOCwzLjcKCWwwLDBjMC40LDAuNywxLjcsMSwyLjcsMC4zbDAsMGMyLjItMS43LDQuMy0yLjYsNi41LTMuMWwwLDBjMC42LTAuOCwxLjItMS43LDEuOS0yLjdsMCwwYzAuMS0wLjEsMC4xLTAuMiwwLTAuMmwwLDAKCWMwLTAuMS0wLjEtMC4xLTAuMy0wLjFsMCwwQzEwNS42LDUxLjUsMTAyLjcsNTIuNSw5OS45LDU0LjYiLz4KPGxpbmVhckdyYWRpZW50IGlkPSJwYXRoNDAwNl8xXyIgZ3JhZGllbnRVbml0cz0idXNlclNwYWNlT25Vc2UiIHgxPSItODE1LjEzMjUiIHkxPSI1ODYuNzEwNiIgeDI9Ii04MTQuMTMyNSIgeTI9IjU4Ni43MTA2IiBncmFkaWVudFRyYW5zZm9ybT0ibWF0cml4KDAgLTc4LjQzMDYgLTc4LjQzMDYgMCA0NjIwOS42NDQ1IC02MzgzOC40NzI3KSI+Cgk8c3RvcCAgb2Zmc2V0PSIwIiBzdHlsZT0ic3RvcC1jb2xvcjojMDgxNDJFIi8+Cgk8c3RvcCAgb2Zmc2V0PSIwLjgwOSIgc3R5bGU9InN0b3AtY29sb3I6IzE3MzI2RSIvPgoJPHN0b3AgIG9mZnNldD0iMSIgc3R5bGU9InN0b3AtY29sb3I6IzBENjlBOSIvPgo8L2xpbmVhckdyYWRpZW50Pgo8cGF0aCBpZD0icGF0aDQwMDYiIGNsYXNzPSJzdDIwIiBkPSJNMTkzLjUsMjMuOGMwLDAuMSwwLjEsMC4xLDAuMSwwLjJsMCwwQzE5My42LDIzLjksMTkzLjYsMjMuOCwxOTMuNSwyMy44eiIvPgo8bGluZWFyR3JhZGllbnQgaWQ9InBhdGg0MDI4XzFfIiBncmFkaWVudFVuaXRzPSJ1c2VyU3BhY2VPblVzZSIgeDE9Ii04MTUuMDAyOCIgeTE9IjU4Ni45MjgzIiB4Mj0iLTgxNC4wMDI4IiB5Mj0iNTg2LjkyODMiIGdyYWRpZW50VHJhbnNmb3JtPSJtYXRyaXgoMCAtODAuMTI1NSAtODAuMTI1NSAwIDQ3MTg1LjYwNTUgLTY1MjA4LjE3OTcpIj4KCTxzdG9wICBvZmZzZXQ9IjAiIHN0eWxlPSJzdG9wLWNvbG9yOiMwODE0MkUiLz4KCTxzdG9wICBvZmZzZXQ9IjAuODA5IiBzdHlsZT0ic3RvcC1jb2xvcjojMTczMjZFIi8+Cgk8c3RvcCAgb2Zmc2V0PSIxIiBzdHlsZT0ic3RvcC1jb2xvcjojMEQ2OUE5Ii8+CjwvbGluZWFyR3JhZGllbnQ+CjxwYXRoIGlkPSJwYXRoNDAyOCIgY2xhc3M9InN0MjEiIGQ9Ik0xOTMuOSwyNS4yYy0wLjEsMi4xLTEuOCw0LjItNS45LDYuNGwwLDBjLTQuNywyLjYtOS41LDMuMy0xNC42LDMuNGwwLDAKCWMtMTIuMywwLjEtMjMuOC00LjctMzUuNi03LjNsMCwwYzAsMC41LDAuMSwxLjEtMC4zLDEuNWwwLDBDMTMwLjksMzQuMSwxMjUsMzksMTIxLDQ1LjlsMCwwYy0wLjEsMC4yLTAuMSwwLjMsMC4yLDAuM2wwLDAKCWMxLjEtMC4xLDIuMS0wLjEsMy4xLTAuMmwwLDBjMy42LTUuNyw3LjUtOC45LDEzLjQtMTMuM2wwLDBjMC40LTAuMywwLjktMC42LDAuNy0xLjhsMCwwYzExLjksMi42LDIwLjksNywzNi4zLDcuMWwwLDAKCWM0LjYsMCwxMS0xLjUsMTQuNS0zLjZsMCwwYzQtMi40LDUuMS00LjIsNS4yLTZsMCwwYzAtMC42LTAuMS0xLjUtMC4yLTEuOWwwLDBjLTAuMS0wLjYtMC4yLTEuNC0wLjQtMmwwLDAKCUMxOTMuOSwyNC42LDE5My45LDI0LjksMTkzLjksMjUuMiIvPgo8bGluZWFyR3JhZGllbnQgaWQ9InBhdGg0MDUwXzFfIiBncmFkaWVudFVuaXRzPSJ1c2VyU3BhY2VPblVzZSIgeDE9Ii04MTUuMzUzNyIgeTE9IjU4Ni4zMzk1IiB4Mj0iLTgxNC4zNTM3IiB5Mj0iNTg2LjMzOTUiIGdyYWRpZW50VHJhbnNmb3JtPSJtYXRyaXgoMCAtNzUuNzAwNiAtNzUuNzAwNiAwIDQ0NTIzLjEyNSAtNjE2MzEuMTU2MikiPgoJPHN0b3AgIG9mZnNldD0iMCIgc3R5bGU9InN0b3AtY29sb3I6IzA4MTQyRSIvPgoJPHN0b3AgIG9mZnNldD0iMC44MDkiIHN0eWxlPSJzdG9wLWNvbG9yOiMxNzMyNkUiLz4KCTxzdG9wICBvZmZzZXQ9IjEiIHN0eWxlPSJzdG9wLWNvbG9yOiMwRDY5QTkiLz4KPC9saW5lYXJHcmFkaWVudD4KPHBhdGggaWQ9InBhdGg0MDUwIiBjbGFzcz0ic3QyMiIgZD0iTTEzNi42LDM5LjdjLTAuMSwwLjEtMC4zLDAuMy0wLjUsMC40bDAsMGMtMS4yLDEuMi0xLjUsMi44LTEuNCw0bDAsMGMwLjEsMC41LDAuMywwLjYsMC41LDAuNQoJbDAsMGMwLjIsMCwwLjUtMC4xLDAuNy0wLjJsMCwwYzAuMS0wLjcsMC40LTEuMywxLTEuOWwwLDBjMC41LTAuNCwxLjEtMC42LDEuNi0wLjVsMCwwYzAuNS0wLjksMC42LTIsMC0yLjVsMCwwCgljLTAuMi0wLjItMC41LTAuMy0wLjktMC4zbDAsMEMxMzcuNCwzOS4zLDEzNywzOS40LDEzNi42LDM5LjciLz4KPGxpbmVhckdyYWRpZW50IGlkPSJwYXRoNDA3Ml8xXyIgZ3JhZGllbnRVbml0cz0idXNlclNwYWNlT25Vc2UiIHgxPSItODE1LjAwMjEiIHkxPSI1ODYuOTI5NCIgeDI9Ii04MTQuMDAyMSIgeTI9IjU4Ni45Mjk0IiBncmFkaWVudFRyYW5zZm9ybT0ibWF0cml4KDAgLTgwLjEzNDIgLTgwLjEzNDIgMCA0NzE3Mi41NTQ3IC02NTIxNS4xODc1KSI+Cgk8c3RvcCAgb2Zmc2V0PSIwIiBzdHlsZT0ic3RvcC1jb2xvcjojMDgxNDJFIi8+Cgk8c3RvcCAgb2Zmc2V0PSIwLjgwOSIgc3R5bGU9InN0b3AtY29sb3I6IzE3MzI2RSIvPgoJPHN0b3AgIG9mZnNldD0iMSIgc3R5bGU9InN0b3AtY29sb3I6IzBENjlBOSIvPgo8L2xpbmVhckdyYWRpZW50Pgo8cGF0aCBpZD0icGF0aDQwNzIiIGNsYXNzPSJzdDIzIiBkPSJNMTQxLjMsNDMuOWMtMS4xLDIuMi0zLDMuMy00LjgsMy45bDAsMGMwLDAtMC40LDAuMS0wLjMsMC40bDAsMGMwLDAuNCwxLjMsMS4yLDIuMSwxLjdsMCwwCgljMC4xLDAsMC4zLTAuMSwwLjMtMC4xbDAsMGMwLjktMC40LDIuNC0xLjMsMy4zLTMuMmwwLDBjMC42LTEuMiwwLjktMi4yLDAuNi00LjRsMCwwYy0wLjItMS41LTAuNS0yLjktMC45LTMuNWwwLDAKCUMxNDIuNSw0MC4zLDE0Mi4yLDQyLjMsMTQxLjMsNDMuOSIvPgo8bGluZWFyR3JhZGllbnQgaWQ9InBhdGg0MDk0XzFfIiBncmFkaWVudFVuaXRzPSJ1c2VyU3BhY2VPblVzZSIgeDE9Ii04MTUuMDAxOSIgeTE9IjU4Ni45Mjk3IiB4Mj0iLTgxNC4wMDE5IiB5Mj0iNTg2LjkyOTciIGdyYWRpZW50VHJhbnNmb3JtPSJtYXRyaXgoMCAtODAuMTM3MiAtODAuMTM3MiAwIDQ3MTMwLjQxOCAtNjUyMTcuNjEzMykiPgoJPHN0b3AgIG9mZnNldD0iMCIgc3R5bGU9InN0b3AtY29sb3I6IzA4MTQyRSIvPgoJPHN0b3AgIG9mZnNldD0iMC44MDkiIHN0eWxlPSJzdG9wLWNvbG9yOiMxNzMyNkUiLz4KCTxzdG9wICBvZmZzZXQ9IjEiIHN0eWxlPSJzdG9wLWNvbG9yOiMwRDY5QTkiLz4KPC9saW5lYXJHcmFkaWVudD4KPHBhdGggaWQ9InBhdGg0MDk0IiBjbGFzcz0ic3QyNCIgZD0iTTEwOC41LDMzLjhjMC4yLDAuNSwwLjIsMS40LTAuMiwyLjRsMCwwYy0zLjMsNy43LTkuNSwxMy43LTE3LjEsMTRsMCwwYy00LjYsMC4xLTgtMi4yLTkuNi01LjYKCWwwLDBjMS4yLDIuNiwzLjYsNC45LDUuNyw2LjJsMCwwYzEuNiwxLDMuNywxLjYsNiwxLjVsMCwwYzcuOS0wLjMsMTMuOS02LjgsMTUuOS0xMi4zbDAsMGMwLjUtMS41LDAuMS0zLjEtMC4xLTQuMWwwLDAKCUMxMDguOSwzNS40LDEwOC44LDM0LjUsMTA4LjUsMzMuOEwxMDguNSwzMy44TDEwOC41LDMzLjh6Ii8+CjxwYXRoIGlkPSJwYXRoNDEwNiIgY2xhc3M9InN0MjUiIGQ9Ik0yOTkuMSw1MS45YzAuMSwwLjMsMC4xLDAuNSwwLjEsMC44QzI5OS4yLDUyLjQsMjk5LjEsNTIuMiwyOTkuMSw1MS45IE0xLDU2LjkKCWMwLTYuNiwyLjktMTMuMSw5LTE5LjNDMzEuNSwxNS45LDg3LjcsMS4zLDE0OS43LDFDMjMxLjksMC43LDI5OC44LDI1LjIsMjk5LDU1LjZjMCw2LjYtMywxMy05LjEsMTkuMgoJYy0yMS41LDIxLjctNzcuNiwzNi40LTEzOS42LDM2LjZDNjguMSwxMTEuOCwxLjIsODcuMywxLDU2LjkgTTE1MCwwQzY2LjcsMCwwLDI1LDAsNTYuMmMwLDMxLjEsNjcuMyw1Ni4yLDE1MCw1Ni4yCgljODIuNywwLDE1MC0yNS4yLDE1MC01Ni4yQzMwMCwyNS4yLDIzMi43LDAsMTUwLDAiLz4KPGxpbmVhckdyYWRpZW50IGlkPSJwYXRoNDEzMF8xXyIgZ3JhZGllbnRVbml0cz0idXNlclNwYWNlT25Vc2UiIHgxPSItODE0LjAyOTEiIHkxPSI1OTIuMTA4NSIgeDI9Ii04MTMuMDI5MSIgeTI9IjU5Mi4xMDg1IiBncmFkaWVudFRyYW5zZm9ybT0ibWF0cml4KC0zNC42NTc5IC0xMjkuMzQ0NSAtMTI5LjM0NDUgMzQuNjU3OSA0ODQ5MC40ODA1IC0xMjU2NzIuMDU0NykiPgoJPHN0b3AgIG9mZnNldD0iMCIgc3R5bGU9InN0b3AtY29sb3I6I0IyQjFCMSIvPgoJPHN0b3AgIG9mZnNldD0iMC4zNSIgc3R5bGU9InN0b3AtY29sb3I6I0RFRERERSIvPgoJPHN0b3AgIG9mZnNldD0iMC42NSIgc3R5bGU9InN0b3AtY29sb3I6I0RFRERERSIvPgoJPHN0b3AgIG9mZnNldD0iMSIgc3R5bGU9InN0b3AtY29sb3I6I0IyQjFCMSIvPgo8L2xpbmVhckdyYWRpZW50Pgo8cGF0aCBpZD0icGF0aDQxMzAiIGNsYXNzPSJzdDI2IiBkPSJNMC41LDU2LjJjMCwxLjUsMC4yLDIuOSwwLjUsNC40bDAsMGMtMC4yLTEuMi0wLjQtMi41LTAuNC0zLjdsMCwwYzAtNi43LDMtMTMuNCw5LjEtMTkuNmwwLDAKCUMzMS4zLDE1LjUsODcuNiwwLjgsMTQ5LjcsMC42bDAsMGM4LjYsMCwxNy4xLDAuMiwyNS4zLDAuN2wwLDBjLTguMS0wLjUtMTYuNS0wLjgtMjUtMC44bDAsMEM2Ny4xLDAuNSwwLjUsMjUuMywwLjUsNTYuMiIvPgo8bGluZWFyR3JhZGllbnQgaWQ9InBhdGg0MTU0XzFfIiBncmFkaWVudFVuaXRzPSJ1c2VyU3BhY2VPblVzZSIgeDE9Ii04MTQuMDUyNiIgeTE9IjU5Mi4wODU3IiB4Mj0iLTgxMy4wNTI2IiB5Mj0iNTkyLjA4NTciIGdyYWRpZW50VHJhbnNmb3JtPSJtYXRyaXgoLTM0LjQ5NyAtMTI4Ljc0NDggLTEyOC43NDQ4IDM0LjQ5NyA0ODM1My44MjgxIC0xMjUxNjEuNzAzMSkiPgoJPHN0b3AgIG9mZnNldD0iMCIgc3R5bGU9InN0b3AtY29sb3I6I0IyQjFCMSIvPgoJPHN0b3AgIG9mZnNldD0iMC4zNSIgc3R5bGU9InN0b3AtY29sb3I6I0RFRERERSIvPgoJPHN0b3AgIG9mZnNldD0iMC42NSIgc3R5bGU9InN0b3AtY29sb3I6I0RFRERERSIvPgoJPHN0b3AgIG9mZnNldD0iMSIgc3R5bGU9InN0b3AtY29sb3I6I0IyQjFCMSIvPgo8L2xpbmVhckdyYWRpZW50Pgo8cGF0aCBpZD0icGF0aDQxNTQiIGNsYXNzPSJzdDI3IiBkPSJNMjk5LjQsNTUuNmMwLDYuNy0zLjEsMTMuMy05LjMsMTkuNWwwLDBjLTIxLjUsMjEuNy03Ny44LDM2LjUtMTM5LjksMzYuOGwwLDAKCWMtOC44LDAtMTcuNC0wLjItMjUuOC0wLjdsMCwwYzguMywwLjUsMTYuOCwwLjgsMjUuNSwwLjhsMCwwYzgyLjUsMCwxNDkuNS0yNS4yLDE0OS41LTU1LjhsMCwwYzAtMS4yLTAuMS0yLjMtMC4zLTMuNWwwLDAKCUMyOTkuNCw1My43LDI5OS40LDU0LjcsMjk5LjQsNTUuNiIvPgo8bGluZWFyR3JhZGllbnQgaWQ9InBhdGg0MTgwXzFfIiBncmFkaWVudFVuaXRzPSJ1c2VyU3BhY2VPblVzZSIgeDE9Ii04MDQuODEzOCIgeTE9IjYwNC4wMjI5IiB4Mj0iLTgwMy44MTM4IiB5Mj0iNjA0LjAyMjkiIGdyYWRpZW50VHJhbnNmb3JtPSJtYXRyaXgoMCAxMTQuOTA5NSAxMTQuOTA5NSAwIC02OTI1Ny45Njg4IDkyNDc5LjM5MDYpIj4KCTxzdG9wICBvZmZzZXQ9IjAiIHN0eWxlPSJzdG9wLWNvbG9yOiNGRkZGRkYiLz4KCTxzdG9wICBvZmZzZXQ9IjAuNTUyMiIgc3R5bGU9InN0b3AtY29sb3I6I0ZGRkZGRiIvPgoJPHN0b3AgIG9mZnNldD0iMC42OTEiIHN0eWxlPSJzdG9wLWNvbG9yOiNGQUZBRkEiLz4KCTxzdG9wICBvZmZzZXQ9IjAuOCIgc3R5bGU9InN0b3AtY29sb3I6I0QzRDJEMiIvPgoJPHN0b3AgIG9mZnNldD0iMSIgc3R5bGU9InN0b3AtY29sb3I6I0JEQkNCQyIvPgo8L2xpbmVhckdyYWRpZW50Pgo8cGF0aCBpZD0icGF0aDQxODAiIGNsYXNzPSJzdDI4IiBkPSJNOC40LDU2LjJjMCwyNy4yLDYzLjQsNDkuMywxNDEuNSw0OS4zbDAsMGM3OC4yLDAsMTQxLjUtMjIuMSwxNDEuNS00OS4zbDAsMAoJQzI5MS41LDI5LDIyOC4yLDcsMTUwLDdsMCwwQzcxLjgsNyw4LjQsMjksOC40LDU2LjIgTTEzLjQsNTYuMmMwLTI0LjksNjEuMS00NSwxMzYuNi00NWwwLDBjNzUuNCwwLDEzNi42LDIwLjEsMTM2LjYsNDVsMCwwCgljMCwyNC45LTYxLjEsNDUtMTM2LjYsNDVsMCwwQzc0LjYsMTAxLjIsMTMuNCw4MS4xLDEzLjQsNTYuMiIvPgo8bGluZWFyR3JhZGllbnQgaWQ9InBhdGg0MjA2XzFfIiBncmFkaWVudFVuaXRzPSJ1c2VyU3BhY2VPblVzZSIgeDE9Ii04MDAuNTU5MyIgeTE9IjYxMS4xNjA3IiB4Mj0iLTc5OS41NTkzIiB5Mj0iNjExLjE2MDciIGdyYWRpZW50VHJhbnNmb3JtPSJtYXRyaXgoMCA1Ni45ODgxIDU2Ljk4ODEgMCAtMzQ2NTUuMzgyOCA0NTY1Ny43NDYxKSI+Cgk8c3RvcCAgb2Zmc2V0PSIwIiBzdHlsZT0ic3RvcC1jb2xvcjojRkZGRkZGIi8+Cgk8c3RvcCAgb2Zmc2V0PSIwLjU1MjIiIHN0eWxlPSJzdG9wLWNvbG9yOiNGRkZGRkYiLz4KCTxzdG9wICBvZmZzZXQ9IjAuNjkxIiBzdHlsZT0ic3RvcC1jb2xvcjojRUZFRUVFIi8+Cgk8c3RvcCAgb2Zmc2V0PSIwLjgiIHN0eWxlPSJzdG9wLWNvbG9yOiNFOUU5RTkiLz4KCTxzdG9wICBvZmZzZXQ9IjEiIHN0eWxlPSJzdG9wLWNvbG9yOiNEM0QyRDIiLz4KPC9saW5lYXJHcmFkaWVudD4KPHBhdGggaWQ9InBhdGg0MjA2IiBjbGFzcz0ic3QyOSIgZD0iTTIzMC4xLDM5LjVjLTAuNiwwLTAuOCwwLjEtMS4xLDAuNmwwLDBjLTAuOSwxLjctMTEuNSwxNy41LTEzLjQsMjAuNmwwLDAKCWMtMC4zLDAuNS0wLjcsMC40LTAuOC0wLjFsMCwwYy0wLjItMS44LTEuOC0zLjktNC4zLTQuOWwwLDBjLTEuOS0wLjgtMy44LTAuOS01LjctMC43bDAsMGMtMy41LDAuNS02LjYsMi4zLTkuMyw0LjRsMCwwCgljLTQuMSwzLjEtNy43LDcuMi0xMi4yLDEwLjJsMCwwYy0yLjUsMS42LTUuOSwzLjEtOC4yLDAuOWwwLDBjLTIuMS0xLjktMS44LTYuMiwxLjMtOS41bDAsMGMwLjMtMC4zLDAuNy0wLjEsMC43LDAuM2wwLDAKCWMtMC4zLDEuNSwwLjEsMywxLjIsNGwwLDBjMS40LDEuMiwzLjQsMS40LDUuMSwwLjZsMCwwYzItMSwzLjItMi45LDMuNS01LjFsMCwwYzAuNS0zLjQtMi4xLTYuMy01LjMtNi42bDAsMAoJYy0yLjYtMC4yLTUuMiwwLjctNy42LDIuOGwwLDBjLTEuMiwxLTEuOSwxLjgtMywzLjNsMCwwYy0wLjMsMC40LTAuNywwLjQtMC42LTAuMWwwLDBjMC4xLTQuMy0xLjctNi43LTUuMi02LjhsMCwwCgljLTIuOC0wLjEtNS43LDEuNC04LDMuM2wwLDBjLTIuNSwyLTQuNyw0LjctNy4xLDcuMmwwLDBjLTAuMywwLjMtMC42LDAuMy0wLjYtMC4zbDAsMGMtMC4xLTIuOS0wLjgtNS42LTIuMS03LjZsMCwwCgljLTAuNS0wLjctMS41LTEtMi4zLTAuNmwwLDBjLTAuNCwwLjItMS43LDAuOC0yLjcsMS42bDAsMGMtMC41LDAuNC0wLjcsMS0wLjUsMS43bDAsMGMxLjMsNC4zLDEsOS4xLTAuNywxMy4ybDAsMAoJYy0xLjYsMy44LTQuNyw3LjEtOC4zLDguM2wwLDBjLTIuNCwwLjgtNC45LDAuNC02LjQtMS43bDAsMGMtMi4xLTIuOS0xLjMtOCwxLjktMTIuM2wwLDBjMi44LTMuNyw2LjgtNi4xLDEwLjgtNy42bDAsMAoJYzAuNS0wLjIsMC42LTAuNSwwLjQtMC45bDAsMGMtMC4yLTAuNy0wLjYtMS42LTAuNy0ybDAsMGMtMC40LTEtMS40LTEuMS0yLjctMWwwLDBjLTIuOSwwLjMtNS41LDEuMy04LjIsMi43bDAsMAoJYy02LjgsMy42LTEwLjIsMTAuNy0xMS43LDE0LjVsMCwwYy0wLjcsMS44LTEuMywyLjktMi4xLDMuOWwwLDBjLTEuMSwxLjQtMi40LDIuNi00LjksNC43bDAsMGMtMC4yLDAuMi0wLjQsMC42LTAuMiwxbDAsMAoJYzAuMywwLjUsMS41LDIuMywxLjksMi41bDAsMGMwLjQsMC4yLDAuOS0wLjEsMS4xLTAuMmwwLDBjMS43LTEuMiwzLjgtMyw0LjgtNC4zbDAsMGMwLjMtMC40LDAuNy0wLjIsMC45LDAuNGwwLDAKCWMwLjksMy40LDMuNCw2LjEsNi44LDcuM2wwLDBjNi4yLDIuMSwxMi43LTAuOSwxNy42LTYuMmwwLDBjMy4xLTMuNCw0LjItNS41LDUuNC03bDAsMGMyLTIuNSw2LTguMSwxMC43LTExLjdsMCwwCgljMS43LTEuMywzLjgtMi4zLDQuOC0xLjdsMCwwYzAuOCwwLjUsMS4xLDEuOC0wLjIsNC4ybDAsMGMtNC44LDguOC0xMS45LDE5LjItMTMuMiwyMS43bDAsMGMtMC4yLDAuNCwwLDAuOCwwLjQsMC44bDAsMAoJYzIuNSwwLDUsMCw3LjMsMGwwLDBjMC40LDAsMC42LTAuMiwwLjctMC41bDAsMGMzLjctNS44LDcuMi0xMS4zLDEwLjktMTdsMCwwYzAuMi0wLjMsMC40LTAuMSwwLjQsMC4xbDAsMGMwLjEsMS4zLDAuNCwzLjEsMS4yLDQuMwoJbDAsMGMxLjQsMi4yLDMuNCwzLjEsNS42LDMuMmwwLDBjMS44LDAsMi43LTAuMiw0LjYtMWwwLDBjMS42LTAuNiwyLjgtMS4zLDMuOC0ybDAsMGMwLjYtMC40LDAuNywwLjMsMC42LDAuNGwwLDAKCWMtMC45LDQuNiwwLjIsMTAuMSw0LjgsMTIuM2wwLDBjNS41LDIuNywxMS41LTEuMSwxNS00LjVsMCwwYzAuMy0wLjMsMC43LTAuMywwLjcsMC40bDAsMGMwLjEsMS4zLDAuNywyLjksMS43LDRsMCwwCgljMi45LDIuOSw4LjgsMS44LDE0LjYtMi44bDAsMGMzLjgtMi45LDcuNy03LDExLjMtMTEuNGwwLDBjMC4xLTAuMiwwLjItMC40LDAtMC43bDAsMGMtMC41LTAuNi0xLjMtMS4yLTEuOS0xLjdsMCwwCgljLTAuMi0wLjItMC42LTAuMS0wLjgsMGwwLDBjLTMuNywzLjUtNi45LDcuNC0xMS43LDEwLjdsMCwwYy0xLjYsMS4xLTQuMiwyLTUuMywwLjVsMCwwYy0wLjQtMC42LTAuNC0xLjQsMC0yLjVsMCwwCgljMS40LTMuNSwyMy40LTM2LjksMjQuNS0zOC45bDAsMGMwLjItMC4zLDAtMC42LTAuNC0wLjZsMCwwQzIzNS40LDM5LjUsMjMyLjQsMzkuNSwyMzAuMSwzOS41IE0xOTUuMyw4MC42CgljLTEuMS0wLjYtMS42LTIuMi0xLjYtMy40bDAsMGMwLjEtMy42LDEuNy03LjMsNC42LTEwLjlsMCwwYzMuNi00LjQsNy42LTYuNywxMC4yLTUuNWwwLDBjMi43LDEuMywxLjgsNC40LDAuNiw2LjlsMCwwCgljLTAuMSwwLjItMC4xLDAuNCwwLDAuNWwwLDBjMCwwLjMsMC40LDAuNSwwLjcsMC42bDAsMGMwLjEsMCwwLjIsMC4xLDAuMSwwLjRsMCwwYy0wLjksMi0xLjgsMy4yLTMsNC45bDAsMAoJYy0xLjEsMS42LTIuMywyLjktMy44LDQuMWwwLDBjLTEuNywxLjQtMy45LDIuOS02LDIuOWwwLDBDMTk2LjUsODEuMSwxOTUuOCw4MC45LDE5NS4zLDgwLjYiLz4KPGxpbmVhckdyYWRpZW50IGlkPSJwYXRoNDIzMl8xXyIgZ3JhZGllbnRVbml0cz0idXNlclNwYWNlT25Vc2UiIHgxPSItODAyLjkxNTIiIHkxPSI2MDcuMjA4MyIgeDI9Ii04MDEuOTE1MiIgeTI9IjYwNy4yMDgzIiBncmFkaWVudFRyYW5zZm9ybT0ibWF0cml4KDAgNzkuMDUyOSA3OS4wNTI5IDAgLTQ3ODczLjQyNTggNjM0ODYuNDg4MykiPgoJPHN0b3AgIG9mZnNldD0iMCIgc3R5bGU9InN0b3AtY29sb3I6I0ZGRkZGRiIvPgoJPHN0b3AgIG9mZnNldD0iMC41NTIyIiBzdHlsZT0ic3RvcC1jb2xvcjojRkZGRkZGIi8+Cgk8c3RvcCAgb2Zmc2V0PSIwLjY5MSIgc3R5bGU9InN0b3AtY29sb3I6I0VGRUVFRSIvPgoJPHN0b3AgIG9mZnNldD0iMC44IiBzdHlsZT0ic3RvcC1jb2xvcjojRTlFOUU5Ii8+Cgk8c3RvcCAgb2Zmc2V0PSIxIiBzdHlsZT0ic3RvcC1jb2xvcjojRDNEMkQyIi8+CjwvbGluZWFyR3JhZGllbnQ+CjxwYXRoIGlkPSJwYXRoNDIzMiIgY2xhc3M9InN0MzAiIGQ9Ik0xMTMuMywxOS4yYy0yLjEsMC00LjIsMC4xLTYuMywwLjNsMCwwYy0xMy41LDEuMS0yNi4zLDguNy0yNi40LDIwLjNsMCwwCgljMCw1LjksNC4yLDEwLjYsMTAuNiwxMC40bDAsMGM3LjYtMC4zLDEzLjgtNi4zLDE3LjEtMTRsMCwwYzEuMi0yLjktMS4xLTQuMS0yLjEtMi40bDAsMGMtMS45LDMtNC43LDUuMy03LjYsNi44bDAsMAoJYy0zLjYsMS43LTcuNCwxLjMtOC41LTEuNmwwLDBjLTEuNi00LjEsMS44LTEwLjIsOS41LTEzLjFsMCwwYzExLjEtNC4xLDIyLjgtMS40LDM0LDAuN2wwLDBjMC4yLDAsMC44LDAuMywwLjIsMC42bDAsMAoJYy0yLDEuMS00LDItNy4xLDQuNmwwLDBjLTIuMiwxLjktNS4xLDQuNC03LjMsNy4xbDAsMGMtMi4yLDIuNy0zLjgsNS4xLTUuOSw3LjhsMCwwYy0wLjMsMC40LTAuNiwwLjQtMC42LDAuNGwwLDAKCWMtNS4xLDAuOS0xMCwxLjQtMTQuNiw0LjZsMCwwYy0wLjksMC42LTEuMywxLjgtMC44LDIuN2wwLDBjMC41LDAuOCwxLjcsMC45LDIuNSwwLjNsMCwwYzIuOC0yLjEsNS43LTMuMSw5LjEtMy4ybDAsMAoJYzAuMSwwLDAuMiwwLDAuMywwLjFsMCwwYzAsMC4xLDAsMC4yLDAsMC4ybDAsMGMtNSw2LjktNi4yLDguNS0xMCwxMi44bDAsMGMtMS45LDIuMi0zLjgsNC4xLTUuOSw2bDAsMGMtOC41LDcuOS0xNy43LDcuOC0yMSwyLjgKCWwwLDBjLTItMy0xLjctNi4xLTAuNC04LjdsMCwwYzEuNi0zLjIsNC44LTUuNSw3LjUtNi45bDAsMGMxLTAuNSwxLjMtMS44LDAuMy0yLjlsMCwwYy0wLjYtMC44LTIuMi0wLjktMy4zLTAuN2wwLDAKCWMtMy41LDAuNi03LjYsMy4zLTEwLjEsNi41bDAsMGMtMi43LDMuNi00LjEsNy45LTMuNywxMi43bDAsMGMwLjgsOC44LDgsMTMuOCwxNi4yLDEzLjhsMCwwYzYuNS0wLjEsMTIuNy0yLDIwLTkuNWwwLDAKCWM2LjktNywxMy4yLTE3LjQsMTktMjcuMWwwLDBjMC4yLTAuMywwLjMtMC41LDEuMi0wLjZsMCwwYzMuNy0wLjUsOS4xLTEsMTIuNi0xLjJsMCwwYzAuOCwwLDAuOSwwLDEuMiwwLjRsMCwwCgljMC45LDEuMSwyLjMsMi4xLDMuNCwyLjdsMCwwYzAuNSwwLjMsMC44LDAuNCwxLjIsMC40bDAsMGMwLjUsMCwwLjktMC4zLDEuMi0wLjZsMCwwYzAuNC0wLjQsMC41LTAuOSwwLjMtMS4zbDAsMAoJYy0wLjItMC40LTIuNi0xLjctMi43LTIuMmwwLDBjLTAuMS0wLjMsMC4zLTAuNCwwLjMtMC40bDAsMGMxLjgtMC42LDMuNi0xLjcsNC44LTMuOWwwLDBjMS4xLTIuMSwxLjMtNS0wLjctNi41bDAsMAoJYy0xLjgtMS40LTQuNS0xLjItNi42LDAuOGwwLDBjLTIuMSwxLjktMi44LDQuNi0yLjUsN2wwLDBjMCwwLjQsMCwwLjYtMC41LDAuNmwwLDBjLTMuMiwwLjMtNi4zLDAuMy05LjgsMC41bDAsMAoJYy0wLjIsMC0wLjMtMC4xLTAuMi0wLjNsMCwwYzQtNi45LDkuOS0xMS44LDE2LjUtMTYuN2wwLDBjMC40LTAuMywwLjMtMC45LDAuMy0xLjVsMCwwYzExLjksMi42LDIzLjMsNy40LDM1LjYsNy4zbDAsMAoJYzUuMSwwLDEwLTAuOCwxNC42LTMuNGwwLDBjNC4xLTIuMiw1LjgtNC4zLDUuOS02LjRsMCwwYzAuMS0xLjUtMC45LTIuNC0yLjQtMi4xbDAsMGMtMTIuNCwyLjktMjQuMywyLjgtMzYuNywxLjNsMCwwCglDMTQwLjgsMjIuNywxMjcuMywxOS4yLDExMy4zLDE5LjJMMTEzLjMsMTkuMkMxMTMuMywxOS4yLDExMy4zLDE5LjIsMTEzLjMsMTkuMiBNMTM0LjcsNDQuMWMtMC4yLTEuMywwLjItMy4xLDEuNy00LjNsMCwwCgljMC43LTAuNiwxLjctMC44LDIuMi0wLjNsMCwwYzAuNywwLjYsMC4zLDItMC4zLDIuOWwwLDBjLTAuNywxLjEtMiwyLTMuMSwyLjJsMCwwYzAsMC0wLjEsMC0wLjEsMGwwLDAKCUMxMzUsNDQuNywxMzQuOCw0NC42LDEzNC43LDQ0LjEiLz4KPC9zdmc+Cg=="
_LOGO_CHEVROLET_B64 = "PD94bWwgdmVyc2lvbj0iMS4wIj8+Cjxzdmcgd2lkdGg9IjQxMTUiIGhlaWdodD0iMjE1NiIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIiB4bWxuczpzdmc9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIiBjbGlwLXJ1bGU9ImV2ZW5vZGQiIGZpbGwtcnVsZT0iZXZlbm9kZCIgdmVyc2lvbj0iMS4xIj4KIDxnIGNsYXNzPSJsYXllciI+CiAgPHRpdGxlPkxheWVyIDE8L3RpdGxlPgogIDxnIGlkPSJzdmdfMSI+CiAgIDxwYXRoIGQ9Im0xNDMwLjc3LDAuMTZjMCwxNzguMzMgMCwzNTYuNjcgMCw1MzVjLTIwLjMzLDAgLTQwLjY3LDAgLTYxLDBjMCwtMTc3LjY3IDAsLTM1NS4zMyAwLC01MzNjMi41OCwtMC43MyA1LjI1LC0xLjIzIDgsLTEuNWMxNy42NiwtMC41IDM1LjMzLC0wLjY3IDUzLC0wLjV6IiBmaWxsPSIjYWFhYmFjIiBpZD0ic3ZnXzIiLz4KICA8L2c+CiAgPGcgaWQ9InN2Z18zIj4KICAgPHBhdGggZD0ibTE0MzAuNzcsMC4xNmMxMS4zMywwIDIyLjY3LDAgMzQsMGMwLDE3OC4zMyAwLDM1Ni42NyAwLDUzNWMtMTEuMzMsMCAtMjIuNjcsMCAtMzQsMGMwLC0xNzguMzMgMCwtMzU2LjY3IDAsLTUzNXoiIGZpbGw9IiNhZGFlYjAiIGlkPSJzdmdfNCIvPgogIDwvZz4KICA8ZyBpZD0ic3ZnXzUiPgogICA8cGF0aCBkPSJtMTQ2NC43NywwLjE2YzE3LDAgMzQsMCA1MSwwYzAsMTc4IDAsMzU2IDAsNTM0Yy0xNi45NywwLjk0IC0zMy45NywxLjI4IC01MSwxYzAsLTE3OC4zMyAwLC0zNTYuNjcgMCwtNTM1eiIgZmlsbD0iI2IwYjFiMyIgaWQ9InN2Z182Ii8+CiAgPC9nPgogIDxnIGlkPSJzdmdfNyI+CiAgIDxwYXRoIGQ9Im0xNTE1Ljc3LDAuMTZjOC42NywwIDE3LjMzLDAgMjYsMGMwLDE3MiAwLDM0NCAwLDUxNmMwLDAuNjcgMCwxLjMzIDAsMmMtMy4wMiw0LjAyIC02LjY4LDcuMzUgLTExLDEwYy00LjUyLDMuMTcgLTkuNTIsNS4xNyAtMTUsNmMwLC0xNzggMCwtMzU2IDAsLTUzNHoiIGZpbGw9IiNiM2I0YjYiIGlkPSJzdmdfOCIvPgogIDwvZz4KICA8ZyBpZD0ic3ZnXzkiPgogICA8cGF0aCBkPSJtMTU0MS43NywwLjE2YzEyLjY3LDAgMjUuMzMsMCAzOCwwYzAsNzguMzMgMCwxNTYuNjcgMCwyMzVjLTE5LjM2LDYuMDYgLTI5LjM2LDE5LjM5IC0zMCw0MGMtMC44Myw3My44MyAtMS4zMywxNDcuODMgLTEuNSwyMjJjLTAuMjQsNy4xIC0yLjQxLDEzLjQ0IC02LjUsMTljMCwtMTcyIDAsLTM0NCAwLC01MTZ6IiBmaWxsPSIjYjViNmI5IiBpZD0ic3ZnXzEwIi8+CiAgPC9nPgogIDxnIGlkPSJzdmdfMTEiPgogICA8cGF0aCBkPSJtMTU3OS43NywwLjE2YzExLDAgMjIsMCAzMywwYzAsNzcuNjcgMCwxNTUuMzMgMCwyMzNjLTYuNTIsLTAuMzIgLTEyLjg2LDAuMDEgLTE5LDFjLTQuNjUsMC41IC05LjMyLDAuODMgLTE0LDFjMCwtNzguMzMgMCwtMTU2LjY3IDAsLTIzNXoiIGZpbGw9IiNiOGI5YmQiIGlkPSJzdmdfMTIiLz4KICA8L2c+CiAgPGcgaWQ9InN2Z18xMyI+CiAgIDxwYXRoIGQ9Im0xNjEyLjc3LDAuMTZjOSwwIDE4LDAgMjcsMGMwLDc3LjY3IDAsMTU1LjMzIDAsMjMzYy05LDAgLTE4LDAgLTI3LDBjMCwtNzcuNjcgMCwtMTU1LjMzIDAsLTIzM3oiIGZpbGw9IiNiYWJjYzAiIGlkPSJzdmdfMTQiLz4KICA8L2c+CiAgPGcgaWQ9InN2Z18xNSI+CiAgIDxwYXRoIGQ9Im0xNjM5Ljc3LDAuMTZjMTMsMCAyNiwwIDM5LDBjMCw3Ny42NyAwLDE1NS4zMyAwLDIzM2MtMTMsMCAtMjYsMCAtMzksMGMwLC03Ny42NyAwLC0xNTUuMzMgMCwtMjMzeiIgZmlsbD0iI2JkYmZjMyIgaWQ9InN2Z18xNiIvPgogIDwvZz4KICA8ZyBpZD0ic3ZnXzE3Ij4KICAgPHBhdGggZD0ibTE2NzguNzcsMC4xNmM4LjMzLDAgMTYuNjcsMCAyNSwwYzAsNzcuNjcgMCwxNTUuMzMgMCwyMzNjLTguMzMsMCAtMTYuNjcsMCAtMjUsMGMwLC03Ny42NyAwLC0xNTUuMzMgMCwtMjMzeiIgZmlsbD0iI2MwYzJjNiIgaWQ9InN2Z18xOCIvPgogIDwvZz4KICA8ZyBpZD0ic3ZnXzE5Ij4KICAgPHBhdGggZD0ibTE3MDMuNzcsMC4xNmMxMi4zMywwIDI0LjY3LDAgMzcsMGMwLDc3LjY3IDAsMTU1LjMzIDAsMjMzYy0xMi4zMywwIC0yNC42NywwIC0zNywwYzAsLTc3LjY3IDAsLTE1NS4zMyAwLC0yMzN6IiBmaWxsPSIjYzNjNWNhIiBpZD0ic3ZnXzIwIi8+CiAgPC9nPgogIDxnIGlkPSJzdmdfMjEiPgogICA8cGF0aCBkPSJtMTc0MC43NywwLjE2YzksMCAxOCwwIDI3LDBjMCw3Ny42NyAwLDE1NS4zMyAwLDIzM2MtOSwwIC0xOCwwIC0yNywwYzAsLTc3LjY3IDAsLTE1NS4zMyAwLC0yMzN6IiBmaWxsPSIjYzZjOGNkIiBpZD0ic3ZnXzIyIi8+CiAgPC9nPgogIDxnIGlkPSJzdmdfMjMiPgogICA8cGF0aCBkPSJtMTc2Ny43NywwLjE2YzEzLjY3LDAgMjcuMzMsMCA0MSwwYzAsNzcuNjcgMCwxNTUuMzMgMCwyMzNjLTEzLjY3LDAgLTI3LjMzLDAgLTQxLDBjMCwtNzcuNjcgMCwtMTU1LjMzIDAsLTIzM3oiIGZpbGw9IiNjOWNjZDEiIGlkPSJzdmdfMjQiLz4KICA8L2c+CiAgPGcgaWQ9InN2Z18yNSI+CiAgIDxwYXRoIGQ9Im0xODA4Ljc3LDAuMTZjMjgwLjY3LDAgNTYxLjMzLDAgODQyLDBjLTU1LjMzLDc3LjY3IC0xMTAuNjcsMTU1LjMzIC0xNjYsMjMzYy0yMjUuMzMsMCAtNDUwLjY3LDAgLTY3NiwwYzAsLTc3LjY3IDAsLTE1NS4zMyAwLC0yMzN6IiBmaWxsPSIjY2JjZmQ0IiBpZD0ic3ZnXzI2Ii8+CiAgPC9nPgogIDxnIGlkPSJzdmdfMjciPgogICA8cGF0aCBkPSJtMjY1MC43NywwLjE2YzIzLjMzLDAgNDYuNjcsMCA3MCwwYy01NS41OSw3OC45MyAtMTExLjU5LDE1Ny41OSAtMTY4LDIzNmMtNC42NywtMC43MiAtOS4zNCwtMS41NiAtMTQsLTIuNWMtMTgsLTAuNSAtMzYsLTAuNjcgLTU0LC0wLjVjNTUuMzMsLTc3LjY3IDExMC42NywtMTU1LjMzIDE2NiwtMjMzeiIgZmlsbD0iI2M5Y2NkMSIgaWQ9InN2Z18yOCIvPgogIDwvZz4KICA8ZyBpZD0ic3ZnXzI5Ij4KICAgPHBhdGggZD0ibTI3MjAuNzcsMC4xNmMxNC40MiwtMC40OSAyOC43NSwwLjE4IDQzLDJjLTYxLjMzLDg2LjMzIC0xMjIuNjcsMTcyLjY3IC0xODQsMjU5Yy00LjgyLC0xMi44MiAtMTMuODIsLTIxLjE1IC0yNywtMjVjNTYuNDEsLTc4LjQxIDExMi40MSwtMTU3LjA3IDE2OCwtMjM2eiIgZmlsbD0iI2M2YzhjZCIgaWQ9InN2Z18zMCIgb3BhY2l0eT0iMSIvPgogIDwvZz4KICA8ZyBpZD0ic3ZnXzMxIj4KICAgPHBhdGggZD0ibTI3NjMuNzcsMi4xNmMxNCwyLjkxIDI1LjgzLDkuNTggMzUuNSwyMGMyLjM2LDIuNzIgNC4xOSw1LjcyIDUuNSw5Yy03My42NCwxMDMuNjQgLTE0Ny42NCwyMDYuOTcgLTIyMiwzMTBjMC4zMywtMjEuNTEgMCwtNDIuODQgLTEsLTY0Yy0wLjY3LC01LjMzIC0xLjMzLC0xMC42NyAtMiwtMTZjNjEuMzMsLTg2LjMzIDEyMi42NywtMTcyLjY3IDE4NCwtMjU5eiIgZmlsbD0iI2MzYzVjYSIgaWQ9InN2Z18zMiIgb3BhY2l0eT0iMSIvPgogIDwvZz4KICA8ZyBpZD0ic3ZnXzMzIj4KICAgPHBhdGggZD0ibTEzNjkuNzcsMi4xNmMwLDE3Ny42NyAwLDM1NS4zMyAwLDUzM2MtNy4zMywwIC0xNC42NywwIC0yMiwwYzAsLTE3NSAwLC0zNTAgMCwtNTI1YzYuNzQsLTQuMDMgMTQuMDgsLTYuNyAyMiwtOHoiIGZpbGw9IiNhN2E4YTkiIGlkPSJzdmdfMzQiIG9wYWNpdHk9IjEiLz4KICA8L2c+CiAgPGcgaWQ9InN2Z18zNSI+CiAgIDxwYXRoIGQ9Im0xMzQ3Ljc3LDEwLjE2YzAsMTc1IDAsMzUwIDAsNTI1Yy0zMi4zMywwIC02NC42NywwIC05NywwYzAsLTc4IDAsLTE1NiAwLC0yMzRjOC4zNCwwLjE3IDE2LjY3LDAgMjUsLTAuNWMyMi4xNCwtMS44MSAzNC45NywtMTMuNjQgMzguNSwtMzUuNWMxLjE2LC02Ny45OSAxLjgzLC0xMzUuOTkgMiwtMjA0YzIuMjQsLTIyLjM0IDEyLjc0LC0zOS4zNCAzMS41LC01MXoiIGZpbGw9IiNhNWE1YTYiIGlkPSJzdmdfMzYiIG9wYWNpdHk9IjEiLz4KICA8L2c+CiAgPGcgaWQ9InN2Z18zNyI+CiAgIDxwYXRoIGQ9Im0yODA0Ljc3LDMxLjE2YzMuMzQsNC44MSA1Ljg0LDEwLjE1IDcuNSwxNmMyLjI1LDguMTkgMy40MiwxNi41MiAzLjUsMjVjLTc3LjY3LDEwOCAtMTU1LjMzLDIxNiAtMjMzLDMyNGMwLC0xOC4zMyAwLC0zNi42NyAwLC01NWM3NC4zNiwtMTAzLjAzIDE0OC4zNiwtMjA2LjM2IDIyMiwtMzEweiIgZmlsbD0iI2MwYzJjNiIgaWQ9InN2Z18zOCIgb3BhY2l0eT0iMSIvPgogIDwvZz4KICA8ZyBpZD0ic3ZnXzM5Ij4KICAgPHBhdGggZD0ibTI4MTUuNzcsNzIuMTZjMCwyOC4zMyAwLDU2LjY3IDAsODVjLTc3LjY0LDEwNy44MiAtMTU1LjE0LDIxNS44MiAtMjMyLjUsMzI0Yy0wLjUsLTI4LjMzIC0wLjY3LC01Ni42NiAtMC41LC04NWM3Ny42NywtMTA4IDE1NS4zMywtMjE2IDIzMywtMzI0eiIgZmlsbD0iI2JkYmZjMyIgaWQ9InN2Z180MCIvPgogIDwvZz4KICA8ZyBpZD0ic3ZnXzQxIj4KICAgPHBhdGggZD0ibTI4MTUuNzcsMTU3LjE2YzAsMTkgMCwzOCAwLDU3Yy03NC4wMiwxMDIuNyAtMTQ3LjY5LDIwNS43IC0yMjEsMzA5Yy01LjI3LC00Ljg1IC04Ljc3LC0xMC44NSAtMTAuNSwtMThjLTEuNDQsLTUuOTIgLTIuMjcsLTExLjkyIC0yLjUsLTE4YzAsLTcwIDAsLTE0MCAwLC0yMTBjMSwyMS4xNiAxLjMzLDQyLjQ5IDEsNjRjMCwxOC4zMyAwLDM2LjY3IDAsNTVjLTAuMTcsMjguMzQgMCw1Ni42NyAwLjUsODVjNzcuMzYsLTEwOC4xOCAxNTQuODYsLTIxNi4xOCAyMzIuNSwtMzI0eiIgZmlsbD0iI2JiYmNiZiIgaWQ9InN2Z180MiIvPgogIDwvZz4KICA8ZyBpZD0ic3ZnXzQzIj4KICAgPHBhdGggZD0ibTI4MTUuNzcsMjE0LjE2Yy0wLjE3LDE0IDAsMjggMC41LDQyYzAuMiw3LjUxIDEuMzcsMTQuODQgMy41LDIyYy02MS41Nyw4NS40NSAtMTIyLjksMTcxLjEyIC0xODQsMjU3Yy0xMi4zOCwxLjQ4IC0yNC4wNCwtMC42OSAtMzUsLTYuNWMtMi41LC0xLjMzIC00LjUsLTMuMTYgLTYsLTUuNWM3My4zMSwtMTAzLjMgMTQ2Ljk4LC0yMDYuMyAyMjEsLTMwOXoiIGZpbGw9IiNiOGJhYmQiIGlkPSJzdmdfNDQiLz4KICA8L2c+CiAgPGcgaWQ9InN2Z180NSI+CiAgIDxwYXRoIGQ9Im0xNTkzLjc3LDIzNC4xNmMxNTQuMzMsMCAzMDguNjcsMCA0NjMsMGMwLDg1LjMzIDAsMTcwLjY3IDAsMjU2YzAsMSAwLDIgMCwzYy0xNjksLTEuMTggLTMzOCwtMi4xOCAtNTA3LC0zYzAsLTcxLjY3IDAsLTE0My4zMyAwLC0yMTVjMC42NCwtMjAuNjEgMTAuNjQsLTMzLjk0IDMwLC00MGM0LjY4LC0wLjE3IDkuMzUsLTAuNSAxNCwtMXoiIGZpbGw9IiNjZGE1MzUiIGlkPSJzdmdfNDYiLz4KICA8L2c+CiAgPGcgaWQ9InN2Z180NyI+CiAgIDxwYXRoIGQ9Im0xNTkzLjc3LDIzNC4xNmM2LjE0LC0wLjk5IDEyLjQ4LC0xLjMyIDE5LC0xYzksMCAxOCwwIDI3LDBjMTMsMCAyNiwwIDM5LDBjOC4zMywwIDE2LjY3LDAgMjUsMGMxMi4zMywwIDI0LjY3LDAgMzcsMGM5LDAgMTgsMCAyNywwYzEzLjY3LDAgMjcuMzMsMCA0MSwwYzIyNS4zMywwIDQ1MC42NywwIDY3NiwwYzE4LC0wLjE3IDM2LDAgNTQsMC41YzQuNjYsMC45NCA5LjMzLDEuNzggMTQsMi41YzEzLjE4LDMuODUgMjIuMTgsMTIuMTggMjcsMjVjMC42Nyw1LjMzIDEuMzMsMTAuNjcgMiwxNmMwLDcwIDAsMTQwIDAsMjEwYy0xNzUsMC44OCAtMzUwLDEuODggLTUyNSwzYzAsLTg1LjMzIDAsLTE3MC42NyAwLC0yNTZjLTE1NC4zMywwIC0zMDguNjcsMCAtNDYzLDB6IiBmaWxsPSIjZDNiMzZiIiBpZD0ic3ZnXzQ4Ii8+CiAgPC9nPgogIDxnIGlkPSJzdmdfNDkiPgogICA8cGF0aCBkPSJtMjgxOS43NywyNzguMTZjNy4yNCwxNC44OCAxOS4yNCwyMi41NCAzNiwyM2MtNTUuNjcsNzggLTExMS4zMywxNTYgLTE2NywyMzRjLTE3LjY3LDAgLTM1LjMzLDAgLTUzLDBjNjEuMSwtODUuODggMTIyLjQzLC0xNzEuNTUgMTg0LC0yNTd6IiBmaWxsPSIjYjViNmI5IiBpZD0ic3ZnXzUwIiBvcGFjaXR5PSIxIi8+CiAgPC9nPgogIDxnIGlkPSJzdmdfNTEiPgogICA8cGF0aCBkPSJtNTAyLjc3LDMwMS4xNmMwLDExNC4zMyAwLDIyOC42NyAwLDM0M2MtMC42MSwwLjg5IC0wLjk0LDEuODkgLTEsM2MtNi45NCwxMi44NyAtMTMuNiwyNS44NyAtMjAsMzljLTMuODQsNi4zNSAtNy4xNywxMy4wMiAtMTAsMjBjLTQuMSw1Ljg2IC03LjQzLDEyLjE5IC0xMCwxOWMtMS45MywyLjg3IC0zLjYsNS44NyAtNSw5YzAsLTE0Mi42NyAwLC0yODUuMzMgMCwtNDI4YzE1LjA2LC0zLjcgMzAuMzksLTUuMzcgNDYsLTV6IiBmaWxsPSIjYzNjNWNhIiBpZD0ic3ZnXzUyIiBvcGFjaXR5PSIxIi8+CiAgPC9nPgogIDxnIGlkPSJzdmdfNTMiPgogICA8cGF0aCBkPSJtNTAyLjc3LDMwMS4xNmM5LjY3LDAgMTkuMzMsMCAyOSwwYzAsOTUgMCwxOTAgMCwyODVjLTIuMjgsNS4zMSAtNC42MiwxMC42NCAtNywxNmMtNC4xNyw3LjAyIC03Ljg0LDE0LjM1IC0xMSwyMmMtNC4xOSw2LjM4IC03Ljg1LDEzLjA0IC0xMSwyMGMwLC0xMTQuMzMgMCwtMjI4LjY3IDAsLTM0M3oiIGZpbGw9IiNjMGMyYzYiIGlkPSJzdmdfNTQiIG9wYWNpdHk9IjEiLz4KICA8L2c+CiAgPGcgaWQ9InN2Z181NSI+CiAgIDxwYXRoIGQ9Im01MzEuNzcsMzAxLjE2YzE1LjMzLDAgMzAuNjcsMCA0NiwwYzAsNzguMzMgMCwxNTYuNjcgMCwyMzVjLTE2LjE2LDIuODMgLTI3LjE2LDExLjgzIC0zMywyN2MtNC4wOCw3LjgzIC04LjQxLDE1LjUgLTEzLDIzYzAsLTk1IDAsLTE5MCAwLC0yODV6IiBmaWxsPSIjYmRiZmMzIiBpZD0ic3ZnXzU2IiBvcGFjaXR5PSIxIi8+CiAgPC9nPgogIDxnIGlkPSJzdmdfNTciPgogICA8cGF0aCBkPSJtNTc3Ljc3LDMwMS4xNmMxMCwwIDIwLDAgMzAsMGMwLDc4IDAsMTU2IDAsMjM0Yy0xMC4wMiwtMC4xMyAtMjAuMDIsMC4yIC0zMCwxYzAsLTc4LjMzIDAsLTE1Ni42NyAwLC0yMzV6IiBmaWxsPSIjYmFiY2MwIiBpZD0ic3ZnXzU4IiBvcGFjaXR5PSIxIi8+CiAgPC9nPgogIDxnIGlkPSJzdmdfNTkiPgogICA8cGF0aCBkPSJtNjA3Ljc3LDMwMS4xNmMxMi42NywwIDI1LjMzLDAgMzgsMGMwLDc4IDAsMTU2IDAsMjM0Yy0xMi42NywwIC0yNS4zMywwIC0zOCwwYzAsLTc4IDAsLTE1NiAwLC0yMzR6IiBmaWxsPSIjYjhiYWJkIiBpZD0ic3ZnXzYwIiBvcGFjaXR5PSIxIi8+CiAgPC9nPgogIDxnIGlkPSJzdmdfNjEiPgogICA8cGF0aCBkPSJtNjQ1Ljc3LDMwMS4xNmMxMywwIDI2LDAgMzksMGMwLDc4IDAsMTU2IDAsMjM0Yy0xMywwIC0yNiwwIC0zOSwwYzAsLTc4IDAsLTE1NiAwLC0yMzR6IiBmaWxsPSIjYjViNmI5IiBpZD0ic3ZnXzYyIiBvcGFjaXR5PSIxIi8+CiAgPC9nPgogIDxnIGlkPSJzdmdfNjMiPgogICA8cGF0aCBkPSJtNjg0Ljc3LDMwMS4xNmM5LjY3LDAgMTkuMzMsMCAyOSwwYzAsNzggMCwxNTYgMCwyMzRjLTkuNjcsMCAtMTkuMzMsMCAtMjksMGMwLC03OCAwLC0xNTYgMCwtMjM0eiIgZmlsbD0iI2IzYjRiNiIgaWQ9InN2Z182NCIgb3BhY2l0eT0iMSIvPgogIDwvZz4KICA8ZyBpZD0ic3ZnXzY1Ij4KICAgPHBhdGggZD0ibTcxMy43NywzMDEuMTZjMTYuMzMsMCAzMi42NywwIDQ5LDBjMCw3OCAwLDE1NiAwLDIzNGMtMTYuMzMsMCAtMzIuNjcsMCAtNDksMGMwLC03OCAwLC0xNTYgMCwtMjM0eiIgZmlsbD0iI2IwYjFiMyIgaWQ9InN2Z182NiIgb3BhY2l0eT0iMSIvPgogIDwvZz4KICA8ZyBpZD0ic3ZnXzY3Ij4KICAgPHBhdGggZD0ibTc2Mi43NywzMDEuMTZjMTEsMCAyMiwwIDMzLDBjMCw3OCAwLDE1NiAwLDIzNGMtMTEsMCAtMjIsMCAtMzMsMGMwLC03OCAwLC0xNTYgMCwtMjM0eiIgZmlsbD0iI2FkYWVhZiIgaWQ9InN2Z182OCIgb3BhY2l0eT0iMSIvPgogIDwvZz4KICA8ZyBpZD0ic3ZnXzY5Ij4KICAgPHBhdGggZD0ibTc5NS43NywzMDEuMTZjMTguMzMsMCAzNi42NywwIDU1LDBjMCw3OCAwLDE1NiAwLDIzNGMtMTguMzMsMCAtMzYuNjcsMCAtNTUsMGMwLC03OCAwLC0xNTYgMCwtMjM0eiIgZmlsbD0iI2FhYWJhYyIgaWQ9InN2Z183MCIgb3BhY2l0eT0iMSIvPgogIDwvZz4KICA8ZyBpZD0ic3ZnXzcxIj4KICAgPHBhdGggZD0ibTg1MC43NywzMDEuMTZjNiwwIDEyLDAgMTgsMGMwLDc4IDAsMTU2IDAsMjM0Yy02LDAgLTEyLDAgLTE4LDBjMCwtNzggMCwtMTU2IDAsLTIzNHoiIGZpbGw9IiNhN2E4YTkiIGlkPSJzdmdfNzIiIG9wYWNpdHk9IjEiLz4KICA8L2c+CiAgPGcgaWQ9InN2Z183MyI+CiAgIDxwYXRoIGQ9Im04NjguNzcsMzAxLjE2YzI2LjY3LDAgNTMuMzMsMCA4MCwwYzAsNzggMCwxNTYgMCwyMzRjLTI2LjY3LDAgLTUzLjMzLDAgLTgwLDBjMCwtNzggMCwtMTU2IDAsLTIzNHoiIGZpbGw9IiNhNGE1YTUiIGlkPSJzdmdfNzQiIG9wYWNpdHk9IjEiLz4KICA8L2c+CiAgPGcgaWQ9InN2Z183NSI+CiAgIDxwYXRoIGQ9Im05NDguNzcsMzAxLjE2YzI4LDAgNTYsMCA4NCwwYzAsNzggMCwxNTYgMCwyMzRjLTI4LDAgLTU2LDAgLTg0LDBjMCwtNzggMCwtMTU2IDAsLTIzNHoiIGZpbGw9IiM5ZjlmOWYiIGlkPSJzdmdfNzYiIG9wYWNpdHk9IjEiLz4KICA8L2c+CiAgPGcgaWQ9InN2Z183NyI+CiAgIDxwYXRoIGQ9Im0xMDMyLjc3LDMwMS4xNmMxNy4zMywwIDM0LjY3LDAgNTIsMGMwLDc4IDAsMTU2IDAsMjM0Yy0xNy4zMywwIC0zNC42NywwIC01MiwwYzAsLTc4IDAsLTE1NiAwLC0yMzR6IiBmaWxsPSIjOWM5ZDliIiBpZD0ic3ZnXzc4IiBvcGFjaXR5PSIxIi8+CiAgPC9nPgogIDxnIGlkPSJzdmdfNzkiPgogICA8cGF0aCBkPSJtMTA4NC43NywzMDEuMTZjNTIuNjcsMCAxMDUuMzMsMCAxNTgsMGMwLDc4IDAsMTU2IDAsMjM0Yy01Mi42NywwIC0xMDUuMzMsMCAtMTU4LDBjMCwtNzggMCwtMTU2IDAsLTIzNHoiIGZpbGw9IiM5ZjlmOWUiIGlkPSJzdmdfODAiIG9wYWNpdHk9IjEiLz4KICA8L2c+CiAgPGcgaWQ9InN2Z184MSI+CiAgIDxwYXRoIGQ9Im0xMjQyLjc3LDMwMS4xNmMyLjY3LDAgNS4zMywwIDgsMGMwLDc4IDAsMTU2IDAsMjM0Yy0yLjY3LDAgLTUuMzMsMCAtOCwwYzAsLTc4IDAsLTE1NiAwLC0yMzR6IiBmaWxsPSIjYTJhM2EyIiBpZD0ic3ZnXzgyIiBvcGFjaXR5PSIxIi8+CiAgPC9nPgogIDxnIGlkPSJzdmdfODMiPgogICA8cGF0aCBkPSJtMjg1NS43NywzMDEuMTZjMTIuNjcsMCAyNS4zMywwIDM4LDBjLTU1LjMzLDc4IC0xMTAuNjcsMTU2IC0xNjYsMjM0Yy0xMywwIC0yNiwwIC0zOSwwYzU1LjY3LC03OCAxMTEuMzMsLTE1NiAxNjcsLTIzNHoiIGZpbGw9IiNiM2I0YjYiIGlkPSJzdmdfODQiIG9wYWNpdHk9IjEiLz4KICA8L2c+CiAgPGcgaWQ9InN2Z184NSI+CiAgIDxwYXRoIGQ9Im0yODkzLjc3LDMwMS4xNmMyMi4zMywwIDQ0LjY3LDAgNjcsMGMtNTUuNjcsNzggLTExMS4zMywxNTYgLTE2NywyMzRjLTIyLDAgLTQ0LDAgLTY2LDBjNTUuMzMsLTc4IDExMC42NywtMTU2IDE2NiwtMjM0eiIgZmlsbD0iI2IwYjFiMyIgaWQ9InN2Z184NiIgb3BhY2l0eT0iMSIvPgogIDwvZz4KICA8ZyBpZD0ic3ZnXzg3Ij4KICAgPHBhdGggZD0ibTI5NjAuNzcsMzAxLjE2YzE0LjMzLDAgMjguNjcsMCA0MywwYy01NS42Nyw3OCAtMTExLjMzLDE1NiAtMTY3LDIzNGMtMTQuMzMsMCAtMjguNjcsMCAtNDMsMGM1NS42NywtNzggMTExLjMzLC0xNTYgMTY3LC0yMzR6IiBmaWxsPSIjYWRhZWFmIiBpZD0ic3ZnXzg4IiBvcGFjaXR5PSIxIi8+CiAgPC9nPgogIDxnIGlkPSJzdmdfODkiPgogICA8cGF0aCBkPSJtMzAwMy43NywzMDEuMTZjMjQuNjcsMCA0OS4zMywwIDc0LDBjLTU1LjY3LDc4IC0xMTEuMzMsMTU2IC0xNjcsMjM0Yy0yNC42NywwIC00OS4zMywwIC03NCwwYzU1LjY3LC03OCAxMTEuMzMsLTE1NiAxNjcsLTIzNHoiIGZpbGw9IiNhYWFiYWMiIGlkPSJzdmdfOTAiIG9wYWNpdHk9IjEiLz4KICA8L2c+CiAgPGcgaWQ9InN2Z185MSI+CiAgIDxwYXRoIGQ9Im0zMDc3Ljc3LDMwMS4xNmM4LDAgMTYsMCAyNCwwYy01NS42Nyw3OCAtMTExLjMzLDE1NiAtMTY3LDIzNGMtOCwwIC0xNiwwIC0yNCwwYzU1LjY3LC03OCAxMTEuMzMsLTE1NiAxNjcsLTIzNHoiIGZpbGw9IiNhN2E4YTkiIGlkPSJzdmdfOTIiIG9wYWNpdHk9IjEiLz4KICA8L2c+CiAgPGcgaWQ9InN2Z185MyI+CiAgIDxwYXRoIGQ9Im0zMTAxLjc3LDMwMS4xNmMzNS42NywwIDcxLjMzLDAgMTA3LDBjLTU1LjY3LDc4IC0xMTEuMzMsMTU2IC0xNjcsMjM0Yy0zNS42NywwIC03MS4zMywwIC0xMDcsMGM1NS42NywtNzggMTExLjMzLC0xNTYgMTY3LC0yMzR6IiBmaWxsPSIjYTRhNWE1IiBpZD0ic3ZnXzk0IiBvcGFjaXR5PSIxIi8+CiAgPC9nPgogIDxnIGlkPSJzdmdfOTUiPgogICA8cGF0aCBkPSJtMzIwOC43NywzMDEuMTZjMzcuMzMsMCA3NC42NywwIDExMiwwYy01NS42Nyw3OCAtMTExLjMzLDE1NiAtMTY3LDIzNGMtMzcuMzMsMCAtNzQuNjcsMCAtMTEyLDBjNTUuNjcsLTc4IDExMS4zMywtMTU2IDE2NywtMjM0eiIgZmlsbD0iIzlmOWY5ZiIgaWQ9InN2Z185NiIgb3BhY2l0eT0iMSIvPgogIDwvZz4KICA8ZyBpZD0ic3ZnXzk3Ij4KICAgPHBhdGggZD0ibTMzMjAuNzcsMzAxLjE2YzIzLjMzLDAgNDYuNjcsMCA3MCwwYy01NS42Nyw3OCAtMTExLjMzLDE1NiAtMTY3LDIzNGMtMjMuMzMsMCAtNDYuNjcsMCAtNzAsMGM1NS42NywtNzggMTExLjMzLC0xNTYgMTY3LC0yMzR6IiBmaWxsPSIjOWM5ZDliIiBpZD0ic3ZnXzk4IiBvcGFjaXR5PSIxIi8+CiAgPC9nPgogIDxnIGlkPSJzdmdfOTkiPgogICA8cGF0aCBkPSJtMzM5MC43NywzMDEuMTZjNzAuNjcsMCAxNDEuMzMsMCAyMTIsMGMtMC42MywyLjU5IC0xLjgsNC45MiAtMy41LDdjLTU0LjM5LDc1LjU1IC0xMDguNTUsMTUxLjIxIC0xNjIuNSwyMjdjLTcxLDAgLTE0MiwwIC0yMTMsMGM1NS42NywtNzggMTExLjMzLC0xNTYgMTY3LC0yMzR6IiBmaWxsPSIjOWY5ZjllIiBpZD0ic3ZnXzEwMCIgb3BhY2l0eT0iMSIvPgogIDwvZz4KICA8ZyBpZD0ic3ZnXzEwMSI+CiAgIDxwYXRoIGQ9Im0zNjAyLjc3LDMwMS4xNmM0NywwIDk0LDAgMTQxLDBjLTU1LjY3LDc4IC0xMTEuMzMsMTU2IC0xNjcsMjM0Yy00Ni42NywwIC05My4zMywwIC0xNDAsMGM1My45NSwtNzUuNzkgMTA4LjExLC0xNTEuNDUgMTYyLjUsLTIyN2MxLjcsLTIuMDggMi44NywtNC40MSAzLjUsLTd6IiBmaWxsPSIjYTRhNWE1IiBpZD0ic3ZnXzEwMiIgb3BhY2l0eT0iMSIvPgogIDwvZz4KICA8ZyBpZD0ic3ZnXzEwMyI+CiAgIDxwYXRoIGQ9Im0zNzQzLjc3LDMwMS4xNmM5LjY3LDAgMTkuMzMsMCAyOSwwYy01NS4xNyw3OC4zMiAtMTEwLjgzLDE1Ni4zMiAtMTY3LDIzNGMtOS42NywwIC0xOS4zMywwIC0yOSwwYzU1LjY3LC03OCAxMTEuMzMsLTE1NiAxNjcsLTIzNHoiIGZpbGw9IiNhN2E4YTkiIGlkPSJzdmdfMTA0IiBvcGFjaXR5PSIxIi8+CiAgPC9nPgogIDxnIGlkPSJzdmdfMTA1Ij4KICAgPHBhdGggZD0ibTM3NzIuNzcsMzAxLjE2YzI3LDAgNTQsMCA4MSwwYy0wLjYzLDIuNTkgLTEuOCw0LjkyIC0zLjUsN2MtNTQuMzksNzUuNTUgLTEwOC41NSwxNTEuMjEgLTE2Mi41LDIyN2MtMjcuMzMsMCAtNTQuNjcsMCAtODIsMGM1Ni4xNywtNzcuNjggMTExLjgzLC0xNTUuNjggMTY3LC0yMzR6IiBmaWxsPSIjYWFhYmFjIiBpZD0ic3ZnXzEwNiIgb3BhY2l0eT0iMSIvPgogIDwvZz4KICA8ZyBpZD0ic3ZnXzEwNyI+CiAgIDxwYXRoIGQ9Im0zODUzLjc3LDMwMS4xNmMxNS4zMywwIDMwLjY3LDAgNDYsMGMtMC4yMSwxLjQyIC0wLjcxLDIuNzYgLTEuNSw0Yy01Ni44LDc4LjI4IC0xMTIuOTcsMTU2Ljk1IC0xNjguNSwyMzZjLTUuNTQsLTMuMDYgLTExLjU0LC00Ljg5IC0xOCwtNS41Yy03Ljk5LC0wLjUgLTE1Ljk5LC0wLjY3IC0yNCwtMC41YzUzLjk1LC03NS43OSAxMDguMTEsLTE1MS40NSAxNjIuNSwtMjI3YzEuNywtMi4wOCAyLjg3LC00LjQxIDMuNSwtN3oiIGZpbGw9IiNhZGFlYWYiIGlkPSJzdmdfMTA4IiBvcGFjaXR5PSIxIi8+CiAgPC9nPgogIDxnIGlkPSJzdmdfMTA5Ij4KICAgPHBhdGggZD0ibTM4OTkuNzcsMzAxLjE2YzIyLjY3LDAgNDUuMzMsMCA2OCwwYy04Mi40OSwxMTUuNjQgLTE2NC45OSwyMzEuMyAtMjQ3LjUsMzQ3Yy0xLjMxLDEuNjkgLTIuODEsMy4wMyAtNC41LDRjMS4yNywtMi4yMSAyLjI3LC00LjU1IDMsLTdjMTAuMzEsLTE4LjYyIDIwLjE1LC0zNy42MiAyOS41LC01N2MxLjE5LC02LjI4IDEuNjksLTEyLjYxIDEuNSwtMTljLTIuMjYsLTEyLjU0IC04LjkzLC0yMS44NyAtMjAsLTI4YzU1LjUzLC03OS4wNSAxMTEuNywtMTU3LjcyIDE2OC41LC0yMzZjMC43OSwtMS4yNCAxLjI5LC0yLjU4IDEuNSwtNHoiIGZpbGw9IiNiMGIxYjMiIGlkPSJzdmdfMTEwIiBvcGFjaXR5PSIxIi8+CiAgPC9nPgogIDxnIGlkPSJzdmdfMTExIj4KICAgPHBhdGggZD0ibTM5NjcuNzcsMzAxLjE2YzExLjY3LDAgMjMuMzMsMCAzNSwwYy0wLjYzLDIuNTkgLTEuOCw0LjkyIC0zLjUsN2MtMTIyLjA1LDE2OS43MiAtMjQzLjcyLDMzOS43MiAtMzY1LDUxMGMtMi4wNSwzLjIxIC00LjU1LDUuODggLTcuNSw4YzUuMDYsLTEwLjA0IDEwLjA2LC0yMC4wNCAxNSwtMzBjMTMuMTYsLTI0LjMyIDI1LjgzLC00OC45OSAzOCwtNzRjNS41MSwtOS42OCAxMC41MSwtMTkuNjggMTUsLTMwYzcuNDksLTEyLjk4IDE0LjQ5LC0yNi4zMiAyMSwtNDBjMS42OSwtMC45NyAzLjE5LC0yLjMxIDQuNSwtNGM4Mi41MSwtMTE1LjcgMTY1LjAxLC0yMzEuMzYgMjQ3LjUsLTM0N3oiIGZpbGw9IiNiM2I0YjYiIGlkPSJzdmdfMTEyIiBvcGFjaXR5PSIxIi8+CiAgPC9nPgogIDxnIGlkPSJzdmdfMTEzIj4KICAgPHBhdGggZD0ibTQwMDIuNzcsMzAxLjE2YzguNjcsMCAxNy4zMywwIDI2LDBjLTIxMy41OSwyOTkuNTkgLTQyNy41OSw1OTguOTMgLTY0Miw4OThjLTguMzMsMCAtMTYuNjcsMCAtMjUsMGM1NS42NywtNzggMTExLjMzLC0xNTYgMTY3LC0yMzRjMTYuMzEsMC4yNyAyOC44MSwtNi40IDM3LjUsLTIwYzkuODYsLTE5LjcyIDE5LjY5LC0zOS4zOSAyOS41LC01OWMxMC44MywtMTkuNjUgMjEuMTYsLTM5LjY1IDMxLC02MGMyLjk1LC0yLjEyIDUuNDUsLTQuNzkgNy41LC04YzEyMS4yOCwtMTcwLjI4IDI0Mi45NSwtMzQwLjI4IDM2NSwtNTEwYzEuNywtMi4wOCAyLjg3LC00LjQxIDMuNSwtN3oiIGZpbGw9IiNiNGI2YjgiIGlkPSJzdmdfMTE0IiBvcGFjaXR5PSIxIi8+CiAgPC9nPgogIDxnIGlkPSJzdmdfMTE1Ij4KICAgPHBhdGggZD0ibTQwMjguNzcsMzAxLjE2YzguMzYsLTAuMTIgMTYuNjksMC4yMSAyNSwxYy0yMTMuOTIsMjk4Ljg1IC00MjcuNTksNTk3Ljg1IC02NDEsODk3Yy04LjY3LDAgLTE3LjMzLDAgLTI2LDBjMjE0LjQxLC0yOTkuMDcgNDI4LjQxLC01OTguNDEgNjQyLC04OTh6IiBmaWxsPSIjYjZiN2JhIiBpZD0ic3ZnXzExNiIvPgogIDwvZz4KICA8ZyBpZD0ic3ZnXzExNyI+CiAgIDxwYXRoIGQ9Im00MDUzLjc3LDMwMi4xNmMxMi44OCwxLjk1IDI0LjU0LDYuNjIgMzUsMTRjLTIxMC42NywyOTQuMzMgLTQyMS4zMyw1ODguNjcgLTYzMiw4ODNjLTE0LjY3LDAgLTI5LjMzLDAgLTQ0LDBjMjEzLjQxLC0yOTkuMTUgNDI3LjA4LC01OTguMTUgNjQxLC04OTd6IiBmaWxsPSIjYjhiYWJkIiBpZD0ic3ZnXzExOCIvPgogIDwvZz4KICA8ZyBpZD0ic3ZnXzExOSI+CiAgIDxwYXRoIGQ9Im00NTYuNzcsMzA2LjE2YzAsMTQyLjY3IDAsMjg1LjMzIDAsNDI4Yy0zLjYsNi44NyAtNi45NCwxMy44NyAtMTAsMjFjLTEuOTEsMi44IC0zLjU3LDUuOCAtNSw5Yy01LjY2LDExLjI5IC0xMS4zMywyMi42MiAtMTcsMzRjLTAuMzMsMCAtMC42NywwIC0xLDBjMC4zMywtMTU5LjE3IDAsLTMxOC4xNyAtMSwtNDc3YzEwLjA1LC03LjY5IDIxLjM4LC0xMi42OSAzNCwtMTV6IiBmaWxsPSIjYzZjOGNkIiBpZD0ic3ZnXzEyMCIgb3BhY2l0eT0iMSIvPgogIDwvZz4KICA8ZyBpZD0ic3ZnXzEyMSI+CiAgIDxwYXRoIGQ9Im00MDg4Ljc3LDMxNi4xNmM4LjkxLDUuNTcgMTUuMjQsMTMuMjQgMTksMjNjLTIwNSwyODYuNjcgLTQxMCw1NzMuMzMgLTYxNSw4NjBjLTEyLDAgLTI0LDAgLTM2LDBjMjEwLjY3LC0yOTQuMzMgNDIxLjMzLC01ODguNjcgNjMyLC04ODN6IiBmaWxsPSIjYmFiY2MwIiBpZD0ic3ZnXzEyMiIvPgogIDwvZz4KICA8ZyBpZD0ic3ZnXzEyMyI+CiAgIDxwYXRoIGQ9Im00MjIuNzcsMzIxLjE2YzEsMTU4LjgzIDEuMzMsMzE3LjgzIDEsNDc3Yy0xLjc0LDQuNDggLTMuNzQsOC44MiAtNiwxM2MtNi44OSwxMi43OCAtMTMuNTYsMjUuNzggLTIwLDM5Yy03LjE3LDEzLjAyIC0xMy44NCwyNi4zNSAtMjAsNDBjLTEuOTEsMi44IC0zLjU3LDUuOCAtNSw5Yy0wLjY3LC0xNjkuMzMgLTEuMzMsLTMzOC42NyAtMiwtNTA4YzcuMDQsLTE1LjA5IDE0Ljg4LC0yOS43NiAyMy41LC00NGM3LjQ5LC0xMSAxNi45OSwtMTkuNjYgMjguNSwtMjZ6IiBmaWxsPSIjYzljY2QxIiBpZD0ic3ZnXzEyNCIgb3BhY2l0eT0iMSIvPgogIDwvZz4KICA8ZyBpZD0ic3ZnXzEyNSI+CiAgIDxwYXRoIGQ9Im00MTA3Ljc3LDMzOS4xNmMyLjg5LDQuNSA0LjcyLDkuNSA1LjUsMTVjMi4yMywxMi4xNiAxLjU2LDI0LjE2IC0yLDM2Yy0xMC4wOCwyMS44MyAtMjAuOTEsNDMuMTYgLTMyLjUsNjRjLTE3OC4yMywyNDguMTIgLTM1Ni4yMyw0OTYuNDUgLTUzNCw3NDVjLTE3LjMzLDAgLTM0LjY3LDAgLTUyLDBjMjA1LC0yODYuNjcgNDEwLC01NzMuMzMgNjE1LC04NjB6IiBmaWxsPSIjYmRiZmMzIiBpZD0ic3ZnXzEyNiIgb3BhY2l0eT0iMSIvPgogIDwvZz4KICA8ZyBpZD0ic3ZnXzEyNyI+CiAgIDxwYXRoIGQ9Im0zNzAuNzcsMzkxLjE2YzAuNjcsMTY5LjMzIDEuMzMsMzM4LjY3IDIsNTA4Yy02Ljc1LDkuOTQgLTkuNDIsMjAuOTQgLTgsMzNjMS4zMSw2LjU5IDMuOTgsMTIuNTkgOCwxOGMtMSw4Mi44MyAtMS4zMywxNjUuODMgLTEsMjQ5Yy0xMDYuMzYsMC40OCAtMjEyLjY5LC0wLjAyIC0zMTksLTEuNWMtMzcuNzIsLTEwLjQxIC01NS4yMiwtMzUuMjQgLTUyLjUsLTc0LjVjMS4wMiwtNS40MSAyLjM1LC0xMC43NSA0LC0xNmMxMjEuOTQsLTIzOC44OCAyNDQuMTEsLTQ3Ny41NSAzNjYuNSwtNzE2eiIgZmlsbD0iI2NjY2VkNCIgaWQ9InN2Z18xMjgiIG9wYWNpdHk9IjEiLz4KICA8L2c+CiAgPGcgaWQ9InN2Z18xMjkiPgogICA8cGF0aCBkPSJtNDA3OC43Nyw0NTQuMTZjLTI3LjE2LDU0LjMyIC01NC44MywxMDguMzIgLTgzLDE2MmMtMTM5LjU3LDE5NC4xMiAtMjc4LjksMzg4LjQ1IC00MTgsNTgzYy0xMSwwIC0yMiwwIC0zMywwYzE3Ny43NywtMjQ4LjU1IDM1NS43NywtNDk2Ljg4IDUzNCwtNzQ1eiIgZmlsbD0iI2MwYzJjNiIgaWQ9InN2Z18xMzAiIG9wYWNpdHk9IjEiLz4KICA8L2c+CiAgPGcgaWQ9InN2Z18xMzEiPgogICA8cGF0aCBkPSJtMjU4MS43Nyw0ODcuMTZjMC4yMyw2LjA4IDEuMDYsMTIuMDggMi41LDE4YzEuNzMsNy4xNSA1LjIzLDEzLjE1IDEwLjUsMThjMS41LDIuMzQgMy41LDQuMTcgNiw1LjVjMTAuOTYsNS44MSAyMi42Miw3Ljk4IDM1LDYuNWMxNy42NywwIDM1LjMzLDAgNTMsMGMxMywwIDI2LDAgMzksMGMyMiwwIDQ0LDAgNjYsMGMxNC4zMywwIDI4LjY3LDAgNDMsMGMyNC42NywwIDQ5LjMzLDAgNzQsMGM4LDAgMTYsMCAyNCwwYzM1LjY3LDAgNzEuMzMsMCAxMDcsMGMzNy4zMywwIDc0LjY3LDAgMTEyLDBjMjMuMzMsMCA0Ni42NywwIDcwLDBjNzEsMCAxNDIsMCAyMTMsMGM0Ni42NywwIDkzLjMzLDAgMTQwLDBjOS42NywwIDE5LjMzLDAgMjksMGMyNy4zMywwIDU0LjY3LDAgODIsMGM4LjAxLC0wLjE3IDE2LjAxLDAgMjQsMC41YzYuNDYsMC42MSAxMi40NiwyLjQ0IDE4LDUuNWMxMS4wNyw2LjEzIDE3Ljc0LDE1LjQ2IDIwLDI4Yy01NjQuMzMsMy4yMSAtMTEyOC42Niw2LjIxIC0xNjkzLDljMCwtMi4zMyAwLC00LjY3IDAsLTdjMCwtMTMgMCwtMjYgMCwtMzljMCwtMy4zMyAwLC02LjY3IDAsLTEwYzAsLTkuNjcgMCwtMTkuMzMgMCwtMjljMCwtMSAwLC0yIDAsLTNjMTc1LC0xLjEyIDM1MCwtMi4xMiA1MjUsLTN6IiBmaWxsPSIjZDJiMTY2IiBpZD0ic3ZnXzEzMiIvPgogIDwvZz4KICA8ZyBpZD0ic3ZnXzEzMyI+CiAgIDxwYXRoIGQ9Im0xNTQ5Ljc3LDI3NS4xNmMwLDcxLjY3IDAsMTQzLjMzIDAsMjE1YzE2OSwwLjgyIDMzOCwxLjgyIDUwNywzYzAsOS42NyAwLDE5LjMzIDAsMjljLTE3MS44MywtMC45MiAtMzQzLjUsLTIuMjYgLTUxNSwtNGMwLC0wLjY3IDAsLTEuMzMgMCwtMmM0LjA5LC01LjU2IDYuMjYsLTExLjkgNi41LC0xOWMwLjE3LC03NC4xNyAwLjY3LC0xNDguMTcgMS41LC0yMjJ6IiBmaWxsPSIjY2VhNzNjIiBpZD0ic3ZnXzEzNCIvPgogIDwvZz4KICA8ZyBpZD0ic3ZnXzEzNSI+CiAgIDxwYXRoIGQ9Im0xNTQxLjc3LDUxOC4xNmMxNzEuNSwxLjc0IDM0My4xNywzLjA4IDUxNSw0YzAsMy4zMyAwLDYuNjcgMCwxMGMtMTc1LjUsLTAuNSAtMzUwLjg0LC0xLjgzIC01MjYsLTRjNC4zMiwtMi42NSA3Ljk4LC01Ljk4IDExLC0xMHoiIGZpbGw9IiNjZmE5M2QiIGlkPSJzdmdfMTM2Ii8+CiAgPC9nPgogIDxnIGlkPSJzdmdfMTM3Ij4KICAgPHBhdGggZD0ibTE1MzAuNzcsNTI4LjE2YzE3NS4xNiwyLjE3IDM1MC41LDMuNSA1MjYsNGMwLDEzIDAsMjYgMCwzOWMtNTA0LC0yLjY3IC0xMDA4LC01LjMzIC0xNTEyLC04YzUuODQsLTE1LjE3IDE2Ljg0LC0yNC4xNyAzMywtMjdjOS45OCwtMC44IDE5Ljk4LC0xLjEzIDMwLC0xYzEyLjY3LDAgMjUuMzMsMCAzOCwwYzEzLDAgMjYsMCAzOSwwYzkuNjcsMCAxOS4zMywwIDI5LDBjMTYuMzMsMCAzMi42NywwIDQ5LDBjMTEsMCAyMiwwIDMzLDBjMTguMzMsMCAzNi42NywwIDU1LDBjNiwwIDEyLDAgMTgsMGMyNi42NywwIDUzLjMzLDAgODAsMGMyOCwwIDU2LDAgODQsMGMxNy4zMywwIDM0LjY3LDAgNTIsMGM1Mi42NywwIDEwNS4zMywwIDE1OCwwYzIuNjcsMCA1LjMzLDAgOCwwYzMyLjMzLDAgNjQuNjcsMCA5NywwYzcuMzMsMCAxNC42NywwIDIyLDBjMjAuMzMsMCA0MC42NywwIDYxLDBjMTEuMzMsMCAyMi42NywwIDM0LDBjMTcuMDMsMC4yOCAzNC4wMywtMC4wNiA1MSwtMWM1LjQ4LC0wLjgzIDEwLjQ4LC0yLjgzIDE1LC02eiIgZmlsbD0iI2QwYWE0MyIgaWQ9InN2Z18xMzgiLz4KICA8L2c+CiAgPGcgaWQ9InN2Z18xMzkiPgogICA8cGF0aCBkPSJtNTQ0Ljc3LDU2My4xNmM1MDQsMi42NyAxMDA4LDUuMzMgMTUxMiw4YzAsMi4zMyAwLDQuNjcgMCw3YzAsMTEgMCwyMiAwLDMzYy01MTAuNjYsLTMuMzMgLTEwMjEuMzMsLTYuMzMgLTE1MzIsLTljMi4zOCwtNS4zNiA0LjcyLC0xMC42OSA3LC0xNmM0LjU5LC03LjUgOC45MiwtMTUuMTcgMTMsLTIzeiIgZmlsbD0iI2QyYWQ0NyIgaWQ9InN2Z18xNDAiLz4KICA8L2c+CiAgPGcgaWQ9InN2Z18xNDEiPgogICA8cGF0aCBkPSJtMzc0OS43Nyw1NjkuMTZjMC4xOSw2LjM5IC0wLjMxLDEyLjcyIC0xLjUsMTljLTkuMzUsMTkuMzggLTE5LjE5LDM4LjM4IC0yOS41LDU3Yy01NTQsMi44OCAtMTEwOCw1LjU0IC0xNjYyLDhjMCwtNi4zMyAwLC0xMi42NyAwLC0xOWMwLC03LjY3IDAsLTE1LjMzIDAsLTIzYzAsLTExIDAsLTIyIDAsLTMzYzU2NC4zNCwtMi43OSAxMTI4LjY3LC01Ljc5IDE2OTMsLTl6IiBmaWxsPSIjZDJiMDYwIiBpZD0ic3ZnXzE0MiIvPgogIDwvZz4KICA8ZyBpZD0ic3ZnXzE0MyI+CiAgIDxwYXRoIGQ9Im01MjQuNzcsNjAyLjE2YzUxMC42NywyLjY3IDEwMjEuMzQsNS42NyAxNTMyLDljMCw3LjY3IDAsMTUuMzMgMCwyM2MtNTE0LjMzLC0zLjM1IC0xMDI4LjY2LC02LjY5IC0xNTQzLC0xMGMzLjE2LC03LjY1IDYuODMsLTE0Ljk4IDExLC0yMnoiIGZpbGw9IiNkM2FmNGMiIGlkPSJzdmdfMTQ0Ii8+CiAgPC9nPgogIDxnIGlkPSJzdmdfMTQ1Ij4KICAgPHBhdGggZD0ibTM5OTUuNzcsNjE2LjE2Yy00MS4xNiw4MS42NSAtODIuODMsMTYyLjk5IC0xMjUsMjQ0Yy04MS4zNiwxMTIuNyAtMTYyLjM2LDIyNS43IC0yNDMsMzM5Yy0xNi42NywwIC0zMy4zMywwIC01MCwwYzEzOS4xLC0xOTQuNTUgMjc4LjQzLC0zODguODggNDE4LC01ODN6IiBmaWxsPSIjYzNjNWNhIiBpZD0ic3ZnXzE0NiIgb3BhY2l0eT0iMSIvPgogIDwvZz4KICA8ZyBpZD0ic3ZnXzE0NyI+CiAgIDxwYXRoIGQ9Im01MTMuNzcsNjI0LjE2YzUxNC4zNCwzLjMxIDEwMjguNjcsNi42NSAxNTQzLDEwYzAsNi4zMyAwLDEyLjY3IDAsMTljMCwxIDAsMiAwLDNjLTUxOC4zNCwtMi43MiAtMTAzNi42NywtNS43MiAtMTU1NSwtOWMwLjA2LC0xLjExIDAuMzksLTIuMTEgMSwtM2MzLjE1LC02Ljk2IDYuODEsLTEzLjYyIDExLC0yMHoiIGZpbGw9IiNkNGIwNGYiIGlkPSJzdmdfMTQ4Ii8+CiAgPC9nPgogIDxnIGlkPSJzdmdfMTQ5Ij4KICAgPHBhdGggZD0ibTM3MTguNzcsNjQ1LjE2Yy0wLjczLDIuNDUgLTEuNzMsNC43OSAtMyw3Yy02LjUxLDEzLjY4IC0xMy41MSwyNy4wMiAtMjEsNDBjLTEzLC0wLjY3IC0yNi4xNiwtMSAtMzkuNSwtMWMtNTMyLjgzLDMuMTIgLTEwNjUuNjYsNS43OCAtMTU5OC41LDhjMCwtMSAwLC0yIDAsLTNjMCwtMTMuMzMgMCwtMjYuNjcgMCwtNDBjMCwtMSAwLC0yIDAsLTNjNTU0LC0yLjQ2IDExMDgsLTUuMTIgMTY2MiwtOHoiIGZpbGw9IiNkMWFmNWIiIGlkPSJzdmdfMTUwIi8+CiAgPC9nPgogIDxnIGlkPSJzdmdfMTUxIj4KICAgPHBhdGggZD0ibTUwMS43Nyw2NDcuMTZjNTE4LjMzLDMuMjggMTAzNi42Niw2LjI4IDE1NTUsOWMwLDEzLjMzIDAsMjYuNjcgMCw0MGMtNTI1LC0zLjM4IC0xMDUwLC02LjcxIC0xNTc1LC0xMGM2LjQsLTEzLjEzIDEzLjA2LC0yNi4xMyAyMCwtMzl6IiBmaWxsPSIjZDZiMjU0IiBpZD0ic3ZnXzE1MiIvPgogIDwvZz4KICA8ZyBpZD0ic3ZnXzE1MyI+CiAgIDxwYXRoIGQ9Im00ODEuNzcsNjg2LjE2YzUyNSwzLjI5IDEwNTAsNi42MiAxNTc1LDEwYzAsMSAwLDIgMCwzYzAsNS42NyAwLDExLjMzIDAsMTdjLTUyOC41LC0yLjUgLTEwNTYuODQsLTUuODMgLTE1ODUsLTEwYzIuODMsLTYuOTggNi4xNiwtMTMuNjUgMTAsLTIweiIgZmlsbD0iI2Q3YjQ1OSIgaWQ9InN2Z18xNTQiLz4KICA8L2c+CiAgPGcgaWQ9InN2Z18xNTUiPgogICA8cGF0aCBkPSJtMzY5NC43Nyw2OTIuMTZjLTQuNDksMTAuMzIgLTkuNDksMjAuMzIgLTE1LDMwYy0zMC4zMywtMC42NyAtNjAuODMsLTEgLTkxLjUsLTFjLTUxMC41LDIuNTQgLTEwMjEsNS4yMSAtMTUzMS41LDhjMCwtNC4zMyAwLC04LjY3IDAsLTEzYzAsLTUuNjcgMCwtMTEuMzMgMCwtMTdjNTMyLjg0LC0yLjIyIDEwNjUuNjcsLTQuODggMTU5OC41LC04YzEzLjM0LDAgMjYuNSwwLjMzIDM5LjUsMXoiIGZpbGw9IiNkMWFlNTgiIGlkPSJzdmdfMTU2Ii8+CiAgPC9nPgogIDxnIGlkPSJzdmdfMTU3Ij4KICAgPHBhdGggZD0ibTQ3MS43Nyw3MDYuMTZjNTI4LjE2LDQuMTcgMTA1Ni41LDcuNSAxNTg1LDEwYzAsNC4zMyAwLDguNjcgMCwxM2MwLDIgMCw0IDAsNmMtNTMxLjY5LC0zLjA0IC0xMDYzLjM1LC02LjM3IC0xNTk1LC0xMGMyLjU3LC02LjgxIDUuOSwtMTMuMTQgMTAsLTE5eiIgZmlsbD0iI2Q4YjY1YyIgaWQ9InN2Z18xNTgiLz4KICA8L2c+CiAgPGcgaWQ9InN2Z18xNTkiPgogICA8cGF0aCBkPSJtMzY3OS43Nyw3MjIuMTZjLTEyLjE3LDI1LjAxIC0yNC44NCw0OS42OCAtMzgsNzRjLTUyOC4zMywyLjkzIC0xMDU2LjY2LDUuNTkgLTE1ODUsOGMwLC0xMCAwLC0yMCAwLC0zMGMwLC0yLjY3IDAsLTUuMzMgMCwtOGMwLC0xMC4zMyAwLC0yMC42NyAwLC0zMWMwLC0yIDAsLTQgMCwtNmM1MTAuNSwtMi43OSAxMDIxLC01LjQ2IDE1MzEuNSwtOGMzMC42NywwIDYxLjE3LDAuMzMgOTEuNSwxeiIgZmlsbD0iI2QxYWQ1NCIgaWQ9InN2Z18xNjAiLz4KICA8L2c+CiAgPGcgaWQ9InN2Z18xNjEiPgogICA8cGF0aCBkPSJtNDYxLjc3LDcyNS4xNmM1MzEuNjUsMy42MyAxMDYzLjMxLDYuOTYgMTU5NSwxMGMwLDEwLjMzIDAsMjAuNjcgMCwzMWMtNTMyLjMzLC0zLjE2IC0xMDY0LjY3LC02LjMzIC0xNTk3LC05LjVjLTQuNTIsLTAuMTcgLTguODUsLTAuNjcgLTEzLC0xLjVjMy4wNiwtNy4xMyA2LjQsLTE0LjEzIDEwLC0yMWMxLjQsLTMuMTMgMy4wNywtNi4xMyA1LC05eiIgZmlsbD0iI2Q5Yjc1ZiIgaWQ9InN2Z18xNjIiLz4KICA8L2c+CiAgPGcgaWQ9InN2Z18xNjMiPgogICA8cGF0aCBkPSJtNDQ2Ljc3LDc1NS4xNmM0LjE1LDAuODMgOC40OCwxLjMzIDEzLDEuNWM1MzIuMzMsMy4xNyAxMDY0LjY3LDYuMzQgMTU5Nyw5LjVjMCwyLjY3IDAsNS4zMyAwLDhjLTUzOC41LC0yLjcgLTEwNzYuODQsLTYuMDMgLTE2MTUsLTEwYzEuNDMsLTMuMiAzLjA5LC02LjIgNSwtOXoiIGZpbGw9IiNkYWI5NjIiIGlkPSJzdmdfMTY0Ii8+CiAgPC9nPgogIDxnIGlkPSJzdmdfMTY1Ij4KICAgPHBhdGggZD0ibTQ0MS43Nyw3NjQuMTZjNTM4LjE2LDMuOTcgMTA3Ni41LDcuMyAxNjE1LDEwYzAsMTAgMCwyMCAwLDMwYzAsMSAwLDIgMCwzYy01NDQsLTIuOTUgLTEwODgsLTUuOTUgLTE2MzIsLTljNS42NywtMTEuMzggMTEuMzQsLTIyLjcxIDE3LC0zNHoiIGZpbGw9IiNkYmJhNjUiIGlkPSJzdmdfMTY2Ii8+CiAgPC9nPgogIDxnIGlkPSJzdmdfMTY3Ij4KICAgPHBhdGggZD0ibTM2NDEuNzcsNzk2LjE2Yy00Ljk0LDkuOTYgLTkuOTQsMTkuOTYgLTE1LDMwYy05Ljg0LDIwLjM1IC0yMC4xNyw0MC4zNSAtMzEsNjBjLTI4LjgzLC0wLjY3IC01Ny44MywtMSAtODcsLTFjLTQ4NCwyLjY0IC05NjgsNC45OCAtMTQ1Miw3YzAsLTEwLjMzIDAsLTIwLjY3IDAsLTMxYzAsLTEzIDAsLTI2IDAsLTM5YzAsLTUgMCwtMTAgMCwtMTVjMCwtMSAwLC0yIDAsLTNjNTI4LjM0LC0yLjQxIDEwNTYuNjcsLTUuMDcgMTU4NSwtOHoiIGZpbGw9IiNkMGFiNGUiIGlkPSJzdmdfMTY4Ii8+CiAgPC9nPgogIDxnIGlkPSJzdmdfMTY5Ij4KICAgPHBhdGggZD0ibTQyMy43Nyw3OTguMTZjMC4zMywwIDAuNjcsMCAxLDBjNTQ0LDMuMDUgMTA4OCw2LjA1IDE2MzIsOWMwLDUgMCwxMCAwLDE1Yy01MjUsLTMuMjUgLTEwNTAsLTYuNDIgLTE1NzUsLTkuNWMtMjEuNSwtMC4xNyAtNDIuODQsLTAuNjcgLTY0LC0xLjVjMi4yNiwtNC4xOCA0LjI2LC04LjUyIDYsLTEzeiIgZmlsbD0iI2RjYmM2OSIgaWQ9InN2Z18xNzAiLz4KICA8L2c+CiAgPGcgaWQ9InN2Z18xNzEiPgogICA8cGF0aCBkPSJtNDE3Ljc3LDgxMS4xNmMyMS4xNiwwLjgzIDQyLjUsMS4zMyA2NCwxLjVjNTI1LDMuMDggMTA1MCw2LjI1IDE1NzUsOS41YzAsMTMgMCwyNiAwLDM5Yy01NDIuNjcsLTMuMDQgLTEwODUuMzMsLTYuMjEgLTE2MjgsLTkuNWMtMTAuNTEsLTAuMTcgLTIwLjg0LC0wLjY3IC0zMSwtMS41YzYuNDQsLTEzLjIyIDEzLjExLC0yNi4yMiAyMCwtMzl6IiBmaWxsPSIjZGRiZDZkIiBpZD0ic3ZnXzE3MiIvPgogIDwvZz4KICA8ZyBpZD0ic3ZnXzE3MyI+CiAgIDxwYXRoIGQ9Im0zOTcuNzcsODUwLjE2YzEwLjE2LDAuODMgMjAuNDksMS4zMyAzMSwxLjVjNTQyLjY3LDMuMjkgMTA4NS4zMyw2LjQ2IDE2MjgsOS41YzAsMTAuMzMgMCwyMC42NyAwLDMxYzAsMyAwLDYgMCw5Yy01NTkuNzYsLTMuNjYgLTExMTkuNDMsLTcuMzIgLTE2NzksLTExYzYuMTYsLTEzLjY1IDEyLjgzLC0yNi45OCAyMCwtNDB6IiBmaWxsPSIjZGZjMDczIiBpZD0ic3ZnXzE3NCIvPgogIDwvZz4KICA8ZyBpZD0ic3ZnXzE3NSI+CiAgIDxwYXRoIGQ9Im0zODcwLjc3LDg2MC4xNmMtNDcuMjIsOTMuNDQgLTk0LjcyLDE4Ni43NyAtMTQyLjUsMjgwYy0yMi4xMywzOC41NiAtNTUuNjMsNTguMjMgLTEwMC41LDU5YzgwLjY0LC0xMTMuMyAxNjEuNjQsLTIyNi4zIDI0MywtMzM5eiIgZmlsbD0iI2M2YzhjZSIgaWQ9InN2Z18xNzYiIG9wYWNpdHk9IjAuOTkiLz4KICA8L2c+CiAgPGcgaWQ9InN2Z18xNzciPgogICA8cGF0aCBkPSJtMzU5NS43Nyw4ODYuMTZjLTkuODEsMTkuNjEgLTE5LjY0LDM5LjI4IC0yOS41LDU5Yy04LjY5LDEzLjYgLTIxLjE5LDIwLjI3IC0zNy41LDIwYy0xMi4zLDAuOTIgLTI0LjY0LDEuMjUgLTM3LDFjLTIyLjMzLDAgLTQ0LjY3LDAgLTY3LDBjLTE1LjMzLDAgLTMwLjY3LDAgLTQ2LDBjLTI3LjMzLDAgLTU0LjY3LDAgLTgyLDBjLTkuNjcsMCAtMTkuMzMsMCAtMjksMGMtNDYuNjcsMCAtOTMuMzMsMCAtMTQwLDBjLTcxLDAgLTE0MiwwIC0yMTMsMGMtMjMuMzMsMCAtNDYuNjcsMCAtNzAsMGMtMzcuMzMsMCAtNzQuNjcsMCAtMTEyLDBjLTM4LC0wLjE3IC03NiwwIC0xMTQsMC41Yy0yMS45NCwzLjMxIC0zMy43OCwxNi4xNSAtMzUuNSwzOC41Yy0wLjUsNTYuNjcgLTAuNjcsMTEzLjMzIC0wLjUsMTcwYzAuMTcsMTcgMCwzNCAtMC41LDUxYy0zLjIxLDI2LjA1IC0xOC4wNSwzOS4zOSAtNDQuNSw0MGMtMTYwLjMzLDAgLTMyMC42NywwIC00ODEsMGMwLC05MyAwLC0xODYgMCwtMjc5YzAsLTE1IDAsLTMwIDAsLTQ1YzAsLTEzLjY3IDAsLTI3LjMzIDAsLTQxYzAsLTMgMCwtNiAwLC05YzQ4NCwtMi4wMiA5NjgsLTQuMzYgMTQ1MiwtN2MyOS4xNywwIDU4LjE3LDAuMzMgODcsMXoiIGZpbGw9IiNjZmE5NDYiIGlkPSJzdmdfMTc4Ii8+CiAgPC9nPgogIDxnIGlkPSJzdmdfMTc5Ij4KICAgPHBhdGggZD0ibTM3Ny43Nyw4OTAuMTZjNTU5LjU3LDMuNjggMTExOS4yNCw3LjM0IDE2NzksMTFjMCwxMy42NyAwLDI3LjMzIDAsNDFjLTU2NCwtMy41MiAtMTEyOCwtNi44NiAtMTY5MiwtMTBjLTEuNDIsLTEyLjA2IDEuMjUsLTIzLjA2IDgsLTMzYzEuNDMsLTMuMiAzLjA5LC02LjIgNSwtOXoiIGZpbGw9IiNlMWMzNzkiIGlkPSJzdmdfMTgwIi8+CiAgPC9nPgogIDxnIGlkPSJzdmdfMTgxIj4KICAgPHBhdGggZD0ibTM2NC43Nyw5MzIuMTZjNTY0LDMuMTQgMTEyOCw2LjQ4IDE2OTIsMTBjMCwxNSAwLDMwIDAsNDVjLTE3MS4zNCwtMC40OSAtMzQyLjY3LC0xLjQ5IC01MTQsLTNjLTAuMzMsMCAtMC42NywwIC0xLDBjLTUuNjIsLTEwLjE1IC0xNC4yOSwtMTUuODIgLTI2LC0xN2MtMS45OCwtMC41IC0zLjk4LC0xIC02LC0xLjVjLTE1LC0wLjUgLTMwLC0wLjY3IC00NSwtMC41Yy0xMS4zMywwIC0yMi42NywwIC0zNCwwYy0yMC4zMywwIC00MC42NywwIC02MSwwYy03LjMzLDAgLTE0LjY3LDAgLTIyLDBjLTMyLjMzLDAgLTY0LjY3LDAgLTk3LDBjLTIuNjcsMCAtNS4zMywwIC04LDBjLTUyLjY3LDAgLTEwNS4zMywwIC0xNTgsMGMtMTcuMzMsMCAtMzQuNjcsMCAtNTIsMGMtMjgsMCAtNTYsMCAtODQsMGMtMjYuNjcsMCAtNTMuMzMsMCAtODAsMGMtNiwwIC0xMiwwIC0xOCwwYy0xOC4zMywwIC0zNi42NywwIC01NSwwYy0xMSwwIC0yMiwwIC0zMywwYy0xNi4zMywwIC0zMi42NywwIC00OSwwYy05LjY3LDAgLTE5LjMzLDAgLTI5LDBjLTEzLDAgLTI2LDAgLTM5LDBjLTEyLjY3LDAgLTI1LjMzLDAgLTM4LDBjLTEwLDAgLTIwLDAgLTMwLDBjLTE1LjMzLDAgLTMwLjY3LDAgLTQ2LDBjLTkuNjcsMCAtMTkuMzMsMCAtMjksMGMtMTUuMzMsMCAtMzAuNjcsMCAtNDYsMGMtMTEsMCAtMjIsMCAtMzMsMGMtMTUuNjUsMS43OCAtMzAuMzEsLTEuMDUgLTQ0LC04LjVjLTIuMiwtMi4zNyAtNC41NCwtNC41NCAtNywtNi41Yy00LjAyLC01LjQxIC02LjY5LC0xMS40MSAtOCwtMTh6IiBmaWxsPSIjZTNjNTdmIiBpZD0ic3ZnXzE4MiIvPgogIDwvZz4KICA8ZyBpZD0ic3ZnXzE4MyI+CiAgIDxwYXRoIGQ9Im0zNzIuNzcsOTUwLjE2YzIuNDYsMS45NiA0LjgsNC4xMyA3LDYuNWMxMy42OSw3LjQ1IDI4LjM1LDEwLjI4IDQ0LDguNWMwLDc4IDAsMTU2IDAsMjM0Yy0xNy4zMywwIC0zNC42NywwIC01MiwwYy0wLjMzLC04My4xNyAwLC0xNjYuMTcgMSwtMjQ5eiIgZmlsbD0iI2M5Y2NkMSIgaWQ9InN2Z18xODQiLz4KICA8L2c+CiAgPGcgaWQ9InN2Z18xODUiPgogICA8cGF0aCBkPSJtNDIzLjc3LDk2NS4xNmMxMSwwIDIyLDAgMzMsMGMwLDc4IDAsMTU2IDAsMjM0Yy0xMSwwIC0yMiwwIC0zMywwYzAsLTc4IDAsLTE1NiAwLC0yMzR6IiBmaWxsPSIjYzZjOGNkIiBpZD0ic3ZnXzE4NiIvPgogIDwvZz4KICA8ZyBpZD0ic3ZnXzE4NyI+CiAgIDxwYXRoIGQ9Im00NTYuNzcsOTY1LjE2YzE1LjMzLDAgMzAuNjcsMCA0NiwwYzAsNzggMCwxNTYgMCwyMzRjLTE1LjMzLDAgLTMwLjY3LDAgLTQ2LDBjMCwtNzggMCwtMTU2IDAsLTIzNHoiIGZpbGw9IiNjM2M1Y2EiIGlkPSJzdmdfMTg4Ii8+CiAgPC9nPgogIDxnIGlkPSJzdmdfMTg5Ij4KICAgPHBhdGggZD0ibTUwMi43Nyw5NjUuMTZjOS42NywwIDE5LjMzLDAgMjksMGMwLDc4IDAsMTU2IDAsMjM0Yy05LjY3LDAgLTE5LjMzLDAgLTI5LDBjMCwtNzggMCwtMTU2IDAsLTIzNHoiIGZpbGw9IiNjMGMyYzYiIGlkPSJzdmdfMTkwIi8+CiAgPC9nPgogIDxnIGlkPSJzdmdfMTkxIj4KICAgPHBhdGggZD0ibTUzMS43Nyw5NjUuMTZjMTUuMzMsMCAzMC42NywwIDQ2LDBjMCw3OCAwLDE1NiAwLDIzNGMtMTUuMzMsMCAtMzAuNjcsMCAtNDYsMGMwLC03OCAwLC0xNTYgMCwtMjM0eiIgZmlsbD0iI2JkYmZjMyIgaWQ9InN2Z18xOTIiLz4KICA8L2c+CiAgPGcgaWQ9InN2Z18xOTMiPgogICA8cGF0aCBkPSJtNTc3Ljc3LDk2NS4xNmMxMCwwIDIwLDAgMzAsMGMwLDc4IDAsMTU2IDAsMjM0Yy0xMCwwIC0yMCwwIC0zMCwwYzAsLTc4IDAsLTE1NiAwLC0yMzR6IiBmaWxsPSIjYmFiY2MwIiBpZD0ic3ZnXzE5NCIvPgogIDwvZz4KICA8ZyBpZD0ic3ZnXzE5NSI+CiAgIDxwYXRoIGQ9Im02MDcuNzcsOTY1LjE2YzEyLjY3LDAgMjUuMzMsMCAzOCwwYzAsNzggMCwxNTYgMCwyMzRjLTEyLjY3LDAgLTI1LjMzLDAgLTM4LDBjMCwtNzggMCwtMTU2IDAsLTIzNHoiIGZpbGw9IiNiOGJhYmQiIGlkPSJzdmdfMTk2Ii8+CiAgPC9nPgogIDxnIGlkPSJzdmdfMTk3Ij4KICAgPHBhdGggZD0ibTY0NS43Nyw5NjUuMTZjMTMsMCAyNiwwIDM5LDBjMCw3OCAwLDE1NiAwLDIzNGMtMTMsMCAtMjYsMCAtMzksMGMwLC03OCAwLC0xNTYgMCwtMjM0eiIgZmlsbD0iI2I1YjZiOSIgaWQ9InN2Z18xOTgiLz4KICA8L2c+CiAgPGcgaWQ9InN2Z18xOTkiPgogICA8cGF0aCBkPSJtNjg0Ljc3LDk2NS4xNmM5LjY3LDAgMTkuMzMsMCAyOSwwYzAsNzggMCwxNTYgMCwyMzRjLTkuNjcsMCAtMTkuMzMsMCAtMjksMGMwLC03OCAwLC0xNTYgMCwtMjM0eiIgZmlsbD0iI2IzYjRiNiIgaWQ9InN2Z18yMDAiLz4KICA8L2c+CiAgPGcgaWQ9InN2Z18yMDEiPgogICA8cGF0aCBkPSJtNzEzLjc3LDk2NS4xNmMxNi4zMywwIDMyLjY3LDAgNDksMGMwLDc4IDAsMTU2IDAsMjM0Yy0xNi4zMywwIC0zMi42NywwIC00OSwwYzAsLTc4IDAsLTE1NiAwLC0yMzR6IiBmaWxsPSIjYjBiMWIzIiBpZD0ic3ZnXzIwMiIvPgogIDwvZz4KICA8ZyBpZD0ic3ZnXzIwMyI+CiAgIDxwYXRoIGQ9Im03NjIuNzcsOTY1LjE2YzExLDAgMjIsMCAzMywwYzAsNzggMCwxNTYgMCwyMzRjLTExLDAgLTIyLDAgLTMzLDBjMCwtNzggMCwtMTU2IDAsLTIzNHoiIGZpbGw9IiNhZGFlYWYiIGlkPSJzdmdfMjA0Ii8+CiAgPC9nPgogIDxnIGlkPSJzdmdfMjA1Ij4KICAgPHBhdGggZD0ibTc5NS43Nyw5NjUuMTZjMTguMzMsMCAzNi42NywwIDU1LDBjMCw3OCAwLDE1NiAwLDIzNGMtMTguMzMsMCAtMzYuNjcsMCAtNTUsMGMwLC03OCAwLC0xNTYgMCwtMjM0eiIgZmlsbD0iI2FhYWJhYyIgaWQ9InN2Z18yMDYiLz4KICA8L2c+CiAgPGcgaWQ9InN2Z18yMDciPgogICA8cGF0aCBkPSJtODUwLjc3LDk2NS4xNmM2LDAgMTIsMCAxOCwwYzAsNzggMCwxNTYgMCwyMzRjLTYsMCAtMTIsMCAtMTgsMGMwLC03OCAwLC0xNTYgMCwtMjM0eiIgZmlsbD0iI2E3YThhOSIgaWQ9InN2Z18yMDgiLz4KICA8L2c+CiAgPGcgaWQ9InN2Z18yMDkiPgogICA8cGF0aCBkPSJtODY4Ljc3LDk2NS4xNmMyNi42NywwIDUzLjMzLDAgODAsMGMwLDc4IDAsMTU2IDAsMjM0Yy0yNi42NywwIC01My4zMywwIC04MCwwYzAsLTc4IDAsLTE1NiAwLC0yMzR6IiBmaWxsPSIjYTRhNWE1IiBpZD0ic3ZnXzIxMCIvPgogIDwvZz4KICA8ZyBpZD0ic3ZnXzIxMSI+CiAgIDxwYXRoIGQ9Im05NDguNzcsOTY1LjE2YzI4LDAgNTYsMCA4NCwwYzAsNzggMCwxNTYgMCwyMzRjLTI4LDAgLTU2LDAgLTg0LDBjMCwtNzggMCwtMTU2IDAsLTIzNHoiIGZpbGw9IiM5ZjlmOWYiIGlkPSJzdmdfMjEyIi8+CiAgPC9nPgogIDxnIGlkPSJzdmdfMjEzIj4KICAgPHBhdGggZD0ibTEwMzIuNzcsOTY1LjE2YzE3LjMzLDAgMzQuNjcsMCA1MiwwYzAsNzggMCwxNTYgMCwyMzRjLTE3LjMzLDAgLTM0LjY3LDAgLTUyLDBjMCwtNzggMCwtMTU2IDAsLTIzNHoiIGZpbGw9IiM5YzlkOWIiIGlkPSJzdmdfMjE0Ii8+CiAgPC9nPgogIDxnIGlkPSJzdmdfMjE1Ij4KICAgPHBhdGggZD0ibTEwODQuNzcsOTY1LjE2YzUyLjY3LDAgMTA1LjMzLDAgMTU4LDBjMCw3OCAwLDE1NiAwLDIzNGMtNTIuNjcsMCAtMTA1LjMzLDAgLTE1OCwwYzAsLTc4IDAsLTE1NiAwLC0yMzR6IiBmaWxsPSIjOWY5ZjllIiBpZD0ic3ZnXzIxNiIvPgogIDwvZz4KICA8ZyBpZD0ic3ZnXzIxNyI+CiAgIDxwYXRoIGQ9Im0xMjQyLjc3LDk2NS4xNmMyLjY3LDAgNS4zMywwIDgsMGMwLDc4IDAsMTU2IDAsMjM0Yy0yLjY3LDAgLTUuMzMsMCAtOCwwYzAsLTc4IDAsLTE1NiAwLC0yMzR6IiBmaWxsPSIjYTJhM2EyIiBpZD0ic3ZnXzIxOCIvPgogIDwvZz4KICA8ZyBpZD0ic3ZnXzIxOSI+CiAgIDxwYXRoIGQ9Im0xMjUwLjc3LDk2NS4xNmMzMi4zMywwIDY0LjY3LDAgOTcsMGMwLDE3NSAwLDM1MCAwLDUyNWMtMTguNSwtMTAuOTYgLTI5LC0yNy4yOSAtMzEuNSwtNDljLTEuMywtNjguNjUgLTEuOTYsLTEzNy4zMiAtMiwtMjA2Yy0zLjY4LC0yMi4zNCAtMTYuODQsLTM0LjE4IC0zOS41LC0zNS41Yy03Ljk5LC0wLjUgLTE1Ljk5LC0wLjY3IC0yNCwtMC41YzAsLTc4IDAsLTE1NiAwLC0yMzR6IiBmaWxsPSIjYTVhNWE2IiBpZD0ic3ZnXzIyMCIgb3BhY2l0eT0iMSIvPgogIDwvZz4KICA8ZyBpZD0ic3ZnXzIyMSI+CiAgIDxwYXRoIGQ9Im0xMzQ3Ljc3LDk2NS4xNmM3LjMzLDAgMTQuNjcsMCAyMiwwYzAsMTc3LjY3IDAsMzU1LjMzIDAsNTMzYy03LjkyLC0xLjMgLTE1LjI1LC0zLjk3IC0yMiwtOGMwLC0xNzUgMCwtMzUwIDAsLTUyNXoiIGZpbGw9IiNhN2E4YTkiIGlkPSJzdmdfMjIyIiBvcGFjaXR5PSIxIi8+CiAgPC9nPgogIDxnIGlkPSJzdmdfMjIzIj4KICAgPHBhdGggZD0ibTEzNjkuNzcsOTY1LjE2YzIwLjMzLDAgNDAuNjcsMCA2MSwwYzAsMTc4LjMzIDAsMzU2LjY3IDAsNTM1Yy0xOCwwLjE3IC0zNiwwIC01NCwtMC41Yy0yLjQyLC0wLjI5IC00Ljc1LC0wLjc5IC03LC0xLjVjMCwtMTc3LjY3IDAsLTM1NS4zMyAwLC01MzN6IiBmaWxsPSIjYWFhYmFjIiBpZD0ic3ZnXzIyNCIvPgogIDwvZz4KICA8ZyBpZD0ic3ZnXzIyNSI+CiAgIDxwYXRoIGQ9Im0xNDMwLjc3LDk2NS4xNmMxMS4zMywwIDIyLjY3LDAgMzQsMGMwLDE3OC4zMyAwLDM1Ni42NyAwLDUzNWMtMTEuMzMsMCAtMjIuNjcsMCAtMzQsMGMwLC0xNzguMzMgMCwtMzU2LjY3IDAsLTUzNXoiIGZpbGw9IiNhZGFlYjAiIGlkPSJzdmdfMjI2Ii8+CiAgPC9nPgogIDxnIGlkPSJzdmdfMjI3Ij4KICAgPHBhdGggZD0ibTE0NjQuNzcsOTY1LjE2YzE1LC0wLjE3IDMwLDAgNDUsMC41YzIuMDIsMC41IDQuMDIsMSA2LDEuNWMwLDE3Ny42NyAwLDM1NS4zMyAwLDUzM2MtMTcsMCAtMzQsMCAtNTEsMGMwLC0xNzguMzMgMCwtMzU2LjY3IDAsLTUzNXoiIGZpbGw9IiNiMGIxYjMiIGlkPSJzdmdfMjI4Ii8+CiAgPC9nPgogIDxnIGlkPSJzdmdfMjI5Ij4KICAgPHBhdGggZD0ibTM1MjguNzcsOTY1LjE2Yy01NS42Nyw3OCAtMTExLjMzLDE1NiAtMTY3LDIzNGMtMTIsMCAtMjQsMCAtMzYsMGM1NS4zMywtNzcuNjcgMTEwLjY3LC0xNTUuMzMgMTY2LC0yMzNjMTIuMzYsMC4yNSAyNC43LC0wLjA4IDM3LC0xeiIgZmlsbD0iI2IzYjRiNiIgaWQ9InN2Z18yMzAiLz4KICA8L2c+CiAgPGcgaWQ9InN2Z18yMzEiPgogICA8cGF0aCBkPSJtMjczMi43Nyw5NjYuMTZjLTQ5LjI4LDcwLjIzIC05OS4yOCwxMzkuOSAtMTUwLDIwOWMtMC4xNywtNTYuNjcgMCwtMTEzLjMzIDAuNSwtMTcwYzEuNzIsLTIyLjM1IDEzLjU2LC0zNS4xOSAzNS41LC0zOC41YzM4LC0wLjUgNzYsLTAuNjcgMTE0LC0wLjV6IiBmaWxsPSIjYTRhNGE1IiBpZD0ic3ZnXzIzMiIvPgogIDwvZz4KICA8ZyBpZD0ic3ZnXzIzMyI+CiAgIDxwYXRoIGQ9Im0yNzMyLjc3LDk2Ni4xNmMzNy4zMywwIDc0LjY3LDAgMTEyLDBjLTEyNy4wMiwxNzguMDIgLTI1NC4wMiwzNTYuMDIgLTM4MSw1MzRjLTM3LjMzLDAgLTc0LjY3LDAgLTExMiwwYzU1LjA4LC03Ny44MSAxMTAuNDEsLTE1NS40OCAxNjYsLTIzM2M2Ljg1LDAuMzIgMTMuNTIsLTAuMDEgMjAsLTFjMjYuNDUsLTAuNjEgNDEuMjksLTEzLjk1IDQ0LjUsLTQwYzAuNSwtMTcgMC42NywtMzQgMC41LC01MWM1MC43MiwtNjkuMSAxMDAuNzIsLTEzOC43NyAxNTAsLTIwOXoiIGZpbGw9IiM5ZjlmOWYiIGlkPSJzdmdfMjM0Ii8+CiAgPC9nPgogIDxnIGlkPSJzdmdfMjM1Ij4KICAgPHBhdGggZD0ibTI4NDQuNzcsOTY2LjE2YzIzLjMzLDAgNDYuNjcsMCA3MCwwYy0xMjcuMDIsMTc4LjAyIC0yNTQuMDIsMzU2LjAyIC0zODEsNTM0Yy0yMy4zMywwIC00Ni42NywwIC03MCwwYzEyNi45OCwtMTc3Ljk4IDI1My45OCwtMzU1Ljk4IDM4MSwtNTM0eiIgZmlsbD0iIzljOWQ5YiIgaWQ9InN2Z18yMzYiLz4KICA8L2c+CiAgPGcgaWQ9InN2Z18yMzciPgogICA8cGF0aCBkPSJtMjkxNC43Nyw5NjYuMTZjNzEsMCAxNDIsMCAyMTMsMGMtNTUuMzYsNzcuNjggLTExMC42OSwxNTUuMzUgLTE2NiwyMzNjLTM2LjY5LC0wLjQyIC03My4zNSwwLjA4IC0xMTAsMS41Yy0yMy45Nyw0LjM3IC0zNS44LDE4Ljg3IC0zNS41LDQzLjVjLTAuNSw1MyAtMC42NywxMDYgLTAuNSwxNTljLTIzLjU3LDMyLjEyIC00Ni45LDY0LjQ1IC03MCw5N2MtNzAuNjcsMCAtMTQxLjMzLDAgLTIxMiwwYzEyNi45OCwtMTc3Ljk4IDI1My45OCwtMzU1Ljk4IDM4MSwtNTM0eiIgZmlsbD0iIzlmOWY5ZSIgaWQ9InN2Z18yMzgiLz4KICA8L2c+CiAgPGcgaWQ9InN2Z18yMzkiPgogICA8cGF0aCBkPSJtMzEyNy43Nyw5NjYuMTZjNDYuNjcsMCA5My4zMywwIDE0MCwwYy01NS4zMyw3Ny42NyAtMTEwLjY3LDE1NS4zMyAtMTY2LDIzM2MtNDYuNjcsMCAtOTMuMzMsMCAtMTQwLDBjNTUuMzEsLTc3LjY1IDExMC42NCwtMTU1LjMyIDE2NiwtMjMzeiIgZmlsbD0iI2E0YTVhNSIgaWQ9InN2Z18yNDAiLz4KICA8L2c+CiAgPGcgaWQ9InN2Z18yNDEiPgogICA8cGF0aCBkPSJtMzI2Ny43Nyw5NjYuMTZjOS42NywwIDE5LjMzLDAgMjksMGMtNTUuMDgsNzcuODEgLTExMC40MSwxNTUuNDggLTE2NiwyMzNjLTkuNjcsMCAtMTkuMzMsMCAtMjksMGM1NS4zMywtNzcuNjcgMTEwLjY3LC0xNTUuMzMgMTY2LC0yMzN6IiBmaWxsPSIjYTdhOGE5IiBpZD0ic3ZnXzI0MiIvPgogIDwvZz4KICA8ZyBpZD0ic3ZnXzI0MyI+CiAgIDxwYXRoIGQ9Im0zMjk2Ljc3LDk2Ni4xNmMyNy4zMywwIDU0LjY3LDAgODIsMGMtNTUuNTksNzcuNTIgLTExMC45MiwxNTUuMTkgLTE2NiwyMzNjLTI3LjMzLDAgLTU0LjY3LDAgLTgyLDBjNTUuNTksLTc3LjUyIDExMC45MiwtMTU1LjE5IDE2NiwtMjMzeiIgZmlsbD0iI2FhYWJhYyIgaWQ9InN2Z18yNDQiLz4KICA8L2c+CiAgPGcgaWQ9InN2Z18yNDUiPgogICA8cGF0aCBkPSJtMzM3OC43Nyw5NjYuMTZjMTUuMzMsMCAzMC42NywwIDQ2LDBjLTU1LjU5LDc3LjUyIC0xMTAuOTIsMTU1LjE5IC0xNjYsMjMzYy0xNS4zMywwIC0zMC42NywwIC00NiwwYzU1LjA4LC03Ny44MSAxMTAuNDEsLTE1NS40OCAxNjYsLTIzM3oiIGZpbGw9IiNhZGFlYWYiIGlkPSJzdmdfMjQ2Ii8+CiAgPC9nPgogIDxnIGlkPSJzdmdfMjQ3Ij4KICAgPHBhdGggZD0ibTM0MjQuNzcsOTY2LjE2YzIyLjMzLDAgNDQuNjcsMCA2NywwYy01NS4zMyw3Ny42NyAtMTEwLjY3LDE1NS4zMyAtMTY2LDIzM2MtMjIuMzMsMCAtNDQuNjcsMCAtNjcsMGM1NS4wOCwtNzcuODEgMTEwLjQxLC0xNTUuNDggMTY2LC0yMzN6IiBmaWxsPSIjYjBiMWIzIiBpZD0ic3ZnXzI0OCIvPgogIDwvZz4KICA8ZyBpZD0ic3ZnXzI0OSI+CiAgIDxwYXRoIGQ9Im0xNTE1Ljc3LDk2Ny4xNmMxMS43MSwxLjE4IDIwLjM4LDYuODUgMjYsMTdjMCwxNzIgMCwzNDQgMCw1MTZjLTguNjcsMCAtMTcuMzMsMCAtMjYsMGMwLC0xNzcuNjcgMCwtMzU1LjMzIDAsLTUzM3oiIGZpbGw9IiNiM2I0YjYiIGlkPSJzdmdfMjUwIi8+CiAgPC9nPgogIDxnIGlkPSJzdmdfMjUxIj4KICAgPHBhdGggZD0ibTE1NDEuNzcsOTg0LjE2YzAuMzMsMCAwLjY3LDAgMSwwYzIuNjgsNS43MSA0LjUyLDExLjcxIDUuNSwxOGMwLjAzLDc2LjM1IDAuNywxNTIuNjggMiwyMjljMi4xOSwxOC4wMiAxMi4wMiwyOS4zNSAyOS41LDM0YzAsNzguMzMgMCwxNTYuNjcgMCwyMzVjLTEyLjY3LDAgLTI1LjMzLDAgLTM4LDBjMCwtMTcyIDAsLTM0NCAwLC01MTZ6IiBmaWxsPSIjYjViNmI5IiBpZD0ic3ZnXzI1MiIvPgogIDwvZz4KICA8ZyBpZD0ic3ZnXzI1MyI+CiAgIDxwYXRoIGQ9Im0xNTQyLjc3LDk4NC4xNmMxNzEuMzMsMS41MSAzNDIuNjYsMi41MSA1MTQsM2MwLDkzIDAsMTg2IDAsMjc5YzE2MC4zMywwIDMyMC42NywwIDQ4MSwwYy02LjQ4LDAuOTkgLTEzLjE1LDEuMzIgLTIwLDFjLTM1LjY3LDAgLTcxLjMzLDAgLTEwNywwYy04LjMzLDAgLTE2LjY3LDAgLTI1LDBjLTI0LjY3LDAgLTQ5LjMzLDAgLTc0LDBjLTE0LjMzLDAgLTI4LjY3LDAgLTQzLDBjLTIyLDAgLTQ0LDAgLTY2LDBjLTEyLjY3LDAgLTI1LjMzLDAgLTM4LDBjLTM2LDAgLTcyLDAgLTEwOCwwYy04Mi42NywwIC0xNjUuMzMsMCAtMjQ4LDBjLTEzLjY3LDAgLTI3LjMzLDAgLTQxLDBjLTksMCAtMTgsMCAtMjcsMGMtMTIuMzMsMCAtMjQuNjcsMCAtMzcsMGMtOC4zMywwIC0xNi42NywwIC0yNSwwYy0xMywwIC0yNiwwIC0zOSwwYy05LDAgLTE4LDAgLTI3LDBjLTExLjA3LDAuMjggLTIyLjA3LC0wLjM4IC0zMywtMmMtMTcuNDgsLTQuNjUgLTI3LjMxLC0xNS45OCAtMjkuNSwtMzRjLTEuMywtNzYuMzIgLTEuOTcsLTE1Mi42NSAtMiwtMjI5Yy0wLjk4LC02LjI5IC0yLjgyLC0xMi4yOSAtNS41LC0xOHoiIGZpbGw9IiNlNGM3ODUiIGlkPSJzdmdfMjU0Ii8+CiAgPC9nPgogIDxnIGlkPSJzdmdfMjU1Ij4KICAgPHBhdGggZD0ibTI5MzMuNzcsMTIzNy4xNmMzNC43NSwtMC4yMiA2MC45MSwxNC40NSA3OC41LDQ0YzE3Ljg1LDQwLjA3IDExLjAyLDc1LjI0IC0yMC41LDEwNS41Yy0zMC44NCwyMS45MSAtNjMuMTcsMjQuMjQgLTk3LDdjLTM3LjI2LC0yNi4xNyAtNDguNzYsLTYxIC0zNC41LC0xMDQuNWMxNC43MSwtMzEuMjIgMzkuMjEsLTQ4LjU1IDczLjUsLTUyem0tNywxNWM0MS43LC0yLjU5IDY4LjIsMTYuMDggNzkuNSw1NmM0LjQsMzUuNzEgLTkuNDQsNjEuNTQgLTQxLjUsNzcuNWMtMzUuMiwxMS40OSAtNjMuNywyLjMyIC04NS41LC0yNy41Yy0xNy43MiwtMzMuODQgLTEyLjg5LC02NC4wMSAxNC41LC05MC41YzkuOTMsLTcuNTggMjAuOTMsLTEyLjc1IDMzLC0xNS41em0tNiwzNGMxMi4wNSwtMC4zNyAyNC4wNSwwLjEzIDM2LDEuNWMxMC40MiwzLjU2IDEzLjI1LDEwLjQgOC41LDIwLjVjLTIuNzgsMy4zMSAtNi4yOCw1LjQ3IC0xMC41LDYuNWMtMTEuMzMsMC41IC0yMi42NiwwLjY3IC0zNCwwLjVjMCwtOS42NyAwLC0xOS4zMyAwLC0yOXoiIGZpbGw9IiM0YjRjNGQiIGlkPSJzdmdfMjU2IiBvcGFjaXR5PSIwLjk2Ii8+CiAgPC9nPgogIDxnIGlkPSJzdmdfMjU3Ij4KICAgPHBhdGggZD0ibTE1NzkuNzcsMTI2NS4xNmMxMC45MywxLjYyIDIxLjkzLDIuMjggMzMsMmMwLDc3LjY3IDAsMTU1LjMzIDAsMjMzYy0xMSwwIC0yMiwwIC0zMywwYzAsLTc4LjMzIDAsLTE1Ni42NyAwLC0yMzV6IiBmaWxsPSIjYjhiYWJkIiBpZD0ic3ZnXzI1OCIvPgogIDwvZz4KICA8ZyBpZD0ic3ZnXzI1OSI+CiAgIDxwYXRoIGQ9Im0xNjEyLjc3LDEyNjcuMTZjOSwwIDE4LDAgMjcsMGMwLDc3LjY3IDAsMTU1LjMzIDAsMjMzYy05LDAgLTE4LDAgLTI3LDBjMCwtNzcuNjcgMCwtMTU1LjMzIDAsLTIzM3oiIGZpbGw9IiNiYWJjYzAiIGlkPSJzdmdfMjYwIi8+CiAgPC9nPgogIDxnIGlkPSJzdmdfMjYxIj4KICAgPHBhdGggZD0ibTE2MzkuNzcsMTI2Ny4xNmMxMywwIDI2LDAgMzksMGMwLDc3LjY3IDAsMTU1LjMzIDAsMjMzYy0xMywwIC0yNiwwIC0zOSwwYzAsLTc3LjY3IDAsLTE1NS4zMyAwLC0yMzN6IiBmaWxsPSIjYmRiZmMzIiBpZD0ic3ZnXzI2MiIvPgogIDwvZz4KICA8ZyBpZD0ic3ZnXzI2MyI+CiAgIDxwYXRoIGQ9Im0xNjc4Ljc3LDEyNjcuMTZjOC4zMywwIDE2LjY3LDAgMjUsMGMwLDc3LjY3IDAsMTU1LjMzIDAsMjMzYy04LjMzLDAgLTE2LjY3LDAgLTI1LDBjMCwtNzcuNjcgMCwtMTU1LjMzIDAsLTIzM3oiIGZpbGw9IiNjMGMyYzYiIGlkPSJzdmdfMjY0Ii8+CiAgPC9nPgogIDxnIGlkPSJzdmdfMjY1Ij4KICAgPHBhdGggZD0ibTE3MDMuNzcsMTI2Ny4xNmMxMi4zMywwIDI0LjY3LDAgMzcsMGMwLDc3LjY3IDAsMTU1LjMzIDAsMjMzYy0xMi4zMywwIC0yNC42NywwIC0zNywwYzAsLTc3LjY3IDAsLTE1NS4zMyAwLC0yMzN6IiBmaWxsPSIjYzNjNWNhIiBpZD0ic3ZnXzI2NiIvPgogIDwvZz4KICA8ZyBpZD0ic3ZnXzI2NyI+CiAgIDxwYXRoIGQ9Im0xNzQwLjc3LDEyNjcuMTZjOSwwIDE4LDAgMjcsMGMwLDc3LjY3IDAsMTU1LjMzIDAsMjMzYy05LDAgLTE4LDAgLTI3LDBjMCwtNzcuNjcgMCwtMTU1LjMzIDAsLTIzM3oiIGZpbGw9IiNjNmM4Y2QiIGlkPSJzdmdfMjY4Ii8+CiAgPC9nPgogIDxnIGlkPSJzdmdfMjY5Ij4KICAgPHBhdGggZD0ibTE3NjcuNzcsMTI2Ny4xNmMxMy42NywwIDI3LjMzLDAgNDEsMGMwLDc3LjY3IDAsMTU1LjMzIDAsMjMzYy0xMy42NywwIC0yNy4zMywwIC00MSwwYzAsLTc3LjY3IDAsLTE1NS4zMyAwLC0yMzN6IiBmaWxsPSIjYzljY2QxIiBpZD0ic3ZnXzI3MCIvPgogIDwvZz4KICA8ZyBpZD0ic3ZnXzI3MSI+CiAgIDxwYXRoIGQ9Im0xODA4Ljc3LDEyNjcuMTZjODIuNjcsMCAxNjUuMzMsMCAyNDgsMGMwLDUwIDAsMTAwIDAsMTUwYzAsMTggMCwzNiAwLDU0YzAsOS42NyAwLDE5LjMzIDAsMjljLTgyLjY3LDAgLTE2NS4zMywwIC0yNDgsMGMwLC03Ny42NyAwLC0xNTUuMzMgMCwtMjMzeiIgZmlsbD0iI2NiY2ZkNCIgaWQ9InN2Z18yNzIiLz4KICA8L2c+CiAgPGcgaWQ9InN2Z18yNzMiPgogICA8cGF0aCBkPSJtMjA1Ni43NywxMjY3LjE2YzM2LDAgNzIsMCAxMDgsMGMtMzUuNjQsNTAuMyAtNzEuNjQsMTAwLjMgLTEwOCwxNTBjMCwtNTAgMCwtMTAwIDAsLTE1MHoiIGZpbGw9IiNiNWI3YjkiIGlkPSJzdmdfMjc0Ii8+CiAgPC9nPgogIDxnIGlkPSJzdmdfMjc1Ij4KICAgPHBhdGggZD0ibTIxNjQuNzcsMTI2Ny4xNmMxMi42NywwIDI1LjMzLDAgMzgsMGMtNDguMzEsNjguMyAtOTYuOTgsMTM2LjMgLTE0NiwyMDRjMCwtMTggMCwtMzYgMCwtNTRjMzYuMzYsLTQ5LjcgNzIuMzYsLTk5LjcgMTA4LC0xNTB6IiBmaWxsPSIjYjJiNGI2IiBpZD0ic3ZnXzI3NiIvPgogIDwvZz4KICA8ZyBpZD0ic3ZnXzI3NyI+CiAgIDxwYXRoIGQ9Im0yMjAyLjc3LDEyNjcuMTZjMjIsMCA0NCwwIDY2LDBjLTU1LjMzLDc3LjY3IC0xMTAuNjcsMTU1LjMzIC0xNjYsMjMzYy0xNS4zMywwIC0zMC42NywwIC00NiwwYzAsLTkuNjcgMCwtMTkuMzMgMCwtMjljNDkuMDIsLTY3LjcgOTcuNjksLTEzNS43IDE0NiwtMjA0eiIgZmlsbD0iI2IwYjFiMyIgaWQ9InN2Z18yNzgiLz4KICA8L2c+CiAgPGcgaWQ9InN2Z18yNzkiPgogICA8cGF0aCBkPSJtMjI2OC43NywxMjY3LjE2YzE0LjMzLDAgMjguNjcsMCA0MywwYy01NS4wOCw3Ny44MSAtMTEwLjQxLDE1NS40OCAtMTY2LDIzM2MtMTQuMzMsMCAtMjguNjcsMCAtNDMsMGM1NS4zMywtNzcuNjcgMTEwLjY3LC0xNTUuMzMgMTY2LC0yMzN6IiBmaWxsPSIjYWRhZWFmIiBpZD0ic3ZnXzI4MCIvPgogIDwvZz4KICA8ZyBpZD0ic3ZnXzI4MSI+CiAgIDxwYXRoIGQ9Im0yMzExLjc3LDEyNjcuMTZjMjQuNjcsMCA0OS4zMywwIDc0LDBjLTU1LjA4LDc3LjgxIC0xMTAuNDEsMTU1LjQ4IC0xNjYsMjMzYy0yNC42NywwIC00OS4zMywwIC03NCwwYzU1LjU5LC03Ny41MiAxMTAuOTIsLTE1NS4xOSAxNjYsLTIzM3oiIGZpbGw9IiNhYWFiYWMiIGlkPSJzdmdfMjgyIi8+CiAgPC9nPgogIDxnIGlkPSJzdmdfMjgzIj4KICAgPHBhdGggZD0ibTIzODUuNzcsMTI2Ny4xNmM4LjMzLDAgMTYuNjcsMCAyNSwwYy01NS41OSw3Ny41MiAtMTEwLjkyLDE1NS4xOSAtMTY2LDIzM2MtOC4zMywwIC0xNi42NywwIC0yNSwwYzU1LjU5LC03Ny41MiAxMTAuOTIsLTE1NS4xOSAxNjYsLTIzM3oiIGZpbGw9IiNhN2E4YTkiIGlkPSJzdmdfMjg0Ii8+CiAgPC9nPgogIDxnIGlkPSJzdmdfMjg1Ij4KICAgPHBhdGggZD0ibTI0MTAuNzcsMTI2Ny4xNmMzNS42NywwIDcxLjMzLDAgMTA3LDBjLTU1LjU5LDc3LjUyIC0xMTAuOTIsMTU1LjE5IC0xNjYsMjMzYy0zNS42NywwIC03MS4zMywwIC0xMDcsMGM1NS4wOCwtNzcuODEgMTEwLjQxLC0xNTUuNDggMTY2LC0yMzN6IiBmaWxsPSIjYTRhNWE1IiBpZD0ic3ZnXzI4NiIvPgogIDwvZz4KICA8ZyBpZD0ic3ZnXzI4NyI+CiAgIDxwYXRoIGQ9Im0yOTA2Ljc3LDEyNzQuMTZjMTguNywtMC40IDM3LjM3LDAuMSA1NiwxLjVjMTQuNyw0LjM4IDIwLjg2LDE0LjIyIDE4LjUsMjkuNWMtMS41Miw5Ljg1IC03LjAyLDE2LjM1IC0xNi41LDE5LjVjLTMuNzIsMC42MiAtNy4zOSwxLjQ1IC0xMSwyLjVjOC42MywxMy43NiAxNy42MywyNy4yNiAyNyw0MC41Yy01LjcsMC44MyAtMTEuMzYsMC42NiAtMTcsLTAuNWMtOC40NiwtMTIuNzUgLTE2Ljc5LC0yNS41OCAtMjUsLTM4LjVjLTUuOTksLTAuNSAtMTEuOTksLTAuNjcgLTE4LC0wLjVjMCwxMy4zMyAwLDI2LjY3IDAsNDBjLTQuNjcsMCAtOS4zMywwIC0xNCwwYzAsLTMxLjMzIDAsLTYyLjY3IDAsLTk0em0xNCwxMmMwLDkuNjcgMCwxOS4zMyAwLDI5YzExLjM0LDAuMTcgMjIuNjcsMCAzNCwtMC41YzQuMjIsLTEuMDMgNy43MiwtMy4xOSAxMC41LC02LjVjNC43NSwtMTAuMSAxLjkyLC0xNi45NCAtOC41LC0yMC41Yy0xMS45NSwtMS4zNyAtMjMuOTUsLTEuODcgLTM2LC0xLjV6IiBmaWxsPSIjNGI0YzRkIiBpZD0ic3ZnXzI4OCIgb3BhY2l0eT0iMC45NSIvPgogIDwvZz4KICA8ZyBpZD0ic3ZnXzI4OSI+CiAgIDxwYXRoIGQ9Im0yODE1Ljc3LDE0MDMuMTZjMC4zOSwxNC4zOCAtMC4xMSwyOC43MSAtMS41LDQzYy02LjI2LDI5LjI1IC0yNC4wOSw0Ni43NSAtNTMuNSw1Mi41Yy00Ljk2LDAuOTEgLTkuOTYsMS40MSAtMTUsMS41YzIzLjEsLTMyLjU1IDQ2LjQzLC02NC44OCA3MCwtOTd6IiBmaWxsPSIjYTJhM2EyIiBpZD0ic3ZnXzI5MCIgb3BhY2l0eT0iMC45OCIvPgogIDwvZz4KICA8ZyBpZD0ic3ZnXzI5MSI+CiAgIDxwYXRoIGQ9Im0xMzMuNzcsMTc5Ny4xNmMxMDQsMCAyMDgsMCAzMTIsMGMwLDIwIDAsNDAgMCw2MGMtODcuMDYsLTAuNDkgLTE3NC4wNiwwLjAxIC0yNjEsMS41Yy02LjksMi45IC0xMC43Myw4LjA3IC0xMS41LDE1LjVjLTAuNjcsNjguMzMgLTAuNjcsMTM2LjY3IDAsMjA1YzAuNzgsNy40NSA0LjYxLDEyLjYxIDExLjUsMTUuNWM4Ni45NCwxLjQ5IDE3My45NCwxLjk5IDI2MSwxLjVjMCwyMCAwLDQwIDAsNjBjLTEwNC42NywwLjE3IC0yMDkuMzMsMCAtMzE0LC0wLjVjLTI2LjE1LC00LjQ5IC00Mi4zMiwtMTkuNjUgLTQ4LjUsLTQ1LjVjLTAuNjcsLTg4LjY3IC0wLjY3LC0xNzcuMzMgMCwtMjY2YzYuMTEsLTI3LjI4IDIyLjk1LC00Mi45NSA1MC41LC00N3oiIGZpbGw9IiM0YjRjNGQiIGlkPSJzdmdfMjkyIiBvcGFjaXR5PSIwLjk5Ii8+CiAgPC9nPgogIDxnIGlkPSJzdmdfMjkzIj4KICAgPHBhdGggZD0ibTQ4NS43NywxNzk3LjE2YzMwLjMzLDAgNjAuNjcsMCA5MSwwYzAsNDcgMCw5NCAwLDE0MWM2Ni4zMywwIDEzMi42NywwIDE5OSwwYzAsLTQ3IDAsLTk0IDAsLTE0MWMzMC4zMywwIDYwLjY3LDAgOTEsMGMwLDExOS42NyAwLDIzOS4zMyAwLDM1OWMtMzAuMzMsMCAtNjAuNjcsMCAtOTEsMGMwLC01Mi42NyAwLC0xMDUuMzMgMCwtMTU4Yy02Ni4zMywwIC0xMzIuNjcsMCAtMTk5LDBjMCw1Mi42NyAwLDEwNS4zMyAwLDE1OGMtMzAuMzMsMCAtNjAuNjcsMCAtOTEsMGMwLC0xMTkuNjcgMCwtMjM5LjMzIDAsLTM1OXoiIGZpbGw9IiM0YjRjNGQiIGlkPSJzdmdfMjk0IiBvcGFjaXR5PSIwLjk5Ii8+CiAgPC9nPgogIDxnIGlkPSJzdmdfMjk1Ij4KICAgPHBhdGggZD0ibTk5NS43NywxNzk3LjE2YzEwNSwwIDIxMCwwIDMxNSwwYzAsMjAgMCw0MCAwLDYwYy04Ny4zMywtMC4xNyAtMTc0LjY3LDAgLTI2MiwwLjVjLTYuNzQsMS43NCAtMTEuMjQsNS45IC0xMy41LDEyLjVjLTEuNDMsMjIuNjMgLTEuOTMsNDUuMjkgLTEuNSw2OGM5Mi42NywwIDE4NS4zMywwIDI3OCwwYzAsMjAgMCw0MCAwLDYwYy05Mi42NywwIC0xODUuMzMsMCAtMjc4LDBjLTAuMTcsMjYgMCw1MiAwLjUsNzhjMC4xMiwxMC4xMSA0Ljk2LDE2LjYxIDE0LjUsMTkuNWM5Ni4zMywwLjUgMTkyLjY3LDAuNjcgMjg5LDAuNWMwLDIwIDAsNDAgMCw2MGMtMTE0LjY3LDAuMTcgLTIyOS4zMywwIC0zNDQsLTAuNWMtMjcuNjMsLTQuMjkgLTQ0LjEzLC0yMC4xMyAtNDkuNSwtNDcuNWMtMC42NywtODcuNjcgLTAuNjcsLTE3NS4zMyAwLC0yNjNjNS44LC0yOC4zIDIyLjk3LC00NC4zIDUxLjUsLTQ4eiIgZmlsbD0iIzRiNGM0ZCIgaWQ9InN2Z18yOTYiIG9wYWNpdHk9IjAuOTkiLz4KICA8L2c+CiAgPGcgaWQ9InN2Z18yOTciPgogICA8cGF0aCBkPSJtMTM0MC43NywxNzk3LjE2YzMxLjU3LC0wLjMzIDYzLjA3LDAgOTQuNSwxYzQxLjI2LDk4LjggODMuMDksMTk3LjMgMTI1LjUsMjk1LjVjNywyIDE0LDIgMjEsMGMyLjEyLC0xLjczIDMuNjIsLTMuOSA0LjUsLTYuNWM0MC43OSwtOTYuNTggODEuMjksLTE5My4yNSAxMjEuNSwtMjkwYzMxLjY3LC0wLjMzIDYzLjM0LDAgOTUsMWMtNDkuNjIsMTExLjkgLTk5Ljc4LDIyMy41NyAtMTUwLjUsMzM1Yy04LjA3LDE0LjA2IC0yMC4yNCwyMS41NiAtMzYuNSwyMi41Yy0xNC44MywwLjE3IC0yOS42NywwLjMzIC00NC41LDAuNWMtMTYuODcsMC4xMiAtMzMuNywtMC4zOCAtNTAuNSwtMS41Yy0xMS43MSwtMS45MyAtMjAuODgsLTcuNzcgLTI3LjUsLTE3LjVjLTkuOTEsLTE5LjM3IC0xOS4yNCwtMzkuMDQgLTI4LC01OWMtNDIuMDcsLTkzLjQ2IC04My41NywtMTg3LjEzIC0xMjQuNSwtMjgxeiIgZmlsbD0iIzRiNGM0ZCIgaWQ9InN2Z18yOTgiIG9wYWNpdHk9IjAuOTkiLz4KICA8L2c+CiAgPGcgaWQ9InN2Z18yOTkiPgogICA8cGF0aCBkPSJtMTgzOS43NywxNzk3LjE2YzExNy42NywtMC4xNyAyMzUuMzMsMCAzNTMsMC41YzMwLjEyLDMuMTIgNDcuNjIsMTkuNjIgNTIuNSw0OS41YzAuNjcsMzYuMzMgMC42Nyw3Mi42NyAwLDEwOWMtMy43NiwyNi4zNiAtMTguNTksNDIuNTMgLTQ0LjUsNDguNWMtMjguMzEsMS4yNiAtNTYuNjQsMS45MyAtODUsMmM2NC44MSw0OS4zMSAxMjkuNDgsOTguODEgMTk0LDE0OC41Yy00NS42NiwxLjE3IC05MS4zMywxLjMzIC0xMzcsMC41Yy02NS4zMywtNTQgLTEzMC42NywtMTA4IC0xOTYsLTE2MmMtOS44MywtOS40NyAtMTIuMzMsLTIwLjY0IC03LjUsLTMzLjVjNC4yMSwtNy4yMSAxMC4zNywtMTEuNzEgMTguNSwtMTMuNWM1MC42NywtMC4zMyAxMDEuMzMsLTAuNjcgMTUyLC0xYzcuNDMsLTEuNzYgMTIuMjYsLTYuMjYgMTQuNSwtMTMuNWMwLjY3LC0yMC4zMyAwLjY3LC00MC42NyAwLC02MWMtMS45NCwtNy42IC02Ljc3LC0xMi4xIC0xNC41LC0xMy41Yy03MCwtMC41IC0xNDAsLTAuNjcgLTIxMCwtMC41YzAsOTkuNjcgMCwxOTkuMzMgMCwyOTljLTMwLDAgLTYwLDAgLTkwLDBjMCwtMTE5LjY3IDAsLTIzOS4zMyAwLC0zNTl6IiBmaWxsPSIjNGI0YzRkIiBpZD0ic3ZnXzMwMCIgb3BhY2l0eT0iMC45OSIvPgogIDwvZz4KICA8ZyBpZD0ic3ZnXzMwMSI+CiAgIDxwYXRoIGQ9Im0yMzc1Ljc3LDE3OTcuMTZjMTAzLjMzLC0wLjE3IDIwNi42NywwIDMxMCwwLjVjMzEuNTgsNS41OSA0OC40MiwyNC40MiA1MC41LDU2LjVjMC42Nyw4MS42NyAwLjY3LDE2My4zMyAwLDI0NWMtMi4wOCwzMi4wOCAtMTguOTIsNTAuOTEgLTUwLjUsNTYuNWMtMTAzLjY3LDAuNjcgLTIwNy4zMywwLjY3IC0zMTEsMGMtMjguMDgsLTQuNDIgLTQ0LjU4LC0yMC41OCAtNDkuNSwtNDguNWMtMC42NywtODcgLTAuNjcsLTE3NCAwLC0yNjFjNS4yMiwtMjguMzkgMjIuMDUsLTQ0LjcyIDUwLjUsLTQ5em01NCw2MGM2NywtMC4xNyAxMzQsMCAyMDEsMC41YzguMjUsMS45MSAxMy4wOCw3LjA4IDE0LjUsMTUuNWMwLjY3LDY4LjY3IDAuNjcsMTM3LjMzIDAsMjA2Yy0xLjI4LDguNjEgLTYuMTEsMTQuMTEgLTE0LjUsMTYuNWMtNjYuNjcsMC42NyAtMTMzLjMzLDAuNjcgLTIwMCwwYy05Ljc4LC0yLjY5IC0xNC45NSwtOS4xOSAtMTUuNSwtMTkuNWMtMC42NywtNjYuMzMgLTAuNjcsLTEzMi42NyAwLC0xOTljMC4yMywtMTAuMTcgNS4wNiwtMTYuODMgMTQuNSwtMjB6IiBmaWxsPSIjNGI0YzRkIiBpZD0ic3ZnXzMwMiIgb3BhY2l0eT0iMC45OSIvPgogIDwvZz4KICA8ZyBpZD0ic3ZnXzMwMyI+CiAgIDxwYXRoIGQ9Im0yODEzLjc3LDE3OTcuMTZjMzAuMzMsMCA2MC42NywwIDkxLDBjMCw5OS42NyAwLDE5OS4zMyAwLDI5OWM5MywwIDE4NiwwIDI3OSwwYzAsMjAgMCw0MCAwLDYwYy0xMjMuMzMsMCAtMjQ2LjY3LDAgLTM3MCwwYzAsLTExOS42NyAwLC0yMzkuMzMgMCwtMzU5eiIgZmlsbD0iIzRiNGM0ZCIgaWQ9InN2Z18zMDQiIG9wYWNpdHk9IjAuOTkiLz4KICA8L2c+CiAgPGcgaWQ9InN2Z18zMDUiPgogICA8cGF0aCBkPSJtMzI2My43NywxNzk3LjE2YzEwNSwwIDIxMCwwIDMxNSwwYzAsMjAgMCw0MCAwLDYwYy04NywtMC4xNyAtMTc0LDAgLTI2MSwwLjVjLTguMTQsMS40NyAtMTIuOTcsNi4zMSAtMTQuNSwxNC41Yy0wLjUsMjIgLTAuNjcsNDQgLTAuNSw2NmM5Mi4zMywwIDE4NC42NywwIDI3NywwYzAsMjAgMCw0MCAwLDYwYy05Mi4zMywwIC0xODQuNjcsMCAtMjc3LDBjLTAuMTcsMjcuMzQgMCw1NC42NyAwLjUsODJjMS43Miw4LjA2IDYuNTYsMTMuMjIgMTQuNSwxNS41Yzk2LDAuNSAxOTIsMC42NyAyODgsMC41YzAsMjAgMCw0MCAwLDYwYy0xMTQuNjcsMC4xNyAtMjI5LjMzLDAgLTM0NCwtMC41Yy0yOS44OCwtNC44OCAtNDYuMzgsLTIyLjM4IC00OS41LC01Mi41Yy0wLjY3LC04NC4zMyAtMC42NywtMTY4LjY3IDAsLTI1M2MzLjU1LC0zMS4wNCAyMC43MSwtNDguNzEgNTEuNSwtNTN6IiBmaWxsPSIjNGI0YzRkIiBpZD0ic3ZnXzMwNiIgb3BhY2l0eT0iMC45OSIvPgogIDwvZz4KICA8ZyBpZD0ic3ZnXzMwNyI+CiAgIDxwYXRoIGQ9Im0zNjI1Ljc3LDE3OTcuMTZjMTM1LDAgMjcwLDAgNDA1LDBjMCwyMCAwLDQwIDAsNjBjLTUyLjY3LDAgLTEwNS4zMywwIC0xNTgsMGMwLDk5LjY3IDAsMTk5LjMzIDAsMjk5Yy0zMCwwIC02MCwwIC05MCwwYzAsLTk5LjY3IDAsLTE5OS4zMyAwLC0yOTljLTUyLjMzLDAgLTEwNC42NywwIC0xNTcsMGMwLC0yMCAwLC00MCAwLC02MHoiIGZpbGw9IiM0YjRjNGQiIGlkPSJzdmdfMzA4IiBvcGFjaXR5PSIwLjk5Ii8+CiAgPC9nPgogPC9nPgo8L3N2Zz4="
_LOGO_PETERBILT_B64 = "PD94bWwgdmVyc2lvbj0iMS4wIiBlbmNvZGluZz0iVVRGLTgiPz4KPHN2ZyB3aWR0aD0iMjAxLjYiIGhlaWdodD0iODYuODY5IiB2ZXJzaW9uPSIxLjEiIHZpZXdCb3g9IjAgMCAyMDEuNiA4Ni44NjkiIHhtbDpzcGFjZT0icHJlc2VydmUiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyIgeG1sbnM6Y2M9Imh0dHA6Ly9jcmVhdGl2ZWNvbW1vbnMub3JnL25zIyIgeG1sbnM6ZGM9Imh0dHA6Ly9wdXJsLm9yZy9kYy9lbGVtZW50cy8xLjEvIiB4bWxuczpyZGY9Imh0dHA6Ly93d3cudzMub3JnLzE5OTkvMDIvMjItcmRmLXN5bnRheC1ucyMiPjxtZXRhZGF0YT48cmRmOlJERj48Y2M6V29yayByZGY6YWJvdXQ9IiI+PGRjOmZvcm1hdD5pbWFnZS9zdmcreG1sPC9kYzpmb3JtYXQ+PGRjOnR5cGUgcmRmOnJlc291cmNlPSJodHRwOi8vcHVybC5vcmcvZGMvZGNtaXR5cGUvU3RpbGxJbWFnZSIvPjxkYzp0aXRsZS8+PC9jYzpXb3JrPjwvcmRmOlJERj48L21ldGFkYXRhPjxkZWZzPjxjbGlwUGF0aCBpZD0iY2xpcFBhdGgyOCI+PHBhdGggZD0ibTMyMC40IDI5My4wNWgxNTEuMnY2NS4xNTJoLTE1MS4yeiIvPjwvY2xpcFBhdGg+PC9kZWZzPjxnIHRyYW5zZm9ybT0ibWF0cml4KDEuMzMzMyAwIDAgLTEuMzMzMyAtNDQzLjIgNDgxLjYpIj48ZyB0cmFuc2Zvcm09InRyYW5zbGF0ZSgxMiAzKSI+PGcgY2xpcC1wYXRoPSJ1cmwoI2NsaXBQYXRoMjgpIj48ZyB0cmFuc2Zvcm09InRyYW5zbGF0ZSgzMjAuNCAzMjUuNjIpIj48cGF0aCBkPSJtMCAwYzAgMTcuOTkxIDMzLjg0NyAzMi41NzYgNzUuNiAzMi41NzZzNzUuNi0xNC41ODUgNzUuNi0zMi41NzZjMC0xNy45OTItMzMuODQ3LTMyLjU3Ni03NS42LTMyLjU3NnMtNzUuNiAxNC41ODQtNzUuNiAzMi41NzYiIGZpbGw9IiNjZjEyM2MiLz48L2c+PGcgdHJhbnNmb3JtPSJ0cmFuc2xhdGUoMzIyLjU1IDMyNS42MikiPjxwYXRoIGQ9Im0wIDBjMCAxNi42MzQgMzIuODg0IDMwLjExNyA3My40NDkgMzAuMTE3IDQwLjU2NCAwIDczLjQ0OC0xMy40ODMgNzMuNDQ4LTMwLjExN3MtMzIuODg0LTMwLjExOC03My40NDgtMzAuMTE4Yy00MC41NjUgMC03My40NDkgMTMuNDg0LTczLjQ0OSAzMC4xMTgiIGZpbGw9IiNmZmYiLz48L2c+PGcgdHJhbnNmb3JtPSJ0cmFuc2xhdGUoMzI1LjE2IDMyNS42MikiPjxwYXRoIGQ9Im0wIDBjMCAxNS4zNiAzMS43MTQgMjcuODEzIDcwLjgzNyAyNy44MTMgMzkuMTIyIDAgNzAuODM2LTEyLjQ1MyA3MC44MzYtMjcuODEzIDAtMTUuMzYxLTMxLjcxNC0yNy44MTMtNzAuODM2LTI3LjgxMy0zOS4xMjMgMC03MC44MzcgMTIuNDUyLTcwLjgzNyAyNy44MTMiIGZpbGw9IiNjZjEyM2MiLz48L2c+PGcgdHJhbnNmb3JtPSJ0cmFuc2xhdGUoMzYxLjQ4IDM0MS43KSI+PHBhdGggZD0ibTAgMGMxLjc0OS00LjExNyAxLjMzOC05LjM2NS0xLjc1LTEyLjY1OS0xLjY0Ny0xLjg1Mi00LjExNy0zLjQ5OS02LjY4OS0zLjI5My0yLjU3NCAwLTQuMzIzIDEuNTQ0LTYuMDczIDMuMjkzLTIuMDU4LTQuNzM0LTEuODUyLTEwLjcwMy0wLjYxNy0xNS44NDktMS4wMy0xLjAyOS0yLjU3My0yLjE2Mi00LjIyLTEuODUzLTEuMDI5IDIuMDU5LTAuOTI2IDQuNTI5LTEuMzM4IDYuODk2LTAuNzIgOS45ODMgMi4wNTggMjAuMDY5IDkuNTcyIDI1LjUyMyAxLjk1NSAxLjMzOCA0LjczNCAyLjE2MiA3LjIwNCAxLjIzNiAxLjc0OS0wLjQxMiAyLjk4NC0xLjg1MyAzLjkxMS0zLjI5NCIgZmlsbD0iI2ZmZiIvPjwvZz48ZyB0cmFuc2Zvcm09InRyYW5zbGF0ZSg0MTEuMyAzNDAuNzgpIj48cGF0aCBkPSJtMCAwYzEuNDQxLTcuNzE5LTMuOTExLTE0LjIwMy03LjQxLTIwLjE3Mi0wLjIwNi0xLjEzMiAwLjMwOS0yLjE2MSAwLjgyMy0yLjg4MiAwLjMwOS0wLjMwOCAxLjAyOS0wLjgyMyAxLjQ0MS0wLjIwNSAzLjc1MSAzLjcyMSAyLjE4NSA5LjQxMyAyLjc2MSA5Ljk2MiAxLjA2NSAxLjM5NiAzLjM5Mi0wLjM1OSA0Ljk5My0wLjU4NyAzLjIzMS0wLjQ3NyA0LjM3IDMuMDExIDYuNDQ4LTAuMTEzLTEuNDQtMi41NzMtMy43MDUtNi4wNzItMi4wNTgtOC45NTQgMC43MjEtMC43MiAxLjk1NS0wLjYxNyAyLjc3OS0wLjEwMyAxLjEzMiAwLjcyMSAyLjM2NyAxLjc1IDIuOTg0IDIuOTg1LTEuMTMxIDcuNjE2IDEuNTQ0IDE2LjA1NSA3LjYxNyAyMC4yNzUgMS4yODYgMC43MDcgMi42ODIgMC41MjMgMy41MjYtMC4zMjEgMi4zNjctMi43NzkgMC41OS03LjE5Mi0wLjY0NS0xMC4xNzctMS45NTYtMy43MDUtNC4yMi02Ljc5Mi02LjM4MS0xMC4xODkgMC40MTItMS4zMzggMC45MjctMi43NzggMi4yNjQtMy42MDIgMC43MjEtMC4zMDkgMi4zODItMC4xMzMgMyAwLjE3NSAzLjg1NSAyLjEzIDUuNTYzIDguOTQ0IDcuNTE5IDEzLjQ3Mi0xLjI4NiAwLTEuOTc1LTAuMTA3LTIuNzU0IDAtMC44NzQgMC4xNS0xLjgxMSAwLjE5NC0yLjAwNyAwLjU1MyAwLjc2NiAxLjkxIDAuNzg0IDIuOTgyIDEuMTM4IDMuMDQ3IDEuNTAxLTAuNTQ5IDMuNzA0LTAuNTQ5IDQuNzY5LTAuNDM5IDAuOTI2IDEuNTQ0IDEuMzAzIDMuMDU1IDEuOTIgNC44MDUgMS4xMzMgMC4zMDkgMi42NjIgMC4zNzUgMy43MzQgMC40NDUtMC4xNDYtMC45NTQtMC40NDEtMS44NzItMS4xNzUtNC4xODUgMy43MDUgMC44MjMgNy42MyAzLjAxOSAxMS42NDQgMS43ODUgMC4yNjctMC40OTQtMC41MTQtMi4wNTktMC45MjYtMi45ODUtMC40Ni0wLjE4OSAwLjcwNiAwLjQyLTMuNDk1IDAuMDk1LTIuNzc5LTAuMjA2LTYuMDE2LTIuMTQxLTguNjkyLTIuODYxLTEuNDQtNC4wMTQtMy44NjgtNy4zMi0zLjg2OC0xMS44NDkgMC4zMjMtMS4yMTMgMC44MjQtMS42NDYgMS44NTItMi4xNjEgMS4yMzYtMC41MTUgMi42NzYgMC4xMDMgMy45MTEgMC40MTItMC4wNDMtMC42NzUgMC4xMDQtMS43NzctMC4xMDMtMi4zNjctMS45NTUtMS4wMy00LjQyNS0xLjIzNS02LjM4MS0wLjIwNi0xLjAyOSAwLjMwOS0xLjU0MyAxLjEzMi0yLjI2NCAxLjg1Mi0yLjk4NC0xLjk1NS03LjUxMi0zLjcwNS0xMC45MDktMS40NC0xLjEzMiAwLjYxNy0yLjI0OCAyLjMyMS0yLjI0OCAyLjMyMS0xLjg1My0xLjY0Ny00LjMzOS0zLjA0Mi03LjAxNC0yLjYzLTEuMjM2IDAuMzA5LTIuNDcxIDEuMTMyLTIuODgyIDIuNDctMS4wMyAyLjU3MyAwLjIwNiA1LjA0MyAwLjgyNCA3LjQxLTAuOTI3IDAuNDEyLTIuMjY1IDAuMjA2LTMuMjk0IDAuMTAzLTEuMDMtMy45MTEtMS45NTYtOS4zNjYtNi45OTktMTAuMDg2LTIuMDU4LTAuMzA5LTMuMTkgMS4yMzUtNC41MjkgMi41NzMtMi4yNjMtMS41NDQtNC45NC0zLjE5LTcuODItMi4xNjEtMy43MDYgMi42NzYtMC41MTYgNy41MTMtMC4xMDQgMTEuMDEyLTAuNDEyIDAuNDEyLTEuMTMyIDAuMzA4LTEuNTQ0IDAuMTAyLTEuNDQxLTEuNjQ2LTEuNjQ3LTQuMzIyLTIuNzc5LTYuMzgtMC45MjYtMi40Ny0zLjA4Ny00LjUyOS01LjY2LTUuMDQzLTEuOTY5LTAuNzI5LTQuMzEgMS4xOS00Ljc0NiAxLjE2Mi0wLjQyNC0wLjAyOC0xLjQ1Mi0wLjg3My0yLjU2MS0wLjk1Ni0yLjU3My0wLjYxOC00Ljk0IDAuOTI2LTYuMTc1IDIuNTczLTIuMjY0LTEuODUzLTUuMDQzLTMuNDk5LTguMTMxLTIuNzc5LTAuOTI2IDAuMzA5LTEuODUyIDAuNTE0LTIuNTczIDEuMjM1LTEuNzQ5LTAuMTAzLTQuMzIyLTIuNjc2LTUuMzUyLTAuMTAzLTAuNTE0IDIuNjc2IDMuNTQxIDAuNTc2IDMuMjI5IDMuNzM4LTAuMTg0IDQuNzM2IDIuNjA3IDguNzAyIDYuMjA1IDkuNzMgMC45MTcgMC4xNDcgMi4wOTMgMC4wMTQgMi44MTQtMC41IDEuMjM1LTEuMDI5IDEuMzM1LTIuOTE1IDAuOTMxLTQuNDU4LTAuODIzLTIuNjc1LTIuNjgxLTQuNTk5LTQuNjM3LTYuNDUyIDAtMC4yMDUgMC4xMjEtMC41MjMgMC41MTYtMC41MTQgNi4wNzIgMS4yMzUgNy4wMTkgOC4xNzQgOS4wNzggMTIuODA1LTEuNTA2LTAuMzMxLTMuODkyLTAuNDA0LTQuODU5IDEuMDg5IDAuMTk2IDAuNDkgMC41NzQgMi4wOTMgMC45MyAyLjU4MyAwLjIzMi0wLjQ1MyAxLjIxOC0wLjk1MiA0Ljg4NC0wLjMzMSAwLjQ3NyAwLjg4MSAxLjkwOCA0LjU1MyAyLjY4IDYuNDk5IDEuMDc1IDAuMzc4IDIuMTY2IDAuMjU3IDMuODU2IDAuMS0wLjM2OC0xLjEyOC0xLjEzOS0zLjAwMS0xLjcyNy00LjYxNiAyLjQ5NyAxLjA2NSAxMS43MTMgNC4yNTkgMTQuODcxIDEuNzYyLTAuMjIxLTAuNjYxLTEuNjE2LTIuNDYtMi4wNTYtMy4yMzEtMC4zMzEtMC4xMS0xLjEwMiAwLjg0NC0zLjQ1MiAwLjc3MS0zLjc0NS0wLjExLTguNDgxLTEuNTQyLTEwLjUzNy0zLjE1OC0xLjMzOS00LjAxNC0zLjM1Ny03LjQ4NS0zLjU2Mi0xMi4xMTYgMC4xODMtMC45NTUgMC43MTktMS44MTQgMS41NDItMi4wMTkgMC44MDgtMC4xMTEgMS41MjUgMC4wNjggMi4wMzkgMC43ODgtMS42NDYgMy4wODctMC4zMDggNi45OTggMS43NSA5LjQ2OSAxLjEzMiAxLjAyOSAyLjQ3IDIuNDY5IDQuMzIyIDIuMzY3IDAuOTI3IDAgMS43NS0wLjQxMiAyLjQ3LTEuMTMyIDEuMzM5LTEuNzUgMS4wMy0zLjkxMSAwLjIwNy01Ljc2NC0xLjAzLTEuODUzLTIuMTYyLTMuOTExLTMuODA5LTUuMjQ5LTAuMjA2LTAuNTE0IDAuMzA5LTAuNjE3IDAuNjE4LTAuODIzIDIuOTg0IDAuMTAzIDQuMDE0IDMuMDg3IDUuMDQzIDUuMjQ5bDIuMzY3IDYuNTg3YzAuMzc4IDAuNzcxIDEuNTcgMC4zMzEgMi42MTcgMC4zNjctMC40NC0xLjM1OCA0LjY5MSAxLjM4MiA1LjQxMS0xLjM5Ni0wLjIwNy0zLjM5Ny0xLjk1NS02LjQ4NS0xLjk1NS05Ljg4MSAwLjMwOC0wLjgyMyAxLjMzOC0wLjUxNCAxLjg1Mi0wLjIwNiAwLjgyNCAwLjYxOCAyLjA1OCAxLjQ0MSAyLjQ2OSAyLjM2Ny0xLjQ0IDcuNjE3IDEuMzM4IDE0LjYxNSA1LjI0OSAyMC4yNzUgMC45MjcgMS4wMyAyLjE2MiAxLjg1MyAzLjUgMi4xNjIgMS4xMzIgMCAyLjI2NC0wLjYxOCAyLjY3Ni0xLjc1IiBmaWxsPSIjZmZmIi8+PC9nPjxnIHRyYW5zZm9ybT0idHJhbnNsYXRlKDM1OC4wOSAzNDAuMTYpIj48cGF0aCBkPSJtMCAwYzEuMjM1LTMuMDg3IDAuMjA2LTYuOTk4LTEuOTU1LTkuMzY1LTEuMDMtMS4wMjktMi4wNTktMS43NS0zLjQ5OS0xLjg1My0yLjA1OSAwLjEwMy0zLjU3NiAxLjk2MS0zLjkxMiAzLjYwMi0wLjIxNSAzLjI3OCAxLjc1IDYuNDg0IDQuMjIgOC4yMzQgMS4wNzIgMC41NTEgMi4xNzMgMS41MjYgMy42NiAwLjkxMSAwLjY3Ny0wLjQxMiAxLjA3MS0wLjc4NCAxLjQ4Ni0xLjUyOSIgZmlsbD0iI2NmMTIzYyIvPjwvZz48ZyB0cmFuc2Zvcm09InRyYW5zbGF0ZSg0MDguODQgMzM3LjI1KSI+PHBhdGggZD0ibTAgMGMtMC44MjMtNC45NC0yLjg5My04LjkyNC01LjU2OS0xMi43MzItMC40MTEgNS4yNSAxLjc1IDEwLjI5MyA0LjUyOCAxNC4zMDYgMC44MjQgMC45MjcgMS4yNjEgMC4yOTggMS4wNDEtMS41NzQiIGZpbGw9IiNjZjEyM2MiLz48L2c+PGcgdHJhbnNmb3JtPSJ0cmFuc2xhdGUoNDMzLjQyIDMzNi42NikiPjxwYXRoIGQ9Im0wIDBjLTAuNjgzLTMuNTYyLTIuNzc5LTguNTQyLTUuNzYzLTExLjkzOC0wLjYxOCA1LjE0NiAxLjM3MSA5LjExIDQuMzEgMTIuNTI1IDEuMjExIDEuMzU4IDEuNjg4IDAuNDQgMS40NTMtMC41ODciIGZpbGw9IiNjZjEyM2MiLz48L2c+PGcgdHJhbnNmb3JtPSJ0cmFuc2xhdGUoNDIzLjIzIDMzNC4xOSkiPjxwYXRoIGQ9Im0wIDBjMC4zNDYtMC45MDItMC4yMDUtMi4yNjQtMS4wMjktMy4wODctMC44MjQtMC43MjEtMS43NS0xLjMzOC0yLjg4Mi0wLjkyNy0wLjgyMyAwLjUxNS0xLjE0IDEuMzg3LTAuODIzIDIuNDcgMC40MTIgMS4xMzMgMS4zMzcgMi4xNjIgMi40NjkgMi40NyAwLjkyNyAwLjIwNiAxLjg1NC0wLjEwMyAyLjI2NS0wLjkyNiIgZmlsbD0iI2ZmZiIvPjwvZz48ZyB0cmFuc2Zvcm09InRyYW5zbGF0ZSgzODMuMSAzMjYuMTYpIj48cGF0aCBkPSJtMCAwYzAtMi40Ny0xLjg1My00LjAxNC0zLjI5My01LjU1OC0wLjcyMSAxLjk1NiAwLjI3NCA0LjI0IDEuMDI5IDUuNTU4IDAuNDU3IDAuNzM4IDIuMTYxIDEuNTQ0IDIuMjY0IDAiIGZpbGw9IiNjZjEyM2MiLz48L2c+PGcgdHJhbnNmb3JtPSJ0cmFuc2xhdGUoMzYzLjU0IDMyMy42OSkiPjxwYXRoIGQ9Im0wIDBjLTAuODI5LTEuMzQ0LTEuNjQ2LTIuNjc2LTMuMDg4LTMuNDk5LTAuMzA4IDIuNDcgMC44MjYgNC44NyAyLjc4MSA2LjAwMiAxLjUyMSAwLjY3MSAwLjQ3LTEuOTc1IDAuMzA3LTIuNTAzIiBmaWxsPSIjY2YxMjNjIi8+PC9nPjwvZz48L2c+PC9nPjwvc3ZnPgo="
_LOGO_FREIGHTLINER_B64 = "PD94bWwgdmVyc2lvbj0iMS4wIiBlbmNvZGluZz0idXRmLTgiPz4NCjwhLS0gR2VuZXJhdG9yOiBBZG9iZSBJbGx1c3RyYXRvciAxNS4wLjAsIFNWRyBFeHBvcnQgUGx1Zy1JbiAuIFNWRyBWZXJzaW9uOiA2LjAwIEJ1aWxkIDApICAtLT4NCjwhRE9DVFlQRSBzdmcgUFVCTElDICItLy9XM0MvL0RURCBTVkcgMS4xLy9FTiIgImh0dHA6Ly93d3cudzMub3JnL0dyYXBoaWNzL1NWRy8xLjEvRFREL3N2ZzExLmR0ZCI+DQo8c3ZnIHZlcnNpb249IjEuMSIgaWQ9IkxheWVyXzEiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyIgeG1sbnM6eGxpbms9Imh0dHA6Ly93d3cudzMub3JnLzE5OTkveGxpbmsiIHg9IjBweCIgeT0iMHB4Ig0KCSB3aWR0aD0iMTUwLjE2N3B4IiBoZWlnaHQ9IjMyLjY2N3B4IiB2aWV3Qm94PSIwIDAgMTUwLjE2NyAzMi42NjciIGVuYWJsZS1iYWNrZ3JvdW5kPSJuZXcgMCAwIDE1MC4xNjcgMzIuNjY3Ig0KCSB4bWw6c3BhY2U9InByZXNlcnZlIj4NCjxwb2x5Z29uIGZpbGw9IiNBQTFEMTciIHBvaW50cz0iMTA0LjQyNiwyLjg0NyAxMDkuMjU0LDIuODQ3IDEwMi40NjYsOC43NDkgIi8+DQo8cG9seWxpbmUgZmlsbD0iI0Y3QjQ5RSIgcG9pbnRzPSIxMDQuNDI2LDIuODQ3IDEwMi40NjQsOC43NDkgMTA2LjE2LDMuNDA5ICIvPg0KPHBvbHlnb24gZmlsbD0iI0U2MzMyOSIgcG9pbnRzPSIxMDQuNDI2LDIuODQ3IDEwNS43MjEsNC4wMzIgMTA5LjI1NCwyLjg0NyAiLz4NCjxwYXRoIGZpbGw9IiMwMDUyMzkiIGQ9Ik0zMC4zNDEsMTEuNzQzYy0wLjUwOC0wLjQ2OC0xLjE0OC0wLjcwMi0xLjkyMi0wLjcwMmMtMC45NzgsMC0xLjk4MiwwLjQ1NS0zLjAxNSwxLjM2Ng0KCWMtMS4wMzQsMC45MS0xLjc2MiwxLjk5OS0yLjE4NCwzLjI2NWwtMi45OTQsOC45NjloLTIuNzU4bDUuMTY2LTE1LjYwNWgyLjc5NWwtMC44MjcsMi40NThjMS42MjgtMS44NiwzLjQ0OC0yLjc1Myw1LjQzMS0yLjc1Mw0KCWMwLjMzOSwwLDAuODQxLDAuMDMxLDEuNTM2LDAuMTY3TDMwLjM0MSwxMS43NDN6Ii8+DQo8cG9seWdvbiBmaWxsPSIjMDA1MjM5IiBwb2ludHM9IjEyLjY0NSw1LjUyNSAxMC42NjQsMTEuNTc5IDE4LjEzOSwxMS41NzkgMTcuMzEyLDE0LjEwNyA5LjgzOCwxNC4xMDcgNi4zOTYsMjQuNjM5IDMuMzQ4LDI0LjYzOSANCgkxMC41MTksMi44NDcgMjMuNzQxLDIuODQ3IDIyLjg3Nyw1LjUyNSAiLz4NCjxwYXRoIGZpbGw9IiMwMDUyMzkiIGQ9Ik0zMi40NjMsMTcuMTA0QzMyLjMwMiwxNy41NiwzMi4xODgsMTgsMzIuMTIsMTguNDE4Yy0wLjIwMiwxLjI1OSwwLDIuMjI3LDAuNjA3LDIuOTAzDQoJYzAuNjA3LDAuNjc3LDEuNTU1LDEuMDE2LDIuODQxLDEuMDE2YzEuMTQyLDAsMi4zNi0wLjQxNSwzLjY1NS0xLjI0NGwtMC43MzYsMi43NzVjLTEuNjI5LDAuNTA0LTMuMDQsMC43NTctNC4yMjksMC43NTcNCgljLTQuMDA2LDAtNS42NTMtMi4yMTEtNC45NDItNi42MzZjMC40MTgtMi42MDMsMS42MTItNC43OTYsMy41ODMtNi41NzljMS45NzEtMS43ODMsNC4yMzMtMi42NzQsNi43ODctMi42NzQNCgljMS41NCwwLDIuNzE2LDAuMzI0LDMuNTMxLDAuOTcyYzAuODE1LDAuNjQ5LDEuMTI2LDEuNTczLDAuOTMyLDIuNzc1Yy0wLjI2OCwxLjY2OC0xLjE5NSwyLjk4NC0yLjc4MiwzLjk0Nw0KCWMtMS41ODgsMC45NjMtMy40MiwxLjQ0NC01LjUwMSwxLjQ0NEMzNC40NzIsMTcuODc1LDMzLjMzNywxNy42MTgsMzIuNDYzLDE3LjEwNCBNMzMuMjU5LDE1LjEyOQ0KCWMwLjY4MywwLjMyNCwxLjUyMywwLjQ4NiwyLjUyLDAuNDg2YzEuNTEsMCwyLjc4Mi0wLjI0LDMuODE3LTAuNzIyYzEuMDM1LTAuNDgsMS42MjctMS4xODQsMS43NzYtMi4xMDkNCgljMC4xODgtMS4xNzMtMC41NC0xLjc1OS0yLjE4NS0xLjc1OUMzNi42ODEsMTEuMDI1LDM0LjcwNSwxMi4zOTMsMzMuMjU5LDE1LjEyOSIvPg0KPHBhdGggZmlsbD0iIzAwNTIzOSIgZD0iTTQzLjUwOSwyNC42NGw0LjM1Ny0xMy4zNzdoLTIuMDU2bDAuNzkzLTIuMjI4aDQuODU3TDQ2LjM5MiwyNC42NEg0My41MDl6IE01MS4yMTUsMi44NjQNCgljMC41MzEsMCwwLjk1NywwLjE4NiwxLjI3OCwwLjU1OGMwLjMyLDAuMzcxLDAuNDQxLDAuODI4LDAuMzYxLDEuMzY5Yy0wLjA3OSwwLjUzMS0wLjMzNCwwLjk4Mi0wLjc2NywxLjM1NA0KCWMtMC40MzEsMC4zNzItMC45MTMsMC41NTgtMS40NDQsMC41NThjLTAuNTMsMC0wLjk1Ny0wLjE4Ni0xLjI3Ny0wLjU1OGMtMC4zMjEtMC4zNzItMC40NDItMC44MjItMC4zNjMtMS4zNTQNCgljMC4wOC0wLjU0MSwwLjMzNi0wLjk5OCwwLjc2OC0xLjM2OUM1MC4yMDMsMy4wNSw1MC42ODUsMi44NjQsNTEuMjE1LDIuODY0Ii8+DQo8cGF0aCBmaWxsPSIjMDA1MjM5IiBkPSJNNjYuOTI2LDkuMDM2bC00Ljg5MywxMy45MDhjLTEuMDQ4LDIuNjgzLTEuOTM4LDUuMDA3LTMuMjkzLDYuMjI4Yy0xLjM1MywxLjIyLTMuODU5LDEuNTI2LTUuOTMyLDEuNTI2DQoJYy0wLjY2NCwwLTEuMzI2LTAuMDU4LTEuOTg0LTAuMThjLTAuNjU4LTAuMTItMS4yNTMtMC4yODItMS43ODYtMC40ODZsMC45MDUtMi42MDNoMC4xMTdjMC4zOTcsMC4yMzIsMC45NDcsMC40NTQsMS42NDksMC42NjcNCgljMC43MDIsMC4yMTUsMS4zNzgsMC4zMjEsMi4wMjgsMC4zMjFjMC43MzYsMCwxLjM3OS0wLjExMywxLjkyOS0wLjM0MmMwLjU1LTAuMjI4LDEuMDIyLTAuNTM1LDEuNDE1LTAuOTI1DQoJYzAuMzg2LTAuMzksMC43MjItMC44NDIsMS4wMDctMS4zNTdjMC4yODUtMC41MTUsMC41MzYtMS4wOTMsMC43NTEtMS43MzFsMC42NDMtMS4zODhjLTAuODgsMC42MzMtMS44MjEsMS4xMzktMi40NjQsMS40NDkNCgljLTAuNjQ1LDAuMzExLTEuMzksMC41MjUtMi4zMTgsMC41MjVjLTEuMjYyLDAtMi4yMDYtMC41MzUtMi43NzQtMS40NThjLTAuNTY3LTAuOTIzLTAuNzIyLTIuMjI0LTAuNDYtMy45MDMNCgljMC4yMDktMS4zNDUsMC41OTctMi42NTEsMS4xNjMtMy45MThjMC41NjQtMS4yNjYsMS4yNTItMi4zOTEsMi4wNjMtMy4zNzVjMC43OTItMC45NTUsMS41MjQtMS43ODQsMi41MTctMi4zNTkNCgljMC45OTEtMC41NzYsMi4xNzctMC44NzMsMy4yMDgtMC44NzNjMC43NDQsMCwxLjM3NSwwLjE3NSwxLjkyOSwwLjM3OGMwLjU1MiwwLjIwNSwxLjAyLDAuNDcsMS40MDQsMC43OTRsMC40ODktMC45SDY2LjkyNnoNCgkgTTYzLjAwOCwxMi4wNjVjLTAuNDQ5LTAuMzA3LTAuOTIxLTAuNTQ1LTEuNDE4LTAuNzE3Yy0wLjQ5Ny0wLjE3Mi0xLjAxMy0wLjI1OC0xLjU0Ny0wLjI1OGMtMC43NiwwLTEuNDg0LDAuMjA3LTIuMTczLDAuNjINCglzLTEuMzE0LDAuOTg2LTEuODc5LDEuNzE5Yy0wLjUzNCwwLjY4Ny0wLjk5MywxLjUxNC0xLjM4MSwyLjQ4NGMtMC4zODcsMC45Ny0wLjY1NiwxLjkzNy0wLjgwNiwyLjkwMg0KCWMtMC4xNzEsMS4wOTQtMC4wOTMsMS45NDEsMC4yMzMsMi41NHMwLjk1LDAuODk2LDEuODczLDAuODk2YzAuNjQ1LDAsMS4zMjEtMC4xNjMsMi4wMzEtMC40ODZjMC43MS0wLjMyNSwxLjQyMS0wLjczMiwyLjEzNC0xLjIyNg0KCUw2My4wMDgsMTIuMDY1eiIvPg0KPHBhdGggZmlsbD0iIzAwNTIzOSIgZD0iTTc0LjQzLDI0LjY0bDMuMjY2LTkuNzdjMC4xMjgtMC4zODcsMC4yMTgtMC43NDEsMC4yNjctMS4wNjJjMC4yODItMS43OTItMC40NDktMi42ODktMi4xOS0yLjY4OQ0KCWMtMC42NjcsMC0xLjQwMiwwLjE5Ni0yLjIwNCwwLjU4OWMtMC44MDIsMC4zOTMtMS40NzIsMC44NTEtMi4wMDgsMS4zNzRsLTMuODU2LDExLjU1SDY0Ljg3TDcyLjE0NSwyLjg3aDIuNjY3TDcyLjMxLDEwLjgNCgljMC41NjMtMC41NzIsMS4zMTgtMS4wNDksMi4yNjMtMS40MzJjMC45NDUtMC4zODMsMS44MjQtMC42MjYsMi42OTUtMC42MjZjMS4zNzQsMCwyLjQwNywwLjQ0NSwzLjA0NCwxLjIzDQoJYzAuNjM3LDAuNzg2LDAuODQ0LDEuODksMC42MjEsMy4zMTVjLTAuMDc4LDAuNDk0LTAuMjA5LDEuMDIyLTAuMzkzLDEuNTg0bC0zLjI2NCw5Ljc3SDc0LjQzeiIvPg0KPHBhdGggZmlsbD0iIzAwNTIzOSIgZD0iTTg1LjQxNCwxMS4xNzloLTEuOEw4NC40Miw5LjAzaDEuNzk5bDEuMTQ5LTMuMjA5bDMuMzM2LTEuMTc2TDg4Ljk3OCw5LjAzaDQuMjY2bC0wLjgwNSwyLjE0OWgtNC4yNjYNCglsLTIuODM3LDcuNjI1Yy0wLjIyMSwwLjU5Mi0wLjM1NiwxLjA1LTAuNDA3LDEuMzc2Yy0wLjIzMiwxLjQ2MiwwLjM4NiwyLjE5MSwxLjg1OCwyLjE5MWMwLjcxNiwwLDEuNTEzLTAuMTc2LDIuMzkyLTAuNTMNCglsLTAuNDgxLDIuMzk1Yy0wLjgzOSwwLjI4Ni0yLjE1MywwLjQwNC0zLjkyNSwwLjQwNGMtMS4xMDIsMC0xLjg5OC0wLjMxMi0yLjQwNS0wLjk4NGMtMC41MDctMC42NzUtMC42NjktMS41OTktMC40OC0yLjc3NA0KCWMwLjA0Mi0wLjI2NywwLjEzNy0wLjU5NywwLjI4Ny0wLjk4OEw4NS40MTQsMTEuMTc5eiIvPg0KPHBhdGggZmlsbD0iIzAwNTIzOSIgZD0iTTk2Ljc1OCwyMi42NzFsLTAuNjM4LDEuOTk0Yy0zLjEwNiwwLTQuNDc5LTEuMTMtNC4xMTctMy4zOTFjMC4xMDktMC42ODQsMC41OTQtMi4yMDcsMS40NTYtNC41NzENCglsNC45OTYtMTMuODNoMi44NzRsLTQuNzMxLDEyLjk5Yy0wLjk4MiwyLjY5OC0xLjUyOCw0LjM4Ny0xLjYzOCw1LjA3MUM5NC43NzQsMjIuMDkyLDk1LjM3NCwyMi42NzEsOTYuNzU4LDIyLjY3MSIvPg0KPHBvbHlnb24gZmlsbD0iIzAwNTIzOSIgcG9pbnRzPSI5OS4yOTcsMjQuNjI4IDEwMy42MiwxMS4zMTggMTAxLjU1OSwxMS4zMTggMTAyLjQwNiw5LjAzNiAxMDcuMTUyLDkuMDM2IDEwMi4xMDIsMjQuNjI4ICIvPg0KPHBhdGggZmlsbD0iIzAwNTIzOSIgZD0iTTExNC45NTMsMjQuNjRsMy4wMDMtOS4xMTFjMC4yNjctMC44MDIsMC40NDMtMS40NjksMC41MjYtMi4wMDFjMC4yNTctMS42NDQtMC40NDUtMi40NjYtMi4xMDYtMi40NjYNCgljLTAuNjM5LDAtMS4zNTIsMC4xOTQtMi4xMzksMC41OGMtMC43ODgsMC4zODctMS40NCwwLjg0Ny0xLjk1NSwxLjM3N2wtMy43NTQsMTEuNjE5bC0yLjczMiwwLjAwMmwzLjg5LTExLjg1Mg0KCWMwLjA5MS0wLjI3LDAuMTY1LTAuNTksMC4yMjItMC45NThjMC4xNTQtMC45ODYsMC4xODktMS44NDIsMC4xMDYtMi41NjZsMi42NzMtMC41MjJjMC4wMzEsMS40MTIsMC4wMzMsMi4xOCwwLjAwNCwyLjMwNg0KCWMxLjM4NS0xLjUzNywzLjE1OC0yLjMwNiw1LjMxNi0yLjMwNmMyLjcyMywwLDMuODU5LDEuNDMxLDMuNDEsNC4yOTJjLTAuMDksMC41NzEtMC4yNTEsMS4yMDktMC40ODMsMS45MTVsLTMuMTI2LDkuNjkNCglMMTE0Ljk1MywyNC42NHoiLz4NCjxwYXRoIGZpbGw9IiMwMDUyMzkiIGQ9Ik0xMjQuNDUsMTcuMDk2Yy0wLjE1NywwLjQ1Ni0wLjI3MSwwLjg5NC0wLjMzNiwxLjMxMmMtMC4yLDEuMjU2LTAuMDA4LDIuMjIyLDAuNTc3LDIuODk2DQoJYzAuNTg1LDAuNjc3LDEuNDk4LDEuMDE0LDIuNzQyLDEuMDE0YzEuMTA0LDAsMi4yODItMC40MTQsMy41MzUtMS4yNDJsLTAuNzIxLDIuNzdjLTEuNTc1LDAuNTA0LTIuOTQyLDAuNzg3LTQuMDkyLDAuNzg3DQoJYy0zLjg3MSwwLTUuNDUyLTIuMjM3LTQuNzUyLTYuNjUyYzAuNDEzLTIuNTk4LDEuNTc1LTQuNzg2LDMuNDg0LTYuNTY1YzEuOTA5LTEuNzc5LDQuMDk4LTIuNjY4LDYuNTY2LTIuNjY4DQoJYzEuNDg2LDAsMi42MjMsMC4zMjQsMy40MDgsMC45N2MwLjc4NiwwLjY0NywxLjA4MywxLjU3LDAuODkzLDIuNzY5Yy0wLjI2NiwxLjY2NS0xLjE2NSwyLjk3OC0yLjcwMiwzLjkzOA0KCWMtMS41MzcsMC45NjItMy4zMSwxLjQ0Mi01LjMxOSwxLjQ0MkMxMjYuMzg4LDE3Ljg2NywxMjUuMjkzLDE3LjYwOSwxMjQuNDUsMTcuMDk2IE0xMjUuMjI1LDE1LjEyNg0KCWMwLjY1OSwwLjMyMywxLjQ3LDAuNDg1LDIuNDMzLDAuNDg1YzEuNDU5LDAsMi42ODktMC4yNCwzLjY5LTAuNzIxYzEuMDAzLTAuNDgsMS41NzctMS4xODIsMS43MjQtMi4xMDUNCgljMC4xODYtMS4xNy0wLjUxNy0xLjc1NS0yLjEwNS0xLjc1NUMxMjguNTQ1LDExLjAzLDEyNi42MywxMi4zOTYsMTI1LjIyNSwxNS4xMjYiLz4NCjxwYXRoIGZpbGw9IiMwMDUyMzkiIGQ9Ik0xNDYuNjIxLDExLjc3M2MtMC40OS0wLjQ2Ni0xLjExMi0wLjctMS44NjMtMC43Yy0wLjk0NywwLTEuOTI0LDAuNDU1LTIuOTMsMS4zNjUNCgljLTEuMDA1LDAuOTA5LTEuNzE0LDEuOTk1LTIuMTI3LDMuMjU5bC0yLjkyNSw4Ljk0MmwtMi42OTksMC4wMDVsNS4xMTUtMTUuNjE0aDIuNjc2bC0wLjgxMiwyLjQ5NQ0KCWMxLjU4Ni0xLjg1NywzLjM0LTIuNzg3LDUuMjY1LTIuNzg3YzAuMzI3LDAsMC44MjgsMC4wNjgsMS41MDIsMC4yMDVMMTQ2LjYyMSwxMS43NzN6Ii8+DQo8L3N2Zz4NCg=="
_LOGO_INTERNATIONAL_B64 = "PD94bWwgdmVyc2lvbj0iMS4wIiBlbmNvZGluZz0iVVRGLTgiPz4KPHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSI0MDk1LjQ4NzkxIiBoZWlnaHQ9IjQ3Ni44MjQwMiIgdmVyc2lvbj0iMS4xIiB2aWV3Qm94PSIwIDAgNDA5NS40ODc5MSA0NzYuODI0MDIiPgogIDwhLS0gR2VuZXJhdG9yOiBBZG9iZSBJbGx1c3RyYXRvciAyOC42LjAsIFNWRyBFeHBvcnQgUGx1Zy1JbiAuIFNWRyBWZXJzaW9uOiAxLjIuMCBCdWlsZCA3MDkpICAtLT4KICA8Zz4KICAgIDxnIGlkPSJMYXllcl8xIj4KICAgICAgPGc+CiAgICAgICAgPGc+CiAgICAgICAgICA8cG9seWdvbiBwb2ludHM9IjU1NS45MzU3OCAyNjAuMjk4MDUgMzI3LjQwMzU0IDMxLjc2NTgxIDM3MS4xNzU4NCA0NDUuMDU4MjIgNTU1LjkzNTc4IDI2MC4yOTgwNSIvPgogICAgICAgICAgPHBvbHlnb24gcG9pbnRzPSIzMTIuMTg2ODQgMzEuNzY2MDMgODMuNjU0NiAyNjAuMjk4MDUgMjY4LjQxNDc2IDQ0NS4wNTgyMiAzMTIuMTg2ODQgMzEuNzY2MDMiLz4KICAgICAgICA8L2c+CiAgICAgICAgPHJlY3QgeD0iNzU0LjQ0NDkzIiB5PSIxMDguNTcwMzYiIHdpZHRoPSI1MC4wOTEwNyIgaGVpZ2h0PSIyNTYuMDIxMDQiLz4KICAgICAgICA8cmVjdCB4PSIyODA3LjE3NDAxIiB5PSIxMDguNTcwMzYiIHdpZHRoPSI1MC4wOTEwNyIgaGVpZ2h0PSIyNTYuMDIxMDQiLz4KICAgICAgICA8cG9seWdvbiBwb2ludHM9IjEzODcuNjk1MTMgMTA4LjU3MDQxIDExNTAuODQ0NjEgMTA4LjU3MDQxIDExNTAuODQ0NjEgMTU0LjY0MTgxIDEyNDQuMjI0MzQgMTU0LjY0MTgxIDEyNDQuMjI0MzQgMzY0LjU5MTQyIDEyOTQuMzE1NCAzNjQuNTkxNDIgMTI5NC4zMTU0IDE1NC42NDE4MSAxMzg3LjY5NTEzIDE1NC42NDE4MSAxMzg3LjY5NTEzIDEwOC41NzA0MSIvPgogICAgICAgIDxwb2x5Z29uIHBvaW50cz0iMjc2MS44NzU2NiAxMDguNTcwNDEgMjUyNS4wMjUxNCAxMDguNTcwNDEgMjUyNS4wMjUxNCAxNTQuNjQxODEgMjYxOC40MDQ4NyAxNTQuNjQxODEgMjYxOC40MDQ4NyAzNjQuNTkxNDIgMjY2OC40OTU5MyAzNjQuNTkxNDIgMjY2OC40OTU5MyAxNTQuNjQxODEgMjc2MS44NzU2NiAxNTQuNjQxODEgMjc2MS44NzU2NiAxMDguNTcwNDEiLz4KICAgICAgICA8cG9seWdvbiBwb2ludHM9IjM4NzIuMzA0NzkgMzE4LjUyMDAyIDM4NzIuMzA0NzkgMTA4LjU3MDQxIDM4MjIuMjE0MTcgMTA4LjU3MDQxIDM4MjIuMjE0MTcgMzY0LjU5MTQyIDQwMTEuODMzMzEgMzY0LjU5MTQyIDQwMTEuODMzMzEgMzE4LjUyMDAyIDM4NzIuMzA0NzkgMzE4LjUyMDAyIi8+CiAgICAgICAgPHBvbHlnb24gcG9pbnRzPSIxNDgzLjIzOTE0IDMxOC41MjAwMiAxNDgzLjIzOTE0IDI1Ny4wNjU2MSAxNjAzLjEzMzA1IDI1Ny4wNjU2MSAxNjAzLjEzMzA1IDIxMC45OTQyIDE0ODMuMjM5MTQgMjEwLjk5NDIgMTQ4My4yMzkxNCAxNTQuNjQxODEgMTYzMy44MjE0NSAxNTQuNjQxODEgMTYzMy44MjE0NSAxMDguNTcwNDEgMTQzMy4xNDgwNyAxMDguNTcwNDEgMTQzMy4xNDgwNyAzNjQuNTkxNDIgMTYzNy44NDExIDM2NC41OTE0MiAxNjM3Ljg0MTEgMzE4LjUyMDAyIDE0ODMuMjM5MTQgMzE4LjUyMDAyIi8+CiAgICAgICAgPHBvbHlnb24gcG9pbnRzPSIxMDU3LjQ2NTEgMTA4LjU3MDQxIDEwNTcuNDY1MSAyNDMuMjAzNTggOTIzLjAzODU5IDEwOC41NzA0MSA4NjkuNDY4OTQgMTA4LjU3MDQxIDg2OS40Njg5NCAzNjQuNTkxNDIgOTE5LjU2IDM2NC41OTE0MiA5MTkuNTYgMTc0LjkyNDE2IDEwNTcuNDY1MSAzMTMuMTg2MDUgMTA1Ny40NjUxIDM2NC41OTE0MiAxMTA3LjU1NjE2IDM2NC41OTE0MiAxMTA3LjU1NjE2IDEwOC41NzA0MSAxMDU3LjQ2NTEgMTA4LjU3MDQxIi8+CiAgICAgICAgPHBvbHlnb24gcG9pbnRzPSIyMTcwLjA1ODg2IDEwOC41NzA0MSAyMTcwLjA1ODg2IDI0My4yMDM1OCAyMDM1LjYzMjM1IDEwOC41NzA0MSAxOTgyLjA2MjcgMTA4LjU3MDQxIDE5ODIuMDYyNyAzNjQuNTkxNDIgMjAzMi4xNTM3NiAzNjQuNTkxNDIgMjAzMi4xNTM3NiAxNzQuOTI0MTYgMjE3MC4wNTg4NiAzMTMuMTg2MDUgMjE3MC4wNTg4NiAzNjQuNTkxNDIgMjIyMC4xNDk5MiAzNjQuNTkxNDIgMjIyMC4xNDk5MiAxMDguNTcwNDEgMjE3MC4wNTg4NiAxMDguNTcwNDEiLz4KICAgICAgICA8cG9seWdvbiBwb2ludHM9IjM0MDguODg1MyAxMDguNTcwNDEgMzQwOC44ODUzIDI0My4yMDM1OCAzMjc0LjQ1ODc5IDEwOC41NzA0MSAzMjIwLjg4OTE0IDEwOC41NzA0MSAzMjIwLjg4OTE0IDM2NC41OTE0MiAzMjcwLjk4MDIgMzY0LjU5MTQyIDMyNzAuOTgwMiAxNzQuOTI0MTYgMzQwOC44ODUzIDMxMy4xODYwNSAzNDA4Ljg4NTMgMzY0LjU5MTQyIDM0NTguOTc2MzYgMzY0LjU5MTQyIDM0NTguOTc2MzYgMTA4LjU3MDQxIDM0MDguODg1MyAxMDguNTcwNDEiLz4KICAgICAgICA8cGF0aCBkPSJNMzAzOS4yMzE1NywxMDIuNjE4MmMtNzMuNjg2NTcsMC0xMzMuNDIxNTQsNTkuNzM0NzQtMTMzLjQyMTU0LDEzMy40MjE1NHM1OS43MzQ5NiwxMzMuNDIxNTQsMTMzLjQyMTU0LDEzMy40MjE1NCwxMzMuNDIxNTQtNTkuNzM0NzQsMTMzLjQyMTU0LTEzMy40MjE1NC01OS43MzQ5Ni0xMzMuNDIxNTQtMTMzLjQyMTU0LTEzMy40MjE1NFpNMzAzOS4yMzE1NywzMjAuMTQzMjNjLTQ2LjQ0OTA0LDAtODQuMTAzNDktMzcuNjU0NDUtODQuMTAzNDktODQuMTAzNDlzMzcuNjU0NDUtODQuMTAzNDksODQuMTAzNDktODQuMTAzNDksODQuMTAzNDksMzcuNjU0NDUsODQuMTAzNDksODQuMTAzNDktMzcuNjU0LDg0LjEwMzQ5LTg0LjEwMzQ5LDg0LjEwMzQ5WiIvPgogICAgICAgIDxwYXRoIGQ9Ik0yNDI1LjIyOTg3LDEwOC41NzA0MWgtNDkuMTYzNzFsLTEwNi4yODg4OSwyMDMuMzc4OTR2NTIuNjQyMDdoNTAuMDkwODR2LTMyLjg2Mjg4bDE0LjI2NDcyLTI5LjQ0MTk0aDEzMy4wMzAzN2wxNC4yNjQ3MiwyOS40NDE5NHYzMi44NjI4OGg1MC4wOTA2MnYtNTIuNjQyMDdsLTEwNi4yODg2Ny0yMDMuMzc4OTRaTTIzNTUuNzA1NTQsMjU3Ljc2MTI0bDQ0Ljk0MjQ4LTkyLjc2MTI3LDQ0Ljk0MjQ4LDkyLjc2MTI3aC04OS44ODQ5NVoiLz4KICAgICAgICA8cGF0aCBkPSJNMzY2NS4xNzcyMywxMDguNTcwNDFoLTQ5LjE2MzcxbC0xMDYuMjg4ODksMjAzLjM3ODk0djUyLjY0MjA3aDUwLjA5MDg0di0zMi44NjI4OGwxNC4yNjQ3Mi0yOS40NDE5NGgxMzMuMDMwMzdsMTQuMjY0NzIsMjkuNDQxOTR2MzIuODYyODhoNTAuMDkwNjJ2LTUyLjY0MjA3bC0xMDYuMjg4NjctMjAzLjM3ODk0Wk0zNTk1LjY1MjksMjU3Ljc2MTI0bDQ0Ljk0MjQ4LTkyLjc2MTI3LDQ0Ljk0MjQ4LDkyLjc2MTI3aC04OS44ODQ5NVoiLz4KICAgICAgICA8cGF0aCBkPSJNMTg3NS4zOTQ1NywyNjQuMTMyOTljMjkuNTQ3NzItMTEuOTk3MzMsNTAuMzkzMDktNDAuOTY3MzksNTAuMzkzMDktNzQuODIxNzF2LS4wMDAyMmMwLTQ0LjU5MTg5LTM2LjE0ODk5LTgwLjc0MDY2LTgwLjc0MDg4LTgwLjc0MDY2aC0xNTEuODU4MDR2MjU2LjAyMTAyaDUwLjA5MTA2di05NC41MzkyNmg3Ni42MDM5MWw1MC40Nzg5LDk0LjUzOTI2aDU4LjY3MTY3bC01My42Mzk3My0xMDAuNDU4NDNaTTE4MzkuMTcxNzQsMjIzLjk4MDc2aC05NS44OTE5M3YtNjkuMzM4OTVoOTUuODkxOTNjMTkuMTQ3NDMsMCwzNC42Njk0NywxNS41MjIwNCwzNC42Njk0NywzNC42Njk0N3MtMTUuNTIyMDQsMzQuNjY5NDctMzQuNjY5NDcsMzQuNjY5NDdaIi8+CiAgICAgIDwvZz4KICAgIDwvZz4KICA8L2c+Cjwvc3ZnPg=="

LOGOS = {
    "Ford": f"data:image/svg+xml;base64,{_LOGO_FORD_B64}",
    "Chevrolet": f"data:image/svg+xml;base64,{_LOGO_CHEVROLET_B64}",
    "Peterbilt": f"data:image/svg+xml;base64,{_LOGO_PETERBILT_B64}",
    "Freightliner": f"data:image/svg+xml;base64,{_LOGO_FREIGHTLINER_B64}",
    "International": f"data:image/svg+xml;base64,{_LOGO_INTERNATIONAL_B64}",
}


if __name__ == "__main__":
    generate_theodore_truck_math_week_series()
