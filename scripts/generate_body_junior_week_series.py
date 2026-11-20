"""
Body Team Junior — Week Series: "Rudy's Rounds" for a pre-reader
Kindergarten (pre-reader) | Science (human body) + oral language | Layout: journal
Causal Arc: Air comes in (nose, mouth, lungs) → the heart pumps Rudy around → food goes down
            the food tube to the tummy → the liver and kidneys clean up → the brain is the boss
            (capstone: name the whole team and retell Rudy's trip)

The little-sibling companion to generate_body_week_series.py. Same narrator (Rudy the Red
Blood Cell), same day order and the same shared demos, so both children work one organ per day
side by side and share body_explorer.html. Everything here is read aloud by a grown-up; the
child's work is pointing, talking, tracing gray words, drawing lines, coloring, cutting and
gluing — no reading or writing from the text.

Through-line: Build-a-Body. On Monday a grown-up traces the child on a big sheet of paper. Every
day he colors, cuts out and glues that day's organs (printed on that day's cutout sheet) onto
his tracing, so by Friday the whole body team is on the wall. Each day also adds one line, with
a hand motion, to Rudy's chant (choral speaking with a repeated pattern).

Day shape (~45-60 minutes in short chunks): story + chant, Point & Talk, his job in the shared
demo, Label It page, Build-a-Body cutouts, and an optional turn in the Body Explorer.

Standards (Virginia SOL, verified against curriculum.db):
  Monday    — VA.SCIENCE.K.k.7.a (living things need air), VA.ENGLISH.K.k.c.2.c (chant)
  Tuesday   — VA.SCIENCE.K.k.6.b (living things have characteristics: a beating heart),
              VA.ENGLISH.K.k.c.1.a (one-on-one discussion)
  Wednesday — VA.SCIENCE.K.k.7.a (living things need food and water), VA.ENGLISH.K.k.c.1.a
  Thursday  — VA.SCIENCE.K.k.7.a (water), VA.SCIENCE.K.k.1 (observe the filter demo, ask
              questions), VA.ENGLISH.K.k.c.2.a (describe an experience in complete sentences)
  Friday    — VA.SCIENCE.K.k.5.a (five senses correspond to body structures), K.k.5.b,
              VA.ENGLISH.K.k.c.2.d (retell events in order with pictures), K.k.dsr.1.d

Organ shapes reuse the coordinate space of scripts/body_week_explorer.py (a 600 x 1000 front
view), so the paper pictures match what he sees on screen.

Output: body_junior_week_series/
  body_junior_week.html                (journal packet: story, Label It, cutouts per day)
  body_junior_week_teacher_guide.html  (sibling schedule, prompts, what to listen for)
  body_explorer.html                   (the shared interactive explorer)
"""

import os

os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import html
import random
import sys
from pathlib import Path

sys.path.insert(0, os.path.abspath("src"))
sys.path.insert(0, os.path.abspath("scripts"))

from body_week_explorer import build_html as build_explorer_html
from worksheet_html_renderer import build_print_packet_html, get_day_palette, render_worksheet_html
from worksheet_layouts import get_layout

random.seed(20261117)

# =============================================================================
# Organ shapes (explorer coordinates). Each element is a filled shape or a "tube"
# (a stroked path drawn as an outlined tube).
# =============================================================================

SKIN, SKIN_LINE = "#f6d7bf", "#c08a68"


def shape(tag: str, attrs: str, fill: str, stroke: str, sw: float = 3) -> dict:
    return {"tag": tag, "attrs": attrs, "fill": fill, "stroke": stroke, "sw": sw}


def tube(d: str, color: str, line: str, w: float) -> dict:
    return {"tube": True, "d": d, "fill": color, "stroke": line, "w": w}


def detail(svg: str) -> dict:
    return {"detail": svg}


LUNG_L = (
    "M 286 300 C 258 282 210 296 200 350 C 190 402 194 452 202 472 C 234 482 270 477 290 466 "
    "C 292 420 292 360 286 300 Z"
)
LUNG_R = (
    "M 310 300 C 338 286 378 300 388 350 C 396 398 396 446 390 466 C 374 472 362 472 354 468 "
    "C 352 448 340 432 326 424 C 314 405 312 360 310 300 Z"
)
HEART = "M 0 22 C -30 0 -38 -22 -22 -34 C -10 -42 0 -34 0 -24 C 0 -34 10 -42 22 -34 C 38 -22 30 0 0 22 Z"
SMALL_INT = (
    "M 310 578 C 290 590 262 605 262 615 C 262 628 338 622 338 636 C 338 650 262 644 262 658 "
    "C 262 672 338 666 338 680 C 338 690 300 690 280 688 C 268 687 258 690 250 690"
)
LARGE_INT = (
    "M 250 690 C 236 690 232 670 232 650 L 232 615 C 232 602 240 597 255 597 L 345 597 "
    "C 360 597 368 602 368 615 L 368 655 C 368 680 350 690 330 690 C 318 690 312 700 310 712"
)
ESOPHAGUS = (
    "M 304 176 C 312 184 314 196 314 210 L 314 300 C 315 360 316 420 320 462 "
    "C 324 490 335 505 345 515"
)

