import os

os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import sys

# Ensure we can import from src
sys.path.insert(0, os.path.abspath("src"))

from worksheets.factory import WorksheetFactory
from worksheet_renderer import (
    render_reading_worksheet_to_image,
    render_reading_worksheet_to_pdf,
    render_feature_matrix_to_image,
    render_feature_matrix_to_pdf,
)


def generate_series():
    output_dir = "minecraft_series"
    os.makedirs(output_dir, exist_ok=True)

    # 3A: The Magic Table
    ws3a_data = {
        "title": "Minecraft Quest 3A: The Magic Table",
        "passage_title": "The Crafting Table",
        "passage": "In Minecraft, you can make a Crafting Table. You use four Wood Planks to make it. Once you have it, you can make big things like beds and doors. It is like a magic table!",
        "instructions": "Read about the table. Then answer the questions and check the words.",
        "questions": [
            {"prompt": "What do you use to make a Crafting Table?", "response_lines": 2},
            {"prompt": "What can you make with the table?", "response_lines": 2},
            {"prompt": "Why is it like a magic table?", "response_lines": 2},
        ],
        "vocabulary": [
            {"term": "Wood Planks", "definition": "Blocks made from a tree."},
            {"term": "Crafting Table", "definition": "A place where you make tools."},
        ],
    }
    ws3a = WorksheetFactory.create("reading_comprehension", ws3a_data)
    render_reading_worksheet_to_image(ws3a, f"{output_dir}/quest_3a_crafting_table.png")
    render_reading_worksheet_to_pdf(ws3a, f"{output_dir}/quest_3a_crafting_table.pdf")

    # 3B: Making Light
    ws3b_data = {
        "title": "Minecraft Quest 3B: Making Light",
        "passage_title": "The Bright Torch",
        "passage": "Minecraft is dark at night. You need a Torch to see. You make a Torch with one Stick and one Coal. Torches keep the monsters away. They are very bright.",
        "instructions": "Read about the torch. Then answer the questions.",
        "questions": [
            {"prompt": "What two things do you need to make a Torch?", "response_lines": 2},
            {"prompt": "Why do you need a Torch?", "response_lines": 2},
            {"prompt": "Where would you put a Torch?", "response_lines": 2},
        ],
        "vocabulary": [
            {"term": "Stick", "definition": "A small piece of wood."},
            {"term": "Torch", "definition": "A tool that makes light."},
        ],
    }
    ws3b = WorksheetFactory.create("reading_comprehension", ws3b_data)
    render_reading_worksheet_to_image(ws3b, f"{output_dir}/quest_3b_torch.png")
    render_reading_worksheet_to_pdf(ws3b, f"{output_dir}/quest_3b_torch.pdf")

    # 4A: Friendly Friends
    ws4a_data = {
        "title": "Minecraft Quest 4A: Friendly Friends",
        "instructions": "Check the boxes for each animal friend.",
        "items": [
            {"name": "Pig", "checked_properties": ["Is Pink", "Makes an Oink sound"]},
            {"name": "Sheep", "checked_properties": ["Is Fluffy", "Makes a Baa sound"]},
        ],
        "properties": ["Is Pink", "Is Fluffy", "Makes a Baa sound", "Makes an Oink sound"],
        "show_answers": False,
    }
    ws4a = WorksheetFactory.create("feature_matrix", ws4a_data)
    render_feature_matrix_to_image(ws4a, f"{output_dir}/quest_4a_friendly_mobs.png")
    render_feature_matrix_to_pdf(ws4a, f"{output_dir}/quest_4a_friendly_mobs.pdf")

    # 4B: Nighttime Visitors
    ws4b_data = {
        "title": "Minecraft Quest 4B: Nighttime Visitors",
        "passage_title": "The Green Mobs",
        "passage": "Watch out! Some mobs are not friendly. The Zombie is green and slow. It makes a loud groan. The Creeper is also green, but it is very quiet. It likes to sneak up on you.",
        "instructions": "Read about the green mobs. Then answer the questions.",
        "questions": [
            {"prompt": "What color is the Zombie?", "response_lines": 2},
            {"prompt": "Is the Creeper loud or quiet?", "response_lines": 2},
            {"prompt": "Which mob sneaks up on you?", "response_lines": 2},
        ],
        "vocabulary": [
            {"term": "Zombie", "definition": "A green mob that moves slow."},
            {"term": "Creeper", "definition": "A quiet green mob that goes boom."},
        ],
    }
    ws4b = WorksheetFactory.create("reading_comprehension", ws4b_data)
    render_reading_worksheet_to_image(ws4b, f"{output_dir}/quest_4b_scary_mobs.png")
    render_reading_worksheet_to_pdf(ws4b, f"{output_dir}/quest_4b_scary_mobs.pdf")

    # Quest 5: Fishing for Food (Critical Reading)
    ws5_data = {
        "title": "Minecraft Quest 5: Fishing for Food",
        "passage_title": "How to Fish",
        "passage": "Fishing is a fun way to get food in Minecraft. First, you need to make a fishing rod. You use 3 sticks and 2 pieces of string. To fish, hold the rod and **right-click** your mouse. The line will fly into the water! Wait for the red and white bobber to splash. When it splashes, **right-click** again to catch your fish.",
        "instructions": "Read the guide carefully to learn how to fish on a PC. Then answer the questions.",
        "questions": [
            {"prompt": "What items do you need to make a fishing rod?", "response_lines": 2},
            {"prompt": "What do you do to make the line fly into the water?", "response_lines": 2},
            {"prompt": "How can you tell that a fish is ready to be caught?", "response_lines": 2},
            {"prompt": "Which mouse button do you use for every step?", "response_lines": 1},
        ],
        "vocabulary": [
            {"term": "Fishing Rod", "definition": "A tool used to catch fish."},
            {"term": "Bobber", "definition": "The red and white ball that floats on water."},
            {"term": "Right-click", "definition": "Pressing the right button on your mouse."},
        ],
    }
    ws5 = WorksheetFactory.create("reading_comprehension", ws5_data)
    render_reading_worksheet_to_image(ws5, f"{output_dir}/quest_5_fishing.png")
    render_reading_worksheet_to_pdf(ws5, f"{output_dir}/quest_5_fishing.pdf")

    # Quest 6: The Tall Stranger (Enderman Encounter)
    ws6_data = {
        "title": "Minecraft Quest 6: The Tall Stranger",
        "passage_title": "The Enderman",
        "passage": "The Enderman is a very tall and black mob. It has glowing purple eyes. Endermen can pick up blocks like dirt or grass and carry them around. They can also teleport, which means they move very fast! If you see an Enderman, be careful. Do not look into its eyes, or it will get angry. If you look at its feet or the ground, it will stay calm and leave you alone.",
        "instructions": "Read about the mysterious Enderman. Then answer the questions and learn the new words.",
        "questions": [
            {"prompt": "What color are the eyes of an Enderman?", "response_lines": 1},
            {"prompt": "What can an Enderman do with blocks?", "response_lines": 2},
            {"prompt": "What happens if you look into an Enderman's eyes?", "response_lines": 2},
            {"prompt": "Where should you look to stay safe?", "response_lines": 2},
        ],
        "vocabulary": [
            {"term": "Enderman", "definition": "A tall, black mob that can move blocks."},
            {"term": "Teleport", "definition": "To move from one place to another instantly."},
            {"term": "Calm", "definition": "To be peaceful and not angry."},
        ],
    }
    ws6 = WorksheetFactory.create("reading_comprehension", ws6_data)
    render_reading_worksheet_to_image(ws6, f"{output_dir}/quest_6_enderman.png")
    render_reading_worksheet_to_pdf(ws6, f"{output_dir}/quest_6_enderman.pdf")

    # Quest 7: Storing Your Treasure (Making a Chest)
    ws7_data = {
        "title": "Minecraft Quest 7: Storing Your Treasure",
        "passage_title": "How to Make a Chest",
        "passage": "When you explore your world, you will find many items. You will get dirt, seeds, and flowers. Soon, your pockets will be full! You need a place to keep your things safe. You need a chest.\n\nTo make a chest, you first need wood. Chop down a tree to get logs. Then, turn the logs into Wood Planks. You need eight Wood Planks to make one chest. Open your Crafting Table and put the planks in a big circle. Leave the middle square empty. Now you have a chest to hold your treasure!",
        "instructions": "Read the story about making a chest. Then answer the questions.",
        "questions": [
            {"prompt": "Why do you need a chest in Minecraft?", "response_lines": 2},
            {"prompt": "How many Wood Planks do you need to craft one chest?", "response_lines": 1},
            {"prompt": "Where do you put the planks on the Crafting Table?", "response_lines": 2},
            {"prompt": "Which square on the Crafting Table stays empty?", "response_lines": 1},
        ],
        "vocabulary": [
            {"term": "Treasure", "definition": "Valuable things that you find and keep."},
            {"term": "Pockets", "definition": "The space where you carry items (inventory)."},
            {"term": "Empty", "definition": "Having nothing inside."},
        ],
    }
    ws7 = WorksheetFactory.create("reading_comprehension", ws7_data)
    render_reading_worksheet_to_image(ws7, f"{output_dir}/quest_7_making_a_chest.png")
    render_reading_worksheet_to_pdf(ws7, f"{output_dir}/quest_7_making_a_chest.pdf")

    # Quest 8: The Double Chest (Using Your Chest)
    ws8_data = {
        "title": "Minecraft Quest 8: The Double Chest",
        "passage_title": "How to Use a Chest",
        "passage": "Using a chest is easy. Just look at the chest and **right-click**. The lid will pop open! Now you can move items from your pockets into the chest. This keeps them safe if you ever get lost.\n\nDid you know you can make a giant chest? If you place two small chests right next to each other, they will snap together. This is called a Double Chest. It has much more room for your blocks and tools. Just remember, you cannot open a chest if there is a solid block sitting on top of it. It needs space to breathe!",
        "instructions": "Read about how to use and grow your chests. Then answer the questions.",
        "questions": [
            {"prompt": "What do you do to open a chest?", "response_lines": 1},
            {"prompt": "How do you make a Double Chest?", "response_lines": 2},
            {
                "prompt": "What happens to the room inside when you make a Double Chest?",
                "response_lines": 2,
            },
            {"prompt": "What can stop a chest from opening?", "response_lines": 2},
        ],
        "vocabulary": [
            {"term": "Giant", "definition": "Something that is very, very big."},
            {"term": "Lid", "definition": "The top part of a box that opens and closes."},
            {"term": "Snap", "definition": "To click or join together quickly."},
        ],
    }
    ws8 = WorksheetFactory.create("reading_comprehension", ws8_data)
    render_reading_worksheet_to_image(ws8, f"{output_dir}/quest_8_using_a_chest.png")
    render_reading_worksheet_to_pdf(ws8, f"{output_dir}/quest_8_using_a_chest.pdf")

    # Quest 9: Finding Iron (Finding and Smelting)
    ws9_data = {
        "title": "Minecraft Quest 9: Finding Iron",
        "passage_title": "How to Find and Use Iron",
        "passage": "After you have stone tools, you are ready to find Iron! Iron is a strong metal. You can find it deep in caves. Look for gray stone with beige or pink spots on it. That is Iron Ore.\n\nYou must use a Stone Pickaxe to mine Iron Ore. A wooden one will not work! Once you have the ore, you must melt it in a furnace with coal. This turns the ore into a shiny Iron Ingot. You can use these ingots to make an Iron Pickaxe. An Iron Pickaxe is much faster and stronger than stone. It can even mine sparkly blue diamonds!",
        "instructions": "Read about finding and using iron. Then answer the questions.",
        "questions": [
            {"prompt": "Where can you find Iron in Minecraft?", "response_lines": 2},
            {"prompt": "Which pickaxe must you use to mine Iron Ore?", "response_lines": 1},
            {"prompt": "What do you use to melt the ore in a furnace?", "response_lines": 1},
            {
                "prompt": "What can an Iron Pickaxe do that a Stone Pickaxe cannot?",
                "response_lines": 2,
            },
        ],
        "vocabulary": [
            {"term": "Ore", "definition": "A type of rock that has metal inside it."},
            {"term": "Ingot", "definition": "A shiny brick made of pure metal."},
            {"term": "Furnace", "definition": "A block used for cooking food or melting ore."},
        ],
    }
    ws9 = WorksheetFactory.create("reading_comprehension", ws9_data)
    render_reading_worksheet_to_image(ws9, f"{output_dir}/quest_9_finding_iron.png")
    render_reading_worksheet_to_pdf(ws9, f"{output_dir}/quest_9_finding_iron.pdf")

    print(f"Successfully generated 9 worksheets in {output_dir}/")


if __name__ == "__main__":
    generate_series()
