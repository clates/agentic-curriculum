"""Generate a demo HTML packet exercising every newly ported worksheet type with filled pages."""
import os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "src"))

from worksheet_html_renderer import render_worksheet_html, build_print_packet_html

pages = []

# ── Page 1: Venn Diagram (full page: diagram + word bank) ──
pages.append(("Monday", render_worksheet_html("vennDiagramWorksheet", {
    "title": "Venn Diagram — Living & Non-Living Things",
    "instructions": "Sort each word into the correct part of the diagram. Cross off each word as you use it.",
    "left_label": "Living", "right_label": "Non-Living", "both_label": "Both?",
    "word_bank": [
        "Dog", "Rock", "Tree", "Car", "Mushroom", "Water",
        "Fish", "Chair", "Flower", "Cloud", "Bird", "Book",
        "Coral", "Fire", "Bacteria", "Sunlight",
    ],
    "left_items": ["Elephant"],
    "right_items": ["Pencil"],
    "both_items": [],
}, "Monday")))

# ── Page 2: Handwriting (full grid: 3×2 = 6 words) ──
pages.append(("Monday", render_worksheet_html("handwritingWorksheet", {
    "title": "Handwriting Practice — Animals",
    "instructions": "Trace each word on the dashed line, then write it on the ruled lines below.",
    "items": [
        {"text": "cat"}, {"text": "dog"}, {"text": "bird"},
        {"text": "fish"}, {"text": "frog"}, {"text": "bear"},
    ],
    "rows": 3, "cols": 2,
}, "Monday")))

# ── Page 3: Pixel Copy (12×12 grid — substantial) ──
pages.append(("Tuesday", render_worksheet_html("pixelCopyWorksheet", {
    "title": "Pixel Copy — Color Grid",
    "instructions": "Look carefully at the reference grid on the left. Copy each color into the matching square on the right.",
    "image_path": "/nonexistent.png",
    "grid_size": 12,
}, "Tuesday")))

# ── Page 4: Alphabet (letter B — trace, practice, words) ──
pages.append(("Tuesday", render_worksheet_html("alphabetWorksheet", {
    "title": "Alphabet Practice — Letter B",
    "instructions": "Practice writing the letter B and reading words with B!",
    "letter": "B",
    "starting_words": ["Ball", "Bear", "Bird", "Blue", "Boat", "Book"],
    "containing_words": ["Cabbage", "Rabbit", "Table", "Zebra", "Cabin", "Bubble"],
}, "Tuesday")))

# ── Page 5: Sequencing (6 steps with room for cut-out cards) ──
pages.append(("Wednesday", render_worksheet_html("sequencingWorksheet", {
    "title": "Sequencing — How to Make a Sandwich",
    "instructions": "Cut out each step card below. Paste them in the correct order on another sheet of paper.",
    "activity_name": "Making a Peanut Butter & Jelly Sandwich",
    "steps": [
        {"text": "Get two slices of bread", "correct_order": 1},
        {"text": "Spread peanut butter on one slice", "correct_order": 2},
        {"text": "Spread jelly on the other slice", "correct_order": 3},
        {"text": "Put the two slices together", "correct_order": 4},
        {"text": "Cut the sandwich in half", "correct_order": 5},
        {"text": "Put it on a plate and enjoy!", "correct_order": 6},
    ],
}, "Wednesday")))

# ── Page 6: Fill in the Blank (longer passage with more gaps) ──
pages.append(("Wednesday", render_worksheet_html("fillInBlankWorksheet", {
    "title": "Fill in the Blank — Our Solar System",
    "instructions": "Use the word bank to fill in each blank. Each word is used once.",
    "segments": [
        {"text": "Our solar system has eight "}, {"gap": 1}, {"text": " that orbit the "}, {"gap": 2}, {"text": "."},
        {"newline": True},
        {"text": "The closest planet is "}, {"gap": 3}, {"text": ", and the largest is "}, {"gap": 4}, {"text": "."},
        {"newline": True},
        {"text": "Earth is the "}, {"gap": 5}, {"text": " planet from the Sun and the only one known to have "}, {"gap": 6}, {"text": "."},
        {"newline": True},
        {"text": "Beyond the planets lies the "}, {"gap": 7}, {"text": " belt, full of rocky objects."},
    ],
    "word_bank": ["planets", "Sun", "Mercury", "Jupiter", "third", "life", "asteroid"],
    "answers": {"1": "planets", "2": "Sun", "3": "Mercury", "4": "Jupiter", "5": "third", "6": "life", "7": "asteroid"},
}, "Wednesday")))

