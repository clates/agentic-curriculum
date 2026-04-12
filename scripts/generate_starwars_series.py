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
    output_dir = "starwars_series"
    os.makedirs(output_dir, exist_ok=True)

    # 1: The Brave Jedi
    ws1_data = {
        "title": "Star Wars Quest 1: The Brave Jedi",
        "passage_title": "The Way of the Jedi",
        "passage": "A Jedi is a brave hero who keeps peace in the galaxy. They are very kind and help people who are in trouble. Jedi train for a long time to learn how to be calm and strong. They wear long robes made of soft cloth and carry a special tool called a lightsaber.\n\nA lightsaber is a glowing sword made of pure energy. It can be many colors like blue, green, or even purple. Jedi only use their lightsabers to protect others. They also use a power called the Force to jump high and move objects with their minds!",
        "instructions": "Read about the Jedi. Then answer the questions and check the words.",
        "questions": [
            {"prompt": "What kind of person is a Jedi?", "response_lines": 2},
            {"prompt": "What do Jedi wear and what weapon do they carry?", "response_lines": 2},
            {"prompt": "What can a Jedi do using the Force?", "response_lines": 2},
        ],
        "vocabulary": [
            {"term": "Jedi", "definition": "A hero who keeps peace and uses the Force."},
            {"term": "Lightsaber", "definition": "A glowing sword made of energy."},
            {"term": "Galaxy", "definition": "The big world in the stars where Star Wars happens."},
        ],
    }
    ws1 = WorksheetFactory.create("reading_comprehension", ws1_data)
    render_reading_worksheet_to_image(ws1, f"{output_dir}/quest_1_jedi.png")
    render_reading_worksheet_to_pdf(ws1, f"{output_dir}/quest_1_jedi.pdf")

    # 2: My Own Lightsaber (Opinion)
    ws2_data = {
        "title": "Star Wars Quest 2: My Own Lightsaber",
        "passage_title": "The Colors of Energy",
        "passage": "Every Jedi must build their own lightsaber when they are ready. They go on a quest to find a special crystal that makes the blade glow. The crystal chooses the Jedi just as much as the Jedi chooses the crystal. When the light turns on, the room fills with a bright and beautiful color.\n\nMost Jedi have blue or green lightsabers, but there are other colors too. Some Jedi like yellow or white, and a few even have purple! If you were a young Padawan, you would have to choose the color that fits you best. Think about which color you would like to see glowing in your hands.",
        "instructions": "Think about being a Jedi. Then write your opinion.",
        "questions": [
            {
                "prompt": "If you were a Jedi, what color would your lightsaber be?",
                "response_lines": 2,
            },
            {
                "prompt": "Write one sentence telling why you picked that color.",
                "response_lines": 2,
            },
        ],
        "vocabulary": [
            {"term": "Crystal", "definition": "A special stone that makes a lightsaber glow."},
            {"term": "Padawan", "definition": "A student who is learning to be a Jedi."},
        ],
    }
    ws2 = WorksheetFactory.create("reading_comprehension", ws2_data)
    render_reading_worksheet_to_image(ws2, f"{output_dir}/quest_2_my_lightsaber.png")
    render_reading_worksheet_to_pdf(ws2, f"{output_dir}/quest_2_my_lightsaber.pdf")

    # 3: Meet the Droids
    ws3_data = {
        "title": "Star Wars Quest 3: Meet the Droids",
        "passage_title": "Helpful and Dangerous Droids",
        "passage": "Droids are robots that come in many shapes and sizes. Some droids, like R2-D2 and C-3PO, are built to help the heroes. R2-D2 is short and blue, and he can fix spaceships with his many tools. C-3PO is tall and gold, and he can speak thousands of different languages to help everyone understand each other. These droids are very loyal and always try to keep their friends safe from harm.\n\nOther droids are built for battle. The Battle Droids are tall and thin, and they all look exactly the same. But the scariest droids of all are the Droidekas. A Droideka can curl up into a tight ball and roll across the floor very fast! When it stops rolling, it unfolds and stands on three legs. It has powerful blaster arms and can even turn on a blue shield that protects it from lightsabers. You have to be very quick to get past a Droideka!",
        "instructions": "Read about the different kinds of droids. Then answer the questions.",
        "questions": [
            {
                "prompt": "What are two ways R2-D2 and C-3PO help their friends?",
                "response_lines": 2,
            },
            {"prompt": "How does a Droideka move across the floor very fast?", "response_lines": 2},
            {
                "prompt": "What does a Droideka have to protect itself from lightsabers?",
                "response_lines": 2,
            },
        ],
        "vocabulary": [
            {"term": "Droid", "definition": "A robot that can think and do work."},
            {"term": "Droideka", "definition": "A dangerous droid that can roll like a ball."},
            {
                "term": "Shield",
                "definition": "A glowing bubble that stops things from hitting you.",
            },
        ],
    }
    ws3 = WorksheetFactory.create("reading_comprehension", ws3_data)
    render_reading_worksheet_to_image(ws3, f"{output_dir}/quest_3_droids.png")
    render_reading_worksheet_to_pdf(ws3, f"{output_dir}/quest_3_droids.pdf")

    # 4: The Fast Race
    ws4_data = {
        "title": "Star Wars Quest 4: The Fast Race",
        "passage_title": "The Great Podrace",
        "passage": "Anakin is a young boy who is a very good pilot. He is entering a big Podrace in the desert. His podracer has two giant engines that are tied together with purple electricity. Before the race starts, Anakin checks his controls one last time. He is nervous but also very excited to show everyone how fast he can go!\n\nWhen the green light flashes, Anakin zooms across the hot sand. He has to dodge big rocks and stay away from the other racers. Even when his engines get into trouble, Anakin stays calm and fixes them. Finally, he crosses the finish line and wins the race! All his friends cheer and shout for the fastest pilot on Tatooine.",
        "instructions": "Read about the race. Then answer the questions about what happened.",
        "questions": [
            {"prompt": "What does Anakin do before the race starts?", "response_lines": 2},
            {
                "prompt": "What are two things Anakin has to do during the race?",
                "response_lines": 2,
            },
            {"prompt": "How does Anakin feel when he wins?", "response_lines": 2},
        ],
        "vocabulary": [
            {"term": "Podrace", "definition": "A very fast race with flying engines."},
            {"term": "Pilot", "definition": "Someone who flies a ship or a racer."},
            {"term": "Dodge", "definition": "To move quickly out of the way of something."},
        ],
    }
    ws4 = WorksheetFactory.create("reading_comprehension", ws4_data)
    render_reading_worksheet_to_image(ws4, f"{output_dir}/quest_4_race.png")
    render_reading_worksheet_to_pdf(ws4, f"{output_dir}/quest_4_race.pdf")

    # 5: The Force
    ws5_data = {
        "title": "Star Wars Quest 5: The Force",
        "passage_title": "The Power of the Force",
        "passage": "The Force is a mysterious power that is all around us. It is an energy field that connects every living thing in the galaxy. Jedi spend their whole lives learning how to feel the Force. They believe that the Force helps them see things before they happen and gives them the strength to do what is right.\n\nA Jedi can use the Force to do amazing tricks. They can lift heavy ships into the air just by thinking about it. They can also use it to run very fast or jump over tall walls. Most importantly, the Force helps a Jedi stay peaceful and quiet inside, even when things are scary or loud.",
        "instructions": "Read about the Force. Then answer the questions.",
        "questions": [
            {"prompt": "What is the Force and what does it connect?", "response_lines": 2},
            {"prompt": "What are some tricks a Jedi can do with the Force?", "response_lines": 2},
            {"prompt": "How does the Force help a Jedi feel inside?", "response_lines": 2},
        ],
        "vocabulary": [
            {
                "term": "Energy Field",
                "definition": "A power that is everywhere but you cannot see it.",
            },
            {"term": "Connect", "definition": "To join things together like a big web."},
            {"term": "Peaceful", "definition": "To be calm and quiet."},
        ],
    }
    ws5 = WorksheetFactory.create("reading_comprehension", ws5_data)
    render_reading_worksheet_to_image(ws5, f"{output_dir}/quest_5_the_force.png")
    render_reading_worksheet_to_pdf(ws5, f"{output_dir}/quest_5_the_force.pdf")

    print(f"Successfully generated 5 Star Wars worksheets with longer passages in {output_dir}/")


if __name__ == "__main__":
    generate_series()
