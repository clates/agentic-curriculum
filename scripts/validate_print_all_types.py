"""Validate: generate HTML packet for all 10 ported types, screenshot + PDF.
Usage: .hermes-venv/bin/python scripts/validate_print_all_types.py
"""
import os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "src"))
os.chdir(ROOT)

from pathlib import Path

from worksheet_html_renderer import render_worksheet_html, build_print_packet_html

OUT = Path("docs/previews/print-validation")
OUT.mkdir(parents=True, exist_ok=True)

MONDAY = "#1d4ed8"

packets = [
    # (day_label, html_fragment) — one per ported type
    ("Venn Diagram", render_worksheet_html("vennDiagramWorksheet", {
        "title": "Venn Diagram — Animals",
        "left_label": "Mammals", "right_label": "Birds", "both_label": "Both",
        "word_bank": ["dog", "eagle", "bat", "whale", "penguin", "ostrich", "cat"],
        "left_items": ["dog", "cat"], "both_items": ["bat", "whale"],
        "right_items": ["eagle", "penguin", "ostrich"],
    }, "Monday")),
    ("Handwriting", render_worksheet_html("handwritingWorksheet", {
        "title": "Handwriting — Animals",
        "rows": 4, "cols": 2,
        "items": [
            {"text": "cat", "image_path": "", "sub_label": "feline"},
            {"text": "dog", "image_path": "", "sub_label": "canine"},
            {"text": "bat", "image_path": ""},
            {"text": "bird", "image_path": ""},
            {"text": "fish", "image_path": ""},
            {"text": "frog", "image_path": ""},
            {"text": "bear", "image_path": ""},
            {"text": "deer", "image_path": ""},
        ],
    }, "Monday")),
    ("Pixel Copy", render_worksheet_html("pixelCopyWorksheet", {
        "title": "Pixel Copy — Pattern", "grid_size": 16,
        "image_path": "", "instructions": "Copy the pattern on the left to the grid on the right!",
    }, "Monday")),
    ("Alphabet", render_worksheet_html("alphabetWorksheet", {
        "title": "Alphabet — Letter B", "letter": "B",
        "starting_words": ["ball", "bat", "bed", "big", "blue"],
        "containing_words": ["cabin", "rabbit", "table", "umbrella"],
    }, "Monday")),
    ("Sequencing", render_worksheet_html("sequencingWorksheet", {
        "title": "Sequencing — Morning Routine", "activity_name": "Morning Routine",
        "steps": [
            {"text": "Wake up", "correct_order": 1},
            {"text": "Brush teeth", "correct_order": 2},
            {"text": "Eat breakfast", "correct_order": 3},
            {"text": "Get dressed", "correct_order": 4},
            {"text": "Go to school", "correct_order": 5},
        ],
    }, "Monday")),
    ("Fill In Blank", render_worksheet_html("fillInBlankWorksheet", {
        "title": "Fill in the Blank — Seasons",
        "segments": [
            {"text": "In "}, {"gap": 1}, {"text": ", flowers bloom and birds return."},
            {"newline": True},
            {"text": "In "}, {"gap": 2}, {"text": ", it is hot and we go swimming."},
            {"newline": True},
            {"text": "In autumn, "}, {"gap": 3}, {"text": " fall from the trees."},
            {"newline": True},
            {"text": "In "}, {"gap": 4}, {"text": ", snow covers the ground."},
        ],
        "word_bank": ["spring", "summer", "leaves", "winter"],
        "answers": {"1": "spring", "2": "summer", "3": "leaves", "4": "winter"},
    }, "Monday")),
    ("Story Map", render_worksheet_html("storyMapWorksheet", {
        "title": "Story Map — The Three Little Pigs",
        "fields": [
            {"label": "Characters", "prompt": "Who is in the story?", "lines": 3},
            {"label": "Setting", "prompt": "Where does it happen?", "lines": 2},
            {"label": "Problem", "prompt": "What goes wrong?", "lines": 2},
            {"label": "Solution", "prompt": "How is it fixed?", "lines": 2},
        ],
    }, "Monday")),
    ("Number Line", render_worksheet_html("numberLineWorksheet", {
        "title": "Number Line — 0 to 20",
        "tasks": [
            {"start": 0, "end": 20, "step": 2, "hidden_positions": [4, 8, 12, 16], "prompt": "Fill in the missing even numbers:"},
            {"start": 0, "end": 15, "step": 5, "hidden_positions": [5, 10], "mark_positions": [15], "prompt": "Mark 15 on the line:"},
        ],
    }, "Monday")),
    ("Labeled Diagram", render_worksheet_html("labeledDiagramWorksheet", {
        "title": "Labeled Diagram — Plant",
        "labels": [
            {"number": 1, "answer": "Flower", "hint": "colorful part"},
            {"number": 2, "answer": "Stem", "hint": "green stalk"},
            {"number": 3, "answer": "Leaves", "hint": "catch sunlight"},
            {"number": 4, "answer": "Roots", "hint": "underground"},
        ],
        "word_bank": True, "image_path": "",
    }, "Monday")),
    ("Two Operand", render_worksheet_html("twoOperandWorksheet", {
        "title": "Two-Operand Addition",
        "problems": [
            {"operand_one": 23, "operand_two": 45, "operator": "+"},
            {"operand_one": 67, "operand_two": 12, "operator": "+"},
            {"operand_one": 54, "operand_two": 31, "operator": "+"},
            {"operand_one": 89, "operand_two": 10, "operator": "+"},
            {"operand_one": 34, "operand_two": 56, "operator": "+"},
            {"operand_one": 18, "operand_two": 72, "operator": "+"},
            {"operand_one": 91, "operand_two": 15, "operator": "+"},
            {"operand_one": 43, "operand_two": 27, "operator": "+"},
            {"operand_one": 65, "operand_two": 33, "operator": "+"},
            {"operand_one": 12, "operand_two": 88, "operator": "+"},
            {"operand_one": 76, "operand_two": 24, "operator": "+"},
            {"operand_one": 39, "operand_two": 41, "operator": "+"},
            {"operand_one": 57, "operand_two": 19, "operator": "+"},
            {"operand_one": 83, "operand_two": 11, "operator": "+"},
            {"operand_one": 25, "operand_two": 64, "operator": "+"},
            {"operand_one": 99, "operand_two": 50, "operator": "+"},
        ],
    }, "Monday")),
]

# Build packet
pages = [(label, html or "") for label, html in packets]
packet_html = build_print_packet_html(pages, "Print Validation — All 10 Ported Types")

packet_path = OUT / "all_10_types.html"
packet_path.write_text(packet_html)
print(f"Packet: {packet_path} ({packet_path.stat().st_size} bytes, {len(packets)} pages)")

# Verify page count
page_count = packet_html.count('<div class="page')
print(f"Page divs: {page_count}")
assert page_count == len(packets), f"Expected {len(packets)} pages, got {page_count}"
print("✓ Page count matches")