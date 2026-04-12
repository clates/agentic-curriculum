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
    render_venn_diagram_to_image,
    render_venn_diagram_to_pdf,
    render_tree_map_to_image,
    render_tree_map_to_pdf,
    render_feature_matrix_to_image,
    render_feature_matrix_to_pdf,
)


def generate_civics_series():
    output_dir = "civics_series"
    os.makedirs(output_dir, exist_ok=True)

    # 1. American Symbols (Reading Comprehension) - NEW
    symbols_reading_data = {
        "title": "Symbols of Our Nation",
        "passage_title": "The Signs of America",
        "passage": "A symbol is an object or a picture that stands for something else. The United States has many important symbols that represent our history and our values. \n\nThe American Flag is one of our most famous symbols. It has 50 stars to represent the 50 states and 13 stripes to represent the original 13 colonies. Another symbol is the Bald Eagle, which stands for strength and freedom. \n\nWe also have famous landmarks. The Statue of Liberty was a gift from France and represents freedom and liberty for people coming to America. The Liberty Bell, located in Philadelphia, was rung to celebrate our independence. Finally, the White House is a symbol of our government because it is where the President lives and works. These symbols help us remember that we are all part of one big country.",
        "instructions": "Read about our symbols. Then answer the questions.",
        "questions": [
            {"prompt": "What do the 50 stars on the American Flag represent?", "response_lines": 2},
            {"prompt": "Which symbol represents strength and freedom?", "response_lines": 2},
            {
                "prompt": "Where is the Liberty Bell located, and what does it represent?",
                "response_lines": 2,
            },
        ],
        "vocabulary": [
            {"term": "Symbol", "definition": "An object that stands for an idea or a country."},
            {"term": "Independence", "definition": "Freedom from being controlled by others."},
            {"term": "Colony", "definition": "An area that is controlled by another country."},
        ],
    }
    ws1_read = WorksheetFactory.create("reading_comprehension", symbols_reading_data)
    render_reading_worksheet_to_image(ws1_read, f"{output_dir}/01_symbols_reading.png")
    render_reading_worksheet_to_pdf(ws1_read, f"{output_dir}/01_symbols_reading.pdf")

    # 2. American Symbols (Matching)
    symbols_items = [
        {"word": "American Flag", "image": "assets/civics/flag.png"},
        {"word": "Bald Eagle", "image": "assets/civics/eagle.png"},
        {"word": "Statue of Liberty", "image": "assets/civics/liberty.png"},
        {"word": "Liberty Bell", "image": "assets/civics/bell.png"},
        {"word": "The White House", "image": "assets/civics/building.png"},
    ]
    shuffled_symbols_right = symbols_items[:]
    random.shuffle(shuffled_symbols_right)

    symbols_data = {
        "title": "American Symbols Match",
        "instructions": "Draw a line to match the name of the symbol to its picture.",
        "left_items": [{"text": item["word"]} for item in symbols_items],
        "right_items": [{"image_path": item["image"]} for item in shuffled_symbols_right],
    }
    ws2_match = WorksheetFactory.create("matching", symbols_data)
    render_matching_to_image(ws2_match, f"{output_dir}/02_symbols_match.png")
    render_matching_to_pdf(ws2_match, f"{output_dir}/02_symbols_match.pdf")

    # 3. Being a Good Citizen (Reading Comprehension)
    citizen_data = {
        "title": "Being a Good Citizen",
        "passage_title": "Our Community Heroes",
        "passage": "A citizen is a person who belongs to a community, like a city or a country. Being a good citizen means helping others and following the rules. \n\nCitizens have both rights and responsibilities. A right is a freedom that everyone has, like the right to speak and be heard. A responsibility is something you should do to help out. Some examples of responsibilities are following laws, voting in elections, and keeping our parks clean. \n\nYou can be a good citizen even when you are young! You can help a neighbor, pick up trash, or follow the rules at school. When everyone works together as good citizens, our community becomes a better place for everyone.",
        "instructions": "Read about being a citizen. Then answer the questions.",
        "questions": [
            {"prompt": "What is a citizen?", "response_lines": 2},
            {
                "prompt": "What is the difference between a right and a responsibility?",
                "response_lines": 2,
            },
            {"prompt": "What is one way you can be a good citizen today?", "response_lines": 2},
        ],
        "vocabulary": [
            {"term": "Citizen", "definition": "A member of a community or country."},
            {"term": "Right", "definition": "A freedom that belongs to everyone."},
            {"term": "Responsibility", "definition": "A duty or something you should do to help."},
        ],
    }
    ws3_read = WorksheetFactory.create("reading_comprehension", citizen_data)
    render_reading_worksheet_to_image(ws3_read, f"{output_dir}/03_good_citizen_reading.png")
    render_reading_worksheet_to_pdf(ws3_read, f"{output_dir}/03_good_citizen_reading.pdf")

    # 4. Being a Good Citizen (Odd One Out) - NEW
    citizen_odd_data = {
        "title": "Citizenship: Odd One Out",
        "instructions": "In each row, circle the action that does NOT show being a good citizen. Then explain why.",
        "rows": [
            {
                "items": ["Picking up trash", "Recycling a bottle", "Littering in the park"],
                "odd_item": "Littering in the park",
                "explanation": "Littering makes the community dirty, while the others help keep it clean.",
            },
            {
                "items": ["Following rules", "Breaking a law", "Helping a neighbor"],
                "odd_item": "Breaking a law",
                "explanation": "Good citizens follow laws to keep everyone safe.",
            },
            {
                "items": ["Shouting in class", "Being kind", "Sharing with friends"],
                "odd_item": "Shouting in class",
                "explanation": "Being kind and sharing are responsibilities, but shouting is not helpful.",
            },
        ],
        "reasoning_lines": 2,
        "show_answers": False,
    }
    ws4_odd = WorksheetFactory.create("odd_one_out", citizen_odd_data)
    from worksheet_renderer import render_odd_one_out_to_image, render_odd_one_out_to_pdf

    render_odd_one_out_to_image(ws4_odd, f"{output_dir}/04_good_citizen_odd_one_out.png")
    render_odd_one_out_to_pdf(ws4_odd, f"{output_dir}/04_good_citizen_odd_one_out.pdf")

    # 5. Who is in Charge? (Reading Comprehension)
    charge_reading_data = {
        "title": "Who is in Charge?",
        "passage_title": "Leaders of the Land",
        "passage": "In our country, we have different leaders for different places. A Mayor is the leader of a city or a town. Mayors work at City Hall and help make decisions about local things, like fixing parks, picking up trash, and making sure the fire trucks are ready. People in the city vote to choose the Mayor they think will do the best job.\n\nThe President is the leader of the whole United States! The President lives and works in the White House in Washington, D.C. While a Mayor helps one city, the President helps all fifty states. The President meets with leaders from other countries and makes sure our national laws are followed. \n\nBoth the Mayor and the President are elected by voters. This means they are chosen by the people to serve the community. They both have to follow the rules of the Constitution and work hard to keep people safe and happy.",
        "instructions": "Read about our leaders. Then answer the questions.",
        "questions": [
            {
                "prompt": "Where does a Mayor work, and what is one job they do?",
                "response_lines": 2,
            },
            {
                "prompt": "How is the President's job different from the Mayor's job?",
                "response_lines": 2,
            },
            {"prompt": "What does it mean to be 'elected' by voters?", "response_lines": 2},
        ],
        "vocabulary": [
            {"term": "Mayor", "definition": "The leader of a city or town."},
            {"term": "President", "definition": "The leader of the whole country."},
            {"term": "Elected", "definition": "Chosen by people through voting."},
        ],
    }
    ws5_read = WorksheetFactory.create("reading_comprehension", charge_reading_data)
    render_reading_worksheet_to_image(ws5_read, f"{output_dir}/05_who_is_in_charge_reading.png")
    render_reading_worksheet_to_pdf(ws5_read, f"{output_dir}/05_who_is_in_charge_reading.pdf")

    # 6. Who is in Charge? (Venn Diagram)
    venn_data = {
        "title": "Venn Diagram: Mayor vs. President",
        "instructions": "Use what you read to sort the words into the diagram.",
        "left_label": "Mayor",
        "right_label": "President",
        "both_label": "Both Leaders",
        "word_bank": [
            "Leads a city",
            "Works at City Hall",
            "Leads the country",
            "Works at the White House",
            "Makes big decisions",
            "Follows the laws",
            "Helps people",
            "Elected by voters",
        ],
        "left_items": ["Helps local parks"],
        "right_items": ["Commander-in-Chief"],
        "both_items": ["Follow the Constitution"],
    }
    ws6_venn = WorksheetFactory.create("venn_diagram", venn_data)
    render_venn_diagram_to_image(ws6_venn, f"{output_dir}/06_who_is_in_charge_venn.png")
    render_venn_diagram_to_pdf(ws6_venn, f"{output_dir}/06_who_is_in_charge_venn.pdf")

    # 7. Rules and Laws (Reading Comprehension)
    rules_reading_data = {
        "title": "Rules and Laws",
        "passage_title": "Why We Have Rules",
        "passage": "Rules are instructions that tell us what we can and cannot do. We have rules in many places, like at home and at school. Rules help us stay safe and get along with others. For example, a rule at home might be 'No dessert before dinner.' A rule at school might be 'Walk, don't run, in the hallway.' If you break a rule, you might get a timeout or lose a privilege. \n\nLaws are like rules, but they are for everyone in a community, state, or country. Laws are made by the government. They are very important because they keep everyone safe and fair. For example, there is a law that says cars must stop at red lights. This keeps drivers and walkers safe. \n\nThe biggest difference between a rule and a law is who makes it and what happens if it is broken. Parents and teachers make rules, but the government makes laws. If someone breaks a law, they might have to pay a fine or even go to jail. Following both rules and laws shows that you are a responsible citizen!",
        "instructions": "Read about rules and laws. Then answer the questions.",
        "questions": [
            {"prompt": "Why do we have rules at home and school?", "response_lines": 2},
            {"prompt": "Who makes the laws for our community and country?", "response_lines": 2},
            {"prompt": "What is one big difference between a rule and a law?", "response_lines": 2},
        ],
        "vocabulary": [
            {"term": "Rules", "definition": "Instructions for behavior at home or school."},
            {"term": "Laws", "definition": "Official rules made by the government for everyone."},
            {"term": "Fine", "definition": "Money someone has to pay if they break a law."},
        ],
    }
    ws7_read = WorksheetFactory.create("reading_comprehension", rules_reading_data)
    render_reading_worksheet_to_image(ws7_read, f"{output_dir}/07_rules_laws_reading.png")
    render_reading_worksheet_to_pdf(ws7_read, f"{output_dir}/07_rules_laws_reading.pdf")

    # 8. Rules and Laws (Feature Matrix)
    matrix_data = {
        "title": "Rules vs. Laws",
        "instructions": "Use what you read to check the box for each item.",
        "items": [
            {"name": "Wear a seatbelt", "checked_properties": ["Community Law"]},
            {"name": "Brush your teeth", "checked_properties": ["Home Rule"]},
            {"name": "No running in halls", "checked_properties": ["School Rule"]},
            {"name": "Stop at red lights", "checked_properties": ["Community Law"]},
            {"name": "Do your homework", "checked_properties": ["Home Rule", "School Rule"]},
        ],
        "properties": ["Home Rule", "School Rule", "Community Law"],
        "show_answers": False,
    }
    ws8_matrix = WorksheetFactory.create("feature_matrix", matrix_data)
    render_feature_matrix_to_image(ws8_matrix, f"{output_dir}/08_rules_vs_laws_matrix.png")
    render_feature_matrix_to_pdf(ws8_matrix, f"{output_dir}/08_rules_vs_laws_matrix.pdf")

    # 9. Three Branches of Government (Reading Comprehension) - NEW
    branches_reading_data = {
        "title": "The Three Branches of Government",
        "passage_title": "The Balance of Power",
        "passage": "The United States government is divided into three parts called branches. We have three branches so that no single person or group has too much power. This is called a system of 'Checks and Balances.' \n\nThe Legislative Branch is made up of Congress. Their main job is to write and vote on new laws. The Executive Branch is led by the President. Their job is to carry out the laws and make sure they are followed. The President is also the leader of our military. \n\nThe Judicial Branch is made up of our courts, including the Supreme Court. Their job is to explain the laws and decide if they follow the Constitution. The Constitution is the highest law of our land. By working together, these three branches help keep our government fair and protect the rights of all citizens.",
        "instructions": "Read about the three branches. Then answer the questions.",
        "questions": [
            {
                "prompt": "Why did the founders divide our government into three branches?",
                "response_lines": 2,
            },
            {"prompt": "What is the main job of the Legislative Branch?", "response_lines": 2},
            {"prompt": "Who leads the Executive Branch and what do they do?", "response_lines": 2},
        ],
        "vocabulary": [
            {"term": "Branch", "definition": "A part or division of the government."},
            {"term": "Congress", "definition": "The group of people who make national laws."},
            {
                "term": "Constitution",
                "definition": "The set of rules that our government must follow.",
            },
        ],
    }
    ws9_read = WorksheetFactory.create("reading_comprehension", branches_reading_data)
    render_reading_worksheet_to_image(ws9_read, f"{output_dir}/09_three_branches_reading.png")
    render_reading_worksheet_to_pdf(ws9_read, f"{output_dir}/09_three_branches_reading.pdf")

    # 10. Three Branches of Government (Tree Map)
    tree_data = {
        "title": "The Three Branches of Government",
        "instructions": "Sort the groups and jobs into the correct branch of the US Government.",
        "root_label": "US Government",
        "branches": [
            {
                "label": "Legislative",
                "slots": [{"text": "Makes the laws"}, {"text": "Congress"}],
                "slot_count": 2,
            },
            {
                "label": "Executive",
                "slots": [{"text": "Carries out laws"}, {"text": "President"}],
                "slot_count": 2,
            },
            {
                "label": "Judicial",
                "slots": [{"text": "Decides if laws are fair"}, {"text": "Supreme Court"}],
                "slot_count": 2,
            },
        ],
        "word_bank": [
            "Congress",
            "President",
            "Supreme Court",
            "Makes laws",
            "Carries out laws",
            "Decides if laws are fair",
        ],
    }
    ws4 = WorksheetFactory.create("tree_map", tree_data)
    render_tree_map_to_image(ws4, f"{output_dir}/04_three_branches.png")
    render_tree_map_to_pdf(ws4, f"{output_dir}/04_three_branches.pdf")

    # 5. Rules and Laws (Feature Matrix)
    matrix_data = {
        "title": "Rules vs. Laws",
        "instructions": "Check the box to show where each rule or law is followed.",
        "items": [
            {"name": "Wear a seatbelt", "checked_properties": ["Community Law"]},
            {"name": "Brush your teeth", "checked_properties": ["Home Rule"]},
            {"name": "No running in halls", "checked_properties": ["School Rule"]},
            {"name": "Stop at red lights", "checked_properties": ["Community Law"]},
            {"name": "Do your homework", "checked_properties": ["Home Rule", "School Rule"]},
        ],
        "properties": ["Home Rule", "School Rule", "Community Law"],
        "show_answers": False,
    }
    ws5 = WorksheetFactory.create("feature_matrix", matrix_data)
    render_feature_matrix_to_image(ws5, f"{output_dir}/05_rules_vs_laws.png")
    render_feature_matrix_to_pdf(ws5, f"{output_dir}/05_rules_vs_laws.pdf")

    print(f"Successfully generated Civics & Government series in {output_dir}/")


if __name__ == "__main__":
    generate_civics_series()
