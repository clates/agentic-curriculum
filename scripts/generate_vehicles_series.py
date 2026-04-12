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


def generate_vehicles_series():
    output_dir = "vehicles_series"
    os.makedirs(output_dir, exist_ok=True)

    # 1. Vehicles Worksheet (Nouns)
    vehicles_items = [
        {"word": "CAR", "image": "assets/vehicles/car.png"},
        {"word": "BUS", "image": "assets/vehicles/bus.png"},
        {"word": "VAN", "image": "assets/vehicles/van.png"},
        {"word": "RIG", "image": "assets/vehicles/rig.png"},
        {"word": "CAB", "image": "assets/vehicles/cab.png"},
        {"word": "JEEP", "image": "assets/vehicles/jeep.png"},
        {"word": "TOW", "image": "assets/vehicles/tow.png"},
        {"word": "DUMP", "image": "assets/vehicles/dump.png"},
    ]

    shuffled_vehicles_right = vehicles_items[:]
    random.shuffle(shuffled_vehicles_right)

    vehicles_data = {
        "title": "Cars and Trucks Match",
        "instructions": "Read the word on the left. Match it to the vehicle on the right!",
        "left_items": [{"text": item["word"]} for item in vehicles_items],
        "right_items": [{"image_path": item["image"]} for item in shuffled_vehicles_right],
    }

    ws_vehicles = WorksheetFactory.create("matching", vehicles_data)
    render_matching_to_image(ws_vehicles, f"{output_dir}/01_vehicles_match.png")
    render_matching_to_pdf(ws_vehicles, f"{output_dir}/01_vehicles_match.pdf")

    # 2. Road and Work Worksheet
    work_items = [
        {"word": "FIRE", "image": "assets/vehicles/fire.png"},
        {"word": "GAS", "image": "assets/vehicles/gas.png"},
        {"word": "TIRE", "image": "assets/vehicles/tire.png"},
        {"word": "STOP", "image": "assets/vehicles/stop.png"},
        {"word": "ROAD", "image": "assets/vehicles/road.png"},
        {"word": "TRACTOR", "image": "assets/vehicles/tractor.png"},
        {"word": "TANK", "image": "assets/vehicles/tank.png"},
    ]

    shuffled_work_right = work_items[:]
    random.shuffle(shuffled_work_right)

    work_data = {
        "title": "Road and Work Match",
        "instructions": "Match the word to the sign, tool, or truck!",
        "left_items": [{"text": item["word"]} for item in work_items],
        "right_items": [{"image_path": item["image"]} for item in shuffled_work_right],
    }

    ws_work = WorksheetFactory.create("matching", work_data)
    render_matching_to_image(ws_work, f"{output_dir}/02_road_work_match.png")
    render_matching_to_pdf(ws_work, f"{output_dir}/02_road_work_match.pdf")

    # 3. Mystery Shadow Match (Vehicle recognition)
    shadow_items = vehicles_items[:]
    random.shuffle(shadow_items)

    shadow_left = shadow_items[:]
    shadow_right = shadow_items[:]
    random.shuffle(shadow_right)

    shadow_data = {
        "title": "Vehicle Shadow Match",
        "instructions": "Can you match the vehicle to its mystery shadow?",
        "left_items": [{"image_path": item["image"]} for item in shadow_left],
        "right_items": [{"image_path": item["image"], "as_shadow": True} for item in shadow_right],
    }

    ws_shadow = WorksheetFactory.create("matching", shadow_data)
    render_matching_to_image(ws_shadow, f"{output_dir}/03_vehicle_shadows.png")
    render_matching_to_pdf(ws_shadow, f"{output_dir}/03_vehicle_shadows.pdf")

    print(f"Successfully generated vehicles series in {output_dir}/")


if __name__ == "__main__":
    generate_vehicles_series()
