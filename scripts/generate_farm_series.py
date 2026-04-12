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


def generate_farm_series():
    output_dir = "farm_series"
    os.makedirs(output_dir, exist_ok=True)

    # 1. Farm Animals Worksheet
    animal_items = [
        {"word": "PIG", "image": "assets/farm/pig.png"},
        {"word": "COW", "image": "assets/farm/cow.png"},
        {"word": "HEN", "image": "assets/farm/hen.png"},
        {"word": "DOG", "image": "assets/farm/dog.png"},
        {"word": "CAT", "image": "assets/farm/cat.png"},
        {"word": "DUCK", "image": "assets/farm/duck.png"},
        {"word": "GOAT", "image": "assets/farm/goat.png"},
        {"word": "SHEEP", "image": "assets/farm/sheep.png"},
    ]

    shuffled_animals_right = animal_items[:]
    random.shuffle(shuffled_animals_right)

    animals_data = {
        "title": "Farm Animals Match",
        "instructions": "Read the word. Match it to the correct farm animal!",
        "left_items": [{"text": item["word"]} for item in animal_items],
        "right_items": [{"image_path": item["image"]} for item in shuffled_animals_right],
    }

    ws_animals = WorksheetFactory.create("matching", animals_data)
    render_matching_to_image(ws_animals, f"{output_dir}/01_farm_animals_match.png")
    render_matching_to_pdf(ws_animals, f"{output_dir}/01_farm_animals_match.pdf")

    # 2. Farm Handwriting Worksheet (Replaces Things Match)
    handwriting_items = [
        {"text": "PIG", "image_path": "assets/farm/pig.png"},
        {"text": "COW", "image_path": "assets/farm/cow.png"},
        {"text": "HEN", "image_path": "assets/farm/hen.png"},
        {"text": "DOG", "image_path": "assets/farm/dog.png"},
        {"text": "CAT", "image_path": "assets/farm/cat.png"},
        {"text": "TRACTOR", "image_path": "assets/farm/tractor.png"},
        {"text": "BOX", "image_path": "assets/farm/box.png"},
        {"text": "DUCK", "image_path": "assets/farm/duck.png"},
    ]
    # Keep them in a consistent order or shuffle
    random.shuffle(handwriting_items)

    handwriting_data = {
        "title": "Farm Words Handwriting",
        "instructions": "Practice writing these farm words!",
        "items": handwriting_items,
        "rows": 4,
        "cols": 2,
    }

    ws_handwriting = WorksheetFactory.create("handwriting", handwriting_data)
    render_handwriting_to_image(ws_handwriting, f"{output_dir}/02_farm_handwriting.png")
    render_handwriting_to_pdf(ws_handwriting, f"{output_dir}/02_farm_handwriting.pdf")

    # 3. Farm Shadow Match (Animal recognition)

    shadow_left = animal_items[:]
    shadow_right = animal_items[:]
    random.shuffle(shadow_right)

    shadow_data = {
        "title": "Farm Mystery Shadows",
        "instructions": "Can you match the farm animal to its mystery shadow?",
        "left_items": [{"image_path": item["image"]} for item in shadow_left],
        "right_items": [{"image_path": item["image"], "as_shadow": True} for item in shadow_right],
    }

    ws_shadow = WorksheetFactory.create("matching", shadow_data)
    render_matching_to_image(ws_shadow, f"{output_dir}/03_farm_shadows.png")
    render_matching_to_pdf(ws_shadow, f"{output_dir}/03_farm_shadows.pdf")

    print(f"Successfully generated farm series in {output_dir}/")


if __name__ == "__main__":
    generate_farm_series()
