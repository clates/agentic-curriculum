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


def generate_series():
    output_dir = "minecraft_villains_series"
    os.makedirs(output_dir, exist_ok=True)

    series_data = [
        {
            "title": "Minecraft Quest: The Wicked Witch",
            "passage_title": "The Witch in the Swamp",
            "passage": "If you are exploring a dark swamp, you might find a small wooden hut sitting on long legs in the water. This is the home of the Witch! She is a mob that looks a bit like a villager, but she wears a tall black hat with a green jewel. The Witch loves to brew strange potions in her big black pot called a cauldron. She is not very friendly and will hiss at you if you get too close to her home.\n\nWhen a Witch is in a battle, she does not use a sword or a bow. Instead, she throws glass bottles filled with magic potions! Some potions can make you move very slow, and others can make you feel weak. She can even drink her own potions to heal herself if she gets hurt. If you see a Witch, it is best to keep your distance and use a bow to stay safe from her splashy magic.",
            "instructions": "Read about the mysterious Witch. Then answer the questions and learn the new words.",
            "questions": [
                {
                    "prompt": "Where does the Witch live and what does her house look like?",
                    "response_lines": 2,
                },
                {
                    "prompt": "What does the Witch throw at you during a battle?",
                    "response_lines": 2,
                },
                {"prompt": "How does the Witch use potions to help herself?", "response_lines": 2},
            ],
            "vocabulary": [
                {
                    "term": "Cauldron",
                    "definition": "A big black pot used for brewing magic potions.",
                },
                {"term": "Hiss", "definition": "A sharp sound made to show anger or warning."},
                {"term": "Distance", "definition": "The amount of space between two things."},
            ],
        },
        {
            "title": "Minecraft Quest: The Grumpy Pillagers",
            "passage_title": "The Pillager Outpost",
            "passage": "Pillagers are grumpy mobs that like to go on adventures, just like you! They carry dark banners with a gray face on them to show they are part of a team. You can often find them living in tall towers called outposts. These towers are made of dark wood and stone. Pillagers walk around their towers to keep watch, and they will start to chase you if they see you coming near their camp.\n\nA Pillager uses a weapon called a crossbow. It is like a regular bow, but it can hold an arrow ready to fire. They are very good at aiming! Sometimes, a group of Pillagers will go on a patrol through the woods or near a village. If you defeat the leader with the banner, you might start a raid, so be careful! It is always a good idea to have a shield ready to block their arrows.",
            "instructions": "Read about the Pillagers and their towers. Then answer the questions.",
            "questions": [
                {
                    "prompt": "What do Pillagers carry to show they are on a team?",
                    "response_lines": 2,
                },
                {
                    "prompt": "What is the name of the tall tower where Pillagers live?",
                    "response_lines": 1,
                },
                {"prompt": "How is a crossbow different from a regular bow?", "response_lines": 2},
            ],
            "vocabulary": [
                {"term": "Banner", "definition": "A tall flag with a picture on it."},
                {"term": "Outpost", "definition": "A small camp or tower used to keep watch."},
                {
                    "term": "Patrol",
                    "definition": "To walk around an area to keep it safe or look for enemies.",
                },
            ],
        },
        {
            "title": "Minecraft Quest: The Scary Vindicator",
            "passage_title": "The Axe in the Mansion",
            "passage": "The Vindicator is a very strong and fast mob that lives in giant houses called Woodland Mansions. These mansions are hidden deep in the dark forest and have many secret rooms. The Vindicator looks like a pillager, but he does not use a crossbow. Instead, he carries a sharp iron axe! He keeps his arms crossed until he sees someone he doesn't like. Then, he pulls out his axe and runs very fast to catch them.\n\nVindicators are very brave and will not stop chasing you until you are far away. They are the guards of the mansion and protect the treasure hidden inside. Because they run so fast, you have to be very quick to dodge their swings. If you explore a mansion, listen for the sound of their heavy footsteps on the wooden floors. It is a sign that a Vindicator is nearby and ready to protect his home.",
            "instructions": "Read about the fast-running Vindicator. Then answer the questions.",
            "questions": [
                {
                    "prompt": "Where do Vindicators live and what do they protect?",
                    "response_lines": 2,
                },
                {
                    "prompt": "What weapon does a Vindicator use when he is angry?",
                    "response_lines": 1,
                },
                {
                    "prompt": "Why do you have to be very quick when fighting a Vindicator?",
                    "response_lines": 2,
                },
            ],
            "vocabulary": [
                {
                    "term": "Mansion",
                    "definition": "A very large and expensive house with many rooms.",
                },
                {
                    "term": "Vindicator",
                    "definition": "A strong mob that uses an axe to protect its home.",
                },
                {"term": "Nearby", "definition": "Something that is close to you."},
            ],
        },
    ]

    for _i, data in enumerate(series_data, start=1):
        ws = WorksheetFactory.create("reading_comprehension", data)
        file_name = data["title"].lower().replace(" ", "_").replace(":", "")
        render_reading_worksheet_to_image(ws, f"{output_dir}/{file_name}.png")
        render_reading_worksheet_to_pdf(ws, f"{output_dir}/{file_name}.pdf")
        print(f"Generated: {file_name}")

    print(
        f"\nSuccessfully generated {len(series_data)} Minecraft Villains worksheets in {output_dir}/"
    )


if __name__ == "__main__":
    generate_series()
