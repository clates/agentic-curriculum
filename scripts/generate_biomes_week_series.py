"""
Earth, Biomes & Seasons — Week Series
Grade 1 | Science | Causal Arc: Sun → Tilt → Seasons → Climate Zones → Topography → Biomes

Structure: 5 days × 2 sheets + 1 Friday capstone + 1 end-of-week parent feedback = 13 worksheets
Minecraft hook: framing device at the start of each reading card passage.

Custom worksheet: render_earth_diagram_to_image / _to_pdf
  — A labeled diagram showing Earth's axial tilt, the Sun, and the two hemispheres.
  — Built with pure Pillow (no factory), same pattern as generate_baseball_drills.py.
"""

import math
import os

os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, os.path.abspath("src"))

from worksheets.factory import WorksheetFactory
from worksheet_renderer import (
    render_reading_worksheet_to_image,
    render_reading_worksheet_to_pdf,
    render_tree_map_to_image,
    render_tree_map_to_pdf,
    render_odd_one_out_to_image,
    render_odd_one_out_to_pdf,
    render_feature_matrix_to_image,
    render_feature_matrix_to_pdf,
)

# ---------------------------------------------------------------------------
# Font helpers (mirrors worksheet_renderer internals)
# ---------------------------------------------------------------------------

_FONT_CANDIDATES = (
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
)
_FONT_BOLD_CANDIDATES = (
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
)
_FONT_ITALIC_CANDIDATES = (
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Oblique.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationSans-Italic.ttf",
)


def _font(size, bold=False, italic=False):
    candidates = (
        _FONT_BOLD_CANDIDATES if bold else (_FONT_ITALIC_CANDIDATES if italic else _FONT_CANDIDATES)
    )
    for path in candidates:
        if Path(path).exists():
            return ImageFont.truetype(path, size)
    return ImageFont.load_default()


# ---------------------------------------------------------------------------
# Custom renderer: Earth Axial Tilt / Climate Zones Labeled Diagram
# ---------------------------------------------------------------------------


