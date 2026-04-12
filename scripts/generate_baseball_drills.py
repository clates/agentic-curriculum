"""
Generate 4-per-sheet printable keyring drill cards for baseball practice.

Output: baseball_drills_series/  (PNG preview + PDF for printing)
  - sheet_1.png / sheet_1.pdf  (cards 1–4)
  - sheet_2.png / sheet_2.pdf  (cards 5–8)

Each card:
  - Title bar (card number + drill name)
  - FOCUS line (one sentence, highlighted)
  - Setup section
  - Execute section
  - Key Tip section
  - Punched-hole marker circle (top-center) for keyring
"""

import os

os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import sys
import math
from PIL import Image, ImageDraw, ImageFont

# ---------------------------------------------------------------------------
# Path setup — mirror the pattern used by all other generate_*.py scripts
# ---------------------------------------------------------------------------
sys.path.insert(0, os.path.abspath("src"))

# ---------------------------------------------------------------------------
# Reuse font helpers from worksheet_renderer
# ---------------------------------------------------------------------------
from pathlib import Path

_FONT_CANDIDATES = (
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
)
_FONT_BOLD_CANDIDATES = (
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
)


def _load_font(size: int, bold: bool = False):
    candidates = _FONT_BOLD_CANDIDATES if bold else _FONT_CANDIDATES
    for path in candidates:
        if Path(path).exists():
            return ImageFont.truetype(path, size)
    return ImageFont.load_default()


def _text_width(font, text: str) -> int:
    bbox = font.getbbox(text or " ")
    return int(bbox[2] - bbox[0])


def _line_height(font, extra: int = 6) -> int:
    try:
        ascent, descent = font.getmetrics()
        return ascent + descent + extra
    except Exception:
        bbox = font.getbbox("Ag")
        return int(bbox[3] - bbox[1]) + extra


def _wrap_text(text: str, font, max_width: int) -> list[str]:
    words = text.strip().split()
    if not words:
        return []
    lines = []
    current = words[0]
    for word in words[1:]:
        candidate = f"{current} {word}"
        if _text_width(font, candidate) <= max_width:
            current = candidate
        else:
            lines.append(current)
            current = word
    lines.append(current)
    return lines


# ---------------------------------------------------------------------------
# Drill data
# ---------------------------------------------------------------------------