ORGANS: dict[str, dict] = {
    "nose_mouth": {
        "bbox": (282, 112, 36, 68),
        "els": [
            shape("path", 'd="M 300 116 L 291 146 Q 300 154 309 146 Z"', "#efc4a4", SKIN_LINE, 2),
            shape("ellipse", 'cx="300" cy="170" rx="15" ry="7"', "#7f1d1d", "#9f1239", 2),
            shape("ellipse", 'cx="300" cy="173" rx="8" ry="3"', "#f472b6", "#9f1239", 1),
        ],
    },
    "windpipe": {
        "bbox": (250, 178, 96, 160),
        "els": [
            tube("M 294 184 L 294 300", "#f1f5f9", "#6b7280", 11),
            tube(
                "M 294 300 Q 276 310 260 332 M 294 300 Q 314 310 336 332", "#f1f5f9", "#6b7280", 7
            ),
            detail(
                '<g stroke="#6b7280" stroke-width="2">'
                + "".join(
                    f'<line x1="289" y1="{y}" x2="299" y2="{y}"/>'
                    for y in (205, 225, 245, 265, 285)
                )
                + "</g>"
            ),
        ],
    },
    "lungs": {
        "bbox": (188, 280, 212, 205),
        "els": [
            shape("path", f'd="{LUNG_L}"', "#fda4af", "#e11d48"),
            shape("path", f'd="{LUNG_R}"', "#fda4af", "#e11d48"),
        ],
    },
    "lungL": {
        "bbox": (188, 280, 106, 205),
        "els": [shape("path", f'd="{LUNG_L}"', "#fda4af", "#e11d48")],
    },
    "lungR": {
        "bbox": (306, 284, 94, 192),
        "els": [shape("path", f'd="{LUNG_R}"', "#fda4af", "#e11d48")],
    },
    "heart": {
        "bbox": (268, 360, 110, 110),
        "els": [
            shape(
                "path",
                f'd="{HEART}" transform="translate(322 415) rotate(-35) scale(1.45)"',
                "#dc2626",
                "#7f1d1d",
                2.4,
            )
        ],
    },
    "esophagus": {"bbox": (294, 168, 60, 356), "els": [tube(ESOPHAGUS, "#e7b98f", "#a16207", 9)]},
    "stomach": {
        "bbox": (306, 494, 102, 102),
        "els": [
            shape(
                "path",
                'd="M 345 510 C 365 495 400 500 402 530 C 405 565 385 590 355 592 C 335 593 318 585 '
                '310 575 C 322 572 340 568 352 558 C 366 545 360 525 345 510 Z"',
                "#fbcfe8",
                "#db2777",
            )
        ],
    },
    "smallInt": {"bbox": (244, 570, 102, 126), "els": [tube(SMALL_INT, "#f9a8d4", "#be185d", 8)]},
    "largeInt": {"bbox": (220, 586, 160, 138), "els": [tube(LARGE_INT, "#f59e0b", "#b45309", 12)]},
    "liver": {
        "bbox": (190, 476, 148, 86),
        "els": [
            shape(
                "path",
                'd="M 196 492 C 230 478 300 478 330 492 C 335 505 322 520 300 528 C 270 545 230 '
                '560 210 552 C 196 540 192 510 196 492 Z"',
                "#9a3412",
                "#7c2d12",
            )
        ],
    },
    "kidneys": {
        "bbox": (220, 543, 160, 70),
        "els": [
            shape(
                "path",
                'd="M 245 545 C 230 545 222 560 222 578 C 222 598 232 610 247 610 C 258 610 262 600 '
                '256 590 C 252 582 252 572 256 565 C 262 555 258 545 245 545 Z"',
                "#be123c",
                "#881337",
            ),
            shape(
                "path",
                'd="M 355 545 C 370 545 378 560 378 578 C 378 598 368 610 353 610 C 342 610 338 600 '
                '344 590 C 348 582 348 572 344 565 C 338 555 342 545 355 545 Z"',
                "#be123c",
                "#881337",
            ),
            tube("M 254 598 C 262 640 280 680 292 700", "#fde047", "#a16207", 3),
            tube("M 346 598 C 338 640 320 680 308 700", "#fde047", "#a16207", 3),
        ],
    },
    "kidneyPair": {
        "bbox": (220, 543, 160, 70),
        "els": [],  # filled in below from "kidneys", without the thin tubes
    },
    "smallIntPad": {
        "bbox": (248, 596, 104, 100),
        "els": [
            shape("rect", 'x="252" y="600" width="96" height="92" rx="26"', "#fce7f3", "#be185d"),
            tube(
                "M 268 612 C 300 606 332 612 332 622 C 332 634 268 628 268 642 C 268 656 332 650 "
                "332 664 C 332 676 290 682 268 680",
                "#f9a8d4",
                "#be185d",
                6,
            ),
        ],
    },
    "bladder": {
        "bbox": (270, 686, 60, 44),
        "els": [shape("ellipse", 'cx="300" cy="708" rx="26" ry="18"', "#fdf2f8", "#db2777")],
    },
    "brain": {
        "bbox": (238, 38, 124, 100),
        "els": [
            shape("ellipse", 'cx="300" cy="88" rx="58" ry="46"', "#f9a8d4", "#be185d"),
            detail(
                '<g fill="none" stroke="#be185d" stroke-width="2" stroke-linecap="round">'
                '<path d="M 300 44 L 300 132"/><path d="M 252 78 C 262 66 272 86 282 72"/>'
                '<path d="M 256 104 C 266 92 276 112 286 98"/><path d="M 318 72 C 328 86 338 66 348 78"/>'
                '<path d="M 314 98 C 324 112 334 92 344 104"/></g>'
            ),
        ],
    },
    "eyes": {
        "bbox": (262, 116, 76, 22),
        "els": [
            shape("ellipse", 'cx="276" cy="126" rx="10" ry="7"', "#ffffff", "#334155", 2),
            shape("ellipse", 'cx="324" cy="126" rx="10" ry="7"', "#ffffff", "#334155", 2),
            detail(
                '<circle cx="276" cy="126" r="4" fill="#1e3a8a"/><circle cx="324" cy="126" r="4" fill="#1e3a8a"/>'
            ),
        ],
    },
    "ears": {
        "bbox": (216, 98, 168, 40),
        "els": [
            shape("ellipse", 'cx="229" cy="118" rx="10" ry="18"', "#f2c4a6", SKIN_LINE, 2.5),
            shape("ellipse", 'cx="371" cy="118" rx="10" ry="18"', "#f2c4a6", SKIN_LINE, 2.5),
        ],
    },
}

ORGANS["kidneyPair"]["els"] = [e for e in ORGANS["kidneys"]["els"] if not e.get("tube")]

BODY_SILHOUETTE = (
    f'<g stroke="{SKIN_LINE}" stroke-linecap="round" fill="none">'
    '<line x1="195" y1="275" x2="130" y2="610" stroke-width="58"/>'
    '<line x1="405" y1="275" x2="470" y2="610" stroke-width="58"/>'
    '<line x1="262" y1="700" x2="250" y2="975" stroke-width="80"/>'
    '<line x1="338" y1="700" x2="350" y2="975" stroke-width="80"/></g>'
    f'<g stroke="{SKIN}" stroke-linecap="round" fill="none">'
    '<line x1="195" y1="275" x2="130" y2="610" stroke-width="52"/>'
    '<line x1="405" y1="275" x2="470" y2="610" stroke-width="52"/>'
    '<line x1="262" y1="700" x2="250" y2="975" stroke-width="74"/>'
    '<line x1="338" y1="700" x2="350" y2="975" stroke-width="74"/></g>'
    '<path d="M 245 230 L 355 230 Q 415 236 420 285 L 412 560 Q 408 690 370 735 L 230 735 '
    f'Q 192 690 188 560 L 180 285 Q 185 236 245 230 Z" fill="{SKIN}" stroke="{SKIN_LINE}" '
    'stroke-width="3"/>'
    f'<rect x="272" y="180" width="56" height="64" rx="12" fill="{SKIN}"/>'
    f'<ellipse cx="300" cy="112" rx="72" ry="86" fill="{SKIN}" stroke="{SKIN_LINE}" stroke-width="3"/>'
)


def organ_svg(name: str, mode: str = "color") -> str:
    """Draw an organ. mode: color (finished), outline (white with a black line, to color in),
    ghost (faded, for organs learned on earlier days)."""
    out = []
    for e in ORGANS[name]["els"]:
        if "detail" in e:
            if mode != "ghost":
                svg = e["detail"]
                if mode == "outline":
                    svg = svg.replace('fill="#1e3a8a"', 'fill="#111"')
                out.append(svg)
            continue
        if e.get("tube"):
            line = "#111" if mode == "outline" else e["stroke"]
            inner = "#fff" if mode == "outline" else e["fill"]
            op = ' opacity="0.35"' if mode == "ghost" else ""
            out.append(
                f'<g fill="none" stroke-linecap="round" stroke-linejoin="round"{op}>'
                f'<path d="{e["d"]}" stroke="{line}" stroke-width="{e["w"] + 5}"/>'
                f'<path d="{e["d"]}" stroke="{inner}" stroke-width="{e["w"]}"/></g>'
            )
            continue
        fill = "#fff" if mode == "outline" else e["fill"]
        stroke = "#111" if mode == "outline" else e["stroke"]
        sw = max(e["sw"], 3.5) if mode == "outline" else e["sw"]
        op = ' opacity="0.35"' if mode == "ghost" else ""
        out.append(
            f'<{e["tag"]} {e["attrs"]} fill="{fill}" stroke="{stroke}" stroke-width="{sw}"{op}/>'
        )
    return "".join(out)


