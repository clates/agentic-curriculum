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
)


def generate_mobs_series():
    output_dir = "minecraft_mobs_series"
    os.makedirs(output_dir, exist_ok=True)

    # 1. Animals Worksheet
    animals_items = [
        {"word": "PIG", "image": "assets/pig.png"},
        {"word": "CAT", "image": "assets/cat.png"},
        {"word": "FROG", "image": "assets/frog.png"},
        {"word": "WOLF", "image": "assets/wolf.png"},
        {"word": "BAT", "image": "assets/bat.png"},
        {"word": "COD", "image": "assets/cod.png"},
        {"word": "COW", "image": "assets/cow.png"},
        {"word": "BEE", "image": "assets/bee.png"},
    ]

    shuffled_animals_right = animals_items[:]
    random.shuffle(shuffled_animals_right)

    animals_data = {
        "title": "Minecraft Animals Match",
        "instructions": "Read the word. Match it to the friendly animal!",
        "left_items": [{"text": item["word"]} for item in animals_items],
        "right_items": [{"image_path": item["image"]} for item in shuffled_animals_right],
    }

    ws_animals = WorksheetFactory.create("matching", animals_data)
    render_matching_to_image(ws_animals, f"{output_dir}/animals_match.png")
    render_matching_to_pdf(ws_animals, f"{output_dir}/animals_match.pdf")

    # 2. Bad Guys Worksheet
    bad_guys_items = [
        {"word": "WEB", "image": "assets/web.png"},
        {"word": "CREEP", "image": "assets/creeper.png"},
        {"word": "ZOMBIE", "image": "assets/zombie.png"},
        {"word": "BONE", "image": "assets/skeleton.png"},
        {"word": "TNT", "image": "assets/tnt.png"},
        {"word": "SLIME", "image": "assets/slime.png"},
        {"word": "END", "image": "assets/enderman.png"},
        {"word": "FLY", "image": "assets/phantom.png"},
    ]

    shuffled_bad_guys_right = bad_guys_items[:]
    random.shuffle(shuffled_bad_guys_right)

    bad_guys_data = {
        "title": "Minecraft Monsters Match",
        "instructions": "Be careful! Match the word to the monster or block.",
        "left_items": [{"text": item["word"]} for item in bad_guys_items],
        "right_items": [{"image_path": item["image"]} for item in shuffled_bad_guys_right],
    }

    ws_bad_guys = WorksheetFactory.create("matching", bad_guys_data)
    render_matching_to_image(ws_bad_guys, f"{output_dir}/monsters_match.png")
    render_matching_to_pdf(ws_bad_guys, f"{output_dir}/monsters_match.pdf")

    print(f"Successfully generated mobs series in {output_dir}/")


if __name__ == "__main__":
    generate_mobs_series()
