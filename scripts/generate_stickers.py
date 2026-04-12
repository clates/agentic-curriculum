import os

os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from PIL import Image

# Configuration
DPI = 300
A4_WIDTH = int(8.27 * DPI)  # 2481 px
A4_HEIGHT = int(11.69 * DPI)  # 3507 px
ICON_SIZE = int(2.5 * DPI)  # 2.5 inches (750 px)
SPACING = int(0.2 * DPI)  # 0.2 inch gap

# Local Asset Paths
ASSETS_DIR = "assets"
ASSET_FILES = [
    "zombie.png",
    "skeleton.png",
    "enderman.png",
    "pig.png",
    "wolf.png",
    "sword.png",
    "creeper.png",
    "villager.png",
    "dirt.png",
    "grass_block.png",
    "tnt.png",
    "diamond.png",
]


def load_image(filename):
    path = os.path.join(ASSETS_DIR, filename)
    print(f"Loading {path}...")
    img = Image.open(path).convert("RGBA")
    # Resize to exactly 1 inch using Nearest Neighbor to preserve pixel art look if it's small
    # or Lanczos if it's high res. For Minecraft, Nearest usually looks better for resizing UP,
    # but since we are resizing TO 1 inch (300px), and original icons are small,
    # Nearest will keep them crisp.

    # If the image is smaller than target, use NEAREST to keep it blocky
    if img.width < ICON_SIZE:
        img = img.resize((ICON_SIZE, ICON_SIZE), Image.Resampling.NEAREST)
    else:
        img.thumbnail((ICON_SIZE, ICON_SIZE), Image.Resampling.LANCZOS)
    return img


def create_sticker_sheet():
    # Create blank A4 canvas
    sheet = Image.new("RGBA", (A4_WIDTH, A4_HEIGHT), (255, 255, 255, 255))

    # Load assets
    icons = []
    for filename in ASSET_FILES:
        try:
            icons.append(load_image(filename))
        except Exception as e:
            print(f"Failed to load {filename}: {e}")

    if not icons:
        print("No icons loaded. Exiting.")
        return

    x_cursor = SPACING
    y_cursor = SPACING
    icon_idx = 0

    while y_cursor + ICON_SIZE < A4_HEIGHT:
        while x_cursor + ICON_SIZE < A4_WIDTH:
            # Paste current icon
            current_icon = icons[icon_idx % len(icons)]

            # Center the icon within the 1-inch slot if it's not square
            offset_x = (ICON_SIZE - current_icon.width) // 2
            offset_y = (ICON_SIZE - current_icon.height) // 2

            sheet.paste(current_icon, (x_cursor + offset_x, y_cursor + offset_y), current_icon)

            x_cursor += ICON_SIZE + SPACING
            icon_idx += 1

        x_cursor = SPACING
        y_cursor += ICON_SIZE + SPACING

    output_path = "minecraft_a4_stickers.png"
    sheet.save(output_path)
    print(f"\nSuccess! '{output_path}' is ready to print.")


if __name__ == "__main__":
    create_sticker_sheet()