def icon_svg(name: str, x: float, y: float, size: float) -> str:
    """An organ shrunk to fit a size x size box at (x, y), for word cards."""
    bx, by, bw, bh = ORGANS[name]["bbox"]
    s = size / max(bw, bh)
    ox = x + (size - bw * s) / 2 - bx * s
    oy = y + (size - bh * s) / 2 - by * s
    return f'<g transform="translate({ox:.1f} {oy:.1f}) scale({s:.4f})">{organ_svg(name)}</g>'


def rudy_svg(r: float, cx: float = 0, cy: float = 0, colored: bool = True) -> str:
    fill = "#dc2626" if colored else "#fff"
    k = r / 12
    return (
        f'<g transform="translate({cx} {cy}) scale({k:.3f})">'
        f'<circle r="12" fill="{fill}" stroke="#111" stroke-width="1.4"/>'
        '<circle cx="-4" cy="-3" r="2.3" fill="#fff" stroke="#111" stroke-width=".6"/>'
        '<circle cx="4" cy="-3" r="2.3" fill="#fff" stroke="#111" stroke-width=".6"/>'
        '<circle cx="-4" cy="-3" r="1" fill="#111"/><circle cx="4" cy="-3" r="1" fill="#111"/>'
        '<path d="M -4.5 4 Q 0 8 4.5 4" fill="none" stroke="#111" stroke-width="1.3" '
        'stroke-linecap="round"/></g>'
    )


# =============================================================================
# Page pieces
# =============================================================================

JR_CSS = """
<style>
  .jr-label-svg { height: 5.1in; max-width: 100%; display: block; margin: 0 auto 8px; }
  .jr-words { display: grid; gap: 0.16in 0.2in; margin: 4px 0 8px; }
  .jr-word { position: relative; border: 3px solid #111; border-radius: 14px; height: 0.85in;
    display: flex; align-items: center; justify-content: center; gap: 8px; padding: 0 8px; }
  .jr-word-dot { position: absolute; top: -9px; left: 50%; margin-left: -8px; width: 16px;
    height: 16px; border-radius: 50%; background: #111; }
  .jr-emoji { font-size: 30pt; line-height: 1; }
  .jr-trace { font-size: 25pt; font-weight: bold; color: #d4d4d8;
    -webkit-text-stroke: 1px #a1a1aa; letter-spacing: .03em; white-space: nowrap; }
  .jr-chant { border: 3px solid; border-radius: 14px; padding: 8px 14px; margin: 8px 0 10px;
    font-size: 15pt; line-height: 1.45; text-align: center; break-inside: avoid; }
  .jr-chant small { display: block; font-size: 9pt; color: #555; text-transform: uppercase;
    letter-spacing: .08em; }
  .jr-chant i { font-size: 10pt; color: #444; }
  .jr-talk { border-left: 6px solid; background: #fff7ed; border-radius: 0 10px 10px 0;
    padding: 6px 12px; margin: 8px 0; font-size: 11pt; break-inside: avoid; }
  .jr-talk b { display: block; font-size: 9pt; text-transform: uppercase; letter-spacing: .08em; }
  .jr-talk li { margin: 3px 0; }
  .jr-cut { display: flex; flex-wrap: wrap; gap: 0.18in 0.25in; align-items: flex-end;
    justify-content: center; margin-top: 6px; }
  .jr-piece { text-align: center; font-size: 10pt; font-weight: bold; break-inside: avoid; }
  .jr-piece svg { display: block; margin: 0 auto 3px; }
  .jr-piece small { display: block; font-weight: normal; color: #444; }
  .jr-match { display: grid; grid-template-columns: 1fr 1.4in 1fr; row-gap: 0.16in; margin-top: 8px; }
  .jr-mcard { border: 3px solid #111; border-radius: 14px; height: 0.95in; display: flex;
    align-items: center; justify-content: center; gap: 10px; font-size: 13pt; font-weight: bold; }
  .jr-mcard span { font-size: 38pt; line-height: 1; }
  .jr-dot { display: flex; align-items: center; }
  .jr-dot.l { justify-content: flex-start; } .jr-dot.r { justify-content: flex-end; }
  .jr-dot i { width: 14px; height: 14px; border-radius: 50%; background: #111; display: block; }
  .jr-cards { display: grid; grid-template-columns: repeat(4, 1fr); gap: 0.15in; margin: 8px 0; }
  .jr-card { border: 2px dashed #111; border-radius: 10px; height: 2.1in; display: flex;
    flex-direction: column; align-items: center; justify-content: center; text-align: center;
    padding: 6px; font-size: 10.5pt; font-weight: bold; }
  .jr-card svg { margin-bottom: 4px; }
  .jr-check { columns: 2; font-size: 12pt; margin-top: 6px; }
  .jr-check div { break-inside: avoid; margin: 4px 0; display: flex; align-items: center; gap: 8px; }
  .jr-check .bx { width: 0.24in; height: 0.24in; border: 2px solid #111; border-radius: 4px; }
  .jr-check .n { display: inline-flex; width: 0.3in; height: 0.3in; border-radius: 50%; color: #fff;
    align-items: center; justify-content: center; font-weight: bold; font-size: 11pt; }
</style>
"""


def block(kind: str, data: dict, day: str) -> str:
    fragment = render_worksheet_html(kind, data, day)
    if fragment is None:
        raise ValueError(f"No HTML renderer for kind={kind!r}")
    return fragment


def chant_box(day: str, lines: list[tuple[str, str]], new_from: int) -> str:
    primary, light = get_day_palette(day)
    rows = []
    for i, (line, motion) in enumerate(lines):
        weight = "bold" if i >= new_from else "normal"
        rows.append(
            f'<div style="font-weight:{weight}">{html.escape(line)} <i>({html.escape(motion)})</i></div>'
        )
    return (
        f'<div class="jr-chant" style="border-color:{primary};background:{light}">'
        f"<small>Rudy's chant — say it together with the motions</small>{''.join(rows)}</div>"
    )


def talk_box(day: str, questions: list[str]) -> str:
    primary, _ = get_day_palette(day)
    items = "".join(f"<li>{html.escape(q)}</li>" for q in questions)
    return (
        f'<div class="jr-talk" style="border-color:{primary}"><b style="color:{primary}">'
        f"Talk together — grown-up asks, you answer out loud</b><ul>{items}</ul></div>"
    )