DRILLS = [
    {
        "number": 1,
        "name": "Hit the Tee",
        "focus": "Eye discipline — lock eyes on a specific target to improve contact consistency.",
        "setup": [
            "Wrap three strips of different colored tape (e.g., red, blue, green) around the neck of the batting tee.",
            "No ball needed.",
        ],
        "execute": [
            "Hitter takes their normal stance.",
            'Coach calls out a color — e.g., "RED!"',
            "Hitter swings and makes contact with that specific color on the tee.",
        ],
        "tip": "Keeps eyes locked on a small target, building the habit of watching all the way to contact.",
    },
    {
        "number": 2,
        "name": "Plunger Drill",
        "focus": "Early success — build confidence with an oversized target before scaling down to a baseball.",
        "setup": [
            "Insert an upside-down bathroom plunger into the batting tee hole.",
            "Place a large, light ball (kickball or beach ball) on the plunger cup.",
        ],
        "execute": [
            "Hitter takes their stance facing the oversized ball.",
            "Swing and make solid contact with the large ball.",
            "Progress: gradually move to smaller balls as confidence grows (volleyball → softball → baseball).",
        ],
        "tip": "Start big, work small. The large target builds the swing pattern before introducing a regulation ball.",
    },
    {
        "number": 3,
        "name": "Red, White & Blue Bases",
        "focus": "Base navigation — replace abstract base numbers with memorable colors for young players.",
        "setup": [
            "Replace or overlay bases: 1st = Red, 2nd = White, 3rd = Blue.",
            "Use colored throw-down bases or colored tape.",
        ],
        "execute": [
            "Batter hits the ball normally.",
            'Coach yells the color instead of the number — e.g., "RUN TO RED!"',
            "Player sprints to the corresponding colored base.",
        ],
        "tip": 'Colors are far easier for ages 4–5 to recall under pressure than "First" or "Third."',
    },
    {
        "number": 4,
        "name": "High-Low Throw",
        "focus": "Throwing accuracy — teach players to control the trajectory of their throws.",
        "setup": [
            "Run a strip of tape or rope across a fence at chest height.",
            "Player stands at a natural throwing distance.",
        ],
        "execute": [
            "Player gets set in throwing position.",
            'Coach calls "HIGH" or "LOW."',
            "Player throws the ball above the tape (HIGH) or below it (LOW).",
        ],
        "tip": "Separates throwing from catching into distinct, focused skills. One task at a time = faster learning.",
    },
    {
        "number": 5,
        "name": "Running THROUGH First",
        "focus": "Base-running efficiency — sprint through first base, not to it.",
        "setup": [
            "Place a cone 10–15 feet beyond first base in foul territory.",
            "The cone is the new finish line.",
        ],
        "execute": [
            "Player hits and immediately sprints toward first base.",
            "Run all the way through the bag to the cone.",
            "After crossing the bag, turn toward foul territory.",
        ],
        "tip": "The cone shifts the mental finish line beyond first base, maximizing speed through the bag.",
    },
    {
        "number": 6,
        "name": "Color Code Fielding",
        "focus": "Visual tracking — train players to watch the ball all the way into the glove.",
        "setup": [
            "Mark several baseballs with different colored tape or stickers (e.g., blue dot, yellow dot).",
            "Player gets into fielding position.",
        ],
        "execute": [
            "Coach rolls or hits a grounder toward the player.",
            "Player fields the ball.",
            "Upon glove contact, player immediately calls out the color on the ball.",
        ],
        "tip": "If the player can name the color, they watched it all the way in. Silence = eyes off the ball.",
    },
    {
        "number": 7,
        "name": "Bench Throwing",
        "focus": "Arm extension — feel a full arm arc for players who short-arm their throws.",
        "setup": [
            "Player lies on their back on a bench, throwing arm hanging freely off the side.",
            "Coach stands a short distance away to receive the throw.",
        ],
        "execute": [
            "Allow gravity to pull the arm fully downward into natural extension.",
            "From the extended position, bring the arm up through the full throwing arc.",
            "Release and follow through to the coach.",
        ],
        "tip": "Gravity creates the extension for them — players feel the correct full-arm motion they can't muscle through.",
    },
    {
        "number": 8,
        "name": "Block It",
        "focus": "Body positioning — keeping the ball in front is just as important as catching it.",
        "setup": [
            "Player takes fielding position (infield stance).",
            "Coach positioned 10–15 feet away with several balls.",
        ],
        "execute": [
            "Coach rolls balls to the left or right of the player.",
            "Player moves laterally like a hockey or soccer goalie.",
            "Goal: get the body in front of the ball to block it, even without a clean catch.",
        ],
        "tip": 'Reframes "missed it" as a success if the ball stays in front. A blocked ball is a prevented run.',
    },
    {
        "number": 9,
        "name": "Bungee Target Throw",
        "focus": "Throwing mechanics — develop a repeatable, accurate release by aiming at a defined target.",
        "setup": [
            "Attach green bungee cords in circles on the fence — these are the large targets.",
            "Attach blue bungee cords in circles nearby — these are the small targets.",
            "Player throws from an age-appropriate distance.",
        ],
        "execute": [
            "Start on green: throw at the larger green bungee circles to groove a consistent release.",
            "Once the player is hitting green reliably, call 'BLUE' — they switch to the smaller target.",
            "Alternate back to green any time the player needs to reset confidence.",
        ],
        "tip": "Accuracy comes from repeating the same mechanics, not from trying harder. Green builds the pattern; blue tests it.",
    },
    {
        "number": 10,
        "name": "Reach-Back Throw",
        "focus": "Arm extension — build the habit of a full reach-back before every throw.",
        "setup": [
            "Player stands in throwing stance, facing their target.",
            "Coach positions behind and to the throwing-arm side, holding a ball.",
        ],
        "execute": [
            "Player looks forward at the target and reaches the throwing arm as far back as possible — fully extended.",
            "Coach places the ball directly into the outstretched hand.",
            "Player throws immediately from that extended position with no windup adjustment.",
        ],
        "tip": "Loading at full extension makes the correct arm path the only path. Players learn the feel, not just the instruction.",
    },
    {
        "number": 11,
        "name": "Color Call Grounder",
        "focus": "Decision-making — process a color signal and a moving ball at the same time.",
        "setup": [
            "Coach has a bucket of mixed color-coded baseballs (tape or stickers).",
            "Player takes fielding position at an age-appropriate distance.",
            "Agree on one target color before starting (e.g., 'Field the BLUE balls only').",
        ],
        "execute": [
            "Coach rolls a grounder and calls a color out loud as the ball leaves their hand.",
            "If the called color matches the target — player fields it normally.",
            "If it does not match — player lets it go (or steps aside).",
        ],
        "tip": "Missing the ball on purpose is the right answer here. Hesitating on a non-match means the brain is still learning to process two signals at once — that's exactly the goal.",
    },
    {
        "number": 12,
        "name": "Bucket Sort",
        "focus": "Fielding transition — secure the ball and move out of the catch quickly and deliberately.",
        "setup": [
            "Place two or three buckets a few steps apart, each labeled with a color (tape or cone).",
            "Coach has a bucket of mixed color-coded baseballs.",
            "Player starts in fielding position between the buckets and the coach.",
        ],
        "execute": [
            "Coach hits or rolls grounders in rapid succession.",
            "Player fields each ball, reads its color, and carries or underhand-tosses it into the matching bucket.",
            "Reset immediately to fielding position before the next ball arrives.",
        ],
        "tip": "Speed is secondary — a clean field and a correct sort beats a rushed one. Push the pace only after the movement pattern is solid.",
    },
    {
        "number": 13,
        "name": "Color Target Relay",
        "focus": "Fielding-to-throw transition — field cleanly first, then select and hit a target.",
        "setup": [
            "Place a colored cone at first, second, and third base (matching the ball colors in use).",
            "Coach positions at home plate area with a bucket of mixed color-coded baseballs.",
            "A catcher or bucket stands at each base to receive throws.",
        ],
        "execute": [
            "Coach rolls a grounder and simultaneously calls a color.",
            "Player fields the ball cleanly.",
            "Player throws to the base whose cone matches the called color.",
        ],
        "tip": "The throw target is decided by the color call — not by where the player is looking. This trains fielders to process their target before they ever have the ball in hand.",
    },
]