def _render_earth_diagram() -> Image.Image:
    """
    Draws a labeled diagram showing:
      - The Sun on the left (yellow circle, labeled)
      - Earth tilted at ~23.5° on the right (blue circle)
      - Earth's axis drawn through it (dashed line)
      - Labels: North Pole, South Pole, Equator, Northern Hemisphere,
                Southern Hemisphere, Axis (23.5°), Sunlight arrows
      - Three horizontal bands on Earth: Tropical Zone (equator),
        Temperate Zones (mid), Polar Zones (top/bottom)
      - Title and instructions at top
      - Student label lines at bottom: "The ___ is tilted ___ degrees."
    """
    W, H = 1050, 1020
    MARGIN = 60
    img = Image.new("RGB", (W, H), "white")
    draw = ImageDraw.Draw(img)

    title_font = _font(36, bold=True)
    label_font = _font(22, bold=True)
    body_font = _font(20)
    small_font = _font(17)
    italic_font = _font(20, italic=True)

    # ── Title ──────────────────────────────────────────────────────────────
    draw.text(
        (MARGIN, 20), "Earth's Tilt and the Sun — Labeled Diagram", font=title_font, fill="black"
    )
    draw.text(
        (MARGIN, 66),
        "Use this diagram during the lesson. Label the parts and answer the questions below.",
        font=italic_font,
        fill="#444444",
    )

    # ── Sun ────────────────────────────────────────────────────────────────
    sun_cx, sun_cy = 170, 370
    sun_r = 70
    # Glow
    for dr in range(18, 0, -3):
        alpha_col = (255, 255, int(200 - dr * 8))
        draw.ellipse(
            [sun_cx - sun_r - dr, sun_cy - sun_r - dr, sun_cx + sun_r + dr, sun_cy + sun_r + dr],
            fill=alpha_col,
        )
    draw.ellipse(
        [sun_cx - sun_r, sun_cy - sun_r, sun_cx + sun_r, sun_cy + sun_r],
        fill=(255, 220, 30),
        outline=(200, 140, 0),
        width=3,
    )
    sun_tw = draw.textlength("SUN", font=label_font)
    draw.text((sun_cx - sun_tw // 2, sun_cy - 14), "SUN", font=label_font, fill=(120, 70, 0))

    # ── Sunlight arrows ────────────────────────────────────────────────────
    arrow_color = (200, 140, 0)
    arrow_targets = [300, 340, 370, 400, 440]
    for ay in arrow_targets:
        x0, x1 = sun_cx + sun_r + 6, sun_cx + sun_r + 80
        draw.line([(x0, ay), (x1, ay)], fill=arrow_color, width=3)
        draw.polygon([(x1, ay - 7), (x1 + 14, ay), (x1, ay + 7)], fill=arrow_color)

    slabel_x = sun_cx + sun_r + 18
    draw.text((slabel_x, 460), "Sunlight", font=small_font, fill=arrow_color)

    # ── Earth ──────────────────────────────────────────────────────────────
    earth_cx, earth_cy = 700, 370
    earth_r = 180

    # Ocean base
    draw.ellipse(
        [earth_cx - earth_r, earth_cy - earth_r, earth_cx + earth_r, earth_cy + earth_r],
        fill=(70, 130, 200),
        outline=(30, 80, 160),
        width=3,
    )

    # Climate zone bands (clipped to circle via chord approximation)
    # Tropical zone: ±30° from equator  → y ± earth_r * sin(30°) = ± earth_r/2
    trop_half = int(earth_r * 0.50)
    # Polar zones: poleward of 60° → y ± earth_r * sin(60°) ≈ ± earth_r * 0.87
    polar_half = int(earth_r * 0.87)

    def draw_band(y_top, y_bot, color):
        """Draw a horizontal band clipped inside the Earth circle."""
        for dy in range(min(y_top, y_bot), max(y_top, y_bot) + 1):
            rel = dy - earth_cy
            if abs(rel) > earth_r:
                continue
            half_w = int(math.sqrt(max(0, earth_r**2 - rel**2)))
            x0 = earth_cx - half_w
            x1 = earth_cx + half_w
            draw.line([(x0, dy), (x1, dy)], fill=color)

    # Tropical (warm yellow-green)
    draw_band(earth_cy - trop_half, earth_cy + trop_half, (200, 230, 100))
    # North temperate (light green)
    draw_band(earth_cy - polar_half, earth_cy - trop_half, (140, 200, 100))
    # South temperate
    draw_band(earth_cy + trop_half, earth_cy + polar_half, (140, 200, 100))
    # North polar (light blue/white)
    draw_band(earth_cy - earth_r, earth_cy - polar_half, (200, 230, 255))
    # South polar
    draw_band(earth_cy + polar_half, earth_cy + earth_r, (200, 230, 255))

    # Re-draw outline
    draw.ellipse(
        [earth_cx - earth_r, earth_cy - earth_r, earth_cx + earth_r, earth_cy + earth_r],
        outline=(30, 80, 160),
        width=3,
    )

    # Equator line
    draw.line(
        [(earth_cx - earth_r, earth_cy), (earth_cx + earth_r, earth_cy)],
        fill=(180, 50, 50),
        width=3,
    )

    # Axial tilt line (23.5° from vertical)
    tilt_rad = math.radians(23.5)
    ax_dx = int(earth_r * math.sin(tilt_rad))
    ay_dy = int(earth_r * math.cos(tilt_rad))
    axis_top = (earth_cx + ax_dx, earth_cy - ay_dy - 30)
    axis_bottom = (earth_cx - ax_dx, earth_cy + ay_dy + 30)

    # Dashed axis line
    def dashed_line(draw, p1, p2, fill, width=3, dash=14):
        dx, dy = p2[0] - p1[0], p2[1] - p1[1]
        length = math.hypot(dx, dy)
        steps = int(length / dash)
        for i in range(steps):
            if i % 2 == 0:
                t0, t1 = i / steps, min(1.0, (i + 0.7) / steps)
                x0 = int(p1[0] + dx * t0)
                y0 = int(p1[1] + dy * t0)
                x1 = int(p1[0] + dx * t1)
                y1 = int(p1[1] + dy * t1)
                draw.line([(x0, y0), (x1, y1)], fill=fill, width=width)

    dashed_line(draw, axis_top, axis_bottom, fill=(60, 60, 60), width=3)
    # Axis arrowheads
    draw.ellipse(
        [axis_top[0] - 6, axis_top[1] - 6, axis_top[0] + 6, axis_top[1] + 6], fill=(60, 60, 60)
    )
    draw.ellipse(
        [axis_bottom[0] - 6, axis_bottom[1] - 6, axis_bottom[0] + 6, axis_bottom[1] + 6],
        fill=(60, 60, 60),
    )

    # ── Labels with leader lines ────────────────────────────────────────────
    def label_line(text, tx, ty, lx1, ly1, lx2, ly2, font=label_font, color="black"):
        draw.line([(lx1, ly1), (lx2, ly2)], fill="#888888", width=2)
        draw.text((tx, ty), text, font=font, fill=color)

    # North Pole
    label_line(
        "North Pole ★",
        axis_top[0] + 12,
        axis_top[1] - 10,
        axis_top[0],
        axis_top[1],
        axis_top[0] + 10,
        axis_top[1],
        color=(30, 30, 120),
    )

    # South Pole
    label_line(
        "South Pole ★",
        axis_bottom[0] + 12,
        axis_bottom[1] - 5,
        axis_bottom[0],
        axis_bottom[1],
        axis_bottom[0] + 10,
        axis_bottom[1],
        color=(30, 30, 120),
    )

    # Equator
    eq_lx = earth_cx + earth_r + 8
    draw.line([(earth_cx + earth_r, earth_cy), (eq_lx, earth_cy)], fill="#888888", width=2)
    draw.text((eq_lx + 4, earth_cy - 14), "Equator", font=label_font, fill=(180, 50, 50))

    # Northern Hemisphere
    draw.text(
        (earth_cx - 96, earth_cy - trop_half - 50),
        "Northern\nHemisphere",
        font=small_font,
        fill=(20, 80, 20),
    )

    # Southern Hemisphere
    draw.text(
        (earth_cx - 96, earth_cy + trop_half + 14),
        "Southern\nHemisphere",
        font=small_font,
        fill=(20, 80, 20),
    )

    # Tropical Zone label (left side)
    trp_lx = earth_cx - earth_r - 8
    draw.line(
        [(trp_lx, earth_cy - trop_half), (trp_lx - 60, earth_cy - trop_half)],
        fill="#888888",
        width=2,
    )
    draw.line(
        [(trp_lx, earth_cy + trop_half), (trp_lx - 60, earth_cy + trop_half)],
        fill="#888888",
        width=2,
    )
    draw.line(
        [(trp_lx - 60, earth_cy - trop_half), (trp_lx - 60, earth_cy + trop_half)],
        fill="#888888",
        width=2,
    )
    draw.text((trp_lx - 58, earth_cy - 12), "Tropical\nZone", font=small_font, fill=(140, 120, 0))

    # Axis angle label
    angle_x = earth_cx + ax_dx + 14
    angle_y = earth_cy - ay_dy + 40
    draw.text((angle_x, angle_y), "Axis\n(23.5°)", font=small_font, fill=(60, 60, 60))

    # ── Student fill-in lines ───────────────────────────────────────────────
    # Fixed start: diagram occupies ~600px (earth bottom ~550 + 30px gap + axis bottom)
    # Use 620 as a safe start for the fill-in section
    y_fill = 630
    draw.line([(MARGIN, y_fill - 2), (W - MARGIN, y_fill - 2)], fill="#cccccc", width=1)
    draw.text((MARGIN, y_fill + 6), "Fill in the blanks:", font=label_font, fill="black")
    y_fill += 42

    prompts = [
        "1. Earth's axis is tilted _______ degrees.",
        "2. The _______________________ is the imaginary line around the middle of Earth.",
        "3. The zone closest to the Equator is called the _______________________ Zone.",
        "4. The two coldest zones near the poles are called _______________________ Zones.",
    ]
    for p in prompts:
        draw.text((MARGIN + 20, y_fill), p, font=body_font, fill="black")
        y_fill += 36

    return img


def render_earth_diagram_to_image(output_path: str) -> Path:
    img = _render_earth_diagram()
    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    img.save(out, format="PNG")
    return out


def render_earth_diagram_to_pdf(output_path: str) -> Path:
    img = _render_earth_diagram().convert("RGB")
    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    img.save(out, format="PDF")
    return out


# ---------------------------------------------------------------------------
# Generation
# ---------------------------------------------------------------------------


def generate_biomes_week_series():
    output_dir = "biomes_week_series"
    os.makedirs(output_dir, exist_ok=True)

    # =========================================================================
    # MONDAY — The Sun, Earth's Tilt, and Why Seasons Exist
    # =========================================================================

    mon_reading = {
        "title": "Monday: The Sun, Earth's Tilt & Seasons",
        "passage_title": "Why Does Summer Feel So Different From Winter?",
        "passage": (
            "Steve just opened a brand-new Minecraft world and noticed something strange: "
            "his wheat grows fast and tall when the sun is high in the sky, but slower when the days are short. "
            "Why would that be? The answer is one of the most important ideas in all of science — "
            "and it starts with a tilt.\n\n"
            "Our Earth travels around the Sun once every 365 days — that is one year. "
            "But Earth does not stand up perfectly straight as it travels. "
            "It leans to one side at an angle of about 23.5 degrees. "
            "This lean is called Earth's AXIAL TILT, and it is the reason we have seasons.\n\n"
            "When the Northern Hemisphere (the top half of Earth) tilts TOWARD the Sun, "
            "sunlight hits it more directly — almost straight down. "
            "Direct sunlight is stronger and spreads over a smaller area, so it warms the land more. "
            "That is SUMMER. When the Northern Hemisphere tilts AWAY from the Sun, "
            "sunlight arrives at a low angle and spreads over a wider area, so it is weaker. "
            "That is WINTER. The Southern Hemisphere always experiences the opposite — "
            "when it is summer in the north, it is winter in the south!\n\n"
            "The EQUATOR is an imaginary line around the middle of Earth. "
            "Places near the equator barely tilt toward or away from the Sun, "
            "so they stay warm all year long and do not have four seasons the way we do. "
            "The POLES — the very top (North Pole) and bottom (South Pole) of Earth — "
            "tilt the most dramatically and experience extreme seasons: "
            "months of endless daylight in summer and months of total darkness in winter."
        ),
        "instructions": "Read the passage, study the labeled diagram, then answer the questions.",
        "questions": [
            {
                "prompt": "Why does Earth have seasons? What would happen if Earth had NO tilt?",
                "response_lines": 3,
            },
            {
                "prompt": "When the Northern Hemisphere tilts toward the Sun, what season is it there? What season is happening in the Southern Hemisphere at the same time?",
                "response_lines": 3,
            },
            {
                "prompt": "Why do places near the equator not have four seasons like we do?",
                "response_lines": 2,
            },
            {
                "prompt": "Point to a spot on the globe/diagram. Is that place having summer or winter right now? How do you know?",
                "response_lines": 3,
            },
        ],
        "vocabulary": [
            {
                "term": "Orbit",
                "definition": "The path Earth travels around the Sun — one trip takes 365 days (one year).",
            },
            {
                "term": "Axial Tilt",
                "definition": "Earth's 23.5° lean — the reason we have seasons.",
            },
            {
                "term": "Hemisphere",
                "definition": "Half of Earth. The Northern Hemisphere is above the equator; the Southern is below.",
            },
            {
                "term": "Equator",
                "definition": "The imaginary line around Earth's middle that divides it into north and south halves.",
            },
            {
                "term": "North Pole / South Pole",
                "definition": "The very top and bottom points of Earth's axis — the coldest, most extreme-season places on Earth.",
            },
            {
                "term": "Direct Sunlight",
                "definition": "Sunlight hitting at a steep angle — concentrated, strong, and warming (summer).",
            },
            {
                "term": "Indirect Sunlight",
                "definition": "Sunlight arriving at a shallow angle — spread out, weaker, and less warming (winter).",
            },
            {
                "term": "Season",
                "definition": "A time of year defined by temperature and daylight length — Spring, Summer, Autumn, Winter.",
            },
            {
                "term": "Axis",
                "definition": "The imaginary pole that runs from the North Pole to the South Pole through Earth's center.",
            },
        ],
    }
    ws = WorksheetFactory.create("reading_comprehension", mon_reading)
    render_reading_worksheet_to_image(ws, f"{output_dir}/01_monday_reading_card.png")
    render_reading_worksheet_to_pdf(ws, f"{output_dir}/01_monday_reading_card.pdf")

    # Monday Activity: Earth Axial Tilt Labeled Diagram (custom renderer)
    render_earth_diagram_to_image(f"{output_dir}/02_monday_earth_diagram.png")
    render_earth_diagram_to_pdf(f"{output_dir}/02_monday_earth_diagram.pdf")

    # =========================================================================
    # TUESDAY — Climate Zones: Earth's Three Temperature Belts
    # =========================================================================

    tue_reading = {
        "title": "Tuesday: Climate Zones",
        "passage_title": "Earth's Three Temperature Belts",
        "passage": (
            "In Minecraft, when Steve walks far enough north, the Jungle biome slowly turns into "
            "a Taiga, then a Snowy biome. The game is hinting at something real: "
            "Earth has distinct CLIMATE ZONES — large regions where the temperature and weather "
            "follow predictable patterns all year long.\n\n"
            "Climate zones exist because of axial tilt. Remember: places near the equator "
            "always receive direct, strong sunlight. Places near the poles always receive "
            "weak, angled sunlight. This creates three major climate zones:\n\n"
            "The TROPICAL ZONE surrounds the equator, between roughly 30 degrees North and "
            "30 degrees South latitude. It receives direct sunlight nearly year-round and is "
            "always warm or hot. Rain is common. This is where the world's rainforests thrive.\n\n"
            "The TEMPERATE ZONES sit between the tropical zone and the polar zones — "
            "from about 30 to 60 degrees latitude in both hemispheres. "
            "These zones experience all four seasons: warm summers and cold winters. "
            "Most of the United States, Europe, and China are in a temperate zone.\n\n"
            "The POLAR ZONES cover the areas above 60 degrees latitude, closest to the North "
            "and South Poles. They receive sunlight at a very shallow angle all year. "
            "They are extremely cold, have little rain, and experience the most extreme "
            "seasons — including months of near-total darkness in winter.\n\n"
            "LATITUDE is the measure of how far north or south you are from the equator, "
            "measured in degrees. The equator is 0°. The North Pole is 90° North. "
            "Knowing a place's latitude tells you which climate zone it is in — "
            "and from there, you can predict a lot about its weather, plants, and animals."
        ),
        "instructions": "Read about climate zones. Then answer the questions and sort the word bank.",
        "questions": [
            {
                "prompt": "Name the three climate zones. Which one is warmest? Which is coldest?",
                "response_lines": 3,
            },
            {
                "prompt": "What is latitude? How does latitude help you predict what the weather is like in a place?",
                "response_lines": 3,
            },
            {
                "prompt": "If you live at 45° North latitude, which climate zone are you in? What seasons would you expect?",
                "response_lines": 2,
            },
            {
                "prompt": "Why does the tropical zone stay warm all year while the polar zones stay cold all year?",
                "response_lines": 3,
            },
        ],
        "vocabulary": [
            {
                "term": "Climate Zone",
                "definition": "A large region of Earth with predictable long-term weather patterns.",
            },
            {
                "term": "Tropical Zone",
                "definition": "The warm belt around the equator (0°–30° latitude) — receives direct sunlight year-round.",
            },
            {
                "term": "Temperate Zone",
                "definition": "The mid-latitude belt (30°–60°) that experiences all four seasons.",
            },
            {
                "term": "Polar Zone",
                "definition": "The cold region near the poles (60°–90°) — receives only shallow, weak sunlight.",
            },
            {
                "term": "Latitude",
                "definition": "A measurement in degrees of how far north or south a location is from the equator.",
            },
            {
                "term": "Climate",
                "definition": "The average weather pattern of a place over many years — not today's weather, but what to expect generally.",
            },
            {
                "term": "Precipitation",
                "definition": "Any form of water falling from the sky — rain, snow, sleet, or hail.",
            },
            {
                "term": "Temperature Belt",
                "definition": "Another name for a climate zone — a band of Earth with similar temperature ranges.",
            },
        ],
    }
    ws = WorksheetFactory.create("reading_comprehension", tue_reading)
    render_reading_worksheet_to_image(ws, f"{output_dir}/03_tuesday_reading_card.png")
    render_reading_worksheet_to_pdf(ws, f"{output_dir}/03_tuesday_reading_card.pdf")

    # Tuesday Activity: Tree Map — Climate Zones → Characteristics
    tue_tree = {
        "title": "Tuesday: Climate Zones — Tree Map",
        "instructions": "Sort the words from the word bank into the correct climate zone.",
        "root_label": "Earth's Climate Zones",
        "branches": [
            {
                "label": "Tropical Zone",
                "slots": [
                    {"text": "Always warm"},
                    {"text": "Near the equator"},
                ],
                "slot_count": 2,
            },
            {
                "label": "Temperate Zone",
                "slots": [
                    {"text": "Four seasons"},
                    {"text": "Warm summers"},
                ],
                "slot_count": 2,
            },
            {
                "label": "Polar Zone",
                "slots": [
                    {"text": "Extremely cold"},
                    {"text": "Dark winters"},
                ],
                "slot_count": 2,
            },
        ],
        "word_bank": [
            "Always warm",
            "Four seasons",
            "Extremely cold",
            "Near the equator",
            "Warm summers",
            "Dark winters",
            "Rainforests grow here",
            "Most of the United States",
            "Near the poles",
        ],
    }
    ws = WorksheetFactory.create("tree_map", tue_tree)
    render_tree_map_to_image(ws, f"{output_dir}/04_tuesday_tree_map.png")
    render_tree_map_to_pdf(ws, f"{output_dir}/04_tuesday_tree_map.pdf")

    # =========================================================================
    # WEDNESDAY — Topography: How Landforms Shape the Land (and Biomes)
    # =========================================================================

    wed_reading = {
        "title": "Wednesday: Topography & Landforms",
        "passage_title": "Mountains, Valleys, and the Shape of the Land",
        "passage": (
            "Steve loves exploring Minecraft's terrain — one minute he is climbing a steep mountain, "
            "the next he is sailing across a flat plains biome. "
            "The shape of the land is called TOPOGRAPHY, and in the real world it is one of the most "
            "powerful forces shaping where different plants, animals, and biomes exist.\n\n"
            "A MOUNTAIN is a large landform that rises steeply above the surrounding land. "
            "Mountains are cold at the top because temperature drops about 3°F for every 1,000 feet "
            "of elevation. High mountain peaks can be covered in snow even in the tropics! "
            "Mountains also create a special effect called a RAIN SHADOW. "
            "When wet ocean wind hits a mountain, it is forced upward. As it rises, it cools and "
            "drops its moisture as rain or snow on the windward (facing) side. "
            "By the time the air crosses the peak, it is dry. "
            "The other side — the LEEWARD side — receives very little rain. "
            "This is why deserts often form just east of mountain ranges.\n\n"
            "A VALLEY is a low area between hills or mountains, often carved by a river. "
            "Valleys tend to be warmer and wetter than the surrounding mountains. "
            "Rich soil in river valleys makes them some of the best farming land on Earth.\n\n"
            "A PLAIN is a large, flat area of land. Flat land holds heat, allows grasses to spread "
            "in every direction, and allows wind to sweep unobstructed. "
            "The world's great grasslands — the African Savanna, the American Great Plains, "
            "the Eurasian Steppe — are all flat or gently rolling plains.\n\n"
            "A PLATEAU is like a mountain with a flat top — a high, elevated area of flat land. "
            "Plateaus are often dry because they block moisture in a similar way to mountains. "
            "Finally, COASTLINES — where land meets ocean — have their own unique climates. "
            "The ocean absorbs and releases heat slowly, making coastal areas milder "
            "(less extreme) in both summer and winter than inland areas at the same latitude."
        ),
        "instructions": "Read about topography. Then answer the questions and complete the odd-one-out.",
        "questions": [
            {
                "prompt": "What is a rain shadow? Describe which side of a mountain gets more rain and why.",
                "response_lines": 3,
            },
            {
                "prompt": "Why are mountain peaks cold even when they are in a tropical climate zone?",
                "response_lines": 2,
            },
            {
                "prompt": "Why are coastlines milder in temperature than inland areas at the same latitude?",
                "response_lines": 2,
            },
            {
                "prompt": "If you know a desert lies just east of a mountain range, what does that tell you about the wind direction?",
                "response_lines": 3,
            },
        ],
        "vocabulary": [
            {
                "term": "Topography",
                "definition": "The shape, height, and arrangement of the physical features of the land.",
            },
            {
                "term": "Mountain",
                "definition": "A large landform rising steeply above surrounding land — colder at the top due to elevation.",
            },
            {
                "term": "Elevation",
                "definition": "Height above sea level — temperature drops as elevation rises.",
            },
            {
                "term": "Rain Shadow",
                "definition": "The dry region on the leeward side of a mountain, where air has already lost its moisture.",
            },
            {
                "term": "Windward Side",
                "definition": "The side of a mountain facing the wind — receives the most rain and snow.",
            },
            {
                "term": "Leeward Side",
                "definition": "The side of a mountain sheltered from the wind — dry because the air lost moisture on the other side.",
            },
            {
                "term": "Valley",
                "definition": "A low area between hills or mountains, often containing a river and rich soil.",
            },
            {
                "term": "Plain",
                "definition": "A large, flat area of land — ideal for grasses and farming.",
            },
            {
                "term": "Plateau",
                "definition": "An elevated area of flat land — high like a mountain but flat on top.",
            },
            {
                "term": "Coastline",
                "definition": "Where land meets the ocean — ocean proximity moderates temperature extremes.",
            },
        ],
    }
    ws = WorksheetFactory.create("reading_comprehension", wed_reading)
    render_reading_worksheet_to_image(ws, f"{output_dir}/05_wednesday_reading_card.png")
    render_reading_worksheet_to_pdf(ws, f"{output_dir}/05_wednesday_reading_card.pdf")

    # Wednesday Activity: Odd One Out — Landforms & Topography Logic
    wed_odd = {
        "title": "Wednesday: Topography — Odd One Out",
        "instructions": "Circle the item in each row that does NOT belong. Write why on the line.",
        "rows": [
            {
                "items": ["Mountain", "Valley", "Plateau", "Rain Cloud"],
                "odd_item": "Rain Cloud",
                "explanation": "Mountain, Valley, and Plateau are landforms. A rain cloud is weather, not a landform.",
            },
            {
                "items": ["Windward wet", "Leeward dry", "Rain shadow", "Valleys frozen"],
                "odd_item": "Valleys frozen",
                "explanation": "Valleys are warm and wet. The others describe the rain shadow effect correctly.",
            },
            {
                "items": ["Coastline", "Ocean mild", "Dry leeward", "Coast mild"],
                "odd_item": "Dry leeward",
                "explanation": "A dry leeward side is about mountains, not coastlines. The other three describe how oceans moderate coastal climates.",
            },
            {
                "items": ["Up = colder", "Peak snow", "Plains warm", "Valley cold"],
                "odd_item": "Valley cold",
                "explanation": "Valleys are warmer than peaks because they have lower elevation. The others correctly describe how elevation affects temperature.",
            },
            {
                "items": ["Savanna", "Great Plains", "Steppe", "Amazon Forest"],
                "odd_item": "Amazon Forest",
                "explanation": "Savanna, Great Plains, and Steppe are all flat grassland plains. The Amazon is a dense, wet tropical forest.",
            },
        ],
        "reasoning_lines": 2,
        "show_answers": False,
    }
    ws = WorksheetFactory.create("odd_one_out", wed_odd)
    render_odd_one_out_to_image(ws, f"{output_dir}/06_wednesday_odd_one_out.png")
    render_odd_one_out_to_pdf(ws, f"{output_dir}/06_wednesday_odd_one_out.pdf")

    # =========================================================================
    # THURSDAY — Biomes: How Climate + Topography Create Six Biomes
    # =========================================================================

    thu_reading = {
        "title": "Thursday: Earth's Biomes",
        "passage_title": "Why Does This Place Look the Way It Does?",
        "passage": (
            "Steve has explored every biome in Minecraft: the steamy Jungle, the frozen Tundra, "
            "the sandy Desert, the rolling Plains, the leafy Forest, and the deep Ocean. "
            "But why do these places look so different? The answer is everything we have learned this week: "
            "climate zone + topography + rainfall = BIOME.\n\n"
            "A BIOME is a large region of Earth defined by its climate, the type of plants that grow there, "
            "and the animals that live there. The same biome can appear on different continents "
            "if the climate conditions are similar. Here are Earth's six major biomes:\n\n"
            "TROPICAL RAINFOREST: Found near the equator in the tropical zone. "
            "Hot and wet all year — more than 80 inches of rain annually. "
            "Dense canopy of tall trees, extraordinary biodiversity. "
            "Examples: Amazon (South America), Congo (Africa), Borneo (Asia).\n\n"
            "DESERT: Found at about 30° latitude (tropical zone edges) or on the leeward side of mountains. "
            "Receives less than 10 inches of rain per year. Very hot days, cold nights. "
            "Plants store water (cactus, succulents). Examples: Sahara, Mojave, Atacama.\n\n"
            "GRASSLAND / SAVANNA: Flat or rolling plains in temperate and tropical zones. "
            "Seasonal rain — wet seasons and dry seasons. Too dry for many trees, "
            "but perfect for grasses and large grazing animals. "
            "Examples: African Savanna, American Great Plains, Eurasian Steppe.\n\n"
            "TEMPERATE FOREST: Found in temperate zones with moderate rainfall spread across all four seasons. "
            "Deciduous trees (oaks, maples, birches) lose their leaves in autumn. "
            "Rich, dark soil. Examples: Eastern United States, Western Europe, East Asia.\n\n"
            "TUNDRA: Found in polar zones and at the tops of very high mountains. "
            "Extremely cold, very little precipitation, almost no trees. "
            "The soil is called PERMAFROST — permanently frozen just below the surface. "
            "Short mosses, lichens, and grasses survive here. "
            "Examples: Northern Canada, Alaska, Siberia, Antarctica.\n\n"
            "OCEAN: Covers over 70% of Earth's surface. The ocean is the world's largest biome. "
            "It has its own zones — sunlit surface waters full of life, and cold, dark deep zones. "
            "The ocean regulates Earth's temperature and produces more than half of all the "
            "oxygen in our atmosphere through tiny organisms called PHYTOPLANKTON."
        ),
        "instructions": "Read about all six biomes. Then answer the questions.",
        "questions": [
            {
                "prompt": "Which biome is always hot and wet? Which is always cold and dry? What climate zone is each in?",
                "response_lines": 3,
            },
            {
                "prompt": "Explain how a desert can form both at 30° latitude AND on the leeward side of a mountain. What do these two situations have in common?",
                "response_lines": 3,
            },
            {
                "prompt": "What is permafrost? Why does it prevent trees from growing in the tundra?",
                "response_lines": 2,
            },
            {
                "prompt": "Why is the ocean considered a biome? Name two ways it supports life on the rest of Earth.",
                "response_lines": 3,
            },
            {
                "prompt": "If you wanted to find a temperate forest, what latitude range and what kind of rainfall pattern would you look for?",
                "response_lines": 2,
            },
        ],
        "vocabulary": [
            {
                "term": "Biome",
                "definition": "A large region of Earth defined by its climate, plants, and animals.",
            },
            {
                "term": "Tropical Rainforest",
                "definition": "Hot, wet biome near the equator — receives 80+ inches of rain per year, dense with life.",
            },
            {
                "term": "Desert",
                "definition": "Biome with less than 10 inches of rain per year — hot days, cold nights, plants store water.",
            },
            {
                "term": "Grassland / Savanna",
                "definition": "Flat biome with seasonal rain — too dry for many trees but rich with grasses and grazing animals.",
            },
            {
                "term": "Temperate Forest",
                "definition": "Biome in temperate zones with four seasons and deciduous trees that lose leaves in autumn.",
            },
            {
                "term": "Deciduous",
                "definition": "Trees that shed their leaves in autumn and grow new ones in spring.",
            },
            {
                "term": "Tundra",
                "definition": "Cold, nearly treeless biome in polar regions — frozen soil, mosses, and lichens survive here.",
            },
            {
                "term": "Permafrost",
                "definition": "A layer of soil that stays permanently frozen below the surface in tundra and polar regions.",
            },
            {
                "term": "Ocean Biome",
                "definition": "Earth's largest biome — covers 70% of the surface and regulates global temperature and oxygen.",
            },
            {
                "term": "Phytoplankton",
                "definition": "Tiny ocean organisms that use sunlight to make food AND produce over half of Earth's oxygen.",
            },
            {
                "term": "Biodiversity",
                "definition": "The variety of different plant and animal species in a region — rainforests have the highest biodiversity on Earth.",
            },
            {
                "term": "Canopy",
                "definition": "The top layer of a rainforest formed by the tallest trees — blocks most sunlight from reaching the forest floor.",
            },
        ],
    }
    ws = WorksheetFactory.create("reading_comprehension", thu_reading)
    render_reading_worksheet_to_image(ws, f"{output_dir}/07_thursday_reading_card.png")
    render_reading_worksheet_to_pdf(ws, f"{output_dir}/07_thursday_reading_card.pdf")

    # Thursday Activity: Feature Matrix — Six Biomes, split into Part A and Part B
    # Strict max 6 properties per sheet so column headers are legible

    # Part A: Temperature & Moisture — 6 properties exactly
    BIOME_ROWS_A = [
        {"name": "Rainforest", "checked_properties": ["Always Warm", "Very Wet"]},
        {"name": "Desert", "checked_properties": ["Very Dry", "Hot + Cold"]},
        {"name": "Grassland", "checked_properties": ["Seasonal Rain", "Warm"]},
        {"name": "Temp. Forest", "checked_properties": ["Four Seasons", "Moderate Rain"]},
        {"name": "Tundra", "checked_properties": ["Very Cold", "Very Dry"]},
        {"name": "Ocean", "checked_properties": ["Moderate Rain"]},
    ]
    thu_matrix_a = {
        "title": "Biomes Part A: Temperature & Moisture",
        "instructions": "Check the boxes that describe each biome's temperature and rainfall.",
        "items": BIOME_ROWS_A,
        "properties": [
            "Always Warm",
            "Very Cold",
            "Four Seasons",
            "Very Wet",
            "Seasonal Rain",
            "Very Dry",
        ],
        "show_answers": False,
    }
    ws = WorksheetFactory.create("feature_matrix", thu_matrix_a)
    render_feature_matrix_to_image(ws, f"{output_dir}/08a_thursday_feature_matrix_climate.png")
    render_feature_matrix_to_pdf(ws, f"{output_dir}/08a_thursday_feature_matrix_climate.pdf")

    # Part B: Plants & Special Features — 6 properties exactly
    BIOME_ROWS_B = [
        {"name": "Rainforest", "checked_properties": ["Dense Trees", "Permafrost"]},
        {"name": "Desert", "checked_properties": ["Stores Water", "Few Plants"]},
        {"name": "Grassland", "checked_properties": ["Grasses", "Migrations"]},
        {"name": "Temp. Forest", "checked_properties": ["Loses Leaves", "Rich Soil"]},
        {"name": "Tundra", "checked_properties": ["Permafrost", "Few Plants"]},
        {"name": "Ocean", "checked_properties": ["Makes Oxygen", "Migrations"]},
    ]
    # Fix: Rainforest doesn't have Permafrost — correct the data
    BIOME_ROWS_B[0]["checked_properties"] = ["Dense Trees"]
    thu_matrix_b = {
        "title": "Biomes Part B: Plants & Features",
        "instructions": "Check the boxes that describe each biome's plants and special features.",
        "items": BIOME_ROWS_B,
        "properties": [
            "Dense Trees",
            "Grasses",
            "Few Plants",
            "Stores Water",
            "Loses Leaves",
            "Permafrost",
        ],
        "show_answers": False,
    }
    ws = WorksheetFactory.create("feature_matrix", thu_matrix_b)
    render_feature_matrix_to_image(ws, f"{output_dir}/08b_thursday_feature_matrix_plants.png")
    render_feature_matrix_to_pdf(ws, f"{output_dir}/08b_thursday_feature_matrix_plants.pdf")

    # =========================================================================
    # FRIDAY — Seasons IN the Biomes + Personal Connection
    # =========================================================================

    fri_reading = {
        "title": "Friday: Seasons Across Biomes + My Biome",
        "passage_title": "How Every Biome Experiences Time Differently",
        "passage": (
            "Steve has one final question before he picks his Minecraft base biome: "
            "do all biomes have the same four seasons? The answer is a resounding NO — "
            "and understanding how each biome experiences time is the last piece of the puzzle.\n\n"
            "In a TEMPERATE FOREST, all four seasons are dramatic and distinct. "
            "Spring brings new leaves and flowers. Summer is warm and green. "
            "Autumn turns the leaves red, orange, and gold before they fall. "
            "Winter is cold and bare — the trees rest. This is the seasonal pattern most familiar "
            "to people who live in North America or Europe.\n\n"
            "In the TROPICAL RAINFOREST, there are no four seasons. "
            "It stays hot all year. Instead of summer and winter, the two seasons are WET and DRY. "
            "The wet season brings heavy rain nearly every day. "
            "The dry season is still warm but much less rainy.\n\n"
            "In the DESERT, seasons do technically change, but the story is told in temperature more than rain. "
            "Summer days can exceed 120°F (49°C). Winters can be surprisingly cold. "
            "Rain is always rare. Desert life waits for the brief rainy season to reproduce and grow.\n\n"
            "In the GRASSLAND and SAVANNA, the wet and dry seasons drive everything. "
            "Animals migrate thousands of miles following the rains, "
            "because the rains bring the fresh grass they need.\n\n"
            "In the TUNDRA, the seasons are extreme in a different way. "
            "Winter is nine months of dark, frozen land. "
            "The 'summer' is a brief six to ten weeks when the top layer of soil thaws just enough "
            "for mosses and wildflowers to bloom explosively. "
            "The sun never fully sets during tundra summer — that is called the MIDNIGHT SUN.\n\n"
            "The OCEAN also has seasons — water temperatures change, currents shift, "
            "and food becomes more or less abundant. "
            "Many ocean animals, like gray whales, migrate between warm and cold waters "
            "with the seasons, just like land animals do."
        ),
        "instructions": "Read about seasons in each biome. Then answer the questions and share your opinion!",
        "questions": [
            {
                "prompt": "Name the two seasons a tropical rainforest has instead of four. What causes them?",
                "response_lines": 2,
            },
            {
                "prompt": "What is the midnight sun? Which biome experiences it, and why does it happen?",
                "response_lines": 3,
            },
            {
                "prompt": "How do seasons affect animals in the grassland/savanna? Use the word 'migration' in your answer.",
                "response_lines": 3,
            },
            {
                "prompt": "OPINION: If you could build your Minecraft base in any real biome, which would you choose? Write at least 3 sentences explaining what the seasons would be like and why you would enjoy living there.",
                "response_lines": 5,
            },
        ],
        "vocabulary": [
            {
                "term": "Wet Season",
                "definition": "The rainy half of the year in tropical regions — replaces spring/summer in the rainforest and savanna.",
            },
            {
                "term": "Dry Season",
                "definition": "The less-rainy half of the year in tropical regions — still warm, but much less precipitation.",
            },
            {
                "term": "Migration",
                "definition": "The seasonal movement of animals from one region to another following food, water, or temperature.",
            },
            {
                "term": "Midnight Sun",
                "definition": "The phenomenon in polar regions during summer where the sun stays above the horizon even at midnight.",
            },
            {
                "term": "Permafrost Thaw",
                "definition": "The brief seasonal melting of the top layer of tundra soil that allows summer plants to bloom.",
            },
            {
                "term": "Current",
                "definition": "A large, flowing stream of water within the ocean — currents carry warm or cold water around the globe.",
            },
            {
                "term": "Biodiversity Pulse",
                "definition": "The explosion of life (flowers, insects, animals) that occurs in tundra during its brief summer.",
            },
            {
                "term": "Temperature Extreme",
                "definition": "When temperature swings very high or very low — deserts and tundras both experience this.",
            },
        ],
    }
    ws = WorksheetFactory.create("reading_comprehension", fri_reading)
    render_reading_worksheet_to_image(ws, f"{output_dir}/09_friday_reading_card.png")
    render_reading_worksheet_to_pdf(ws, f"{output_dir}/09_friday_reading_card.pdf")

    # =========================================================================
    # FRIDAY CAPSTONE — All Six Biomes Synthesis Feature Matrix
    # =========================================================================

    # Capstone — two clean 6-property sheets for from-memory review
    capstone_matrix_a = {
        "title": "Capstone Part A: Climate & Zone (From Memory)",
        "instructions": "Without notes: check every box that applies. Check your reading cards when done!",
        "items": [
            {"name": "Rainforest"},
            {"name": "Desert"},
            {"name": "Grassland"},
            {"name": "Temp. Forest"},
            {"name": "Tundra"},
            {"name": "Ocean"},
        ],
        "properties": [
            "Tropical Zone",
            "Temperate Zone",
            "Polar Zone",
            "Hot All Year",
            "Cold All Year",
            "Four Seasons",
        ],
        "show_answers": False,
    }

    capstone_matrix_b = {
        "title": "Capstone Part B: Plants & Features (From Memory)",
        "instructions": "Without notes: check every box that applies. Check your reading cards when done!",
        "items": [
            {"name": "Rainforest"},
            {"name": "Desert"},
            {"name": "Grassland"},
            {"name": "Temp. Forest"},
            {"name": "Tundra"},
            {"name": "Ocean"},
        ],
        "properties": [
            "Dense Trees",
            "Permafrost",
            "Mostly Grasses",
            "Few Plants",
            "Migrations",
            "Makes Oxygen",
        ],
        "show_answers": False,
    }
    ws = WorksheetFactory.create("feature_matrix", capstone_matrix_a)
    render_feature_matrix_to_image(ws, f"{output_dir}/10a_friday_capstone_climate.png")
    render_feature_matrix_to_pdf(ws, f"{output_dir}/10a_friday_capstone_climate.pdf")

    ws = WorksheetFactory.create("feature_matrix", capstone_matrix_b)
    render_feature_matrix_to_image(ws, f"{output_dir}/10b_friday_capstone_plants.png")
    render_feature_matrix_to_pdf(ws, f"{output_dir}/10b_friday_capstone_plants.pdf")

    # =========================================================================
    # END-OF-WEEK PARENT FEEDBACK
    # =========================================================================

    feedback = {
        "title": "End-of-Week Parent Feedback — Earth, Biomes & Seasons",
        "passage_title": "Week Summary & Teaching Notes",
        "passage": (
            "This week followed a causal arc: starting from first principles (the Sun and Earth's tilt) "
            "and building through seasons, climate zones, topography, biomes, and seasonal variation within biomes. "
            "Each concept was scaffolded on the previous one — by Friday, your child should be able to explain "
            "WHY a rainforest is wet and WHY a tundra is frozen, not just name them.\n\n"
            "Key concepts to check for genuine understanding (not just recall):\n"
            "• Axial tilt causes seasons — not distance from the Sun (common misconception).\n"
            "• Climate zones are about consistent, year-round patterns, not just current weather.\n"
            "• Rain shadows: wet side faces the wind; dry side is leeward.\n"
            "• Biomes are defined by climate + vegetation together — same latitude = similar biome.\n"
            "• Tropical regions have wet/dry seasons, not four seasons.\n\n"
            "Suggested follow-on activities for next week:\n"
            "• Find your current location on the globe — what biome do you live in?\n"
            "• Track daily weather for two weeks and compare to your biome's expected climate.\n"
            "• Research one animal from each biome and how it adapts to seasonal changes.\n"
            "• In Minecraft, navigate between biomes and identify their real-world counterparts."
        ),
        "instructions": "Please complete this feedback sheet after the week wraps up.",
        "questions": [
            {
                "prompt": "Overall comfort with the week's content (1 = struggled throughout, 5 = strong grasp of all concepts):",
                "response_lines": 1,
            },
            {
                "prompt": "Which day's lesson generated the most curiosity or questions? What did they ask?",
                "response_lines": 3,
            },
            {
                "prompt": "Was the causal arc (Sun → tilt → seasons → biomes) clear to your child by Friday? Did any step in the chain need more time?",
                "response_lines": 3,
            },
            {
                "prompt": "Did your child make the Minecraft connection naturally, or did it need prompting? Any moments where the game deepened the real-world concept?",
                "response_lines": 3,
            },
            {
                "prompt": "Which biome did they choose for their opinion piece on Friday, and why? Any surprises?",
                "response_lines": 2,
            },
            {"prompt": "Topics or vocabulary to revisit next week:", "response_lines": 2},
        ],
        "vocabulary": [
            {
                "term": "Key Misconception to Watch",
                "definition": "Earth is NOT closer to the Sun in summer — seasons are caused by TILT, not distance.",
            },
            {
                "term": "Strongest Concept This Week",
                "definition": "(Fill in after the week — which idea stuck best?)",
            },
            {
                "term": "Next Week's Hook",
                "definition": "Animal adaptations — how do creatures survive in their specific biome across all four seasons?",
            },
        ],
    }
    ws = WorksheetFactory.create("reading_comprehension", feedback)
    render_reading_worksheet_to_image(ws, f"{output_dir}/11_parent_feedback.png")
    render_reading_worksheet_to_pdf(ws, f"{output_dir}/11_parent_feedback.pdf")

    print(f"\nSuccessfully generated Earth, Biomes & Seasons series in '{output_dir}/'")
    print("13 worksheets (26 files: PNG + PDF each):\n")
    print("  Mon:     01_monday_reading_card                (Reading: Sun, Tilt, Seasons)")
    print("           02_monday_earth_diagram               (Custom: Labeled Axial Tilt Diagram)")
    print("  Tue:     03_tuesday_reading_card               (Reading: Climate Zones)")
    print("           04_tuesday_tree_map                   (Tree Map: 3 Climate Zones)")
    print("  Wed:     05_wednesday_reading_card             (Reading: Topography & Landforms)")
    print("           06_wednesday_odd_one_out              (Odd One Out: Landform Logic)")
    print("  Thu:     07_thursday_reading_card              (Reading: 6 Biomes)")
    print("           08a_thursday_feature_matrix_climate   (Feature Matrix Part A: Climate)")
    print("           08b_thursday_feature_matrix_plants    (Feature Matrix Part B: Plants)")
    print("  Fri:     09_friday_reading_card                (Reading: Seasons + Opinion)")
    print("           10a_friday_capstone_climate           (Capstone Part A: Climate)")
    print("           10b_friday_capstone_plants            (Capstone Part B: Plants)")
    print("  Wrap-up: 11_parent_feedback                    (End-of-week parent feedback)")


if __name__ == "__main__":
    generate_biomes_week_series()
