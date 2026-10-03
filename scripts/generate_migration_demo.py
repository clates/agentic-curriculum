"""Generate a demo HTML packet exercising every newly ported worksheet type."""
import os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "src"))

from worksheet_html_renderer import render_worksheet_html, build_print_packet_html

pages = []

# 1. Venn diagram
pages.append(("Monday", render_worksheet_html("vennDiagramWorksheet", {
    "title": "Venn Diagram — Animals & Plants",
    "instructions": "Sort each word into the correct part of the diagram.",
    "left_label": "Animals", "right_label": "Plants", "both_label": "Both",
    "word_bank": ["Dog", "Tree", "Mushroom", "Fish", "Flower", "Coral"],
    "left_items": ["Elephant"],
    "right_items": ["Oak Tree"],
    "both_items": [],
}, "Monday")))

# 2. Handwriting
pages.append(("Monday", render_worksheet_html("handwritingWorksheet", {
    "title": "Handwriting Practice — Animals",
    "instructions": "Trace each word, then write it on the lines below.",
    "items": [
        {"text": "cat", "image_path": None},
        {"text": "dog", "image_path": None},
        {"text": "bird", "image_path": None},
        {"text": "fish", "image_path": None},
    ],
    "rows": 2, "cols": 2,
}, "Monday")))

# 3. Pixel copy
pages.append(("Tuesday", render_worksheet_html("pixelCopyWorksheet", {
    "title": "Pixel Copy — Color Grid",
    "instructions": "Copy the colors from the left grid into the right grid.",
    "image_path": "/nonexistent.png",
    "grid_size": 8,
}, "Tuesday")))

# 4. Alphabet
pages.append(("Tuesday", render_worksheet_html("alphabetWorksheet", {
    "title": "Alphabet Practice — Letter B",
    "instructions": "Practice writing the letter B and reading B words!",
    "letter": "B",
    "starting_words": ["Ball", "Bear", "Bird", "Blue"],
    "containing_words": ["Cabbage", "Rabbit", "Table", "Zebra"],
}, "Tuesday")))

# 5. Sequencing
pages.append(("Wednesday", render_worksheet_html("sequencingWorksheet", {
    "title": "Sequencing — Brush Your Teeth",
    "instructions": "Cut out each step and paste them in the correct order.",
    "activity_name": "Brushing Your Teeth",
    "steps": [
        {"text": "Put toothpaste on the toothbrush", "correct_order": 1},
        {"text": "Wet the toothbrush with water", "correct_order": 2},
        {"text": "Brush all your teeth for 2 minutes", "correct_order": 3},
        {"text": "Rinse your mouth with water", "correct_order": 4},
    ],
}, "Wednesday")))

# 6. Fill in the blank
pages.append(("Wednesday", render_worksheet_html("fillInBlankWorksheet", {
    "title": "Fill in the Blank — Our Solar System",
    "instructions": "Use the word bank to fill in each blank.",
    "segments": [
        {"text": "The "}, {"gap": 1}, {"text": " is the star at the center of our solar system."},
        {"newline": True},
        {"text": "The "}, {"gap": 2}, {"text": " is the closest planet to the Sun."},
        {"newline": True},
        {"text": "Earth has one "}, {"gap": 3}, {"text": " that orbits around it."},
    ],
    "word_bank": ["Sun", "Mercury", "moon"],
    "answers": {"1": "Sun", "2": "Mercury", "3": "moon"},
}, "Wednesday")))

# 7. Story map
pages.append(("Thursday", render_worksheet_html("storyMapWorksheet", {
    "title": "Story Map — The Three Little Pigs",
    "instructions": "Fill in each box about the story you read.",
    "story_title_field": True,
    "fields": [
        {"label": "Characters", "prompt": "Who is in the story?", "lines": 2},
        {"label": "Setting", "prompt": "Where does the story happen?", "lines": 1},
        {"label": "Problem", "prompt": "What goes wrong?", "lines": 2},
        {"label": "Solution", "prompt": "How is the problem fixed?", "lines": 2},
    ],
}, "Thursday")))

# 8. Number line
pages.append(("Thursday", render_worksheet_html("numberLineWorksheet", {
    "title": "Number Lines — Count by 1s and 2s",
    "instructions": "Fill in the missing numbers on each number line.",
    "tasks": [
        {"start": 0, "end": 10, "step": 1, "hidden_positions": [3, 7], "mark_positions": [5], "prompt": "Count from 0 to 10"},
        {"start": 0, "end": 20, "step": 2, "hidden_positions": [8, 14], "mark_positions": [10], "prompt": "Count by 2s from 0 to 20"},
    ],
}, "Thursday")))

# 9. Labeled diagram
pages.append(("Friday", render_worksheet_html("labeledDiagramWorksheet", {
    "title": "Labeled Diagram — Parts of a Flower",
    "instructions": "Label each part of the flower using the word bank.",
    "image_path": None,
    "labels": [
        {"number": 1, "answer": "Petals"},
        {"number": 2, "answer": "Stem"},
        {"number": 3, "answer": "Leaves"},
        {"number": 4, "answer": "Roots"},
    ],
    "word_bank": True,
}, "Friday")))

# 10. Two-operand math
pages.append(("Friday", render_worksheet_html("twoOperandWorksheet", {
    "title": "Math Practice — Addition & Subtraction",
    "instructions": "Solve each problem in the box.",
    "problems": [
        {"operand_one": 23, "operand_two": 15, "operator": "+"},
        {"operand_one": 47, "operand_two": 28, "operator": "-"},
        {"operand_one": 56, "operand_two": 34, "operator": "+"},
        {"operand_one": 31, "operand_two": 19, "operator": "+"},
    ],
}, "Friday")))

# Build the packet
packet_html = build_print_packet_html(pages, "PIL-to-HTML Migration — All 10 New Types")

outdir = os.path.join(ROOT, "docs", "previews", "html-migration")
os.makedirs(outdir, exist_ok=True)
outpath = os.path.join(outdir, "all_types_packet.html")
with open(outpath, "w") as f:
    f.write(packet_html)

print(f"Packet written: {outpath}")
print(f"Size: {len(packet_html)} bytes, {packet_html.count('<div class=\"page')} pages")