# ---------------------------------------------------------------------------
# Layout constants — letter paper (8.5 × 11 in) at 150 DPI for fast preview
# ---------------------------------------------------------------------------
DPI = 150
PAGE_W = int(8.5 * DPI)  # 1275 px
PAGE_H = int(11.0 * DPI)  # 1650 px
MARGIN = int(0.18 * DPI)  # tight outer margin

# 2×2 grid
COLS = 2
ROWS = 2
GUTTER = int(0.12 * DPI)  # narrow gap between cards

CARD_W = (PAGE_W - 2 * MARGIN - (COLS - 1) * GUTTER) // COLS
CARD_H = (PAGE_H - 2 * MARGIN - (ROWS - 1) * GUTTER) // ROWS

# Cut-line style
CUT_DASH = 8
CUT_GAP = 6
CUT_COLOR = (180, 180, 180)

# Card colors
TITLE_BG = (20, 60, 120)  # deep navy
TITLE_FG = (255, 255, 255)
FOCUS_BG = (255, 243, 180)  # soft yellow highlight
FOCUS_FG = (80, 40, 0)
SECTION_LABEL_FG = (20, 60, 120)
BODY_FG = (30, 30, 30)
CARD_BG = (250, 252, 255)
HOLE_COLOR = (200, 200, 200)
BORDER_COLOR = (20, 60, 120)
ROUNDED_RADIUS = 14

PAD = int(0.055 * DPI)  # inner card padding


def _draw_dashed_line(draw, x0, y0, x1, y1, dash=CUT_DASH, gap=CUT_GAP, color=CUT_COLOR, width=1):
    """Draw a horizontal or vertical dashed line."""
    dx = x1 - x0
    dy = y1 - y0
    length = math.sqrt(dx * dx + dy * dy)
    if length == 0:
        return
    ux, uy = dx / length, dy / length
    pos = 0.0
    drawing = True
    while pos < length:
        seg = dash if drawing else gap
        end = min(pos + seg, length)
        if drawing:
            draw.line(
                [(x0 + ux * pos, y0 + uy * pos), (x0 + ux * end, y0 + uy * end)],
                fill=color,
                width=width,
            )
        pos = end
        drawing = not drawing


def _rounded_rect(draw, x0, y0, x1, y1, r, fill, outline=None, outline_width=2):
    draw.rounded_rectangle(
        [x0, y0, x1, y1], radius=r, fill=fill, outline=outline, width=outline_width
    )


