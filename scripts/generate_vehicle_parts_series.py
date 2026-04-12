import os

os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import sys

# Ensure we can import from src
sys.path.insert(0, os.path.abspath("src"))

from worksheets.factory import WorksheetFactory
from worksheet_renderer import (
    render_handwriting_to_image,
    render_handwriting_to_pdf,
)


def generate_vehicle_parts_series():
    output_dir = "vehicle_parts_series"
    os.makedirs(output_dir, exist_ok=True)

    # Vehicle parts mapping
    # TIRE, DOOR, ROOF, GEAR, WHEEL, LAMP, SEAT, GAS
    items = [
        {"text": "TIRE", "image_path": "assets/vehicles/tire.png", "sub_label": "Big black tire"},
        {"text": "DOOR", "image_path": "assets/vehicles/door.png", "sub_label": "Car door"},
        {"text": "ROOF", "image_path": "assets/vehicles/car.png", "sub_label": "Car top"},
        {"text": "GEAR", "image_path": "assets/vehicles/gear.png", "sub_label": "Spinning gear"},
        {"text": "WHEEL", "image_path": "assets/vehicles/wheel.png", "sub_label": "Steering wheel"},
        {"text": "LAMP", "image_path": "assets/vehicles/light.png", "sub_label": "Bright light"},
        {"text": "SEAT", "image_path": "assets/vehicles/seat.png", "sub_label": "Comfortable seat"},
        {"text": "GAS", "image_path": "assets/vehicles/gas_pump.png", "sub_label": "Fill it up"},
    ]

    # Handwriting Worksheet with "Bottom Rail" style
    handwriting_data = {
        "title": "Vehicle Parts Handwriting",
        "instructions": "Practice writing these car part words on the bottom rail!",
        "items": items,
        "rows": 4,
        "cols": 2,
        "metadata": {"bottom_rail": True},
    }

    ws_handwriting = WorksheetFactory.create("handwriting", handwriting_data)
    render_handwriting_to_image(ws_handwriting, f"{output_dir}/vehicle_parts_handwriting.png")
    render_handwriting_to_pdf(ws_handwriting, f"{output_dir}/vehicle_parts_handwriting.pdf")

    print(f"Successfully generated vehicle parts series in {output_dir}/")


if __name__ == "__main__":
    generate_vehicle_parts_series()
