"""Demo: one generic error_audit template, three themed worksheets.

  1. Clock Doctor (Maya, telling time) — fix_mode=redraw
  2. Array Detective (Dev, multiplication) — fix_mode=rewrite
  3. Division Detective (Priya, long division) — fix_mode=rewrite + answer key

Outputs PNG + PDF per sheet into error_audit_demo/.
"""
import os

os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import sys

sys.path.insert(0, os.path.abspath("src"))

from worksheets.factory import WorksheetFactory
from worksheet_renderer import (
    render_error_audit_to_image,
    render_error_audit_to_pdf,
)

OUT = "error_audit_demo_series"
os.makedirs(OUT, exist_ok=True)


def build(name, payload):
    ws = WorksheetFactory.create("error_audit", payload)
    img = render_error_audit_to_image(ws, f"{OUT}/{name}.png")
    pdf = render_error_audit_to_pdf(ws, f"{OUT}/{name}.pdf")
    key = WorksheetFactory.create("error_audit", {**payload, "show_answers": True})
    render_error_audit_to_image(key, f"{OUT}/{name}_key.png")
    print(f"OK {img} + {pdf} (+ key)")


# 1 — Clock Doctor: redraw mode. Specimen body describes the (buggy) clock
# in words since PIL has no clock-face art yet.
build("01_clock_doctor", {
    "title": "Telling Time: Half Hour",
    "theme_label": "Clock Doctor",
    "instructions": (
        "Rory Raccoon drew these clocks, but every one has a bug! "
        "Circle the bug, check the suspect that did it, "
        "then redraw the clock fixed in the starter circle."
    ),
    "legend": ["Hour-hand trap", "Minute mix-up", "Missing hand"],
    "fix_mode": "redraw",
    "verify": True,
    "specimens": [
        {
            "prompt": "Rory says this clock shows 3:30.",
            "lines": ["Study Rory's clock. What did he get wrong?"],
            "art": {"kind": "clock", "hour": 3.0, "minute": 30},
            "bug_location": "Hour hand points exactly at 3; at 3:30 it sits halfway between 3 and 4.",
            "diagnosis": "Hour-hand trap",
        },
        {
            "prompt": "Rory says this clock shows 9:00.",
            "lines": ["Study Rory's clock. What did he get wrong?"],
            "art": {"kind": "clock", "hour": 9.0, "minute": 0, "missing": "minute"},
            "bug_location": "Minute hand is missing; at 9:00 it points straight up at 12.",
            "diagnosis": "Missing hand",
        },
    ],
})

# 2 — Array Detective: rewrite mode, ELL-friendly short text.
build("02_array_detective", {
    "title": "Multiplication as Arrays",
    "theme_label": "Array Detective",
    "instructions": (
        "Each row shows an array and a kid's claim about it. "
        "One claim is wrong! Circle the bug, check the suspect, "
        "then write the fixed sentence on the lines."
    ),
    "legend": ["Counted wrong", "Rows/columns mixed", "Plus instead of times"],
    "fix_mode": "rewrite",
    "verify": True,
    "specimens": [
        {
            "prompt": "Milo's array: 3 rows of 4 dots. Milo says 3 + 4 = 7.",
            "lines": ['Milo\'s claim: "3 rows of 4 is 3 + 4 = 7."'],
            "art": {"kind": "dots", "rows": 3, "cols": 4},
            "bug_location": "Milo added instead of multiplying.",
            "diagnosis": "Plus instead of times",
            "fix_text": "3 rows of 4 is 3 x 4 = 12.",
        },
        {
            "prompt": "Zoe's array: 2 rows of 5 dots. Zoe says 5 rows of 2.",
            "lines": ['Zoe\'s claim: "This shows 5 rows of 2."'],
            "art": {"kind": "dots", "rows": 2, "cols": 5},
            "bug_location": "Rows and columns are swapped in the claim.",
            "diagnosis": "Rows/columns mixed",
            "fix_text": "This shows 2 rows of 5, which is 10.",
        },
    ],
})

# 3 — Division Detective: rewrite mode, upper elementary.
build("03_division_detective", {
    "title": "Long Division: Find the Bug",
    "theme_label": "Division Detective",
    "instructions": (
        "Each case shows a solved long-division problem with one planted error. "
        "Circle the wrong step, name the suspect, and rework it correctly."
    ),
    "legend": ["Digit too big", "Bad remainder", "Subtraction slip"],
    "fix_mode": "rewrite",
    "verify": True,
    "specimens": [
        {
            "prompt": "Case: 96 / 4. Sam's work says quotient 24, remainder 4.",
            "lines": [
                "4 goes into 9 two times (2 x 4 = 8), subtract: 1.",
                "Bring down 6 -> 16. 4 goes into 16 four times.",
                "Quotient 24, remainder 4.",
            ],
            "bug_location": "Remainder 4 is wrong: 24 x 4 = 96 exactly, so remainder is 0.",
            "diagnosis": "Bad remainder",
            "fix_text": "96 / 4 = 24 remainder 0. Check: 24 x 4 = 96.",
        },
        {
            "prompt": "Case: 75 / 3. Ana's work says quotient 26.",
            "lines": [
                "3 goes into 7 two times (2 x 3 = 6), subtract: 1.",
                "Bring down 5 -> 15. 3 goes into 15 six times (6 x 3 = 18).",
                "Quotient 26.",
            ],
            "bug_location": "Second digit: 6 x 3 = 18 is bigger than 15. 15 / 3 is 5.",
            "diagnosis": "Digit too big",
            "fix_text": "75 / 3 = 25. Check: 25 x 3 = 75.",
        },
    ],
})

print("DONE:", sorted(os.listdir(OUT)))