def _measure_card_content(drill: dict, content_w: int, scale: float = 1.0):
    """
    Return pre-computed layout data for a card's content area.
    Fonts and wrapped lines are pre-calculated so we can do a two-pass render
    (measure then place) to fill vertical space evenly.
    scale: multiplier on base font sizes — auto-fitted per card by the caller.
    """
    section_label_font = _load_font(int(0.215 * DPI * scale), bold=True)
    body_font = _load_font(int(0.198 * DPI * scale))
    focus_font = _load_font(int(0.198 * DPI * scale), bold=False)
    focus_label_font = _load_font(int(0.215 * DPI * scale), bold=True)
    tip_label_font = _load_font(int(0.194 * DPI * scale), bold=True)
    tip_body_font = _load_font(int(0.187 * DPI * scale), bold=False)

    slh = _line_height(section_label_font, extra=2)
    blh = _line_height(body_font, extra=2)
    flh = _line_height(focus_font, extra=2)
    tlh = _line_height(tip_body_font, extra=2)

    # FOCUS block
    focus_label = "FOCUS"
    focus_label_w = _text_width(focus_label_font, focus_label + "  ")
    focus_wrapped = _wrap_text(drill["focus"], focus_font, content_w - focus_label_w)
    focus_block_h = max(_line_height(focus_label_font), len(focus_wrapped) * flh) + int(PAD * 0.5)

    # SETUP section
    setup_items = drill["setup"]
    setup_lines: list[list[str]] = []
    for item in setup_items:
        bullet_w = _text_width(body_font, "• ")
        setup_lines.append(_wrap_text(item, body_font, content_w - bullet_w))
    setup_h = slh + sum(len(wl) * blh for wl in setup_lines)

    # EXECUTE section
    execute_items = [f"{i + 1}. {step}" for i, step in enumerate(drill["execute"])]
    execute_lines: list[list[str]] = []
    for item in execute_items:
        execute_lines.append(_wrap_text(item, body_font, content_w))
    execute_h = slh + sum(len(wl) * blh for wl in execute_lines)

    # TIP block
    tip_label = "KEY TIP:"
    tip_label_w = _text_width(tip_label_font, tip_label + " ")
    tip_wrapped = _wrap_text(drill["tip"], tip_body_font, content_w - tip_label_w)
    tip_block_h = max(_line_height(tip_label_font), len(tip_wrapped) * tlh) + int(PAD * 0.6)

    total_content_h = focus_block_h + setup_h + execute_h + tip_block_h

    return {
        "section_label_font": section_label_font,
        "body_font": body_font,
        "focus_font": focus_font,
        "focus_label_font": focus_label_font,
        "tip_label_font": tip_label_font,
        "tip_body_font": tip_body_font,
        "slh": slh,
        "blh": blh,
        "flh": flh,
        "tlh": tlh,
        "focus_label": focus_label,
        "focus_label_w": focus_label_w,
        "focus_wrapped": focus_wrapped,
        "focus_block_h": focus_block_h,
        "setup_items": setup_items,
        "setup_lines": setup_lines,
        "setup_h": setup_h,
        "execute_items": execute_items,
        "execute_lines": execute_lines,
        "execute_h": execute_h,
        "tip_label": tip_label,
        "tip_label_w": tip_label_w,
        "tip_wrapped": tip_wrapped,
        "tip_block_h": tip_block_h,
        "total_content_h": total_content_h,
    }


def _fit_scale(drill: dict, content_w: int, available_h: int) -> float:
    """
    Binary-search for the largest font scale where total content height
    fits within available_h (with 3 inter-section gaps at gap=0.07*DPI).
    """
    gap = int(0.07 * DPI)
    lo, hi = 0.3, 1.0
    best = lo
    for _ in range(18):  # 18 iterations → precision < 0.0001
        mid = (lo + hi) / 2
        m = _measure_card_content(drill, content_w, scale=mid)
        total = m["total_content_h"] + 3 * gap
        if total <= available_h:
            best = mid
            lo = mid
        else:
            hi = mid
    return best