def label_it_svg(
    today: list[str], ghosts: list[str], crop: tuple, words: list[tuple[str, str]]
) -> str:
    """A big body picture with today's organs to color, then a row of word cards underneath.

    words: (word, icon) where icon is an organ key or an emoji. Cards are shuffled so their
    order never gives the answer away; the child draws each line from a card's dot himself.
    """
    x0, y0, x1, y1 = crop
    organs = "".join(organ_svg(g, "ghost") for g in ghosts) + "".join(
        organ_svg(t, "outline") for t in today
    )
    picture = (
        f'<svg class="jr-label-svg" viewBox="{x0 - 20} {y0 - 10} {x1 - x0 + 40} {y1 - y0 + 20}" '
        f'xmlns="http://www.w3.org/2000/svg">'
        f'<clipPath id="crop-{x0}-{y0}"><rect x="{x0 - 20}" y="{y0 - 10}" width="{x1 - x0 + 40}" '
        f'height="{y1 - y0 + 20}"/></clipPath>'
        f'<g clip-path="url(#crop-{x0}-{y0})">{BODY_SILHOUETTE}{organs}</g></svg>'
    )
    order = list(words)
    random.shuffle(order)
    cards = []
    for word, icon in order:
        if icon in ORGANS:
            pic = f'<svg width="0.6in" height="0.6in" viewBox="0 0 100 100">{icon_svg(icon, 4, 4, 92)}</svg>'
        else:
            pic = f'<span class="jr-emoji">{icon}</span>'
        cards.append(
            f'<div class="jr-word"><i class="jr-word-dot"></i>{pic}'
            f'<span class="jr-trace" style="font-size:{25 if len(word) <= 7 else 19}pt">'
            f"{html.escape(word)}</span></div>"
        )
    cols = min(len(order), 3)
    return (
        picture
        + f'<div class="jr-words" style="grid-template-columns:repeat({cols},1fr)">{"".join(cards)}</div>'
    )


def cut_piece(name: str, width_in: float, caption: str, note: str = "") -> str:
    bx, by, bw, bh = ORGANS[name]["bbox"]
    pad = max(bw, bh) * 0.04
    h_in = width_in * (bh + 2 * pad) / (bw + 2 * pad)
    note_html = f"<small>{html.escape(note)}</small>" if note else ""
    return (
        f'<div class="jr-piece"><svg width="{width_in:.2f}in" height="{h_in:.2f}in" '
        f'viewBox="{bx - pad:.1f} {by - pad:.1f} {bw + 2 * pad:.1f} {bh + 2 * pad:.1f}" '
        f'xmlns="http://www.w3.org/2000/svg">{organ_svg(name, "outline")}</svg>'
        f"{html.escape(caption)}{note_html}</div>"
    )


def rudy_pieces(n: int, size_in: float = 1.0) -> str:
    one = (
        f'<svg width="{size_in}in" height="{size_in}in" viewBox="-13 -13 26 26">'
        f"{rudy_svg(12, colored=False)}</svg>"
    )
    return "".join(f'<div class="jr-piece">{one}</div>' for _ in range(n))


