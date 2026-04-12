import os

os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import sys

# Ensure we can import from src
sys.path.insert(0, os.path.abspath("src"))

from worksheets.factory import WorksheetFactory
from worksheet_renderer import (
    render_reading_worksheet_to_image,
    render_reading_worksheet_to_pdf,
)


def generate_nether_series():
    output_dir = "nether_series"
    os.makedirs(output_dir, exist_ok=True)

    # 1: Surviving the Nether
    ws_data = {
        "title": "Minecraft Quest: Surviving the Nether",
        "passage_title": "The Crimson Depths",
        "passage": "The Nether is a dangerous, fiery dimension located deep beneath the Overworld. It is a land of red rocks, glowing lava oceans, and strange creatures. To enter the Nether, a player must build a portal frame out of Obsidian and light it with a Flint and Steel. Once inside, you will find that the ceiling is covered in glowing Glowstone and the ground is often made of Netherrack, a red rock that burns forever.\n\nThere are many different biomes in the Nether. The Crimson Forest is filled with giant red mushrooms and Piglins, while the Warped Forest is a calm, teal-colored woods where Endermen gather. If you find yourself in a Soul Sand Valley, the blue fire and skeleton remains make it a spooky place to explore. Watch out for the Basalt Deltas, where gray ash falls from the sky and sharp rocks make it hard to walk.\n\nSurviving the Nether requires careful preparation. You should always wear at least one piece of Gold armor so the Piglins stay friendly. Bringing a bow is helpful for fighting Ghasts, which are giant floating creatures that shoot explosive fireballs. Most importantly, you should carry a Potion of Fire Resistance or a Golden Apple in case you fall into the vast oceans of lava!",
        "instructions": "Read about the Nether. Then answer the questions and review the vocabulary terms.",
        "questions": [
            {
                "prompt": "What blocks are needed to build a portal to the Nether?",
                "response_lines": 2,
            },
            {
                "prompt": "Why is it important to wear Gold armor when exploring the Nether?",
                "response_lines": 2,
            },
            {
                "prompt": "Name two different biomes found in the Nether and describe what they look like.",
                "response_lines": 3,
            },
            {
                "prompt": "What is a Ghast and how do you defend yourself against one?",
                "response_lines": 2,
            },
            {"prompt": "What items should you bring to stay safe from lava?", "response_lines": 2},
        ],
        "vocabulary": [
            {
                "term": "Netherrack",
                "definition": "A red rock found in the Nether that stays on fire once lit.",
            },
            {
                "term": "Piglin",
                "definition": "A creature that loves gold and will trade with players who wear gold armor.",
            },
            {
                "term": "Obsidian",
                "definition": "A dark, hard volcanic glass used to build portals.",
            },
            {
                "term": "Ghast",
                "definition": "A large, white, floating monster that cries and shoots fireballs.",
            },
        ],
    }

    ws = WorksheetFactory.create("reading_comprehension", ws_data)
    render_reading_worksheet_to_image(ws, f"{output_dir}/nether_survival.png")
    render_reading_worksheet_to_pdf(ws, f"{output_dir}/nether_survival.pdf")

    print(f"Successfully generated Nether reading worksheet in {output_dir}/")


if __name__ == "__main__":
    generate_nether_series()
