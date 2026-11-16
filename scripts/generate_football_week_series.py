"""
Football — Week Series: "Coach Newton's Playbook"
Grade 2–3 | Science (physics) + Math (measurement & units) |
Causal Arc: Forces & Inertia → Forces Combine (Net Force) → Mass Resists Force (Collisions)
            → Machines Multiply Force (Levers) → Every Force Has a Partner (Trajectory Capstone)

Narrator: Coach Isaac Newton, introduced on Monday. A cheerful youth-football coach of the Mighty
Apples who treats every play as a physics experiment. Two team rules recur all week:
  Rule 1 — "Every incomplete pass is information." (a failed test is data, adjust the play)
  Rule 2 — "Every number needs a unit." ("It's 10." ... "Ten WHAT?")

Day shape (~2 hours): 1st Half (~60 min) = Film Study reading + Coach's Demo + application sheet.
2nd Half (~60 min) = Practice Field: independent Play Card stations with unit-labeled lab logs.

Output: football_week_series/
  football_week.html                (student packet, playbook-skinned)
  football_week_teacher_guide.html  (answer keys, demo scripts, materials, timing)

Standards (Virginia SOL, verified against curriculum.db):
  Monday    — VA.SCIENCE.2.2.2, 2.2.2.a, 2.2.2.b   (contact vs. non-contact forces; inertia)
  Tuesday   — VA.SCIENCE.3.3.2, 3.3.2.a, 3.3.2.b   (multiple forces, net force, direction & size)
  Wednesday — VA.SCIENCE.2.2.3.a, 3.3.2.b, 2.2.2.a (mass; more mass needs more force; collisions)
  Thursday  — VA.SCIENCE.3.3.2.c, 3.3.2.d          (simple machines change/increase force; uses)
  Friday    — VA.SCIENCE.3.3.2.a–d, 2.2.2.b, 2.2.2.c, 3.3.1 (capstone: action/reaction,
              gravity & trajectory, forces in our lives, engineering design-test-improve)
"""

import os

os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import html as _html
import sys
from pathlib import Path

sys.path.insert(0, os.path.abspath("src"))

from worksheet_html_renderer import (
    build_print_packet_html,
    get_day_palette,
    render_worksheet_html,
)


def _e(text: object) -> str:
    return _html.escape(str(text))


# ── Playbook skin ──────────────────────────────────────────────────────────
# Injected into the packet <head>. Print-friendly: white pages, green chalk accents.

PLAYBOOK_CSS = """
<style>
  body { counter-reset: play; }
  .page { counter-increment: play; }
  .page::before {
    content: "COACH NEWTON'S PLAYBOOK  \\00B7  MIGHTY APPLES  \\00B7  PAGE " counter(play);
    display: block; font-size: 7.5pt; font-weight: bold; letter-spacing: 0.16em;
    color: #14532d; padding-bottom: 7px; margin-bottom: 6px;
    background-image: repeating-linear-gradient(90deg, #14532d 0 2px, transparent 2px 24px);
    background-size: 100% 5px; background-position: bottom left; background-repeat: no-repeat;
    border-bottom: 1.5px solid #14532d;
  }
  .day-header-title::before { content: "\\1F3C8  "; }
  .passage { border-left-color: #14532d; background: #f4f8f4; line-height: 1.45;
    padding: 6px 10px; }
  .passage p { margin-bottom: 4px; }
  .question { margin-bottom: 5px; }
  .answer-line { height: 20px; margin-bottom: 2px; }
  .ws-instructions { margin-bottom: 5px; line-height: 1.35; }
  .name-date-row { margin-bottom: 6px; }
  .vocab-section { margin-top: 5px; }
  .vocab-item { padding: 2px 5px; }

  /* Play cards */
  .pb-huddle { border: 2px solid #14532d; border-radius: 6px; padding: 5px 10px;
    font-size: 9.5pt; margin-bottom: 8px; background: #f4f8f4; }
  .pb-huddle b { color: #14532d; }
  .pb-station { border: 1.5px solid #555; border-radius: 6px; padding: 6px 10px 7px;
    margin-bottom: 8px; break-inside: avoid; page-break-inside: avoid; }
  .pb-station-head { font-size: 11pt; font-weight: bold; margin-bottom: 2px; }
  .pb-gear { font-size: 8.5pt; color: #555; font-style: italic; margin-bottom: 3px; }
  .pb-steps { font-size: 9.5pt; padding-left: 18px; margin-bottom: 5px; line-height: 1.4; }
  .pb-steps li { margin-bottom: 1px; }
  table.pb-log { width: 100%; border-collapse: collapse; font-size: 9.5pt; margin: 3px 0 2px; }
  table.pb-log th { color: white; padding: 3px 6px; font-size: 9pt; border: 1px solid #555; }
  table.pb-log td { border: 1px solid #999; height: 25px; padding: 0 6px; }
  table.pb-log td.pb-row-label { font-weight: bold; background: #fafafa; }
  table.pb-log th.pb-unit-col { background: #ca8a04 !important; color: #111; }
  table.pb-log td.pb-unit-cell { background: #fef9c3; width: 0.95in; }
  .pb-circle { font-size: 9.5pt; margin: 4px 0 2px; }
  .pb-circle span { border: 1.5px solid #555; border-radius: 12px; padding: 1px 9px;
    margin: 0 3px; white-space: nowrap; }
  .pb-fill { display: inline-block; min-width: 0.8in; border-bottom: 1px solid #333; }
  .pb-ref { border: 2px dashed #ca8a04; background: #fefce8; border-radius: 6px;
    padding: 4px 10px; font-size: 9.5pt; margin-bottom: 7px; }
  .pb-ref b { color: #a16207; }
  .pb-coach { border-left: 5px solid #9d174d; background: #fdf2f8; padding: 4px 10px;
    font-size: 9.5pt; margin-bottom: 7px; }
  .pb-adjust { font-size: 9.5pt; margin-bottom: 4px; }
  .pb-adjust .answer-line { height: 20px; }
  .pb-grid2 { display: grid; grid-template-columns: 1fr 1fr; gap: 6px 12px; }
  .pb-fa { border: 1.5px solid #bbb; border-radius: 5px; padding: 3px 7px 5px;
    break-inside: avoid; page-break-inside: avoid; }
  .pb-fa-num { font-size: 8.5pt; font-weight: bold; color: #666; }
  .pb-fa svg { display: block; width: 100%; height: auto; }
  .pb-fa-line { font-size: 9pt; margin-top: 2px; }

  /* Cover */
  .cv-title { text-align: center; font-size: 26pt; font-weight: bold; color: #14532d;
    letter-spacing: 0.04em; line-height: 1.1; margin-top: 4px; }
  .cv-sub { text-align: center; font-size: 11pt; color: #444; margin-bottom: 8px; }
  .cv-field { text-align: center; margin: 4px 0 10px; }
  .cv-field svg { width: 100%; max-width: 6.6in; height: auto; }
  .cv-rules { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; margin-bottom: 10px; }
  .cv-rule { border: 2.5px solid #14532d; border-radius: 8px; padding: 7px 10px; font-size: 10pt; }
  .cv-rule h4 { font-size: 11pt; color: #14532d; margin-bottom: 3px; }
  .cv-dialog { font-size: 10pt; margin-top: 4px; padding-left: 8px; border-left: 3px solid #ca8a04; }
  table.cv-plays { width: 100%; border-collapse: collapse; font-size: 10pt; margin-bottom: 10px; }
  table.cv-plays th { background: #14532d; color: white; padding: 4px 8px; text-align: left; }
  table.cv-plays td { border: 1px solid #bbb; padding: 4px 8px; }
  .cv-player { border: 2px solid #333; border-radius: 8px; padding: 7px 12px; font-size: 10.5pt;
    display: grid; grid-template-columns: 1fr 1fr; gap: 6px 16px; }
  .cv-player span { border-bottom: 1px solid #444; }
  .cv-halves { font-size: 9.5pt; margin-bottom: 10px; }
</style>
"""

# Renderer section headings → playbook vocabulary (applied to the packet HTML only).
HEADING_SWAPS = {
    "<h3>Words to Know</h3>": "<h3>Playbook Terms</h3>",
    "<h3>Questions</h3>": "<h3>Film Study Questions</h3>",
}


# ── SVG helpers ────────────────────────────────────────────────────────────


def _football_svg(cx: float, cy: float, rx: float = 30, ry: float = 17) -> str:
    laces = "".join(
        f'<line x1="{cx + dx}" y1="{cy - 4}" x2="{cx + dx}" y2="{cy + 4}" '
        f'stroke="white" stroke-width="2"/>'
        for dx in (-8, -3, 2, 7)
    )
    return (
        f'<ellipse cx="{cx}" cy="{cy}" rx="{rx}" ry="{ry}" fill="#8b4513" stroke="#3b1d08" '
        f'stroke-width="2"/>'
        f'<line x1="{cx - 11}" y1="{cy}" x2="{cx + 11}" y2="{cy}" stroke="white" '
        f'stroke-width="2"/>{laces}'
    )


def force_arrow_svg(forces: list[tuple[str, int]]) -> str:
    """A football with labeled force arrows. forces = [("R"|"L", bands), ...].

    Arrow length is proportional to strength; same-direction arrows stack vertically.
    Labels sit past each arrowhead so they never overlap the ball.
    """
    unit_px, gap = 22, 30
    cx = 225
    rights = [f for f in forces if f[0] == "R"]
    lefts = [f for f in forces if f[0] == "L"]
    rows = max(len(rights), len(lefts), 1)
    cy = 8 + rows * 14
    height = cy * 2
    parts = [
        '<defs><marker id="ah" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="11" '
        'markerHeight="11" markerUnits="userSpaceOnUse" orient="auto">'
        '<path d="M0,0 L10,5 L0,10 z" fill="#111"/></marker></defs>'
    ]
    for side, group in (("R", rights), ("L", lefts)):
        for i, (_, bands) in enumerate(group):
            y = cy - (len(group) - 1) * 13 + i * 26
            sign = 1 if side == "R" else -1
            x1 = cx + sign * gap
            x2 = x1 + sign * bands * unit_px
            word = "band" if bands == 1 else "bands"
            anchor = "start" if side == "R" else "end"
            parts.append(
                f'<line x1="{x1}" y1="{y}" x2="{x2}" y2="{y}" stroke="#111" stroke-width="3" '
                f'marker-end="url(#ah)"/>'
                f'<text x="{x2 + sign * 6}" y="{y + 4}" font-size="14" font-weight="bold" '
                f'text-anchor="{anchor}">{bands} {word}</text>'
            )
    parts.append(_football_svg(cx, cy, 24, 13))
    return (
        f'<svg viewBox="0 0 450 {height}" xmlns="http://www.w3.org/2000/svg">'
        f'{"".join(parts)}</svg>'
    )