def generate_body_junior_week_series():
    output_dir = Path("body_junior_week_series")
    output_dir.mkdir(exist_ok=True)
    pages: list[tuple[str, str]] = []
    journal = get_layout("journal")

    def page(day: str, idx: int, title: str, subtitle: str, inner: str) -> None:
        primary, light = get_day_palette(day)
        meta = {
            "day_label": day,
            "title": title,
            "subtitle": subtitle,
            "day_index": idx,
            "total_days": 5,
            "rail_text": f"{day} · Rudy's Rounds",
        }
        pages.append((day, JR_CSS + journal.render_page(inner, meta, primary, light)))

    chant = [
        ("Breathe in, breathe out — that's what lungs are all about!", "arms up, arms down"),
        ("Lub-dub, lub-dub — my heart pumps blood!", "pat your chest"),
        ("Chew, chew, swallow, squish — my tummy makes soup from every dish!", "rub your tummy"),
        ("Clean it up and wash it out — that's what kidneys are about!", "pretend to wash hands"),
        (
            "Eyes and ears send messages in — my brain says GO, and off I spin!",
            "tap your head, spin",
        ),
    ]

    # =========================================================================
    # MONDAY — Air comes in: nose, mouth, windpipe, lungs
    # =========================================================================
    day = "Monday"
    page(
        day,
        1,
        "Meet Rudy!",
        "Air comes in your nose and mouth and goes down to your lungs.",
        block(
            "storyPanel",
            {
                "who": "Rudy the Red Blood Cell (grown-up reads)",
                "text": "Hi! I'm Rudy. I'm a red blood cell — a tiny, tiny part of you. I'm so "
                "small you can't see me, but you have LOTS of me inside you right now!\n\n"
                "I ride in your blood like a little red truck. My job is to carry AIR to every "
                "part of your body.\n\n"
                "Air comes in your NOSE and your MOUTH. It zooms down a tube called the "
                "WINDPIPE into your two LUNGS. Your lungs are like two big, squishy sponges. "
                "That's where I load up! Breathe in — I load up. Breathe out — the old air goes "
                "away.",
            },
            day,
        )
        + chant_box(day, chant[:1], 0)
        + block(
            "taskList",
            {
                "tasks": [
                    {
                        "prompt": "Point to your NOSE. Point to your MOUTH.",
                        "detail": "Air comes in here!",
                    },
                    {
                        "prompt": "Put your hands on your chest and take a BIG breath.",
                        "detail": "Feel your chest get bigger? Your lungs are filling up like balloons.",
                    },
                    {
                        "prompt": "Breathe on a cold window or mirror.",
                        "detail": "See the foggy spot? That's your breath coming OUT.",
                    },
                ]
            },
            day,
        )
        + block(
            "doingCard",
            {
                "label": "Do it with your brother",
                "text": "Build the bottle lung together. YOUR job: pull the bottom balloon down and "
                "watch the balloon inside puff up — that's what your muscle under your lungs does! "
                "Then trace your whole body on a big sheet of paper. Draw your face: eyes, ears, "
                "NOSE and MOUTH.",
            },
            day,
        )
        + talk_box(
            day,
            [
                "Where does air come into your body?",
                "What happens to your breathing when you run fast? Let's run and find out!",
                "Can you breathe through just your nose? Just your mouth?",
            ],
        ),
    )
    page(
        day,
        1,
        "Label It: Air Parts",
        "Trace each gray word. Draw a line from the word to the body part. Color the lungs pink.",
        label_it_svg(
            ["nose_mouth", "windpipe", "lungs"],
            [],
            (180, 40, 420, 500),
            [("nose", "👃"), ("mouth", "👄"), ("windpipe", "windpipe"), ("lungs", "lungs")],
        )
        + block(
            "noteBox",
            {
                "text": "Grown-up: point to each part on the picture and ask, “What's this one? Can you find it on YOU?”"
            },
            day,
        ),
    )
    page(
        day,
        1,
        "Build-a-Body: Lungs",
        "Color, cut on the thick line, and glue onto your body tracing.",
        '<div class="jr-cut">'
        + cut_piece("lungL", 2.4, "Lung", "color it pink")
        + cut_piece("windpipe", 1.5, "Windpipe", "glue it on top")
        + cut_piece("lungR", 2.15, "Lung", "the smaller one, next to the heart")
        + "</div>"
        + block(
            "doingCard",
            {
                "label": "Glue it on",
                "text": "Glue the windpipe from the bottom of your neck down to your chest, then one lung "
                "on each side. The smaller lung goes on YOUR left side — that's where your heart "
                "will go tomorrow!",
            },
            day,
        ),
    )

    # =========================================================================
    # TUESDAY — The heart pumps Rudy around
    # =========================================================================
    day = "Tuesday"
    page(
        day,
        2,
        "The Pump",
        "Your heart pumps your blood all around your body.",
        block(
            "storyPanel",
            {
                "who": "Rudy (grown-up reads)",
                "text": "Rudy here! After I load up in the lungs, I need a push. That push comes "
                "from your HEART.\n\n"
                "Your heart is a strong muscle about as big as your fist. It squeezes, squeezes, "
                "squeezes, all day and all night, even when you sleep! Every squeeze pushes me "
                "through tubes all over your body — up to your head, down to your toes, and back "
                "again.\n\n"
                "Listen! Your heart makes a sound: lub-dub, lub-dub. When you run, it beats "
                "faster to move me faster. Zoom!",
            },
            day,
        )
        + chant_box(day, chant[:2], 1)
        + block(
            "taskList",
            {
                "tasks": [
                    {
                        "prompt": "Make a fist. That's how big your heart is!",
                        "detail": "Squeeze and open your fist again and again. That's what your heart does.",
                    },
                    {
                        "prompt": "Put your hand on your chest, a little to the left. Feel the thump?",
                        "detail": "If it's hard to feel, try after the jumping below.",
                    },
                    {
                        "prompt": "Jump 20 times, then feel your chest again.",
                        "detail": "Is your heart going faster or slower now?",
                    },
                ]
            },
            day,
        )
        + block(
            "doingCard",
            {
                "label": "Do it with your brother",
                "text": "Listen through the paper-tube stethoscope: you listen to your brother's heart, "
                "then he listens to yours. Say the sound you hear out loud: lub-dub! Then help him "
                "count heartbeats for his Pulse Lab — you say GO and STOP.",
            },
            day,
        )
        + talk_box(
            day,
            [
                "Why does your heart go faster when you run?",
                "Does your heart ever stop to take a nap? Why not?",
                "Is your heart shaped like a Valentine heart? (Look at the picture!)",
            ],
        ),
    )
    page(
        day,
        2,
        "Label It: The Heart",
        "Trace each gray word. Draw a line to the body part. Color the heart red.",
        label_it_svg(
            ["heart"],
            ["windpipe", "lungs"],
            (180, 200, 420, 500),
            [("heart", "heart"), ("lungs", "lungs")],
        )
        + block(
            "noteBox",
            {
                "text": "Then draw Rudy (a small red circle with a smile) next to the heart, ready to be pumped!"
            },
            day,
        ),
    )
    page(
        day,
        2,
        "Build-a-Body: Heart and Rudys",
        "Color the heart red. Color the Rudys too: some bright red, some dark red. Cut them out.",
        '<div class="jr-cut">'
        + cut_piece("heart", 2.3, "Heart", "about as big as your fist")
        + rudy_pieces(8)
        + "</div>"
        + block(
            "doingCard",
            {
                "label": "Glue it on",
                "text": "Glue the heart between the lungs, a little to YOUR left. Then draw a red crayon "
                "path from the heart down to one foot and back, and from the heart up to your head "
                "and back. Glue the Rudys along the path: bright red Rudys going OUT from the heart, "
                "dark red Rudys coming BACK. (Blood is always red — never blue!)",
            },
            day,
        ),
    )

    # =========================================================================
    # WEDNESDAY — Food goes down the food tube to the tummy
    # =========================================================================
    day = "Wednesday"
    page(
        day,
        3,
        "The Food Factory",
        "Food goes in your mouth, down the food tube, to your tummy.",
        block(
            "storyPanel",
            {
                "who": "Rudy (grown-up reads)",
                "text": "Rudy here! Your body needs FOOD to grow and play. Let's follow a bite!\n\n"
                "Your TEETH chew it up. Then you swallow, and it slides down the FOOD TUBE. The "
                "food tube is a different tube from the windpipe — air goes one way, food goes the "
                "other.\n\n"
                "The food lands in your STOMACH, your tummy. It squishes and squeezes the food "
                "into soup! Then the soup goes into a long, twisty tube called the INTESTINES. The "
                "good stuff soaks into the blood around me, and the leftovers come out when you go "
                "to the bathroom.",
            },
            day,
        )
        + chant_box(day, chant[:3], 2)
        + block(
            "taskList",
            {
                "tasks": [
                    {
                        "prompt": "Take a bite of cracker. Chew it slowly 20 times.",
                        "detail": "Your teeth and spit are already turning it into mush!",
                    },
                    {
                        "prompt": "Put your fingers gently on your throat and swallow.",
                        "detail": "Feel it move? That's the food tube squeezing.",
                    },
                    {
                        "prompt": "Put your hand on your tummy.",
                        "detail": "Your stomach is up high, under your ribs. The intestines are lower down.",
                    },
                ]
            },
            day,
        )
        + block(
            "doingCard",
            {
                "label": "Do it with your brother",
                "text": "Make the zip-bag stomach. YOUR job: crumble the crackers in and SQUISH the bag "
                "until it's soup. Then go outside and help stretch out the long string — that's how "
                "long a grown-up's intestine is! Walk along it from one end to the other.",
            },
            day,
        )
        + talk_box(
            day,
            [
                "Where does your food go after you swallow it?",
                "Why do grown-ups say, “Don't talk with your mouth full”? (Hint: two tubes!)",
                "What's your favorite food to give your body?",
            ],
        ),
    )
    page(
        day,
        3,
        "Label It: Food Parts",
        "Trace each gray word. Draw a line to the body part. Color the stomach and intestines.",
        label_it_svg(
            ["esophagus", "stomach", "smallInt", "largeInt"],
            ["lungs", "heart"],
            (180, 130, 420, 730),
            [
                ("mouth", "👄"),
                ("food tube", "esophagus"),
                ("stomach", "stomach"),
                ("intestines", "smallInt"),
            ],
        )
        + block(
            "noteBox",
            {
                "text": "Grown-up: trace the food's trip with your finger — mouth, food tube, stomach, intestines — and let him do it next."
            },
            day,
        ),
    )
    page(
        day,
        3,
        "Build-a-Body: Food Parts",
        "Color, cut on the thick line, and glue onto your body tracing.",
        '<div class="jr-cut">'
        + cut_piece("esophagus", 0.75, "Food tube", "")
        + cut_piece("stomach", 2.0, "Stomach", "")
        + cut_piece("largeInt", 2.8, "Big intestine", "cut around the outside")
        + cut_piece("smallIntPad", 2.0, "Small intestine", "glue it inside the big one")
        + "</div>"
        + block(
            "doingCard",
            {
                "label": "Glue it on",
                "text": "Glue the food tube from your mouth down behind the heart to the stomach. The "
                "stomach goes on YOUR left, under the lungs. Glue the big intestine low in your "
                "belly and the small intestine inside it.",
            },
            day,
        ),
    )

    # =========================================================================
    # THURSDAY — The clean-up crew: liver, kidneys, bladder
    # =========================================================================
    day = "Thursday"
    page(
        day,
        4,
        "The Clean-Up Crew",
        "Your liver and kidneys clean your blood.",
        block(
            "storyPanel",
            {
                "who": "Rudy (grown-up reads)",
                "text": "Rudy here! Your body makes trash, just like a kitchen does. The trash goes "
                "into the blood. Time for the clean-up crew!\n\n"
                "Your LIVER is a big organ under your ribs on your right side. It cleans yucky "
                "stuff out of the blood.\n\n"
                "Your two KIDNEYS are shaped like beans. They sit in your back. They wash the "
                "trash and extra water out of the blood. That makes PEE! The pee waits in your "
                "BLADDER, a stretchy bag, until you go to the bathroom. Drinking water helps your "
                "kidneys do their job.",
            },
            day,
        )
        + chant_box(day, chant[:4], 3)
        + block(
            "taskList",
            {
                "tasks": [
                    {
                        "prompt": "Put your hand on your right side, under your ribs.",
                        "detail": "Your liver is right there!",
                    },
                    {
                        "prompt": "Put both hands on your back, just above your waist.",
                        "detail": "Your two kidneys are under your hands.",
                    },
                    {
                        "prompt": "Drink a big glass of water.",
                        "detail": "Your kidneys say thank you!",
                    },
                ]
            },
            day,
        )
        + block(
            "doingCard",
            {
                "label": "Do it with your brother",
                "text": "Do the coffee-filter demo together. YOUR job: stir the dirt and glitter into the "
                "water, then pour it through the filter. Tell what you see: what got stuck? What went "
                "through? Use a whole sentence: “The ___ got stuck.”",
            },
            day,
        )
        + talk_box(
            day,
            [
                "What does the liver do?",
                "Why is it good to drink water?",
                "Tell me about the filter: what happened when you poured the dirty water?",
            ],
        ),
    )
    page(
        day,
        4,
        "Label It: Clean-Up Crew",
        "Trace each gray word. Draw a line to the body part. Color the liver brown and the kidneys red.",
        label_it_svg(
            ["liver", "kidneys", "bladder"],
            ["stomach", "largeInt", "smallInt"],
            (180, 460, 420, 740),
            [("liver", "liver"), ("kidneys", "kidneys"), ("bladder", "bladder")],
        )
        + block(
            "noteBox",
            {
                "text": "Grown-up: the kidneys are really in his back, behind the tummy. Have him put his hands there while he draws the line."
            },
            day,
        ),
    )
    page(
        day,
        4,
        "Build-a-Body: Clean-Up Crew",
        "Color, cut on the thick line, and glue onto your body tracing.",
        '<div class="jr-cut">'
        + cut_piece("liver", 3.6, "Liver", "color it brown")
        + cut_piece("kidneyPair", 3.4, "Kidneys", "cut them out — there are two!")
        + cut_piece("bladder", 1.6, "Bladder", "")
        + "</div>"
        + block(
            "doingCard",
            {
                "label": "Glue it on",
                "text": "Glue the liver under the lungs on YOUR right side. Glue one kidney on each side, "
                "low behind the tummy, and the bladder at the very bottom. Then draw two yellow "
                "tubes from the kidneys down to the bladder — that's where the pee goes!",
            },
            day,
        ),
    )

    # =========================================================================
    # FRIDAY — The brain is the boss; five senses; name the whole team
    # =========================================================================
    day = "Friday"
    page(
        day,
        5,
        "The Boss!",
        "Your brain is the boss of your body.",
        block(
            "storyPanel",
            {
                "who": "Rudy (grown-up reads)",
                "text": "Rudy here, at my favorite stop: your BRAIN! It's inside your head, safe "
                "under your hard skull, like a helmet.\n\n"
                "Your brain is the BOSS. It keeps your lungs breathing and your heart beating, "
                "even when you sleep.\n\n"
                "Your brain also gets messages from your five SENSES. Your EYES see. Your EARS "
                "hear. Your NOSE smells. Your TONGUE tastes. Your SKIN feels. Then the brain says "
                "what to do: “Catch that ball!” “Smell that cookie!” Thanks for riding along with "
                "me this week, buddy!",
            },
            day,
        )
        + chant_box(day, chant, 4)
        + block(
            "taskList",
            {
                "tasks": [
                    {
                        "prompt": "Senses game: close your eyes. What can you hear? What can you smell?",
                        "detail": "Grown-up: shake a jingly thing, then hold up an orange or a cookie.",
                    },
                    {
                        "prompt": "Catch game: a grown-up drops a ruler or a scarf. Catch it!",
                        "detail": "Your eyes tell your brain, and your brain tells your hand. Fast!",
                    },
                    {
                        "prompt": "Say the WHOLE chant with all the motions.",
                        "detail": "Teach it to someone in your family tonight!",
                    },
                ]
            },
            day,
        )
        + talk_box(
            day,
            [
                "Who is the boss of your body?",
                "Which sense do you use when you eat ice cream? (Maybe more than one!)",
                "What was your favorite body part this week? Why?",
            ],
        ),
    )
    page(
        day,
        5,
        "Label It: The Boss and the Senses",
        "Trace each gray word. Draw a line to the body part. Color the brain pink.",
        label_it_svg(
            ["brain", "eyes", "ears", "nose_mouth"],
            [],
            (200, 30, 400, 196),
            [("brain", "brain"), ("eye", "👁️"), ("ear", "👂"), ("nose", "👃"), ("mouth", "👅")],
        ),
    )

    senses = [("👁️", "eyes"), ("👂", "ears"), ("👃", "nose"), ("👅", "tongue"), ("✋", "skin")]
    things = [
        ("🌈", "rainbow", "eyes"),
        ("🔔", "bell", "ears"),
        ("🌸", "flower", "nose"),
        ("🍦", "ice cream", "tongue"),
        ("🧸", "soft teddy", "skin"),
    ]
    shuffled_things = things[:]
    while [t[2] for t in shuffled_things] == [s[1] for s in senses]:
        random.shuffle(shuffled_things)
    match_rows = "".join(
        f'<div class="jr-mcard"><span>{s_icon}</span>{s_word}</div><div class="jr-dot l"><i></i>'
        f'<i style="margin-left:auto"></i></div><div class="jr-mcard"><span>{t_icon}</span>{t_word}</div>'
        for (s_icon, s_word), (t_icon, t_word, _) in zip(senses, shuffled_things, strict=True)
    )
    page(
        day,
        5,
        "Five Senses Match",
        "Which body part do you use? Draw a line from each body part to the thing it senses.",
        f'<div class="jr-match">{match_rows}</div>'
        + block(
            "noteBox",
            {
                "text": "Grown-up: read each word. After each line, ask: “Can you use that sense right now? Show me!”"
            },
            day,
        ),
    )

    team = [
        "nose_mouth",
        "windpipe",
        "lungs",
        "heart",
        "esophagus",
        "stomach",
        "smallInt",
        "largeInt",
        "liver",
        "kidneys",
        "bladder",
        "brain",
    ]
    team_words = [
        "nose & mouth",
        "windpipe",
        "lungs",
        "heart",
        "food tube",
        "stomach",
        "small intestine",
        "big intestine",
        "liver",
        "kidneys",
        "bladder",
        "brain",
    ]
    markers = {
        "nose_mouth": (316, 150),
        "windpipe": (294, 240),
        "lungs": (230, 400),
        "heart": (330, 420),
        "esophagus": (316, 260),
        "stomach": (372, 548),
        "smallInt": (300, 640),
        "largeInt": (236, 648),
        "liver": (246, 506),
        "kidneys": (360, 600),
        "bladder": (300, 708),
        "brain": (300, 84),
    }
    primary, _ = get_day_palette(day)
    order = [
        k
        for k in [
            "kidneys",
            "largeInt",
            "liver",
            "stomach",
            "smallInt",
            "bladder",
            "windpipe",
            "lungs",
            "esophagus",
            "heart",
            "nose_mouth",
            "brain",
        ]
    ]
    marks = "".join(
        f'<circle cx="{markers[k][0]}" cy="{markers[k][1]}" r="15" fill="{primary}" stroke="#fff" '
        f'stroke-width="3"/><text x="{markers[k][0]}" y="{markers[k][1] + 6}" font-size="17" '
        f'font-weight="bold" fill="#fff" text-anchor="middle">{team.index(k) + 1}</text>'
        for k in team
    )
    body_full = (
        f'<svg viewBox="170 20 260 740" style="height:6.4in;display:block;margin:0 auto" '
        f'xmlns="http://www.w3.org/2000/svg">{BODY_SILHOUETTE}'
        + "".join(organ_svg(k) for k in order)
        + organ_svg("eyes")
        + organ_svg("ears")
        + marks
        + "</svg>"
    )
    check = "".join(
        f'<div><span class="n" style="background:{primary}">{i}</span><span class="bx"></span>{w}</div>'
        for i, w in enumerate(team_words, 1)
    )
    page(
        day,
        5,
        "Can You Name It? The Whole Team",
        "Grown-up points to a number. Can you name that body part and tell its job? Check the box!",
        '<div style="display:grid;grid-template-columns:3.1in 1fr;gap:0.2in;align-items:center">'
        f'<div>{body_full}</div><div class="jr-check" style="columns:1">{check}</div></div>',
    )

    retell = [
        ("lungs", "Rudy loads up with air in the LUNGS."),
        ("heart", "The HEART squeezes and pumps him."),
        ("run", "Rudy drops off air all over the body, so you can run and play."),
        ("heart", "Back to the HEART — and around again!"),
    ]
    cards_order = list(range(len(retell)))
    while cards_order == sorted(cards_order):
        random.shuffle(cards_order)
    retell_cards = []
    for i in cards_order:
        key, text = retell[i]
        if key == "run":
            pic = '<div style="font-size:44pt;line-height:1">🏃</div>'
        else:
            pic = f'<svg width="1.1in" height="1.1in" viewBox="0 0 100 100">{icon_svg(key, 5, 5, 90)}</svg>'
        retell_cards.append(f'<div class="jr-card">{pic}{html.escape(text)}</div>')
    page(
        day,
        5,
        "Retell Rudy's Trip + Build-a-Body: Brain",
        "Cut out the four cards. Put them in order and tell Rudy's trip in your own words.",
        f'<div class="jr-cards">{"".join(retell_cards)}</div>'
        + '<div class="jr-cut">'
        + cut_piece("brain", 3.0, "Brain", "color it pink and glue it in the head")
        + "</div>"
        + block(
            "doingCard",
            {
                "label": "Finish your body",
                "text": "Glue the brain in the head. Draw yellow lines (nerves) from the brain down the back "
                "and out to the hands and feet. Then hang your body team on the wall and give a tour: "
                "point to each part and tell what it does!",
            },
            day,
        ),
    )

    page(
        day,
        5,
        "Grown-Up Notes",
        "A few notes for next week's planning.",
        block(
            "taskList",
            {
                "tasks": [
                    {
                        "prompt": "How many of the 12 body parts could he name on Friday?",
                        "response_lines": 1,
                    },
                    {
                        "prompt": "Which activity did he love most? (chant, cutting, demos, explorer?)",
                        "response_lines": 1,
                    },
                    {
                        "prompt": "Could he retell Rudy's trip in order with the cards?",
                        "response_lines": 1,
                    },
                    {
                        "prompt": "Questions he asked that we should explore next:",
                        "response_lines": 2,
                    },
                ]
            },
            day,
        ),
    )

    packet = build_print_packet_html(
        pages, packet_title="Body Team Junior — Rudy's Rounds", layout="journal"
    )
    packet_path = output_dir / "body_junior_week.html"
    packet_path.write_text(packet, encoding="utf-8")

    match_key = "".join(
        f"<li>{s_word} &rarr; {next(t[1] for t in things if t[2] == s_word)}</li>"
        for _, s_word in senses
    )
    retell_key = " &rarr; ".join(f"card {cards_order.index(i) + 1}" for i in range(len(retell)))
    guide = TEACHER_GUIDE.replace("{{MATCH_KEY}}", match_key).replace("{{RETELL_KEY}}", retell_key)
    assert "{{" not in guide
    guide_path = output_dir / "body_junior_week_teacher_guide.html"
    guide_path.write_text(guide, encoding="utf-8")
    explorer_path = output_dir / "body_explorer.html"
    explorer_path.write_text(build_explorer_html(), encoding="utf-8")

    print(f"Generated {len(pages)} pages -> {output_dir}/")
    print(f"Packet:        {packet_path}")
    print(f"Teacher guide: {guide_path}")
    print(f"Body explorer: {explorer_path}")
    for d, n in [("Mon", 3), ("Tue", 3), ("Wed", 3), ("Thu", 3), ("Fri", 6)]:
        print(f"  {d}: {n} pages")