def _draw_card(draw: ImageDraw.ImageDraw, drill: dict, cx: int, cy: int):
    """Render a single drill card with top-left corner at (cx, cy)."""

    x0, y0 = cx, cy
    x1, y1 = cx + CARD_W, cy + CARD_H

    # --- Card background ---
    _rounded_rect(
        draw, x0, y0, x1, y1, ROUNDED_RADIUS, fill=CARD_BG, outline=BORDER_COLOR, outline_width=2
    )

    # --- Keyring hole (top-center) ---
    hole_r = int(0.040 * DPI)
    hx = x0 + CARD_W // 2
    hy = y0 + hole_r + 3
    draw.ellipse(
        [hx - hole_r, hy - hole_r, hx + hole_r, hy + hole_r],
        fill=(255, 255, 255),
        outline=HOLE_COLOR,
        width=2,
    )
    draw.ellipse(
        [hx - hole_r - 3, hy - hole_r - 3, hx + hole_r + 3, hy + hole_r + 3],
        outline=(160, 160, 160),
        width=1,
    )

    # --- Title bar ---
    title_h = int(0.26 * DPI)
    title_top = y0 + hole_r * 2 + 4
    title_bottom = title_top + title_h

    _rounded_rect(
        draw,
        x0 + 2,
        title_top,
        x1 - 2,
        title_bottom + ROUNDED_RADIUS,
        ROUNDED_RADIUS,
        fill=TITLE_BG,
    )
    draw.rectangle(
        [x0 + 2, title_bottom - ROUNDED_RADIUS, x1 - 2, title_bottom + ROUNDED_RADIUS],
        fill=TITLE_BG,
    )

    title_font_size = int(0.220 * DPI)
    num_font_size = int(0.185 * DPI)
    num_font = _load_font(num_font_size, bold=True)

    num_text = f"#{drill['number']}"
    num_w = _text_width(num_font, num_text)
    num_x = x0 + PAD
    num_y = title_top + (title_h - _line_height(num_font)) // 2
    draw.text((num_x, num_y), num_text, font=num_font, fill=(180, 210, 255))

    name_text = drill["name"]
    name_font = _load_font(title_font_size, bold=True)
    available_title_w = CARD_W - num_w - PAD * 3
    name_lines = _wrap_text(name_text, name_font, available_title_w)
    if len(name_lines) > 1:
        name_font = _load_font(int(title_font_size * 0.82), bold=True)
        name_lines = _wrap_text(name_text, name_font, available_title_w)
    name_total_h = len(name_lines) * _line_height(name_font)
    ny = title_top + (title_h - name_total_h) // 2
    name_x = x0 + num_w + PAD * 2
    for line in name_lines:
        draw.text((name_x, ny), line, font=name_font, fill=TITLE_FG)
        ny += _line_height(name_font)

    # --- Content area (two-pass: measure then distribute) ---
    content_x = x0 + PAD
    content_w = CARD_W - PAD * 2
    content_area_top = title_bottom + PAD
    content_area_bottom = y1 - PAD
    available_h = content_area_bottom - content_area_top

    # Auto-fit: find largest scale where content fills but doesn't overflow
    scale = _fit_scale(drill, content_w, available_h)
    m = _measure_card_content(drill, content_w, scale=scale)

    # Fixed inter-section gap
    gap = int(0.07 * DPI)

    y = content_area_top + int(PAD * 0.3)  # minimal top breathing room

    slh = m["slh"]
    blh = m["blh"]

    # --- FOCUS block ---
    focus_block_h = m["focus_block_h"]
    flh = m["flh"]
    fx0 = x0 + PAD // 2
    fx1 = x1 - PAD // 2
    fy0 = y
    fy1 = fy0 + focus_block_h
    _rounded_rect(draw, fx0, fy0, fx1, fy1, 8, fill=FOCUS_BG)

    fl_y = fy0 + (focus_block_h - _line_height(m["focus_label_font"])) // 2
    draw.text(
        (fx0 + PAD // 2, fl_y), m["focus_label"], font=m["focus_label_font"], fill=(180, 100, 0)
    )

    ft_x = fx0 + m["focus_label_w"] + PAD // 2
    ft_y = fy0 + (focus_block_h - len(m["focus_wrapped"]) * flh) // 2
    for line in m["focus_wrapped"]:
        draw.text((ft_x, ft_y), line, font=m["focus_font"], fill=FOCUS_FG)
        ft_y += flh

    y = fy1 + gap

    # --- SETUP section ---
    draw.text((content_x, y), "SETUP", font=m["section_label_font"], fill=SECTION_LABEL_FG)
    y += slh
    bullet_w = _text_width(m["body_font"], "• ")
    for wrapped_lines in m["setup_lines"]:
        first = True
        for line in wrapped_lines:
            if first:
                draw.text((content_x, y), "•", font=m["body_font"], fill=BODY_FG)
                draw.text((content_x + bullet_w, y), line, font=m["body_font"], fill=BODY_FG)
                first = False
            else:
                draw.text((content_x + bullet_w, y), line, font=m["body_font"], fill=BODY_FG)
            y += blh
    y += gap

    # --- EXECUTE section ---
    draw.text((content_x, y), "DO IT", font=m["section_label_font"], fill=SECTION_LABEL_FG)
    y += slh
    for _item_text, wrapped_lines in zip(m["execute_items"], m["execute_lines"], strict=False):
        for line in wrapped_lines:
            draw.text((content_x, y), line, font=m["body_font"], fill=BODY_FG)
            y += blh
    y += gap

    # --- KEY TIP block ---
    tip_block_h = m["tip_block_h"]
    tlh = m["tlh"]
    tx0 = x0 + PAD // 2
    tx1 = x1 - PAD // 2
    ty0 = y
    ty1 = ty0 + tip_block_h
    # Clamp to card bottom
    if ty1 > y1 - 4:
        ty0 = y1 - 4 - tip_block_h
        ty1 = y1 - 4
    _rounded_rect(draw, tx0, ty0, tx1, ty1, 8, fill=(220, 235, 255))

    tl_y = ty0 + (tip_block_h - _line_height(m["tip_label_font"])) // 2
    draw.text((tx0 + PAD // 2, tl_y), m["tip_label"], font=m["tip_label_font"], fill=TITLE_BG)
    tb_x = tx0 + m["tip_label_w"] + PAD // 2
    tb_y = ty0 + (tip_block_h - len(m["tip_wrapped"]) * tlh) // 2
    for line in m["tip_wrapped"]:
        draw.text((tb_x, tb_y), line, font=m["tip_body_font"], fill=(30, 30, 80))
        tb_y += tlh


def render_sheet(drills_on_sheet: list[dict]) -> Image.Image:
    """Render up to 4 drill cards on a single page."""
    img = Image.new("RGB", (PAGE_W, PAGE_H), (240, 240, 240))
    draw = ImageDraw.Draw(img)

    # White page background
    draw.rectangle([0, 0, PAGE_W - 1, PAGE_H - 1], fill=(255, 255, 255))

    # Draw cut lines (full page cross)
    mid_x = MARGIN + CARD_W + GUTTER // 2
    mid_y = MARGIN + CARD_H + GUTTER // 2
    _draw_dashed_line(draw, MARGIN, mid_y, PAGE_W - MARGIN, mid_y, width=1)
    _draw_dashed_line(draw, mid_x, MARGIN, mid_x, PAGE_H - MARGIN, width=1)

    # Page footer
    footer_font = _load_font(int(0.045 * DPI))
    draw.text(
        (PAGE_W // 2 - 140, PAGE_H - MARGIN + 4),
        "Baseball Practice Drill Cards  —  Print, cut & punch hole for keyring",
        font=footer_font,
        fill=(150, 150, 150),
    )

    # Place cards
    positions = [
        (MARGIN, MARGIN),
        (MARGIN + CARD_W + GUTTER, MARGIN),
        (MARGIN, MARGIN + CARD_H + GUTTER),
        (MARGIN + CARD_W + GUTTER, MARGIN + CARD_H + GUTTER),
    ]

    for i, drill in enumerate(drills_on_sheet):
        cx, cy = positions[i]
        _draw_card(draw, drill, cx, cy)

    return img


def save_pdf(images: list[Image.Image], path: str):
    """Save a list of PIL Images as a multi-page PDF using Pillow's built-in PDF support."""
    if not images:
        return
    rgb_images = [img.convert("RGB") for img in images]
    rgb_images[0].save(
        path,
        format="PDF",
        save_all=True,
        append_images=rgb_images[1:],
        resolution=DPI,
    )


def generate_baseball_drills():
    output_dir = "baseball_drills_series"
    os.makedirs(output_dir, exist_ok=True)

    all_pages = []
    num_sheets = math.ceil(len(DRILLS) / 4)

    for sheet_idx in range(num_sheets):
        start = sheet_idx * 4
        drills_slice = DRILLS[start : start + 4]
        img = render_sheet(drills_slice)

        png_path = os.path.join(output_dir, f"sheet_{sheet_idx + 1}.png")
        img.save(png_path)
        print(f"Saved {png_path}")
        all_pages.append(img)

    # Single combined PDF
    pdf_path = os.path.join(output_dir, "baseball_drill_cards.pdf")
    save_pdf(all_pages, pdf_path)
    print(f"Saved {pdf_path}")

    png_list = ", ".join(f"sheet_{i + 1}.png" for i in range(num_sheets))
    print(f"\nDone! Output in ./{output_dir}/")
    print(f"  {png_list}  — PNG previews")
    print("  baseball_drill_cards.pdf   — print-ready PDF")


if __name__ == "__main__":
    generate_baseball_drills()