def cover_field_svg() -> str:
    """A chalk-style play diagram: Apples (O) vs. defense (X), routes as arrows."""
    w, h = 640, 230
    yard_lines = "".join(
        f'<line x1="{x}" y1="10" x2="{x}" y2="{h - 10}" stroke="white" stroke-width="2" '
        f'opacity="0.55"/>'
        for x in range(40, w, 70)
    )
    hashes = "".join(
        f'<line x1="{x}" y1="70" x2="{x}" y2="78" stroke="white" stroke-width="2" opacity="0.5"/>'
        f'<line x1="{x}" y1="{h - 78}" x2="{x}" y2="{h - 70}" stroke="white" stroke-width="2" '
        f'opacity="0.5"/>'
        for x in range(40, w, 14)
    )
    o_pos = [(250, 95), (250, 115), (250, 135), (250, 155), (250, 75), (215, 115), (250, 195)]
    x_pos = [(290, 95), (290, 115), (290, 135), (290, 155), (330, 75), (345, 175), (380, 120)]
    os_ = "".join(
        f'<circle cx="{x}" cy="{y}" r="8" fill="none" stroke="white" stroke-width="3"/>'
        for x, y in o_pos
    )
    xs = "".join(
        f'<g stroke="#fde047" stroke-width="3"><line x1="{x - 7}" y1="{y - 7}" x2="{x + 7}" '
        f'y2="{y + 7}"/><line x1="{x - 7}" y1="{y + 7}" x2="{x + 7}" y2="{y - 7}"/></g>'
        for x, y in x_pos
    )
    routes = (
        '<defs><marker id="cah" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="5" '
        'markerHeight="5" orient="auto"><path d="M0,0 L10,5 L0,10 z" fill="white"/></marker></defs>'
        '<path d="M250,75 L330,40 L470,40" fill="none" stroke="white" stroke-width="3" '
        'stroke-dasharray="7 5" marker-end="url(#cah)"/>'
        '<path d="M250,195 L300,205 Q380,215 430,160" fill="none" stroke="white" '
        'stroke-width="3" stroke-dasharray="7 5" marker-end="url(#cah)"/>'
        '<path d="M215,115 Q330,60 520,100" fill="none" stroke="#fca5a5" stroke-width="3" '
        'marker-end="url(#cah)"/>'
        '<text x="520" y="90" fill="#fca5a5" font-size="13" font-weight="bold" '
        'text-anchor="middle">trajectory!</text>'
    )
    ball = _football_svg(232, 115, 12, 7)
    return (
        f'<svg viewBox="0 0 {w} {h}" xmlns="http://www.w3.org/2000/svg">'
        f'<rect x="0" y="0" width="{w}" height="{h}" rx="10" fill="#166534"/>'
        f"{yard_lines}{hashes}{routes}{os_}{xs}{ball}"
        f'<text x="{w - 20}" y="{h - 16}" fill="white" font-size="13" font-weight="bold" '
        f'text-anchor="end">'
        f"O = Mighty Apples   X = Defense   - - - = route</text></svg>"
    )


# ── Play card builders ─────────────────────────────────────────────────────


def _header(day_label: str, half: str, title: str, primary: str) -> str:
    return (
        f'<div class="day-header" style="background:{primary};">'
        f'<div class="day-header-label">{_e(day_label)} &middot; {_e(half)}</div>'
        f'<div class="day-header-title">{_e(title)}</div></div>'
        f'<div class="ws-title" style="color:{primary};border-bottom-color:{primary};">'
        f"{_e(title)}</div>"
        '<div class="name-date-row"><span>Name:&nbsp;&nbsp;___________________________</span>'
        '<span class="short">Date:&nbsp;&nbsp;_______________</span></div>'
    )


def log_table(headers: list[str], rows: list[str], primary: str, unit_col: bool = True) -> str:
    """Lab log. With unit_col, the last header becomes the yellow Unit column."""
    plain = headers[:-1] if unit_col else headers
    ths = "".join(f'<th style="background:{primary};">{_e(h)}</th>' for h in plain)
    last_td = ""
    if unit_col:
        ths += f'<th class="pb-unit-col">{_e(headers[-1])}</th>'
        last_td = '<td class="pb-unit-cell"></td>'
    middle = len(plain) - 1
    trs = "".join(
        f'<tr><td class="pb-row-label">{_e(r)}</td>' + "<td></td>" * middle + last_td + "</tr>"
        for r in rows
    )
    return f'<table class="pb-log"><thead><tr>{ths}</tr></thead><tbody>{trs}</tbody></table>'


def station(name: str, gear: str, steps: list[str], body: str = "") -> str:
    lis = "".join(f"<li>{_e(s)}</li>" for s in steps)
    return (
        f'<div class="pb-station"><div class="pb-station-head">{_e(name)}</div>'
        f'<div class="pb-gear">Gear: {_e(gear)}</div><ol class="pb-steps">{lis}</ol>{body}</div>'
    )


def circle_row(prompt: str, options: list[str]) -> str:
    opts = "".join(f"<span>{_e(o)}</span>" for o in options)
    return f'<div class="pb-circle">{_e(prompt)} {opts}</div>'


def ref_box(text: str) -> str:
    return f'<div class="pb-ref">&#x1F6A9; <b>REF\'S RULE &mdash;</b> {_e(text)}</div>'


def coach_box(text: str) -> str:
    return (
        f'<div class="pb-coach">&#x1F4E3; <b>COACH\'S QUESTION</b> (say it out loud &mdash; '
        f"no writing!): {_e(text)}</div>"
    )


def adjust_box(text: str) -> str:
    return (
        f'<div class="pb-adjust"><b>ADJUST THE PLAY:</b> {_e(text)}'
        '<div class="answer-lines"><div class="answer-line"></div></div></div>'
    )


def huddle(text: str) -> str:
    return f'<div class="pb-huddle"><b>HUDDLE UP:</b> {_e(text)}</div>'


# Tuesday force-arrow problems: (forces, net bands, direction)
FORCE_PROBLEMS: list[tuple[list[tuple[str, int]], int, str]] = [
    ([("L", 3), ("R", 3)], 0, "no motion"),
    ([("L", 1), ("R", 4)], 3, "right"),
    ([("L", 5), ("R", 2)], 3, "left"),
    ([("R", 2), ("R", 3)], 5, "right"),
    ([("L", 2), ("L", 2), ("R", 4)], 0, "no motion"),
    ([("L", 2), ("L", 1), ("R", 6)], 3, "right"),
]


