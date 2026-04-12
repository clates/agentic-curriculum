import os

os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import sys
import random

# Ensure we can import from src
sys.path.insert(0, os.path.abspath("src"))

from worksheets.factory import WorksheetFactory
from worksheet_renderer import (
    render_matching_to_image,
    render_matching_to_pdf,
    render_handwriting_to_image,
    render_handwriting_to_pdf,
)


def generate_disney_series():
    output_dir = "disney_series_v2"
    os.makedirs(output_dir, exist_ok=True)

    # Character/Item mapping from Disney API
    disney_items = [
        {"word": "CAT", "image": "assets/disney_api/simba.jpg", "desc": "Lion King"},
        {"word": "SNOW", "image": "assets/disney_api/olaf.jpg", "desc": "Frozen"},
        {"word": "RAFT", "image": "assets/disney_api/moana.png", "desc": "Moana"},
        {"word": "DRAG", "image": "assets/disney_api/mushu.jpg", "desc": "Mulan"},
        {"word": "PIG", "image": "assets/disney_api/pua.jpg", "desc": "Moana"},
        {"word": "DEER", "image": "assets/disney_api/sven.jpg", "desc": "Frozen"},
        {"word": "BIRD", "image": "assets/disney_api/zazu.jpg", "desc": "Lion King"},
        {"word": "HEN", "image": "assets/disney_api/heihei.jpg", "desc": "Moana"},
    ]

    # 1. Disney Character Match
    matching_pool = disney_items[:]
    shuffled_right = matching_pool[:]
    random.shuffle(shuffled_right)

    matching_data = {
        "title": "Disney Friends Match",
        "instructions": "Read the word. Match it to the Disney friend!",
        "left_items": [{"text": item["word"]} for item in matching_pool],
        "right_items": [{"image_path": item["image"]} for item in shuffled_right],
    }

    ws_matching = WorksheetFactory.create("matching", matching_data)
    render_matching_to_image(ws_matching, f"{output_dir}/01_disney_match.png")
    render_matching_to_pdf(ws_matching, f"{output_dir}/01_disney_match.pdf")

    # 2. Disney Handwriting
    handwriting_pool = disney_items[:]
    random.shuffle(handwriting_pool)
    handwriting_data = {
        "title": "Disney Words Handwriting",
        "instructions": "Practice writing these Disney words!",
        "items": [
            {"text": item["word"], "image_path": item["image"], "sub_label": item["desc"]}
            for item in handwriting_pool
        ],
        "rows": 4,
        "cols": 2,
    }

    ws_handwriting = WorksheetFactory.create("handwriting", handwriting_data)
    render_handwriting_to_image(ws_handwriting, f"{output_dir}/02_disney_handwriting.png")
    render_handwriting_to_pdf(ws_handwriting, f"{output_dir}/02_disney_handwriting.pdf")

    # 3. Disney Shadow Match
    shadow_pool = disney_items[:]
    shadow_shuffled_right = shadow_pool[:]
    random.shuffle(shadow_shuffled_right)

    shadow_data = {
        "title": "Disney Mystery Shadows",
        "instructions": "Can you match the Disney friend to its mystery shadow?",
        "left_items": [{"image_path": item["image"]} for item in shadow_pool],
        "right_items": [
            {"image_path": item["image"], "as_shadow": True} for item in shadow_shuffled_right
        ],
    }

    ws_shadow = WorksheetFactory.create("matching", shadow_data)
    render_matching_to_image(ws_shadow, f"{output_dir}/03_disney_shadows.png")
    render_matching_to_pdf(ws_shadow, f"{output_dir}/03_disney_shadows.pdf")

    print(f"Successfully generated Disney series v2 in {output_dir}/")


if __name__ == "__main__":
    generate_disney_series()
