"""Generate the cut-and-sequence worksheet series for ages 5-6.

Each worksheet shows 5 steps of a simple daily (or Minecraft) activity in a
shuffled order.  Students cut out the cards and paste them back in the correct
sequence.  An answer-key version is also produced for each activity.

Run with:
    venv/bin/python3 generate_sequencing_series.py
"""

import os

os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import random
import sys

sys.path.insert(0, os.path.abspath("src"))

from worksheets.factory import WorksheetFactory
from worksheet_renderer import render_sequencing_to_image, render_sequencing_to_pdf

OUTPUT_DIR = "sequencing_series"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# ---------------------------------------------------------------------------
# Activity definitions
# Each step dict has:
#   text         – short, child-readable label
#   correct_order – 1-based position in the correct sequence
#   image_path   – optional path to an asset image
# ---------------------------------------------------------------------------

ACTIVITIES = [
    # 1. Making a Bowl of Cereal
    {
        "activity_name": "Making a Bowl of Cereal",
        "title": "Making a Bowl of Cereal",
        "instructions": (
            "Cut out each step. Paste the cards in the correct order to show how to make cereal!"
        ),
        "steps": [
            {"text": "Get a bowl from the cabinet.", "correct_order": 1},
            {"text": "Pour the cereal into the bowl.", "correct_order": 2},
            {"text": "Add milk to the bowl.", "correct_order": 3},
            {"text": "Pick up a spoon and eat!", "correct_order": 4},
            {"text": "Put the bowl in the sink.", "correct_order": 5},
        ],
    },
    # 2. Getting Dressed
    {
        "activity_name": "Getting Dressed",
        "title": "Getting Dressed",
        "instructions": (
            "Cut out each step. Paste the cards in the correct order to show how to get dressed!"
        ),
        "steps": [
            {"text": "Pick out your clothes.", "correct_order": 1},
            {"text": "Put on your underwear.", "correct_order": 2},
            {"text": "Put on your shirt.", "correct_order": 3},
            {"text": "Put on your pants.", "correct_order": 4},
            {"text": "Put on your shoes.", "correct_order": 5},
        ],
    },
    # 3. Brushing Teeth
    {
        "activity_name": "Brushing Teeth",
        "title": "Brushing Teeth",
        "instructions": (
            "Cut out each step. Paste the cards in the correct order to show how to brush your teeth!"
        ),
        "steps": [
            {"text": "Get your toothbrush.", "correct_order": 1},
            {"text": "Put toothpaste on the brush.", "correct_order": 2},
            {"text": "Brush all your teeth.", "correct_order": 3},
            {"text": "Rinse your mouth with water.", "correct_order": 4},
            {"text": "Put your toothbrush away.", "correct_order": 5},
        ],
    },
    # 4. Washing Hands
    {
        "activity_name": "Washing Hands",
        "title": "Washing Hands",
        "instructions": (
            "Cut out each step. Paste the cards in the correct order to show how to wash your hands!"
        ),
        "steps": [
            {"text": "Turn on the water.", "correct_order": 1},
            {"text": "Wet your hands.", "correct_order": 2},
            {"text": "Add soap and scrub.", "correct_order": 3},
            {"text": "Rinse the soap off.", "correct_order": 4},
            {"text": "Dry your hands with a towel.", "correct_order": 5},
        ],
    },
    # 5. Planting a Seed (Minecraft crossover!)
    {
        "activity_name": "Planting a Seed (Minecraft!)",
        "title": "Planting a Seed (Minecraft!)",
        "instructions": (
            "Cut out each step. Paste the cards in the correct order to grow your Minecraft crop!"
        ),
        "steps": [
            {
                "text": "Use a hoe to till the dirt.",
                "correct_order": 1,
                "image_path": "assets/dirt.png",
            },
            {
                "text": "Plant the seed in the tilled dirt.",
                "correct_order": 2,
                "image_path": "assets/grass_block.png",
            },
            {
                "text": "Use a water bucket to water the soil.",
                "correct_order": 3,
                "image_path": "assets/mud.png",
            },
            {
                "text": "Wait for the plant to grow!",
                "correct_order": 4,
                "image_path": "assets/log.png",
            },
            {
                "text": "Harvest the crop with your hand.",
                "correct_order": 5,
                "image_path": "assets/villager.png",
            },
        ],
    },
]

# ---------------------------------------------------------------------------
# Generate student and answer-key versions for each activity
# ---------------------------------------------------------------------------

random.seed(42)  # reproducible shuffle

for i, activity in enumerate(ACTIVITIES, start=1):
    slug = (
        activity["activity_name"]
        .lower()
        .replace(" ", "_")
        .replace("(", "")
        .replace(")", "")
        .replace("!", "")
    )
    slug = "".join(c if c.isalnum() or c == "_" else "" for c in slug).strip("_")

    # Shuffle the steps for the student version
    shuffled_steps = activity["steps"][:]
    random.shuffle(shuffled_steps)

    # --- Student worksheet (no answers shown) ---
    student_payload = {
        "title": activity["title"],
        "activity_name": activity["activity_name"],
        "instructions": activity["instructions"],
        "steps": shuffled_steps,
        "show_answers": False,
    }
    ws_student = WorksheetFactory.create("sequencing", student_payload)
    render_sequencing_to_image(ws_student, f"{OUTPUT_DIR}/{i:02d}_{slug}_student.png")
    render_sequencing_to_pdf(ws_student, f"{OUTPUT_DIR}/{i:02d}_{slug}_student.pdf")
    print(f"[{i}] Generated student: {slug}")

    # --- Answer key (correct order numbers shown in red) ---
    answer_payload = {
        "title": activity["title"] + " — Answer Key",
        "activity_name": activity["activity_name"],
        "instructions": activity["instructions"],
        "steps": shuffled_steps,
        "show_answers": True,
    }
    ws_answer = WorksheetFactory.create("sequencing", answer_payload)
    render_sequencing_to_image(ws_answer, f"{OUTPUT_DIR}/{i:02d}_{slug}_answer_key.png")
    render_sequencing_to_pdf(ws_answer, f"{OUTPUT_DIR}/{i:02d}_{slug}_answer_key.pdf")
    print(f"[{i}] Generated answer key: {slug}")

print(f"\nDone! All files saved to: {OUTPUT_DIR}/")