def generate_football_week_series():
    output_dir = Path("football_week_series")
    output_dir.mkdir(exist_ok=True)

    pages: list[tuple[str, str]] = []  # (day_label, html_fragment)

    def add(kind: str, data: dict, day_label: str) -> None:
        fragment = render_worksheet_html(kind, data, day_label)
        if fragment is None:
            raise ValueError(f"No HTML renderer for kind={kind!r}")
        pages.append((day_label, fragment))

    def add_custom(day_label: str, fragment: str) -> None:
        pages.append((day_label, fragment))

    # =========================================================================
    # COVER — the playbook itself
    # =========================================================================

    add_custom(
        "Playbook",
        f"""
<div class="cv-title">COACH NEWTON'S PLAYBOOK</div>
<div class="cv-sub">Physics on the Football Field &middot; A Five-Day Season with the Mighty Apples</div>
<div class="cv-field">{cover_field_svg()}</div>
<div class="cv-rules">
  <div class="cv-rule"><h4>TEAM RULE #1</h4>
    &ldquo;Every incomplete pass is information.&rdquo;<br>
    A test that doesn't work is not a failure &mdash; it's a clue. Ask: <i>What did we learn?
    How will we adjust the play?</i></div>
  <div class="cv-rule"><h4>TEAM RULE #2</h4>
    &ldquo;Every number needs a unit.&rdquo;
    <div class="cv-dialog">Player: &ldquo;I kicked it 10!&rdquo;<br>
    Coach: &ldquo;Ten <b>WHAT?</b>&rdquo;<br>
    Player: &ldquo;Ten <b>yards</b>!&rdquo; &#x2714;</div></div>
</div>
<div class="cv-halves"><b>Every practice has two halves.</b>
<b>1st Half</b> (about 60 minutes): Film Study (read with Coach), Coach's Demo, and a skills
sheet. <b>2nd Half</b> (about 60 minutes): Practice Field &mdash; you run the Play Card stations
on your own and log every result with a number <i>and</i> a unit.</div>
<table class="cv-plays">
  <thead><tr><th>Day</th><th>Play</th><th>Big Idea</th></tr></thead>
  <tbody>
    <tr><td>Monday</td><td>Kickoff</td><td>Forces, gravity, and inertia</td></tr>
    <tr><td>Tuesday</td><td>Line of Scrimmage</td><td>Balanced forces and net force</td></tr>
    <tr><td>Wednesday</td><td>Big Hits</td><td>Mass, momentum, and collisions</td></tr>
    <tr><td>Thursday</td><td>The Punter's Leg</td><td>Levers and simple machines</td></tr>
    <tr><td>Friday</td><td>Field Goal Day</td><td>Action, reaction, and trajectory</td></tr>
  </tbody>
</table>
<div class="cv-player">
  <div>Player: <span>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;</span></div>
  <div>Position: <b>Team Physicist</b></div>
  <div>Jersey number: <span>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;</span></div>
  <div>Favorite unit: <span>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;</span></div>
</div>
""",
    )

    # =========================================================================
    # MONDAY — Kickoff: Forces, Gravity, and Inertia
    # Standards: VA.SCIENCE.2.2.2, 2.2.2.a, 2.2.2.b
    # =========================================================================

    add(
        "readingWorksheet",
        {
            "title": "1st Half — Kickoff: Forces and Inertia",
            "passage_title": "Meet Coach Newton!",
            "instructions": (
                "COACH'S DEMO — Before reading: Lay an index card on top of a cup and set a coin "
                "in the middle of the card. Flick the card sideways, FAST. Where did the coin go? "
                "During reading: Stop at the word 'inertia' and explain the coin trick. "
                "After reading: Rest a ball on an upside-down cup like a kicking tee. Watch it "
                "for 30 seconds. Will it ever move on its own?"
            ),
            "passage": (
                "Meet Coach Isaac Newton! Coach wears a red whistle, an apple cap, and the biggest "
                "smile on the sidelines. He coaches a football team called the Mighty Apples, and "
                'he has a secret: every football play is a physics experiment. "Physics is the science of how things move," Coach says. '
                '"And nothing starts, stops, or turns without a force!"\n\n'
                "A force is a push or a pull. When the kicker's foot smacks the ball, that is a "
                "push. When a player grabs a runner's jersey, that is a pull. Kicks, throws, "
                "catches, and tackles are all contact forces, because one thing has to touch "
                "another thing to push or pull it.\n\n"
                "Some forces work from far away. These are non-contact forces. Gravity is the "
                "invisible pull Earth puts on everything. That is why every punt comes back down, "
                "even though nothing touches the ball in the air. Magnetism is another non-contact "
                "force: a magnet can pull a paper clip without touching it.\n\n"
                "Coach Newton's favorite word is inertia. Inertia means an object keeps doing "
                "what it is already doing until a force changes it. A football resting on the "
                "kicking tee will sit there all day until a foot kicks it. A ball flying through "
                "the air would keep going forever, except gravity pulls it down and the air slows "
                "it. Inertia is also why cars have seatbelts: when a car stops suddenly, your body "
                "wants to keep moving forward!\n\n"
                'Before practice, Coach shares two team rules. Rule One: "Every incomplete pass '
                "is information.\" A play that doesn't work isn't a failure. It's a clue for the "
                'next play. Rule Two: "Every number needs a unit." When a player shouts, "I '
                'kicked it 10!" Coach always asks, "Ten WHAT?" Ten yards? Ten feet? Ten inches? '
                "A number without a unit is like a football with no air in it. It doesn't go "
                "anywhere!"
            ),
            "vocabulary": [
                {
                    "term": "inertia",
                    "definition": "An object keeps doing what it is doing (sitting still or moving) until a force changes it.",
                },
                {
                    "term": "non-contact force",
                    "definition": "A push or pull that works from a distance, without touching.",
                },
                {"term": "force", "definition": "A push or a pull."},
                {
                    "term": "gravity",
                    "definition": "The non-contact force that pulls things toward Earth.",
                },
                {
                    "term": "unit",
                    "definition": "The word that tells WHAT you counted or measured: yards, inches, centimeters, tries.",
                },
                {
                    "term": "contact force",
                    "definition": "A push or pull that happens when two things touch, like a kick or a tackle.",
                },
            ],
            "questions": [
                {
                    "prompt": "What is a force? Name two contact forces you could see in a football game.",
                    "response_lines": 2,
                },
                {
                    "prompt": 'Gravity is a non-contact force. What does "non-contact" mean?',
                    "response_lines": 1,
                },
                {
                    "prompt": "In the demo, why did the coin drop into the cup instead of flying away with the card? Use the word inertia.",
                    "response_lines": 2,
                },
                {
                    "prompt": 'REF\'S RULE: A player says, "I threw it 15!" Fix it with a unit: "I threw it 15 ____________."',
                    "response_lines": 0,
                },
                {
                    "prompt": "LET'S DISCUSS: An astronaut floating in space throws a football. Out there, there is almost no gravity pulling on it and no air to slow it down. What will the ball do? When would it ever stop?",
                    "response_lines": 0,
                },
            ],
        },
        "Monday",
    )

    add(
        "wordSortWorksheet",
        {
            "title": "1st Half — Contact or Non-Contact? Force Sort",
            "instructions": (
                "Read each play in the word bank. Does the force happen by TOUCHING, or does it "
                "work from a DISTANCE? Write each play in the correct box. Tip: ask yourself, "
                '"Is anything touching?"'
            ),
            "categories": [
                {"label": "Contact Force (things touch)"},
                {"label": "Non-Contact Force (works from a distance)"},
            ],
            "tiles": [
                "A magnet pulls a paper clip",
                "A kicker's foot hits the ball",
                "A dropped helmet falls to the grass",
                "A receiver catches a pass",
                "A player tackles the runner",
                "Earth pulls a punt back down",
                "A lineman shoves a blocking sled",
                "A fridge magnet holds up the playbook",
                "A quarterback throws the ball",
                "A jumping player lands back on the field",
            ],
        },
        "Monday",
    )

    primary, _ = get_day_palette("Monday")
    add_custom(
        "Monday",
        _header("Monday", "2nd Half: Practice Field", "PLAY #1 — Inertia Trick Plays", primary)
        + huddle(
            "Run all three stations. Predict first, then test. Every result gets a number AND a "
            "unit. A trick that doesn't work is just information: change one thing and try again."
        )
        + station(
            "Station A — The Coin Drop",
            "a cup, an index card, 3 coins",
            [
                "Lay the card on the cup. Put 1 coin in the middle of the card.",
                "Flick the card sideways, fast and flat. Did the coin land in the cup?",
                "Do 5 tries. Then stack 2 coins and do 5 tries. Then stack 3.",
            ],
            log_table(
                ["Coins stacked", "Tries that landed in the cup (out of 5)", "Unit"],
                ["1 coin", "2 coins", "3 coins"],
                primary,
            )
            + circle_row("More coins made the trick:", ["easier", "harder", "no different"]),
        )
        + station(
            "Station B — Fast Pull, Slow Pull",
            "a sheet of paper, a plastic cup (empty), a table",
            [
                "Lay the paper on the table with one edge hanging off. Set the cup on the paper.",
                "SLOW: pull the paper gently toward you. Watch the cup.",
                "FAST: reset, then yank the paper straight out, flat and quick.",
            ],
            circle_row("Slow pull — the cup:", ["moved with the paper", "stayed put"])
            + circle_row("Fast pull — the cup:", ["moved with the paper", "stayed put"]),
        )
        + station(
            "Station C — Crash Test Rider",
            "a toy car, a LEGO figure or eraser (not attached!), blocks, a ruler (cm)",
            [
                "Build a block wall. Set the rider on top of the car.",
                "Roll the car into the wall. Measure how far the rider flew past the wall, in cm.",
                "Do 2 tries. Then give the rider a seatbelt (a rubber band or tape) and try again.",
            ],
            log_table(
                ["Test", "How far the rider flew", "Unit"],
                ["No seatbelt — try 1", "No seatbelt — try 2", "With seatbelt"],
                primary,
            ),
        )
        + ref_box(
            '"It flew 12" is an incomplete pass! Say "It flew 12 centimeters." For counting '
            'tries, the unit is "tries."'
        )
        + coach_box("The car stopped at the wall. Why didn't the rider stop too?"),
    )

    # =========================================================================
    # TUESDAY — Line of Scrimmage: Balanced and Unbalanced Forces, Net Force
    # Standards: VA.SCIENCE.3.3.2, 3.3.2.a, 3.3.2.b
    # =========================================================================

    add(
        "readingWorksheet",
        {
            "title": "1st Half — Line of Scrimmage: Net Force",
            "passage_title": "When Forces Add Up",
            "instructions": (
                "COACH'S DEMO — Loop a rubber band on each end of a toy car. You and your helper "
                "pull opposite ways until both bands stretch the same amount. Does the car move? "
                "Now the helper pulls with TWO bands side by side, stretched the same length. "
                "Which way does the car go? After reading: draw force arrows for both tests."
            ),
            "passage": (
                "Before every play, the Mighty Apples line up nose-to-nose with the other team "
                "along an invisible line called the line of scrimmage. When the ball is snapped, "
                "the linemen crash together and PUSH. Sometimes nobody moves; sometimes one side "
                "drives the other back. Coach Newton grins. \"That's not just "
                "football. That's forces adding up!\"\n\n"
                "Most of the time, more than one force acts on an object at once. If two linemen "
                "push on each other with the same strength in opposite directions, the forces are "
                "balanced. Balanced forces cancel each other out, so the motion doesn't change. "
                "The players stay put, like a tug-of-war rope that won't budge.\n\n"
                "If one lineman pushes harder, the forces are unbalanced. Unbalanced forces change "
                "motion: an object starts, speeds up, slows down, or turns, the way the stronger "
                "force pushes.\n\n"
                "To predict what will happen, scientists find the net force: the force left over "
                "after all the pushes and pulls are combined. When forces point the same way, "
                "you ADD them. Two teammates pushing a blocking sled together push harder than "
                "one. When forces point opposite ways, you SUBTRACT. If the Apples push with 5 "
                "and the other team pushes back with 3, the net force is 2, pointing the way the "
                "Apples are pushing.\n\n"
                "Coach draws forces as force arrows. An arrow points the way the force pushes, "
                "and a longer arrow means a stronger force. Rule Two: every arrow needs a number "
                "AND a unit! Scientists measure force in newtons, named after the real Sir Isaac "
                "Newton, who wrote these rules down over 300 years ago. Our homemade unit is the "
                'rubber band: one band stretched to the same length is "1 band" of force.'
            ),
            "vocabulary": [
                {
                    "term": "net force",
                    "definition": "The force left over after all the pushes and pulls are combined.",
                },
                {
                    "term": "balanced forces",
                    "definition": "Equal forces pushing opposite ways. They cancel, so motion does not change.",
                },
                {
                    "term": "newton",
                    "definition": "The unit scientists use to measure force.",
                },
                {
                    "term": "unbalanced forces",
                    "definition": "Forces that do not cancel. They make an object start, stop, speed up, slow down, or turn.",
                },
                {
                    "term": "force arrow",
                    "definition": "A drawing of a force. It points the way the force pushes; longer means stronger.",
                },
                {
                    "term": "direction",
                    "definition": "The way something is pushed or moving: left, right, up, down, forward, back.",
                },
            ],
            "questions": [
                {
                    "prompt": "Two linemen push on each other just as hard, and nobody moves. Are the forces balanced or unbalanced? How do you know?",
                    "response_lines": 1,
                },
                {
                    "prompt": "A force arrow shows two things: which ____________ and how ____________.",
                    "response_lines": 0,
                },
                {
                    "prompt": "Two players push a sled the same way: one with 4 bands and one with 3 bands. Net force = ______ ______ (number AND unit).",
                    "response_lines": 0,
                },
                {
                    "prompt": "The Apples push with 6 bands. The other team pushes back with 4 bands. What is the net force, and which team moves backward?",
                    "response_lines": 1,
                },
                {
                    "prompt": "LET'S DISCUSS: A football is sitting perfectly still on the grass. Are there ANY forces acting on it? (Hint: think about gravity, and what the ground is doing.)",
                    "response_lines": 0,
                },
            ],
        },
        "Tuesday",
    )

    add(
        "causeEffectWorksheet",
        {
            "title": "1st Half — What Happens Next? Forces Cause and Effect",
            "instructions": (
                "Read each cause. Decide: are the forces balanced or unbalanced? Then write what "
                'happens to the motion. Start your answer with "Balanced:" or "Unbalanced:".'
            ),
            "pairs": [
                {
                    "cause": "Both teams pull a tug-of-war rope with 5 bands of force.",
                    "effect_lines": 1,
                },
                {
                    "cause": "A lineman pushes a blocking sled with 8 bands. Nobody pushes back.",
                    "effect_lines": 1,
                },
                {
                    "cause": "A running back is sprinting straight ahead, and a defender shoves him from the side.",
                    "effect_lines": 1,
                },
                {
                    "cause": "Two teammates push a stuck equipment cart the same way, 3 bands each.",
                    "effect_lines": 1,
                },
                {
                    "cause": "A football rolls across the grass, and the grass rubs against it (friction). Nobody touches it.",
                    "effect_lines": 1,
                },
            ],
        },
        "Tuesday",
    )

    primary, _ = get_day_palette("Tuesday")
    fa_cells = ""
    for i, (forces, _net, _dir) in enumerate(FORCE_PROBLEMS, 1):
        fa_cells += (
            f'<div class="pb-fa"><div class="pb-fa-num">Play {i}</div>{force_arrow_svg(forces)}'
            '<div class="pb-fa-line">Net force: <span class="pb-fill"></span> '
            '<span class="pb-fill"></span> <span style="color:#777">(# + unit)</span></div>'
            f"{circle_row('Ball moves:', ['left', 'right', 'no motion'])}"
            f"{circle_row('Forces are:', ['balanced', 'unbalanced'])}</div>"
        )
    add_custom(
        "Tuesday",
        _header("Tuesday", "2nd Half: Practice Field", "PLAY #2A — Force Arrow Math", primary)
        + huddle(
            "Each football has rubber-band forces pulling on it. Same direction? ADD. Opposite "
            "directions? SUBTRACT the smaller from the bigger. The ball moves toward the "
            "stronger side."
        )
        + f'<div class="pb-grid2">{fa_cells}</div>'
        + station(
            "Draw Your Own Play",
            "a pencil",
            [
                "Draw a football with force arrows that make a net force of 2 bands to the LEFT.",
                "Challenge: draw a play with THREE arrows that is perfectly balanced.",
            ],
            '<div class="pb-grid2"><div style="height:1.1in;border:1px dashed #aaa;'
            'border-radius:4px"></div><div style="height:1.1in;border:1px dashed #aaa;'
            'border-radius:4px"></div></div>',
        )
        + ref_box(
            '"The net force is 3" is an incomplete pass. "The net force is 3 bands" — touchdown!'
        ),
    )

    add_custom(
        "Tuesday",
        _header("Tuesday", "2nd Half: Practice Field", "PLAY #2B — Build a Band-o-Meter", primary)
        + huddle(
            "Scientists use a spring scale to measure force. You're going to build your own out "
            "of a rubber band and a ruler. You'll use it again tomorrow, so build it well!"
        )
        + station(
            "Station A — Build It",
            "1 rubber band, a 30 cm ruler, tape, a paper clip, a sandwich bag, 15 marbles",
            [
                "Tape the ruler to the edge of a table so it hangs straight down, 0 cm at the top.",
                "Tape the rubber band at the 0 cm mark. Bend the paper clip into a hook on the bottom.",
                "Hang the empty bag on the hook. Read the ruler at the bottom of the band. Record it.",
                "Add marbles 5 at a time. Record where the band's bottom reaches each time.",
            ],
            log_table(
                ["Marbles in the bag", "Bottom of the band reaches", "Unit"],
                ["0 marbles (empty bag)", "5 marbles", "10 marbles", "15 marbles"],
                primary,
            )
            + '<div class="pb-fa-line" style="margin-top:4px">Prediction: 20 marbles would reach '
            'about <span class="pb-fill"></span> <span class="pb-fill"></span> '
            '<span style="color:#777">(number + unit)</span></div>',
        )
        + station(
            "Station B — Balanced Forces Check",
            "your Band-o-Meter with 10 marbles in the bag",
            [
                "Let the bag hang perfectly still. Gravity pulls the marbles DOWN.",
                "Something must be pulling UP just as hard, or the bag would fall. What is it?",
                "Draw two force arrows on the bag below: one for gravity, one for the band.",
            ],
            '<div style="height:0.75in;border:1px dashed #aaa;border-radius:4px;'
            'margin-top:3px"></div>',
        )
        + coach_box(
            "Why does the band stretch MORE when you add marbles? What does a bigger stretch tell you?"
        )
        + adjust_box("If your numbers looked strange, what will you change next time?"),
    )

    # =========================================================================
    # WEDNESDAY — Big Hits: Mass, Momentum, Collisions, Energy Transfer
    # Standards: VA.SCIENCE.2.2.3.a, 3.3.2.b, 2.2.2.a
    # =========================================================================

    add(
        "readingWorksheet",
        {
            "title": "1st Half — Big Hits: Mass and Collisions",
            "passage_title": "Why the Big Lineman Moves the Sled",
            "instructions": (
                "COACH'S DEMO — Before reading: Push an empty laundry basket across the floor with "
                "one finger. Fill it with books and try again. Which needed more force to start? "
                "To stop? During reading: Line up two marbles in the groove of a ruler and roll one "
                "into the other. What did each marble do? After reading: Line up 3 marbles "
                "touching, and roll 1 marble into the end of the line. Watch the far end!"
            ),
            "passage": (
                "The Mighty Apples are practicing on the blocking sled. The smallest player, a "
                "speedy kicker, runs into it, and the sled barely wiggles. The biggest lineman hits "
                "it at the same speed, and the sled slides back a whole yard. "
                '"Same speed, different results," says Coach Newton. "Why? Mass!"\n\n'
                "Mass is the amount of matter, or stuff, in an object. All matter has mass and "
                "takes up space, even the air pumped inside a football. Objects with more mass are "
                "harder to start moving and harder to stop once they're moving. That's inertia "
                "again: more mass means more inertia, so it takes a bigger force to change a "
                "heavy object's motion than a light one's.\n\n"
                'A moving object has momentum, which is Coach\'s name for "mass in motion." A big '
                "lineman running fast has a lot of momentum. A small kicker jogging slowly has a "
                "little. More mass or more speed means more momentum, and the more momentum "
                "something has, the harder it is to stop.\n\n"
                "When moving things crash into each other, it's called a collision. In a "
                "collision, energy moves from one object to another. Scientists call this energy "
                "transfer. When a runner bumps into a player who is standing still, some of the "
                "runner's energy of motion moves into the other player, and that player gets "
                "knocked backward. Marbles show this perfectly: roll one marble straight into a "
                "still marble, and the first one stops while the second one rolls away. The "
                "energy jumped across!\n\n"
                "Real players wear helmets and pads to spread out the force of a collision. And "
                'they follow Rule Two: don\'t say "18." Say "18 centimeters!"'
            ),
            "vocabulary": [
                {
                    "term": "momentum",
                    "definition": "Mass in motion. More mass or more speed means more momentum.",
                },
                {
                    "term": "mass",
                    "definition": "The amount of matter (stuff) in an object.",
                },
                {
                    "term": "energy transfer",
                    "definition": "When energy moves from one object to another, like in a collision.",
                },
                {
                    "term": "collision",
                    "definition": "When two objects crash into each other.",
                },
                {
                    "term": "centimeter (cm)",
                    "definition": "A small unit of length. Your fingertip is about 1 centimeter wide.",
                },
                {
                    "term": "matter",
                    "definition": "Anything that has mass and takes up space, even air.",
                },
            ],
            "questions": [
                {
                    "prompt": "What is mass? Name one object with a lot of mass and one with a little.",
                    "response_lines": 1,
                },
                {
                    "prompt": "Why was the full laundry basket harder to start AND harder to stop than the empty one?",
                    "response_lines": 2,
                },
                {
                    "prompt": "In the marble demo, where did the rolling marble's energy go?",
                    "response_lines": 1,
                },
                {
                    "prompt": 'REF\'S RULE: "The marble rolled 18 centimeters." Circle the unit in that sentence. What would "18" alone be missing?',
                    "response_lines": 1,
                },
                {
                    "prompt": "LET'S DISCUSS: Who has more momentum: a giant lineman walking slowly, or a small running back sprinting at top speed? Could the small player ever have MORE? What would need to change?",
                    "response_lines": 0,
                },
            ],
        },
        "Wednesday",
    )

    add(
        "featureMatrixWorksheet",
        {
            "title": "1st Half — Mass Scouting Report",
            "instructions": (
                "Scout each object. Check every box that is true. Careful: one object is "
                "invisible but still counts as matter! Think about the laundry basket demo for "
                "the last three columns."
            ),
            "items": [
                "Bowling ball",
                "Ping-pong ball",
                "Laundry basket full of books",
                "Empty laundry basket",
                "Football",
                "The air inside a balloon",
            ],
            "properties": [
                "Has mass",
                "Takes up space",
                "Needs a BIG push to start",
                "Needs only a small push to start",
                "Hard to stop when rolling fast",
            ],
        },
        "Wednesday",
    )

    primary, _ = get_day_palette("Wednesday")
    add_custom(
        "Wednesday",
        _header("Wednesday", "2nd Half: Practice Field", "PLAY #3 — Collision Lab", primary)
        + huddle(
            "Today you're the crash-test scientist. Change only ONE thing at a time, so you know "
            "what caused the difference. Measure every result in centimeters."
        )
        + station(
            "Station A — Marble Hits",
            'a ruler with a groove, 1 book, 4 marbles (plus 1 big "shooter" marble if you '
            "have one), a second ruler or tape measure",
            [
                "Rest one end of the grooved ruler on the book to make a launch ramp.",
                "Put a target marble on the floor right at the bottom end of the ramp.",
                "Let the hitter go from the TOP of the ramp every time. No pushing!",
                "Measure how far the target marble rolls, in cm.",
            ],
            log_table(
                ["Hitter", "Predict: farthest? (✓ one)", "Target rolled", "Unit"],
                [
                    "1 small marble",
                    "2 small marbles touching",
                    "1 big shooter marble",
                ],
                primary,
            )
            + circle_row("More mass in the hitter made the target roll:", ["farther", "shorter"]),
        )
        + station(
            "Station B — Band-o-Meter Mass Test",
            "your Band-o-Meter from Tuesday, the bag, 4 small objects (try: a toy car, an apple, "
            "a mini football, 10 marbles)",
            [
                "Predict: rank the objects from MOST mass (1) to LEAST mass (4).",
                "Hang each object in the bag. Record where the band's bottom reaches.",
            ],
            log_table(
                ["Object", "My rank guess (1–4)", "Band reaches", "Unit"],
                ["", "", "", ""],
                primary,
            ),
        )
        + ref_box(
            'Comparing results? "The shooter rolled it 9 cm farther" is a full play. '
            '"It was 9 more" is a fumble!'
        )
        + coach_box("Why do football players wear helmets and pads? Use the word collision."),
    )

    # =========================================================================
    # THURSDAY — The Punter's Leg: Levers and Simple Machines
    # Standards: VA.SCIENCE.3.3.2.c, 3.3.2.d
    # =========================================================================

    add(
        "readingWorksheet",
        {
            "title": "1st Half — The Punter's Leg: Simple Machines",
            "passage_title": "Every Leg Is a Lever",
            "instructions": (
                "COACH'S DEMO — Lay a ruler across a pencil (the fulcrum). Put a stack of 5 coins "
                "on one end (the load). Press the other end down with one finger (the effort). Now "
                "slide the pencil closer to the coins and press again. When was the load easier "
                "to lift? After reading: Slide the pencil close to YOUR end, put a pom-pom on the "
                "far end, and tap. Watch how far and fast that end moves. That's tomorrow's secret!"
            ),
            "passage": (
                "Fourth down! The Apples' punter drops the ball, swings her leg in a long, fast "
                "arc, and BOOM: the ball sails 40 yards down the field. "
                '"Did you know," Coach Newton asks, "that her leg is a machine?"\n\n'
                "A simple machine is a tool with few or no moving parts that makes work easier. "
                "Simple machines can make a force bigger, or change the direction of a force. "
                "There are six of them: the lever, the inclined plane, the wedge, the wheel and "
                "axle, the pulley, and the screw.\n\n"
                "A lever is a stiff bar that turns on a point called the fulcrum. The force you "
                "put in is the effort, and the thing you move is the load. A seesaw is a lever "
                "with its fulcrum in the middle. When the fulcrum is close to the load, a small "
                "effort can lift a big load. That's how a crowbar pries up heavy things!\n\n"
                "A punter's leg is a lever too. Her hip is the fulcrum, her strong thigh muscles "
                "supply the effort, and the football is the load. Her leg trades force for speed: "
                "the muscles near her hip move only a little, but her foot at the end of her long "
                "leg whips around fast and launches the ball. A quarterback's throwing arm works "
                "the same way.\n\n"
                "Simple machines are all over a stadium. The ramp into the stands is an inclined "
                "plane, cleat spikes are wedges, and the equipment cart rolls on wheels and axles. A pulley raises the flag before the game, and "
                "screws hold the goalposts together. Some tools, like scissors, combine two or "
                'more simple machines; those are called compound machines. "Machines let us do '
                'more with the force we have," Coach says. "Tomorrow, we build one."'
            ),
            "vocabulary": [
                {
                    "term": "lever",
                    "definition": "A stiff bar that turns on a fulcrum to lift or move a load.",
                },
                {
                    "term": "effort",
                    "definition": "The force you put into a machine.",
                },
                {
                    "term": "compound machine",
                    "definition": "Two or more simple machines working together, like scissors.",
                },
                {
                    "term": "fulcrum",
                    "definition": "The point a lever turns on.",
                },
                {
                    "term": "simple machine",
                    "definition": "A tool with few or no moving parts that makes a force bigger or changes its direction.",
                },
                {
                    "term": "load",
                    "definition": "The object a machine moves or lifts.",
                },
            ],
            "questions": [
                {
                    "prompt": "What two jobs can a simple machine do with a force?",
                    "response_lines": 1,
                },
                {
                    "prompt": "In the punter's leg: Fulcrum = __________  Effort = __________  Load = __________",
                    "response_lines": 0,
                },
                {
                    "prompt": "In the demo, where did you put the fulcrum to make the coins easiest to lift?",
                    "response_lines": 1,
                },
                {
                    "prompt": 'REF\'S RULE: "The punt went 40 ______." Which unit makes sense: inches, yards, or miles? Why not the other two?',
                    "response_lines": 1,
                },
                {
                    "prompt": "LET'S DISCUSS: Get a pair of scissors (carefully!). Is it a simple machine or a compound machine? Find the fulcrum. Can you find a wedge, too?",
                    "response_lines": 0,
                },
            ],
        },
        "Thursday",
    )

    add(
        "matchingWorksheet",
        {
            "title": "1st Half — Simple Machines at the Stadium",
            "instructions": (
                "Draw a line from each simple machine to where you'd find it at a football "
                "stadium. Each machine has exactly one match."
            ),
            "left_items": [
                "Lever",
                "Inclined plane",
                "Wedge",
                "Wheel and axle",
                "Pulley",
                "Screw",
            ],
            "right_items": [
                "The spikes on cleats that dig into the grass",
                "The rope that raises the flag up the flagpole",
                "The punter's leg swinging from the hip",
                "The twisted bolt holding the goalpost together",
                "The ramp fans walk up into the stands",
                "The round parts rolling the water cart onto the field",
            ],
        },
        "Thursday",
    )

    primary, _ = get_day_palette("Thursday")
    add_custom(
        "Thursday",
        _header("Thursday", "2nd Half: Practice Field", "PLAY #4A — Lever Lab", primary)
        + huddle(
            "Does WHERE you put the fulcrum change how much effort it takes? Let's measure it. "
            "Your effort unit today is pennies."
        )
        + station(
            "Station A — Move the Fulcrum",
            "a 30 cm ruler, a pencil or round marker, 20 pennies",
            [
                "Stack 5 pennies at the 2 cm end of the ruler. That's the load.",
                "Put the pencil under the 15 cm mark. That's the fulcrum.",
                "Add pennies one at a time at the 28 cm end until the load lifts. Count them.",
                "Move the fulcrum to 12 cm, then to 18 cm, and test again each time.",
            ],
            log_table(
                ["Fulcrum under", "Predict pennies", "Pennies it took to lift the load", "Unit"],
                ["15 cm (middle)", "12 cm (near the load)", "18 cm (near the effort)"],
                primary,
            )
            + circle_row("When the fulcrum moved closer to the load, I needed:", ["more", "fewer"])
            + circle_row("pennies. Did the ruler's own weight help?", ["yes", "no", "not sure"]),
        )
        + station(
            "Station B — Simple Machine Scavenger Hunt",
            "your eyes and your house (ask before you open anything!)",
            ["Find one example of each simple machine. Write or draw what you found."],
            log_table(
                ["Machine", "What I found", "Room"],
                ["Lever", "Inclined plane", "Wedge", "Wheel and axle", "Pulley", "Screw"],
                primary,
                unit_col=False,
            ),
        )
        + coach_box("Is a door handle a simple machine? Which one?"),
    )

    add_custom(
        "Thursday",
        _header("Thursday", "2nd Half: Practice Field", "PLAY #4B — Build Your Kicker", primary)
        + huddle(
            "Tomorrow is Field Goal Day, and your team needs a kicker. You're going to build a "
            "catapult: a lever that launches a ball. Build it, test it, fix it, and test again."
        )
        + station(
            "Station C — Catapult Build",
            "7 craft (popsicle) sticks, 4–5 rubber bands, a plastic spoon or bottle cap, tape "
            "or glue, pom-poms or a paper football",
            [
                "Stack 5 sticks. Wrap a rubber band tightly around each end of the stack.",
                "Hold the last 2 sticks together. Wrap a band around ONE end only.",
                "Slide the stack between the 2 sticks, near the banded end. That's your fulcrum!",
                "Wrap a band in an X around the spot where the stack and sticks cross.",
                "Tape the spoon (or bottle cap) to the free end of the top stick.",
                "Load a pom-pom, press the spoon down, and let go. LAUNCH!",
            ],
            log_table(
                ["Test launch", "How far it flew", "Unit"],
                ["Launch 1", "Launch 2", "Launch 3"],
                primary,
            ),
        )
        + station(
            "Label Your Machine",
            "your catapult",
            [
                "Point to the fulcrum. Point to where your effort pushes. Point to the load.",
                "Draw your catapult in the box. Label: fulcrum, effort, load.",
            ],
            '<div style="height:1.15in;border:1px dashed #aaa;border-radius:4px;margin-top:3px">'
            "</div>",
        )
        + adjust_box("If it didn't launch well, what one thing will you change?"),
    )

    # =========================================================================
    # FRIDAY — Field Goal Day: Action/Reaction, Trajectory (Capstone)
    # Standards: VA.SCIENCE.3.3.2.a–d, 2.2.2.b, 2.2.2.c, 3.3.1
    # =========================================================================

    add(
        "readingWorksheet",
        {
            "title": "1st Half — Field Goal Day: Action, Reaction, Trajectory",
            "passage_title": "Three Seconds Left...",
            "instructions": (
                "COACH'S DEMO — Balloon rocket! Tie a string across the room from chair to chair. "
                "Thread a straw onto the string. Blow up a balloon (don't tie it), tape it under "
                "the straw, and let go. Which way did the air go? Which way did the balloon go? "
                "After reading: Toss a ball to your helper three times: flat, medium, and steep. "
                "Watch each path."
            ),
            "passage": (
                "It's game day! The score is tied, there are three seconds left, and the Mighty "
                'Apples need a field goal. Coach Newton gathers the team. "Everything we learned '
                'this week is about to happen in one kick."\n\n'
                "When the kicker's foot hits the ball, the foot pushes on the ball, and the ball "
                "pushes back on the foot just as hard. Forces always come in pairs: an action and "
                "a reaction, equal in strength and opposite in direction. That's why a quarterback "
                "feels the ball push against his hand. It's also how rockets fly. A rocket pushes "
                "hot gas DOWN, and the gas pushes the rocket UP. A balloon rocket pushes air "
                "backward, and the air pushes the balloon forward.\n\n"
                "Once the ball is in the air, inertia keeps it moving forward while gravity pulls "
                "it down. Together they bend the ball's path into a curved arc called a "
                "trajectory. The launch angle, or how steeply the ball is kicked upward, changes "
                "the trajectory. Kick too flat and the ball smacks into the linemen. Kick too "
                "steep and it goes high but not far. A medium angle often travels farthest. "
                "Kickers practice and practice to find the angle that's just right.\n\n"
                "This kick uses the whole playbook. The kicker's leg is a lever. Her foot makes a "
                "contact force, an unbalanced force that starts the ball moving. The collision "
                "transfers energy from her foot to the ball. Gravity, a non-contact force, curves "
                "the trajectory. Physics isn't just in books. It's in every play, every car, and "
                "every rocket on its way to space.\n\n"
                "The kick is up... it's GOOD! The Mighty Apples win! And if it had missed? Coach "
                'would smile and say, "Every incomplete pass is information. Measure it, say the '
                'units, and adjust the play."'
            ),
            "vocabulary": [
                {
                    "term": "trajectory",
                    "definition": "The curved path a thrown or kicked object follows through the air.",
                },
                {
                    "term": "reaction force",
                    "definition": "The equal push back, in the opposite direction.",
                },
                {
                    "term": "engineer",
                    "definition": "A person who designs, tests, and improves things to solve a problem.",
                },
                {
                    "term": "action force",
                    "definition": "The first push in a force pair, like a foot pushing a ball.",
                },
                {
                    "term": "launch angle",
                    "definition": "How steeply something is sent upward when it is thrown or kicked.",
                },
                {
                    "term": "inch",
                    "definition": "A unit of length about as long as the top part of your thumb.",
                },
            ],
            "questions": [
                {
                    "prompt": "In the balloon rocket, what was the action force? What was the reaction force?",
                    "response_lines": 2,
                },
                {
                    "prompt": "What two things work together to curve a football's trajectory?",
                    "response_lines": 1,
                },
                {
                    "prompt": "Name THREE ideas from this week that happen in one field-goal kick.",
                    "response_lines": 2,
                },
                {
                    "prompt": "REF'S RULE: Measure your balloon rocket's best flight. It went ______ ______ (number AND unit).",
                    "response_lines": 0,
                },
                {
                    "prompt": "LET'S DISCUSS: If the Mighty Apples played on the Moon, where gravity pulls much more weakly, how would the trajectory of a kick change? Would field goals be easier or harder?",
                    "response_lines": 0,
                },
            ],
        },
        "Friday",
    )

    add(
        "treeMapWorksheet",
        {
            "title": "1st Half — The Whole Playbook: Tree Map Capstone",
            "instructions": (
                "Sort every playbook term from the word bank into the correct branch. Each term "
                "belongs in only one branch. Look back at Monday through Thursday if you need to!"
            ),
            "root_label": "Coach Newton's Physics Playbook",
            "branches": [
                {"label": "Contact Forces", "slot_count": 3},
                {"label": "Forces from a Distance", "slot_count": 2},
                {"label": "Simple Machines", "slot_count": 3},
                {"label": "Words About Motion", "slot_count": 3},
            ],
            "columns": 4,
            "word_bank": [
                "Inertia",
                "Tackle",
                "Wedge",
                "Gravity",
                "Momentum",
                "Kick",
                "Lever",
                "Magnetism",
                "Trajectory",
                "Pulley",
                "Throw",
            ],
        },
        "Friday",
    )

    primary, _ = get_day_palette("Friday")
    add_custom(
        "Friday",
        _header("Friday", "2nd Half: Practice Field", "PLAY #5 — Field Goal Challenge", primary)
        + huddle(
            "Game time! You are the engineer: design, test, and improve. Every miss is "
            "information. Measure everything, tally everything, and say every unit."
        )
        + station(
            "Station A — Balloon Rocket Trials",
            "the balloon rocket string and straw, balloons, tape, a tape measure",
            [
                "Blow 5 breaths into the balloon, tape it on, and launch. Measure the distance.",
                "Repeat with 10 breaths, then 15 breaths.",
            ],
            log_table(
                ["Balloon size", "Distance it flew", "Unit"],
                ["5 breaths", "10 breaths", "15 breaths"],
                primary,
            )
            + circle_row(
                "More air pushed out backward made the rocket go:", ["farther", "shorter"]
            ),
        )
        + station(
            "Station B — Field Goals",
            "your catapult, pom-poms or paper footballs, goalposts (2 pencils in clay with a "
            "string crossbar), a tape measure",
            [
                "Set the goalposts 12 inches from your catapult. Kick 10 times. Tally every make.",
                "Move the goalposts to 24 inches, then to 36 inches. Kick 10 times at each.",
            ],
            log_table(
                ["Goalpost distance", "Tally of makes", "Total made", "Unit"],
                ["12 inches", "24 inches", "36 inches"],
                primary,
            ),
        )
        + station(
            "Station C — Launch Angle Test",
            "your catapult, 2 books",
            [
                "Launch flat on the floor. Then prop the front up on 1 book, then 2 books.",
                "Measure how far the pom-pom lands each time.",
            ],
            log_table(
                ["Launch angle", "Distance", "Unit"],
                ["Flat (0 books)", "1 book", "2 books"],
                primary,
            ),
        )
        + adjust_box("Which change helped your kicker most? What will you try next season?"),
    )

    add(
        "barGraphWorksheet",
        {
            "title": "2nd Half — Field Goal Stats: Bar Graph",
            "instructions": (
                "Use your Station B tallies. Color one bar for each goalpost distance to show how "
                "many field goals you made. Then answer the questions with numbers AND units."
            ),
            "categories": ["12 inches", "24 inches", "36 inches"],
            "y_max": 10,
            "y_step": 1,
            "x_label": "Distance to the goalposts (inches)",
            "y_label": "Field goals made (kicks)",
            "height_in": 3.0,
            "questions": [
                {
                    "prompt": "From which distance did you make the most field goals? How many? (number + unit)",
                    "response_lines": 1,
                },
                {
                    "prompt": "How many more did you make from 12 inches than from 36 inches? Show your subtraction.",
                    "response_lines": 1,
                },
                {
                    "prompt": "What pattern do you see as the goalposts move farther away? Why might that happen?",
                    "response_lines": 2,
                },
                {
                    "prompt": "Rule One: every miss was information. What did your misses teach you?",
                    "response_lines": 1,
                },
            ],
        },
        "Friday",
    )

    # =========================================================================
    # PARENT FEEDBACK & TEACHING NOTES
    # =========================================================================

    add(
        "readingWorksheet",
        {
            "title": "End-of-Week Parent Feedback — Coach Newton's Playbook",
            "passage_title": "Season Recap & Teaching Notes for the Parent",
            "instructions": (
                "Please complete this sheet after Friday's game. Your notes shape next week's "
                "lessons."
            ),
            "passage": (
                "This week followed a causal arc through forces and motion, pitched at 2nd–3rd "
                "grade. Monday defined forces (contact vs. non-contact) and inertia. Tuesday "
                "showed that several forces act at once and that the net force decides the "
                "motion. Wednesday added mass: more mass resists changes in motion, and "
                "collisions transfer energy. Thursday introduced simple machines, especially the "
                "lever, as ways to increase force or change its direction. Friday tied it all "
                "together in one field-goal kick: action and reaction, gravity bending a "
                "trajectory, and a design-test-improve catapult challenge.\n\n"
                "The math thread was units. Every lab log had a separate yellow Unit column, and "
                "the Ref's Rule boxes practiced turning bare numbers into measurements.\n\n"
                "Key ideas to check for real understanding, not just recall:\n"
                "1) A still object can have forces on it; they're just balanced.\n"
                "2) The net force (not the biggest single force) decides which way something moves.\n"
                "3) More mass means more force is needed to start OR stop motion.\n"
                "4) A lever can trade force for distance and speed; fulcrum position matters.\n"
                "5) Every force has an equal and opposite partner force."
            ),
            "vocabulary": [
                {
                    "term": "Key Misconception to Watch",
                    "definition": '"Moving things need a force to keep moving." Not true: by inertia they keep moving; forces like friction and gravity are what slow or curve them.',
                },
                {
                    "term": "Units Check",
                    "definition": "(Fill in: by Friday, how often did Christopher add a unit without being asked?)",
                },
                {
                    "term": "Strongest Concept This Week",
                    "definition": "(Fill in after the week: which idea did Christopher grasp best?)",
                },
                {
                    "term": "Next Week's Hook",
                    "definition": "Energy and circuits with Minecraft redstone: where does the energy for motion come from, and how can we move it along a wire?",
                },
            ],
            "questions": [
                {
                    "prompt": "Overall comfort with the content (1 = struggled, 5 = strong grasp). Was the 2nd–3rd grade level right?",
                    "response_lines": 1,
                },
                {
                    "prompt": "Did the two-hour, two-half day work? Which half held attention better?",
                    "response_lines": 2,
                },
                {
                    "prompt": "Which Practice Field station sparked the most curiosity or follow-up questions?",
                    "response_lines": 2,
                },
                {
                    "prompt": 'By Friday, how often did "Ten WHAT?" still come up? Which units does he use confidently?',
                    "response_lines": 2,
                },
                {"prompt": "Topics or vocabulary to revisit next week:", "response_lines": 2},
            ],
        },
        "Friday",
    )

    # =========================================================================
    # Assemble & write
    # =========================================================================

    html = build_print_packet_html(pages, packet_title="Coach Newton's Playbook — Football Physics")
    html = html.replace("</head>", PLAYBOOK_CSS + "</head>", 1)
    for old, new in HEADING_SWAPS.items():
        html = html.replace(old, new)
    out_path = output_dir / "football_week.html"
    out_path.write_text(html, encoding="utf-8")

    guide_path = output_dir / "football_week_teacher_guide.html"
    guide_path.write_text(_teacher_guide(), encoding="utf-8")

    print("\nSuccessfully generated Coach Newton's Playbook (Football Physics Week).")
    print(f"Student packet:  {out_path}")
    print(f"Teacher guide:   {guide_path}")
    print(
        f"  {len(pages)} pages — open the packet in a browser and print (dialog opens automatically)\n"
    )
    print("  Pages:")
    labels = [
        "Cover   — Coach Newton's Playbook (team rules, plays, player card)",
        "Mon p1  — 1st Half Reading: Kickoff — Forces and Inertia",
        "Mon p2  — 1st Half Word Sort: Contact vs. Non-Contact Forces",
        "Mon p3  — 2nd Half Play #1: Inertia Trick Plays",
        "Tue p1  — 1st Half Reading: Line of Scrimmage — Net Force",
        "Tue p2  — 1st Half Cause & Effect: Balanced or Unbalanced?",
        "Tue p3  — 2nd Half Play #2A: Force Arrow Math",
        "Tue p4  — 2nd Half Play #2B: Build a Band-o-Meter",
        "Wed p1  — 1st Half Reading: Big Hits — Mass and Collisions",
        "Wed p2  — 1st Half Feature Matrix: Mass Scouting Report",
        "Wed p3  — 2nd Half Play #3: Collision Lab",
        "Thu p1  — 1st Half Reading: The Punter's Leg — Simple Machines",
        "Thu p2  — 1st Half Matching: Simple Machines at the Stadium",
        "Thu p3  — 2nd Half Play #4A: Lever Lab + Scavenger Hunt",
        "Thu p4  — 2nd Half Play #4B: Build Your Kicker (catapult)",
        "Fri p1  — 1st Half Reading: Field Goal Day — Action, Reaction, Trajectory",
        "Fri p2  — 1st Half Tree Map: The Whole Playbook (capstone)",
        "Fri p3  — 2nd Half Play #5: Field Goal Challenge",
        "Fri p4  — Bar Graph: Field Goal Stats",
        "         — Parent Feedback & Teaching Notes",
    ]
    assert len(labels) == len(pages), (len(labels), len(pages))
    for label in labels:
        print(f"    {label}")


