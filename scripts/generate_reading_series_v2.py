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
    render_reading_worksheet_to_image,
    render_reading_worksheet_to_pdf,
)


def generate_varied_toddler_series():
    output_dir = "minecraft_reading_series_v2"
    os.makedirs(output_dir, exist_ok=True)

    # 1. Matching: Word to Image (CVC Focus - Fresh Words)
    # Using: BAT, CAT, LOG, BED, BOX
    # Shuffling left and right columns independently
    left_words = ["BAT", "CAT", "LOG", "BED", "BOX"]
    right_images = [
        {"image_path": "assets/bat.png", "key": "BAT"},
        {"image_path": "assets/cat.png", "key": "CAT"},
        {"image_path": "assets/log.png", "key": "LOG"},
        {"image_path": "assets/bed.png", "key": "BED"},
        {"image_path": "assets/box.png", "key": "BOX"},
    ]

    # Shuffle right images
    shuffled_right = right_images[:]
    random.shuffle(shuffled_right)

    matching_data = {
        "title": "Fresh Word Match!",
        "instructions": "Read the word on the left. Match it to the block or animal on the right!",
        "left_items": [{"text": w} for w in left_words],
        "right_items": [{"image_path": img["image_path"]} for img in shuffled_right],
    }

    ws_match = WorksheetFactory.create("matching", matching_data)
    render_matching_to_image(ws_match, f"{output_dir}/01_word_match_v2.png")
    render_matching_to_pdf(ws_match, f"{output_dir}/01_word_match_v2.pdf")

    # 2. Reading Comprehension: CCVC & CVCC (Fresh Words)
    # Using: FROG, WOLF, DUST (sand), MOSS, FISH
    reading_data = {
        "title": "The Green Pond",
        "passage_title": "A Hop and a Plop",
        "passage": "I see a green frog. The frog can hop. I see a big wolf. The wolf can run. I find green moss on a rock. I catch a fish in the pond. I get sand on my hands. I am glad!",
        "instructions": "Read about the animals. Then answer the questions.",
        "questions": [
            {"prompt": "What color is the frog?", "response_lines": 1},
            {"prompt": "What can the wolf do?", "response_lines": 1},
            {"prompt": "Where is the green moss?", "response_lines": 1},
        ],
        "vocabulary": [
            {"term": "FROG", "definition": "A small green animal that hops."},
            {"term": "MOSS", "definition": "Green fuzzy stuff on rocks."},
            {"term": "POND", "definition": "A small bit of water."},
        ],
    }
    ws_read = WorksheetFactory.create("reading_comprehension", reading_data)
    render_reading_worksheet_to_image(ws_read, f"{output_dir}/02_reading_v2.png")
    render_reading_worksheet_to_pdf(ws_read, f"{output_dir}/02_reading_v2.pdf")

    # 3. Silhouette Matching (CCVC - Varied)
    # Using: Frog, Bat, Cat, Pig, Skeleton
    silhouette_left = [
        {"image_path": "assets/frog.png", "key": "FROG"},
        {"image_path": "assets/bat.png", "key": "BAT"},
        {"image_path": "assets/cat.png", "key": "CAT"},
        {"image_path": "assets/pig.png", "key": "PIG"},
        {"image_path": "assets/skeleton.png", "key": "SKELETON"},
    ]

    shuffled_silhouette_right = silhouette_left[:]
    random.shuffle(shuffled_silhouette_right)

    shadow_data = {
        "title": "Minecraft Mystery Shadows",
        "instructions": "Can you match the mob to its mystery shadow?",
        "left_items": [{"image_path": item["image_path"]} for item in silhouette_left],
        "right_items": [
            {"image_path": item["image_path"], "as_shadow": True}
            for item in shuffled_silhouette_right
        ],
    }

    ws_shadow = WorksheetFactory.create("matching", shadow_data)
    render_matching_to_image(ws_shadow, f"{output_dir}/03_shadow_match_v2.png")
    render_matching_to_pdf(ws_shadow, f"{output_dir}/03_shadow_match_v2.pdf")

    print(f"Successfully generated varied toddler series in {output_dir}/")


if __name__ == "__main__":
    generate_varied_toddler_series()
