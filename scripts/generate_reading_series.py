import os

os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import sys

# Ensure we can import from src
sys.path.insert(0, os.path.abspath("src"))

from worksheets.factory import WorksheetFactory
from worksheet_renderer import (
    render_matching_to_image,
    render_matching_to_pdf,
    render_reading_worksheet_to_image,
    render_reading_worksheet_to_pdf,
)


def generate_advanced_toddler_series():
    output_dir = "minecraft_reading_series"
    os.makedirs(output_dir, exist_ok=True)

    # 1. Matching: Word to Image (CVC Focus)
    # Using words that have reliable assets: COD, POT, NET, PIG, TNT
    matching_data = {
        "title": "Read and Match!",
        "instructions": "Read the word on the left. Draw a line to the picture that matches!",
        "pairs": [
            {"left_text": "PIG", "right_image_path": "assets/pig.png"},
            {"left_text": "TNT", "right_image_path": "assets/tnt.png"},
            {"left_text": "NET", "right_image_path": "assets/net.png"},
            {"left_text": "COD", "right_image_path": "assets/cod.png"},
            {"left_text": "POT", "right_image_path": "assets/pot.png"},
        ],
    }
    # Note: Matching pairs are usually shuffled in the renderer or script
    import random

    random.shuffle(matching_data["pairs"])

    ws_match = WorksheetFactory.create("matching", matching_data)
    render_matching_to_image(ws_match, f"{output_dir}/01_read_and_match.png")
    render_matching_to_pdf(ws_match, f"{output_dir}/01_read_and_match.pdf")

    # 2. Reading Comprehension: Simple CVC/CCVC Story
    reading_data = {
        "title": "A Day in the Mine",
        "passage_title": "The Big Dig",
        "passage": "I see a pig. The pig is big. I dig a pit. I get mud. I see a bug. The bug is on a web. I go to my bed. I rest.",
        "instructions": "Read the story. Then answer the questions.",
        "questions": [
            {"prompt": "What animal do I see?", "response_lines": 1},
            {"prompt": "Where is the bug?", "response_lines": 1},
            {"prompt": "Where do I go to rest?", "response_lines": 1},
        ],
        "vocabulary": [
            {"term": "DIG", "definition": "To make a hole."},
            {"term": "PIT", "definition": "A big hole in the ground."},
            {"term": "REST", "definition": "To sleep or be still."},
        ],
    }
    ws_read = WorksheetFactory.create("reading_comprehension", reading_data)
    render_reading_worksheet_to_image(ws_read, f"{output_dir}/02_simple_reading.png")
    render_reading_worksheet_to_pdf(ws_read, f"{output_dir}/02_simple_reading.pdf")

    # 3. Silhouette Matching (Visual CCVC)
    # Using Wolf, Creeper, Skeleton, Zombie
    shadow_data = {
        "title": "Who's That Mob?",
        "instructions": "Match the Minecraft mob to its shadow!",
        "pairs": [
            {
                "left_image_path": "assets/wolf.png",
                "right_image_path": "assets/wolf.png",
                "right_as_shadow": True,
            },
            {
                "left_image_path": "assets/creeper.png",
                "right_image_path": "assets/creeper.png",
                "right_as_shadow": True,
            },
            {
                "left_image_path": "assets/skeleton.png",
                "right_image_path": "assets/skeleton.png",
                "right_as_shadow": True,
            },
            {
                "left_image_path": "assets/zombie.png",
                "right_image_path": "assets/zombie.png",
                "right_as_shadow": True,
            },
        ],
    }
    random.shuffle(shadow_data["pairs"])

    ws_shadow = WorksheetFactory.create("matching", shadow_data)
    render_matching_to_image(ws_shadow, f"{output_dir}/03_mob_shadows.png")
    render_matching_to_pdf(ws_shadow, f"{output_dir}/03_mob_shadows.pdf")

    print(f"Successfully generated advanced toddler series in {output_dir}/")


if __name__ == "__main__":
    generate_advanced_toddler_series()