# ── Teacher guide ──────────────────────────────────────────────────────────


def _force_key() -> str:
    rows = ""
    for i, (forces, net, direction) in enumerate(FORCE_PROBLEMS, 1):
        desc = " + ".join(
            f"{b} {'band' if b == 1 else 'bands'} {'→' if s == 'R' else '←'}" for s, b in forces
        )
        balanced = "balanced" if net == 0 else "unbalanced"
        unit = "bands" if net != 1 else "band"
        rows += (
            f"<p><strong>Play {i}:</strong> {desc} &rarr; net force <b>{net} {unit}</b>, "
            f"{direction}, {balanced}.</p>"
        )
    return rows


def _teacher_guide() -> str:
    return (
        TEACHER_GUIDE_HEAD
        + TEACHER_GUIDE_BODY.replace("{{FORCE_KEY}}", _force_key())
        + "</body>\n</html>"
    )


TEACHER_GUIDE_HEAD = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>Coach Newton's Playbook — Teacher Guide</title>
  <style>
    @page { size: letter; margin: 0.5in 0.6in; }
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body { font-family: 'Trebuchet MS', Arial, sans-serif; font-size: 11pt; color: #111; line-height: 1.55; }
    @media screen { body { background: #b0b0b0; padding: 24px; } .page { background: white; max-width: 7.5in; margin: 0 auto 28px; padding: 0.45in 0.5in; box-shadow: 0 4px 18px rgba(0,0,0,.28); min-height: 10.3in; } }
    @media print { body { background: white; padding: 0; } .page { padding: 0; box-shadow: none; } * { -webkit-print-color-adjust: exact; print-color-adjust: exact; } }
    .page { page-break-after: always; break-after: page; }
    .page:last-child { page-break-after: avoid; break-after: avoid; }
    h1 { font-size: 18pt; color: #14532d; border-bottom: 3px solid #14532d; padding-bottom: 5px; margin-bottom: 12px; }
    h2 { font-size: 13pt; color: #fff; background: #1d4ed8; padding: 5px 10px; border-radius: 3px; margin: 14px 0 6px; }
    h2.tue { background: #15803d; }
    h2.wed { background: #7c3aed; }
    h2.thu { background: #c2410c; }
    h2.fri { background: #0f766e; }
    h2.gen { background: #14532d; }
    h3 { font-size: 10.5pt; font-weight: bold; color: #444; margin: 8px 0 3px; text-transform: uppercase; letter-spacing: 0.04em; }
    p, li { font-size: 10pt; margin-bottom: 5px; }
    ul, ol { padding-left: 18px; margin-bottom: 8px; }
    table.sched { width: 100%; border-collapse: collapse; font-size: 9.5pt; margin: 4px 0 10px; }
    table.sched th { background: #14532d; color: white; padding: 4px 8px; text-align: left; }
    table.sched td { border: 1px solid #bbb; padding: 3px 8px; vertical-align: top; }
    .answer-box { background: #f0f4ff; border-left: 4px solid #1d4ed8; padding: 6px 10px; margin: 4px 0 10px; border-radius: 0 4px 4px 0; font-size: 10pt; }
    .answer-box.tue { background: #f0fff4; border-color: #15803d; }
    .answer-box.wed { background: #f5f0ff; border-color: #7c3aed; }
    .answer-box.thu { background: #fff7f0; border-color: #c2410c; }
    .answer-box.fri { background: #f0fff8; border-color: #0f766e; }
    .misconception { background: #fff3cd; border-left: 4px solid #d97706; padding: 6px 10px; margin: 4px 0 8px; border-radius: 0 4px 4px 0; font-size: 10pt; }
    .extension { background: #e8f5e9; border-left: 4px solid #15803d; padding: 6px 10px; margin: 4px 0 8px; border-radius: 0 4px 4px 0; font-size: 10pt; }
    .discuss { background: #fce7f3; border-left: 4px solid #9d174d; padding: 6px 10px; margin: 4px 0 8px; border-radius: 0 4px 4px 0; font-size: 10pt; }
    .units { background: #fefce8; border: 2px dashed #ca8a04; padding: 6px 10px; margin: 4px 0 8px; border-radius: 4px; font-size: 10pt; }
  </style>
</head>
<body>
"""

TEACHER_GUIDE_BODY = """
<div class="page">
  <h1>Coach Newton's Playbook — Teacher / Parent Guide</h1>
  <p><strong>Theme:</strong> Football physics &nbsp;|&nbsp; <strong>Audience:</strong> Christopher, age 6, working at 2nd–3rd grade &nbsp;|&nbsp;
  <strong>Narrator:</strong> Coach Isaac Newton of the Mighty Apples</p>
  <p><strong>Causal Arc:</strong> Forces &amp; Inertia &rarr; Forces Combine (Net Force) &rarr; Mass Resists Force (Collisions) &rarr; Machines Multiply Force (Levers) &rarr; Every Force Has a Partner (Trajectory)</p>
  <p><strong>Standards (VA SOL):</strong> 2.2.2 a–c (contact and non-contact forces; forces in our lives), 2.2.3.a (matter has mass and takes up space), 3.3.2 a–d (multiple forces, net force, simple and compound machines), 3.3.1 (engineering practices, Friday).</p>

  <h2 class="gen">The Two Halves of Every Day (~2 hours)</h2>
  <table class="sched">
    <tr><th>Time</th><th>Block</th><th>What you do</th></tr>
    <tr><td>0:00–0:15</td><td>1st Half: Coach's Demo</td><td>Run the demo in the reading page's instructions <em>before</em> reading. Ask for a prediction first, always.</td></tr>
    <tr><td>0:15–0:35</td><td>1st Half: Film Study</td><td>He reads the passage (aloud or silently), then answers the questions. Do the LET'S DISCUSS question out loud together.</td></tr>
    <tr><td>0:35–0:50</td><td>1st Half: Skills Sheet</td><td>Application page (sort, cause/effect, matrix, matching, tree map).</td></tr>
    <tr><td>0:50–1:00</td><td>Halftime Huddle</td><td>Vocabulary quiz-off: you say a Playbook Term, he gives a football example. Snack.</td></tr>
    <tr><td>1:00–2:00</td><td>2nd Half: Practice Field</td><td>Play Card stations, mostly on his own. Set out the gear, read the Huddle box together, then step back. Check in at each Coach's Question.</td></tr>
  </table>

  <h3>The Units Game (all week)</h3>
  <div class="units">
    <p>Keep a yellow sock or dish towel handy as a referee's flag. Any time he says a bare number for a measurement ("It's 10"), toss the flag and call <em>"Flag on the play: illegal number!"</em> He gets the yard back by restating it with a unit ("10 centimeters"). Let him flag YOU too, and slip up on purpose a few times. The yellow Unit column on every lab log is the written version of the same game.</p>
    <p>Units used this week: <b>centimeters</b> and <b>inches</b> (length), <b>yards</b> (football distances, discussion only), <b>bands</b> (homemade force unit), <b>newtons</b> (the real force unit, vocabulary only), and count units: <b>tries, pennies, marbles, kicks, breaths</b>.</p>
  </div>

  <h3>Materials Checklist (gather Sunday night)</h3>
  <ul>
    <li><b>Mon:</b> plastic cups, index cards, 3+ coins, a sheet of paper, toy car, LEGO figure or eraser, blocks, ruler with cm, a ball</li>
    <li><b>Tue:</b> ~10 identical rubber bands, toy car, 30 cm ruler, tape, paper clip, sandwich bag, 15–20 marbles</li>
    <li><b>Wed:</b> laundry basket + books, ruler with a groove, 4 marbles (+1 big shooter if you have one), 1 book, Band-o-Meter, apple, mini football</li>
    <li><b>Thu:</b> pencil or round marker, 20 pennies, 7 popsicle sticks, 4–5 rubber bands, plastic spoon or bottle cap, tape, pom-poms, scissors (discussion)</li>
    <li><b>Fri:</b> ~10 ft of string, a straw, balloons, tape measure, 2 pencils + clay + string (goalposts), crayons for the bar graph</li>
  </ul>
  <p><em>No spring scales needed. The rubber-band "Band-o-Meter" built on Tuesday stands in for one. Use same-size bands so "1 band" means the same force every time.</em></p>
</div>

<div class="page">
  <h2>Monday — Kickoff: Forces, Gravity, and Inertia</h2>
  <h3>Demo Notes</h3>
  <p>Coin-card-cup: the flick must be fast and level. Inertia keeps the coin in place while the card shoots out, and then gravity pulls it into the cup. A slow push drags the coin along with the card (friction wins). Show both and let him say which one is "the trick."</p>
  <h3>Answer Key — Film Study</h3>
  <div class="answer-box">
    <p><strong>Q1:</strong> A force is a push or a pull. Contact examples: kick, throw, catch, tackle, block, snap.</p>
    <p><strong>Q2:</strong> It works without touching, from a distance.</p>
    <p><strong>Q3:</strong> Because of inertia, the coin wanted to stay still, so when the card shot away it stayed in place and gravity pulled it straight down into the cup.</p>
    <p><strong>Q4:</strong> Any sensible length unit: yards, feet, or meters. "Inches" is technically a unit but not sensible for a throw; ask him to defend it.</p>
  </div>
  <h3>LET'S DISCUSS Guidance</h3>
  <div class="discuss"><p><em>Astronaut throws a football in space.</em> It keeps going in a straight line at the same speed, basically forever, until it hits something or a planet's gravity catches it. This is inertia with nothing in the way, and it's the most striking version of the idea. (Fact: the Voyager probes are still coasting out of the solar system decades later.)</p></div>
  <h3>Word Sort Answer Key</h3>
  <div class="answer-box">
    <p><strong>Contact:</strong> kicker's foot hits the ball; receiver catches a pass; player tackles the runner; lineman shoves a blocking sled; quarterback throws the ball.</p>
    <p><strong>Non-contact:</strong> magnet pulls a paper clip; dropped helmet falls; Earth pulls a punt down; fridge magnet holds the playbook; jumping player lands back on the field.</p>
    <p><em>Discussion point: the fridge magnet is touching the fridge, but the force holding it there is magnetism, which works through a gap. Try it through a sheet of paper!</em></p>
  </div>
  <h3>Play #1 Key</h3>
  <div class="answer-box">
    <p><strong>A:</strong> More stacked coins is usually <em>easier</em> (more mass = more inertia, and the stack drops more cleanly). Accept any honest result. The key is that he records "tries" as the unit.</p>
    <p><strong>B:</strong> Slow pull: the cup moves with the paper. Fast pull: the cup stays put (or barely moves).</p>
    <p><strong>C:</strong> No seatbelt: the rider flies forward past the wall (typically 5–20 cm). With a seatbelt: 0 cm, the rider stops with the car. <em>Coach's Q:</em> nothing pushed back on the rider, so by inertia it kept moving forward.</p>
  </div>
  <h3>Misconceptions to Watch</h3>
  <div class="misconception"><p>"The ball stops because it runs out of force." Moving objects don't carry a supply of force that gets used up. They slow down because <em>other</em> forces (friction, air, gravity) act on them. Keep asking, "What force stopped it?"</p></div>
  <h3>Extension Activity</h3>
  <div class="extension"><p>Hold a magnet under a paper plate and steer a paper clip "running back" through a drawn field without touching it. Is the force contact or non-contact? Try through 1, 2, then 5 plates. How many plates until the pull stops working? (That number needs a unit: "plates.")</p></div>

  <h2 class="tue">Tuesday — Line of Scrimmage: Balanced Forces and Net Force</h2>
  <h3>Answer Key — Film Study</h3>
  <div class="answer-box tue">
    <p><strong>Q1:</strong> Balanced. Nobody moves, so the motion didn't change, and only unbalanced forces change motion.</p>
    <p><strong>Q2:</strong> Direction (where it points) and strength (how long it is).</p>
    <p><strong>Q3:</strong> 7 bands (same direction, so add: 4 + 3).</p>
    <p><strong>Q4:</strong> 2 bands toward the other team, so the <em>other</em> team moves backward (6 − 4 = 2).</p>
  </div>
  <h3>LET'S DISCUSS Guidance</h3>
  <div class="discuss"><p><em>A still football on the grass.</em> Yes! Gravity pulls it down, and the ground pushes up just as hard. The forces are balanced, which is why nothing happens. This is the big reveal of the day: "still" does NOT mean "no forces."</p></div>
  <h3>Cause &amp; Effect Key</h3>
  <div class="answer-box tue">
    <p>1. Balanced: the rope doesn't move. &nbsp; 2. Unbalanced: the sled moves forward. &nbsp; 3. Unbalanced: the runner changes direction (veers away from the shove). &nbsp; 4. Unbalanced: forces add up to 6 bands and the cart starts moving. &nbsp; 5. Unbalanced: friction slows the ball until it stops.</p>
  </div>
  <h3>Play #2A Key — Force Arrow Math</h3>
  <div class="answer-box tue">{{FORCE_KEY}}<p><strong>Draw Your Own:</strong> any arrows where left minus right = 2 bands (e.g., 3 bands &larr; and 1 band &rarr;). Balanced with three arrows: e.g., 1 + 2 bands &larr; and 3 bands &rarr;. Check that every arrow is labeled with a unit.</p></div>
  <h3>Play #2B Key — Band-o-Meter</h3>
  <div class="answer-box tue">
    <p>Readings vary with the band. The pattern matters: each +5 marbles adds about the same stretch, so the prediction for 20 marbles should continue that pattern (e.g., 9, 11, 13, 15 cm → about 17 cm). <b>Balanced check:</b> the stretched band pulls UP exactly as hard as gravity pulls DOWN, so the bag hangs still. The arrows should be equal length, pointing opposite ways. <em>Coach's Q:</em> more marbles = more gravity pull, so the band must stretch more to pull back equally. Bigger stretch = bigger force.</p>
  </div>
  <h3>Misconceptions to Watch</h3>
  <div class="misconception"><p>"The bigger force wins, so the answer is the bigger number." Make sure he <em>subtracts</em> for opposite forces. Play 5 (2 + 2 vs. 4) is the trap: two small forces can balance one big one.</p></div>
  <h3>Extension Activity</h3>
  <div class="extension"><p>Real tug-of-war on the carpet with a towel. Then have him pull against you while you secretly pull exactly as hard. When nobody moves, ask: "Am I pulling? How do you know?"</p></div>
</div>

<div class="page">
  <h2 class="wed">Wednesday — Big Hits: Mass, Momentum, and Collisions</h2>
  <h3>Answer Key — Film Study</h3>
  <div class="answer-box wed">
    <p><strong>Q1:</strong> Mass is the amount of matter (stuff) in an object. Any sensible pair works: car / feather, bowling ball / ping-pong ball.</p>
    <p><strong>Q2:</strong> It had more mass, so more inertia, so it took more force to change its motion both to start it and to stop it.</p>
    <p><strong>Q3:</strong> It transferred into the still marble, which rolled away while the first one stopped (or slowed).</p>
    <p><strong>Q4:</strong> Circle "centimeters." "18" alone is missing what was measured, so it could be 18 inches, 18 marbles, or 18 anything.</p>
  </div>
  <h3>LET'S DISCUSS Guidance</h3>
  <div class="discuss"><p>The slow giant may have less momentum than the sprinting small player. Momentum depends on mass <em>and</em> speed, so a small player who is fast enough can match or beat a slow big one. That's why speed matters so much in football. Don't introduce the formula; "both mass and speed count" is the target.</p></div>
  <h3>Feature Matrix Key</h3>
  <div class="answer-box wed">
    <p><strong>Has mass &amp; Takes up space:</strong> ALL six, including the air in the balloon (the key surprise and VA 2.2.3.a).</p>
    <p><strong>Needs a BIG push:</strong> bowling ball, full laundry basket. &nbsp; <strong>Only a small push:</strong> ping-pong ball, empty basket, football, air in a balloon.</p>
    <p><strong>Hard to stop when rolling fast:</strong> bowling ball, full laundry basket.</p>
  </div>
  <h3>Play #3 Key</h3>
  <div class="answer-box wed">
    <p><strong>A:</strong> Usually 1 small &lt; 2 touching &lt; big shooter. More mass in the hitter makes the target roll <b>farther</b>, because more momentum means more energy to transfer. Results can be noisy: if one trial is odd, Rule One applies, so repeat it. Every distance needs "cm."</p>
    <p><strong>B:</strong> Rank guesses vary. The Band-o-Meter stretch is the evidence: more stretch = more gravity pull = more mass. Praise him for revising a ranking after measuring.</p>
    <p><em>Coach's Q:</em> pads and helmets spread the force of a collision over a bigger area and a longer time, so less force hits any one spot.</p>
  </div>
  <h3>Misconceptions to Watch</h3>
  <div class="misconception"><p>"Heavy things fall faster" may come up. Not true without air resistance (Monday's coin and card fall together). Mass changes how hard something is to <em>push</em>, not how fast gravity makes it fall.</p></div>
  <h3>Extension Activity</h3>
  <div class="extension"><p>Make a 5-marble "Newton's cradle" in the ruler groove: roll 1 in and 1 pops out the far end, roll 2 in and 2 pop out. Ask him to predict 3 before trying. Energy and momentum travel through the line.</p></div>

  <h2 class="thu">Thursday — The Punter's Leg: Simple Machines</h2>
  <h3>Answer Key — Film Study</h3>
  <div class="answer-box thu">
    <p><strong>Q1:</strong> Make a force bigger (increase it) or change its direction.</p>
    <p><strong>Q2:</strong> Fulcrum = hip; effort = thigh/leg muscles; load = the football.</p>
    <p><strong>Q3:</strong> Closer to the coins (the load).</p>
    <p><strong>Q4:</strong> Yards. Inches is far too small (40 inches is barely past your feet) and miles is far too big.</p>
  </div>
  <h3>LET'S DISCUSS Guidance</h3>
  <div class="discuss"><p>Scissors are a <b>compound machine</b>: two levers sharing one fulcrum (the screw/pivot in the middle, which is itself a simple machine), and each blade is a wedge. That's three of the six machines in one tool! (VA 3.3.2.d)</p></div>
  <h3>Matching Key</h3>
  <div class="answer-box thu">
    <p>Lever &rarr; punter's leg (3) &nbsp;|&nbsp; Inclined plane &rarr; ramp into the stands (5) &nbsp;|&nbsp; Wedge &rarr; cleat spikes (1) &nbsp;|&nbsp; Wheel and axle &rarr; water cart (6) &nbsp;|&nbsp; Pulley &rarr; flag rope (2) &nbsp;|&nbsp; Screw &rarr; goalpost bolt (4)</p>
  </div>
  <h3>Play #4A / 4B Key</h3>
  <div class="answer-box thu">
    <p><strong>Lever Lab (typical, 30 cm ruler):</strong> fulcrum 15 cm → about 5 pennies; 12 cm (near load) → about 1 penny, or even 0; 18 cm (near effort) → about 10–12 pennies. Closer to the load = <b>fewer</b> pennies. The ruler's own weight genuinely helps when the fulcrum moves toward the load, so a "0 pennies" result is real data, not a mistake. Unit: pennies.</p>
    <p><strong>Scavenger hunt (examples):</strong> lever: door handle, seesaw, bottle opener; inclined plane: ramp, slide, driveway; wedge: knife, doorstop, zipper; wheel and axle: doorknob, car wheel, pizza cutter; pulley: window blinds, flagpole; screw: jar lid, light bulb, bolt. <em>Coach's Q:</em> a lever handle is a lever; a round doorknob is a wheel and axle. Accept either with reasoning.</p>
    <p><strong>Catapult:</strong> fulcrum = the 5-stick stack; effort = his finger pressing the spoon end down; load = the pom-pom. Moving the stack toward the banded end gives a longer, faster arm (more distance); moving it toward the spoon gives a stiffer, shorter launch.</p>
  </div>
  <h3>Misconceptions to Watch</h3>
  <div class="misconception"><p>"Machines create extra force for free." A lever trades: less effort means you push through a longer distance. The catapult does the reverse: a short push becomes a long, fast swing.</p></div>
  <h3>Extension Activity</h3>
  <div class="extension"><p>Rig a pulley: loop a string over a broom handle held between two chairs, tie a small bucket on one end, and pull down to lift it up. Which direction is his effort? Which way does the load move? (Change of direction, VA 3.3.2.c.)</p></div>
</div>

<div class="page">
  <h2 class="fri">Friday — Field Goal Day: Action, Reaction, Trajectory (Capstone)</h2>
  <h3>Answer Key — Film Study</h3>
  <div class="answer-box fri">
    <p><strong>Q1:</strong> Action: the balloon pushes air out backward. Reaction: the air pushes the balloon forward.</p>
    <p><strong>Q2:</strong> Inertia (keeps it moving forward) and gravity (pulls it down).</p>
    <p><strong>Q3:</strong> Any three: leg as a lever; contact force / unbalanced force starting the ball; energy transfer in the collision; gravity curving the trajectory; launch angle; action and reaction between foot and ball.</p>
    <p><strong>Q4:</strong> His measured distance with a length unit (inches, feet, or centimeters).</p>
  </div>
  <h3>LET'S DISCUSS Guidance</h3>
  <div class="discuss"><p>On the Moon, gravity is about one-sixth as strong, so the ball would curve down much more slowly, with a longer, flatter, higher trajectory that goes much farther. Field goals from much longer distance would be easy, but aiming would be a new challenge! (No air on the Moon either, so no wind to worry about.)</p></div>
  <h3>Tree Map Key</h3>
  <div class="answer-box fri">
    <p><strong>Contact Forces:</strong> Tackle, Kick, Throw &nbsp;|&nbsp; <strong>Forces from a Distance:</strong> Gravity, Magnetism &nbsp;|&nbsp; <strong>Simple Machines:</strong> Lever, Wedge, Pulley &nbsp;|&nbsp; <strong>Words About Motion:</strong> Inertia, Momentum, Trajectory</p>
  </div>
  <h3>Play #5 &amp; Bar Graph Key</h3>
  <div class="answer-box fri">
    <p><strong>Balloon:</strong> more breaths usually means farther: more air pushed backward means a longer push forward. <strong>Field goals:</strong> makes usually drop as distance grows; the bar graph should step down. <strong>Launch angle:</strong> results vary; often 1 book (a medium angle) goes farthest, matching the reading. If his result disagrees, that's Rule One: celebrate the data and ask what might explain it.</p>
    <p><strong>Graph Q2</strong> is subtraction with a unit: e.g., 8 kicks − 3 kicks = 5 kicks. Insist the answer carries "kicks."</p>
  </div>
  <h3>Misconceptions to Watch</h3>
  <div class="misconception"><p>"The reaction force happens after the action." The pair happens at exactly the same instant. Another: "If forces are equal and opposite, why does anything move?" The pair acts on <em>different</em> objects (foot pushes the ball, the ball pushes the foot), so they don't cancel each other out.</p></div>
  <h3>Extension Activity</h3>
  <div class="extension"><p>Watch a few real field-goal kicks (slow motion if possible). Pause at contact and ask him to call out every force he can see. Bonus: count the yard lines to estimate the kick distance. In yards, of course.</p></div>

  <hr style="margin: 18px 0; border-color: #ccc;">
  <h2 class="gen">Season Summary — Causal Chain</h2>
  <ol style="padding-left: 20px; font-size: 10pt; line-height: 2;">
    <li><strong>Monday:</strong> Forces are pushes and pulls, by contact or at a distance; inertia means motion only changes when a force acts.</li>
    <li><strong>Tuesday:</strong> Several forces can act at once; the net force decides how motion changes.</li>
    <li><strong>Wednesday:</strong> More mass means more force is needed; collisions transfer energy.</li>
    <li><strong>Thursday:</strong> Simple machines increase or redirect force; levers depend on the fulcrum.</li>
    <li><strong>Friday:</strong> Every force has a partner; gravity and inertia make a trajectory; engineers test and improve.</li>
  </ol>
  <p style="margin-top: 10px;">By Friday, Christopher should be able to narrate one field-goal kick using at least four playbook terms, and every number he says about it should come with a unit.</p>
</div>
"""


if __name__ == "__main__":
    generate_football_week_series()