# ── Page 7: Story Map (4 fields with generous writing space) ──
pages.append(("Thursday", render_worksheet_html("storyMapWorksheet", {
    "title": "Story Map — The Three Little Pigs",
    "instructions": "Fill in each box with details from the story.",
    "story_title_field": True,
    "fields": [
        {"label": "Characters", "prompt": "Who is in the story? List all the characters.", "lines": 3},
        {"label": "Setting", "prompt": "Where and when does the story take place?", "lines": 2},
        {"label": "Problem", "prompt": "What is the main problem in the story?", "lines": 3},
        {"label": "Solution", "prompt": "How do the characters solve the problem?", "lines": 3},
    ],
}, "Thursday")))

# ── Page 8: Number Lines (3 tasks to fill the page) ──
pages.append(("Thursday", render_worksheet_html("numberLineWorksheet", {
    "title": "Number Lines — Count by 1s, 2s, and 5s",
    "instructions": "Fill in the missing numbers on each number line.",
    "tasks": [
        {"start": 0, "end": 10, "step": 1, "hidden_positions": [3, 7], "mark_positions": [5], "prompt": "1. Count from 0 to 10"},
        {"start": 0, "end": 20, "step": 2, "hidden_positions": [8, 14], "mark_positions": [10], "prompt": "2. Count by 2s from 0 to 20"},
        {"start": 0, "end": 50, "step": 5, "hidden_positions": [15, 30, 45], "mark_positions": [25], "prompt": "3. Count by 5s from 0 to 50"},
    ],
}, "Thursday")))

# ── Page 9: Labeled Diagram (6 labels — fills page) ──
pages.append(("Friday", render_worksheet_html("labeledDiagramWorksheet", {
    "title": "Labeled Diagram — Parts of a Flower",
    "instructions": "Write the correct label for each numbered part. Use the word bank if you need help.",
    "image_path": None,
    "labels": [
        {"number": 1, "answer": "Petals"},
        {"number": 2, "answer": "Stamen"},
        {"number": 3, "answer": "Pistil"},
        {"number": 4, "answer": "Sepal"},
        {"number": 5, "answer": "Stem"},
        {"number": 6, "answer": "Roots"},
    ],
    "word_bank": True,
}, "Friday")))

# ── Page 10: Two-Operand Math (16 problems in a 4×4 grid) ──
math_problems = []
ops = ["+", "-", "+", "+", "-", "+", "-", "+", "+", "-", "+", "-", "+", "+", "-", "+"]
for i in range(16):
    a = 10 + (i * 7) % 40
    b = 3 + (i * 5) % 20
    math_problems.append({"operand_one": a, "operand_two": b, "operator": ops[i]})

pages.append(("Friday", render_worksheet_html("twoOperandWorksheet", {
    "title": "Math Practice — Addition & Subtraction",
    "instructions": "Solve each problem. Show your work in the box.",
    "problems": math_problems,
}, "Friday")))

# Build the packet
packet_html = build_print_packet_html(pages, "HTML Migration — All 10 New Types")

outdir = os.path.join(ROOT, "docs", "previews", "html-migration")
os.makedirs(outdir, exist_ok=True)
outpath = os.path.join(outdir, "all_types_packet.html")
with open(outpath, "w") as f:
    f.write(packet_html)

print(f"Packet written: {outpath}")
print(f"Size: {len(packet_html)} bytes, {packet_html.count('<div class=\"page')} pages")