TEACHER_GUIDE = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>Body Team Junior — Grown-Up Guide</title>
  <style>
    @page { size: letter; margin: 0.5in 0.6in; }
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body { font-family: 'Trebuchet MS', Arial, sans-serif; font-size: 11pt; color: #111; line-height: 1.5; }
    @media screen { body { background: #b0b0b0; padding: 24px; } .page { background: white; max-width: 7.5in; margin: 0 auto 28px; padding: 0.45in 0.5in; box-shadow: 0 4px 18px rgba(0,0,0,.28); min-height: 10.3in; } }
    @media print { body { background: white; padding: 0; } .page { padding: 0; box-shadow: none; } * { -webkit-print-color-adjust: exact; print-color-adjust: exact; } }
    .page { page-break-after: always; break-after: page; }
    .page:last-child { page-break-after: avoid; break-after: avoid; }
    h1 { font-size: 18pt; color: #b91c1c; border-bottom: 3px solid #b91c1c; padding-bottom: 5px; margin-bottom: 10px; }
    h2 { font-size: 13pt; color: #fff; background: #1d4ed8; padding: 5px 10px; border-radius: 3px; margin: 14px 0 6px; }
    h2.tue { background: #15803d; } h2.wed { background: #7c3aed; } h2.thu { background: #c2410c; } h2.fri { background: #0f766e; }
    h3 { font-size: 10.5pt; font-weight: bold; color: #444; margin: 8px 0 3px; text-transform: uppercase; letter-spacing: 0.04em; }
    p, li { font-size: 10pt; margin-bottom: 4px; }
    ul, ol { padding-left: 18px; margin-bottom: 6px; }
    table { border-collapse: collapse; width: 100%; font-size: 9.5pt; margin: 4px 0 8px; }
    th, td { border: 1px solid #cbd5e1; padding: 4px 6px; text-align: left; vertical-align: top; }
    th { background: #f1f5f9; }
    .listen { background: #f0f4ff; border-left: 4px solid #1d4ed8; padding: 6px 10px; margin: 4px 0 8px; border-radius: 0 4px 4px 0; }
    .misconception { background: #fff3cd; border-left: 4px solid #d97706; padding: 6px 10px; margin: 4px 0 8px; border-radius: 0 4px 4px 0; }
  </style>
</head>
<body>

<div class="page">
  <h1>Body Team Junior &mdash; Grown-Up Guide</h1>
  <p><strong>Who it's for:</strong> Theodore, a pre-reader, running alongside his brother's Body Team Week. Same narrator (Rudy the Red Blood Cell), same organ each day, same demos &mdash; each boy has his own job.</p>
  <p><strong>How it works:</strong> you read everything aloud. His work is pointing, talking, tracing gray words, drawing lines, coloring, cutting and gluing. Nothing asks him to read or write sentences.</p>
  <p><strong>Standards:</strong> VA.SCIENCE.K.k.7.a (living things need air, food and water), K.k.6.b, K.k.5.a&ndash;b (five senses and their body parts), K.k.1 (observe, ask questions); VA.ENGLISH.K.k.c.1.a (one-on-one discussion), K.k.c.2.a (complete sentences), K.k.c.2.c (chant with a repeated pattern), K.k.c.2.d (retell in order with pictures), K.k.dsr.1.d (related read-alouds).</p>
  <h3>Extra materials (beyond the big-kid list)</h3>
  <ul>
    <li>A sheet of paper as long as he is (butcher paper, wrapping paper turned over, or taped-together printer paper) &mdash; for the Monday body tracing</li>
    <li>Crayons (pink, red, dark red, brown, yellow), child scissors, a glue stick, tape to hang the tracing</li>
    <li>Print the Build-a-Body pages on cardstock if you have it; the pieces survive gluing better</li>
  </ul>
  <h3>A day at a glance (about 45&ndash;60 minutes, in short chunks)</h3>
  <table>
    <tr><th>Chunk</th><th>Theodore</th><th>While his brother&hellip;</th></tr>
    <tr><td>1. Story &amp; chant (5 min)</td><td>Listens to Rudy's story; says the chant with motions</td><td>reads his own Rudy passage</td></tr>
    <tr><td>2. Point &amp; Talk (5&ndash;10)</td><td>Point-and-feel tasks; you ask the Talk Together questions</td><td>works on his questions</td></tr>
    <tr><td>3. Shared demo (10&ndash;15)</td><td>Has his own job in the demo (pulls, squishes, pours, catches)</td><td>runs the demo and his lab sheet</td></tr>
    <tr><td>4. Label It (10)</td><td>Traces gray words, draws a line to each body part, colors</td><td>does his application page</td></tr>
    <tr><td>5. Build-a-Body (10&ndash;15)</td><td>Colors, cuts, glues today's organs on his tracing</td><td>&mdash;</td></tr>
    <tr><td>6. Explorer (5, optional)</td><td>Taps today's day button in <code>body_explorer.html</code>, finds Rudy, taps the organ</td><td>can share the tablet</td></tr>
  </table>
  <h3>Label It tips</h3>
  <p>The word boxes are in mixed-up order on purpose, so he has to find the part. Let him trace the gray letters with a crayon, then draw a line from the black dot to the body part. Ask &ldquo;Can you find it on <em>you</em>?&rdquo; every time. Getting the line right matters much more than neat letters.</p>

  <h2>Monday &mdash; Air Parts</h2>
  <div class="listen"><p><strong>Listen for:</strong> &ldquo;Air goes in my nose (or mouth) and down to my lungs.&rdquo; Any version of &ldquo;my chest gets bigger when I breathe in&rdquo; is a win.</p></div>
  <p><strong>Demo job:</strong> he pulls the bottle lung's bottom balloon down and watches the inside balloon puff up. Say: &ldquo;You just did what your breathing muscle does!&rdquo;</p>
  <div class="misconception"><p>&ldquo;Air goes into my tummy.&rdquo; Big belly breaths make it look that way. The air goes to the lungs; the belly moves because the muscle under the lungs pulls down.</p></div>

  <h2 class="tue">Tuesday &mdash; The Heart</h2>
  <div class="listen"><p><strong>Listen for:</strong> &ldquo;My heart pumps my blood.&rdquo; &ldquo;It goes faster when I run.&rdquo; Accept &ldquo;it beats&rdquo; or &ldquo;it squeezes.&rdquo;</p></div>
  <p><strong>Demo job:</strong> listens through the paper tube and says &ldquo;lub-dub&rdquo; out loud; says GO and STOP for his brother's 15-second pulse counts.</p>
  <div class="misconception"><p>&ldquo;The heart is shaped like a Valentine.&rdquo; Point to the picture: it's more like a fist. And blood is always red, never blue &mdash; that's why the Rudys are bright red and dark red.</p></div>
</div>

<div class="page">
  <h2 class="wed">Wednesday &mdash; Food Parts</h2>
  <div class="listen"><p><strong>Listen for:</strong> the order &mdash; mouth, food tube, tummy, intestines. &ldquo;Food and air go down different tubes.&rdquo;</p></div>
  <p><strong>Demo job:</strong> crumbles crackers into the zip bag and squishes it into soup; walks the length of the 20-foot string outside.</p>
  <div class="misconception"><p>&ldquo;Food goes down the windpipe.&rdquo; The Label It picture shows two separate tubes. A little flap covers the windpipe when we swallow &mdash; that's why we don't talk with our mouths full.</p></div>

  <h2 class="thu">Thursday &mdash; Clean-Up Crew</h2>
  <div class="listen"><p><strong>Listen for:</strong> a complete sentence about the filter (&ldquo;The dirt got stuck&rdquo;), and &ldquo;kidneys make pee&rdquo; / &ldquo;water helps my kidneys.&rdquo; Giggles are fine &mdash; the bathroom is a perfectly good science topic at this age.</p></div>
  <p><strong>Demo job:</strong> stirs the dirt and glitter into the water and pours it through the coffee filter.</p>
  <div class="misconception"><p>&ldquo;The kidneys are in my tummy.&rdquo; They're in his back. Have him put his hands on his back before he glues them on.</p></div>

  <h2 class="fri">Friday &mdash; The Boss</h2>
  <div class="listen"><p><strong>Listen for:</strong> &ldquo;My brain is the boss,&rdquo; and the five senses matched to their body parts. In the retell, any order that starts at the lungs and ends back at the heart is right.</p></div>
  <h3>Five Senses Match &mdash; Answers</h3>
  <ul>{{MATCH_KEY}}</ul>
  <p><em>Accept extra lines with a good reason: ice cream also uses the eyes, nose and skin (it's cold!).</em></p>
  <h3>Retell Cards &mdash; Correct Order</h3>
  <p>Lungs (load up) &rarr; heart (pump) &rarr; body (drop off air so you can run) &rarr; back to the heart. On his sheet that is: {{RETELL_KEY}}.</p>
  <h3>Can You Name It?</h3>
  <p>Point to the numbers in any order. Count what he can name <em>and</em> give a job for (&ldquo;the heart pumps&rdquo;). Eight or more out of 12 is a strong week for a pre-reader.</p>
  <div class="misconception"><p>&ldquo;My eyes see by themselves.&rdquo; The eyes and ears collect the message; the brain figures out what it means. The catch game shows it: eyes tell brain, brain tells hand.</p></div>
  <h3>The chant (all five lines)</h3>
  <ol>
    <li>Breathe in, breathe out &mdash; that's what lungs are all about! <em>(arms up, arms down)</em></li>
    <li>Lub-dub, lub-dub &mdash; my heart pumps blood! <em>(pat your chest)</em></li>
    <li>Chew, chew, swallow, squish &mdash; my tummy makes soup from every dish! <em>(rub your tummy)</em></li>
    <li>Clean it up and wash it out &mdash; that's what kidneys are about! <em>(pretend to wash hands)</em></li>
    <li>Eyes and ears send messages in &mdash; my brain says GO, and off I spin! <em>(tap your head, spin)</em></li>
  </ol>
</div>

</body>
</html>"""


if __name__ == "__main__":
    generate_body_junior_week_series()
