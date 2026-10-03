"""Demo: ten-frame "Make Ten" worksheet for Sam (grade 1, addition within 20).

Outputs PNG + PDF + answer-key PNG into ten_frame_demo/ plus an HTML packet.
Problems mix carrying (sum > 10, bridge the ten) and non-carrying cases.
"""
import os

os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import sys

sys.path.insert(0, os.path.abspath("src"))

from worksheets.factory import WorksheetFactory
from worksheet_renderer import (
    render_ten_frame_to_image,
    render_ten_frame_to_pdf,
)
from worksheet_html_renderer import render_worksheet_html, build_print_packet_html

OUT = "ten_frame_demo"
os.makedirs(OUT, exist_ok=True)

METADATA = {
    "learner": "Sam",
    "grade": 1,
    "subject": "addition_make_ten",
    "strategy": "make-ten-bridge",
    "source": "bank:priya_sam_batch/ten_frame_make_ten",
}

PROBLEMS = [
    # Carrying: 8 + 5 -> 8 + 2 = 10, 10 + 3 = 13
    {"addend_a": 8, "addend_b": 5,
     "label": "Sam has 8 blue blocks and finds 5 red ones.",
     "fill_a": "blue", "fill_b": "red"},
    # Carrying: 9 + 6 -> 9 + 1 = 10, 10 + 5 = 15
    {"addend_a": 9, "addend_b": 6,
     "label": "Sam sees 9 ducks and 6 more swim over.",
     "fill_a": "🦆", "fill_b": "🦆"},
    # Carrying: 7 + 4 -> 7 + 3 = 10, 10 + 1 = 11
    {"addend_a": 7, "addend_b": 4,
     "label": "Sam bakes 7 cookies, then 4 more.",
     "fill_a": "🍪", "fill_b": "🍪"},
    # Non-carrying: 6 + 3 = 9 (no bridge needed)
    {"addend_a": 6, "addend_b": 3,
     "label": "Sam kicks 6 goals, then 3 more.",
     "fill_a": "⚽", "fill_b": "⚽"},
    # Non-carrying make-ten: 8 + 2 = 10 exactly
    {"addend_a": 8, "addend_b": 2,
     "label": "Sam holds 8 cards and picks up 2."},
    # Carrying: 5 + 7 -> 5 + 5 = 10, 10 + 2 = 12
    {"addend_a": 5, "addend_b": 7,
     "label": "Sam spots 5 fish, then 7 turtles.",
     "fill_a": "🐟", "fill_b": "🐢"},
]

payload = {
    "title": "Make Ten: Addition Within 20",
    "instructions": (
        "The first ten-frame shows the first number, the second shows the rest. "
        "Move counters in your head to fill the first frame to ten, "
        "then write the make-ten proof on the lines."
    ),
    "problems": PROBLEMS,
    "equation_lines": 2,
    "metadata": METADATA,
}

ws = WorksheetFactory.create("ten_frame", payload)
img = render_ten_frame_to_image(ws, f"{OUT}/sam_make_ten.png")
pdf = render_ten_frame_to_pdf(ws, f"{OUT}/sam_make_ten.pdf")
key = WorksheetFactory.create("ten_frame", {**payload, "show_answers": True})
render_ten_frame_to_image(key, f"{OUT}/sam_make_ten_key.png")
print(f"OK {img} + {pdf} (+ key)")

# HTML packet via the HTML renderer.
frag = render_worksheet_html(
    "tenFrameWorksheet",
    {
        "title": payload["title"],
        "instructions": payload["instructions"],
        "problems": PROBLEMS,
        "equation_lines": 2,
    },
    "Thursday",
)
assert frag, "no HTML fragment for tenFrameWorksheet"
key_frag = render_worksheet_html(
    "tenFrameWorksheet",
    {
        "title": payload["title"] + " — Answer Key",
        "instructions": payload["instructions"],
        "problems": PROBLEMS,
        "show_answers": True,
    },
    "",
)
assert key_frag, "no HTML fragment for tenFrameWorksheet key"
packet = build_print_packet_html(
    [("Thursday", frag), ("", key_frag)], "Make Ten Demo (HTML)"
)
with open(os.path.join(OUT, "ten_frame_packet.html"), "w") as f:
    f.write(packet)
print("OK ten_frame_packet.html")

print("DONE:", sorted(os.listdir(OUT)))
