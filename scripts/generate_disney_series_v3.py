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


def generate_disney_series_v3():
    output_dir = "disney_series_v3"
    os.makedirs(output_dir, exist_ok=True)

    # Updated character mapping: Replacing Dumbo (BIG) with Olaf (SNOW)
    disney_items = [
        {"word": "FISH", "image": "assets/disney_api/nemo.jpg", "desc": "Nemo"},
        {"word": "DOG", "image": "assets/disney_api/bolt.jpg", "desc": "Bolt"},
        {"word": "BOT", "image": "assets/disney_api/walle.png", "desc": "Wall-E"},
        {"word": "SNOW", "image": "assets/disney_api/olaf.jpg", "desc": "Frozen"},
        {"word": "DRAG", "image": "assets/disney_api/mushu.jpg", "desc": "Mulan"},
        {"word": "PIG", "image": "assets/disney_api/pua.jpg", "desc": "Moana"},
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

    print(f"Successfully regenerated Disney series v3 (replaced Dumbo with Olaf) in {output_dir}/")


if __name__ == "__main__":
    generate_disney_series_v3()
