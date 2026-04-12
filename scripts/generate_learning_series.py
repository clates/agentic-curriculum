import os

os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import sys

# Ensure we can import from src
sys.path.insert(0, os.path.abspath("src"))

from worksheets.factory import WorksheetFactory
from worksheet_renderer import (
    render_handwriting_to_image,
    render_pixel_copy_to_image,
    render_odd_one_out_to_image,
    render_handwriting_to_pdf,
    render_pixel_copy_to_pdf,
    render_odd_one_out_to_pdf,
)


def generate_toddler_series():
    output_dir = "minecraft_learning_series"
    os.makedirs(output_dir, exist_ok=True)

    # 1. Handwriting: Simple Words
    # Using Pig (CVC), TNT (CVC-ish), Mud (CVC - using dirt icon), Wolf (CCVC)
    handwriting_data = {
        "title": "My First Minecraft Words",
        "instructions": "Look at the picture. Trace the word and then try to write it yourself!",
        "items": [
            {"text": "PIG", "image_path": "assets/pig.png", "sub_label": "p-i-g"},
            {"text": "TNT", "image_path": "assets/tnt.png", "sub_label": "t-n-t"},
            {"text": "MUD", "image_path": "assets/dirt.png", "sub_label": "m-u-d"},
            {"text": "WOLF", "image_path": "assets/wolf.png", "sub_label": "w-o-l-f"},
        ],
        "rows": 2,
        "cols": 2,
    }
    ws_hw = WorksheetFactory.create("handwriting", handwriting_data)
    render_handwriting_to_image(ws_hw, f"{output_dir}/01_handwriting_words.png")
    render_handwriting_to_pdf(ws_hw, f"{output_dir}/01_handwriting_words.pdf")

    # 2. Pixel Copy: Simple TNT
    # TNT is great for beginners because it's mostly red and white squares.
    pixel_copy_data = {
        "title": "Pixel Art: TNT",
        "instructions": "Copy the colors into the empty squares to make your own TNT!",
        "image_path": "assets/tnt.png",
        "grid_size": 8,  # Nice big squares for a 3-year-old
    }
    ws_pc = WorksheetFactory.create("pixel_copy", pixel_copy_data)
    render_pixel_copy_to_image(ws_pc, f"{output_dir}/02_pixel_copy_tnt.png")
    render_pixel_copy_to_pdf(ws_pc, f"{output_dir}/02_pixel_copy_tnt.pdf")

    # 3. Odd One Out: Visual Recognition
    odd_one_out_data = {
        "title": "Which One is Different?",
        "instructions": "Find the one that does not belong and draw a big X over it!",
        "rows": [
            {
                "items": [
                    {"text": "PIG", "image_path": "assets/pig.png"},
                    {"text": "PIG", "image_path": "assets/pig.png"},
                    {"text": "CREEPER", "image_path": "assets/creeper.png"},
                    {"text": "PIG", "image_path": "assets/pig.png"},
                ],
                "odd_item": "CREEPER",
                "explanation": "Three are pink pigs, one is a green creeper.",
            },
            {
                "items": [
                    {"text": "TNT", "image_path": "assets/tnt.png"},
                    {"text": "TNT", "image_path": "assets/tnt.png"},
                    {"text": "TNT", "image_path": "assets/tnt.png"},
                    {"text": "DIRT", "image_path": "assets/dirt.png"},
                ],
                "odd_item": "DIRT",
                "explanation": "Three are TNT blocks, one is a dirt block.",
            },
        ],
    }
    ws_ooo = WorksheetFactory.create("odd_one_out", odd_one_out_data)
    render_odd_one_out_to_image(ws_ooo, f"{output_dir}/03_odd_one_out.png")
    render_odd_one_out_to_pdf(ws_ooo, f"{output_dir}/03_odd_one_out.pdf")

    print(f"Successfully generated toddler learning series in {output_dir}/")


if __name__ == "__main__":
    generate_toddler_series()
