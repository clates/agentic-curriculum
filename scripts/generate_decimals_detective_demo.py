"""Demo: Decimals Detective (Priya, grade 5) — text-only error_audit theme.

Three specimens, fix_mode=rewrite (no new art needed):
  1. 0.5 + 0.25 = 0.30 line-up slip (whole-number stacking)
  2. 1.2 vs 1.20 trailing-zero myth
  3. tenths/hundredths place swap (0.7 read as 7 hundredths)

Outputs PNG + PDF + answer-key PNG per sheet into decimals_detective_demo/,
plus one HTML packet page via render_worksheet_html("errorAuditWorksheet").
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
from worksheet_html_renderer import render_worksheet_html, build_print_packet_html

OUT = "decimals_detective_demo"
os.makedirs(OUT, exist_ok=True)

PAYLOAD = {
    "title": "Decimals: Find the Bug",
    "theme_label": "Decimals Detective",
    "instructions": (
        "Each case shows a kid's decimal work with one planted error. "
        "Circle the wrong step, check the suspect that did it, "
        "then rewrite the work correctly in the lined-up grid: "
        "decimal points stay in their column, gray helper zeroes get traced."
    ),
    "legend": ["Line-Up Slip", "Trailing-Zero Myth", "Place Swap"],
    "fix_mode": "rewrite",
    "verify": True,
    "fix_lines": 2,
    "metadata": {
        "learner": "Priya",
        "grade": 5,
        "subject": "decimals",
        "strategy": "misconception-hunter",
        "source": "bank:priya_decimals_batch/Decimals Detective",
    },
    "specimens": [
        {
            "prompt": "Case 1: Maya adds 0.5 + 0.25. Her answer: 0.30.",
            "lines": [
                "Maya's work:",
                "    0.5",
                "  + 0.25",
                "  ------",
                "    0.30",
                "She stacked the numbers flush right, like whole numbers.",
            ],
            "bug_location": (
                "The 5 in 0.5 landed under the hundredths column; "
                "the decimal points were never lined up, so 0.5 added as 0.05."
            ),
            "diagnosis": "Line-Up Slip",
            "fix_text": (
                "Line up the decimal points: 0.50 + 0.25 = 0.75. "
                "Check: 5 tenths + 2 tenths = 7 tenths."
            ),
            "fix_scaffold": {
                "kind": "decimal_stack",
                "addends": ["0.5", "0.25"],
                "answer": "0.75",
            },
        },
        {
            "prompt": "Case 2: Dev compares 1.2 and 1.20. He says 1.20 is bigger.",
            "lines": [
                "Dev's claim: \"1.20 has more digits, so 1.20 > 1.2.\"",
                "He read 1.20 as one hundred twenty and 1.2 as just twelve.",
            ],
            "bug_location": (
                "The trailing zero changes nothing: 1.20 and 1.2 both mean "
                "1 whole, 2 tenths, 0 hundredths."
            ),
            "diagnosis": "Trailing-Zero Myth",
            "fix_text": (
                "1.20 = 1.2. A trailing zero does not change a decimal's value; "
                "they are equal."
            ),
        },
        {
            "prompt": "Case 3: Sam writes seven hundredths for the point on the line.",
            "lines": [
                "The number line shows a point at 0.7.",
                "Sam labels it: \"seven hundredths, 0.07\"",
            ],
            "bug_location": (
                "The point is 7 tenths (0.7), but Sam wrote the 7 in the "
                "hundredths place, swapping tenths for hundredths."
            ),
            "diagnosis": "Place Swap",
            "fix_text": (
                "The point is at 0.7, seven tenths. 0.07 would be seven "
                "hundredths, much closer to 0."
            ),
        },
    ],
}

# 1 — Student sheet: PNG + PDF.
ws = WorksheetFactory.create("error_audit", PAYLOAD)
img = render_error_audit_to_image(ws, f"{OUT}/decimals_detective.png")
pdf = render_error_audit_to_pdf(ws, f"{OUT}/decimals_detective.pdf")
print(f"OK {img} + {pdf}")

# 2 — Answer key: same payload with show_answers=True.
key = WorksheetFactory.create("error_audit", {**PAYLOAD, "show_answers": True})
render_error_audit_to_image(key, f"{OUT}/decimals_detective_key.png")
print("OK decimals_detective_key.png")

# 3 — HTML packet page via the HTML renderer (higher fidelity).
html_data = {
    "title": PAYLOAD["title"],
    "theme_label": PAYLOAD["theme_label"],
    "instructions": PAYLOAD["instructions"],
    "legend": PAYLOAD["legend"],
    "fix_mode": PAYLOAD["fix_mode"],
    "verify": PAYLOAD["verify"],
    "fix_lines": PAYLOAD["fix_lines"],
    "specimens": PAYLOAD["specimens"],
}
frag = render_worksheet_html("errorAuditWorksheet", html_data, "Thursday")
assert frag, "no HTML fragment for decimals_detective"
packet = build_print_packet_html([("Thursday", frag)], "Decimals Detective (HTML)")
with open(os.path.join(OUT, "decimals_detective_packet.html"), "w") as f:
    f.write(packet)
print("OK decimals_detective_packet.html")

print("DONE:", sorted(os.listdir(OUT)))
