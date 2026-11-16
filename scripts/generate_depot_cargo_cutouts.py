"""Depot cargo cutouts — printable base-ten manipulatives for the Truck Depot place-value week.

Theodore is the depot dispatcher: cargo ships as CRATES OF 10 and LOOSE BOXES (ones). Print on
cardstock at 100% scale ("Actual size", not "Fit to page") and cut along the thick lines only.
Thin lines stay on the piece so every crate can still be counted box by box.

Pages:
  1. Long crates  — tens as 1×10 strips (16 pieces)
  2. Stack crates — tens as 2×5 blocks (18 pieces)
  3. Loose boxes  — ones as 1×1 squares (180 pieces)
  4. Loading dock — place-value mat: TENS bay | ONES bay | "__ tens and __ ones is __"

All three piece types share one unit size, so a 1×10 strip, a 2×5 block and ten loose boxes
cover exactly the same area — lay them on top of each other to prove they are all "10".

Output: depot_week_series/depot_cargo_cutouts.html
"""

import os

os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

OUTDIR = "depot_week_series"

UNIT_IN = 0.55  # side of one box, in inches — sized so 9 long crates fit the dock's tens bay
TEN_FILL = "#fde68a"  # amber: crates of ten
ONE_FILL = "#bfdbfe"  # blue: loose boxes


def piece(cols: int, rows: int, fill: str, label: str = "") -> str:
    """One cut-out piece: a cols×rows block of unit boxes with a thick cut outline."""
    cells = "".join('<div class="cell"></div>' for _ in range(cols * rows))
    tag = f'<span class="tag">{label}</span>' if label else ""
    return (
        f'<div class="piece" style="grid-template-columns: repeat({cols}, {UNIT_IN}in); '
        f'grid-template-rows: repeat({rows}, {UNIT_IN}in); background: {fill};">'
        f"{cells}{tag}</div>"
    )


def sheet(cols: int, rows: int, piece_html: str) -> str:
    """Pieces packed edge to edge, so every cut is one long straight line."""
    return (
        f'<div class="sheet" style="grid-template-columns: repeat({cols}, max-content);">'
        + piece_html * (cols * rows)
        + "</div>"
    )


def page(title: str, note: str, body: str) -> str:
    return f"""
<div class="page">
  <div class="head">
    <div class="title">{title}</div>
    <div class="note">{note}</div>
  </div>
  {body}
</div>"""


CUT = "Cut on the <b>thick</b> lines only. Keep the thin lines — they let you count the boxes."


def build_html() -> str:
    long_crates = page(
        "Cargo Crates — Long Crates (10)",
        f"Every long crate holds <b>10 boxes</b>. Count them! &nbsp; {CUT}",
        sheet(1, 16, piece(10, 1, TEN_FILL, "10")),
    )
    stack_crates = page(
        "Cargo Crates — Stack Crates (10)",
        f"A stack crate holds <b>10 boxes</b> too — 2 rows of 5. &nbsp; {CUT}",
        sheet(6, 3, piece(2, 5, TEN_FILL, "10")),
    )
    loose_boxes = page(
        "Loose Boxes (1)",
        "Each square is <b>1 box</b>. Cut along every line. "
        "When you have 10 loose boxes, trade them for a crate!",
        sheet(12, 15, piece(1, 1, ONE_FILL)),
    )
    dock = page(
        "Theodore's Loading Dock",
        "Crates go in the TENS bay. Loose boxes go in the ONES bay. "
        "Never park 10 loose boxes — trade them for a crate!",
        """
  <div class="dock">
    <div class="bay tens">
      <div class="bay-label">TENS<span>crates of 10</span></div>
    </div>
    <div class="bay ones">
      <div class="bay-label">ONES<span>loose boxes</span></div>
    </div>
  </div>
  <div class="tally">
    <span class="blank"></span> tens &nbsp;and&nbsp; <span class="blank"></span> ones
    &nbsp;is&nbsp; <span class="blank wide"></span>
  </div>
  <div class="order">Work order: ______________________ &nbsp;&nbsp; Loaded by: ______________</div>
""",
    )

    return f"""<!DOCTYPE html><html><head><meta charset="utf-8">
<title>Depot Cargo Cutouts — Tens and Ones</title>
<style>
@page {{ size: letter; margin: 0.5in; }}
* {{ box-sizing: border-box; margin: 0; padding: 0; }}
html {{ -webkit-print-color-adjust: exact; print-color-adjust: exact; }}
body {{ font-family: 'Trebuchet MS', Arial, sans-serif; color: #111; }}
@media screen {{
  body {{ background: #b0b0b0; padding: 24px; }}
  .page {{ background: white; margin: 0 auto 28px; padding: 0.5in;
    box-shadow: 0 4px 18px rgba(0,0,0,.28); width: 8.5in; min-height: 11in; }}
}}
.page {{ page-break-after: always; break-after: page; }}
.page:last-child {{ page-break-after: avoid; break-after: avoid; }}
.head {{ border-bottom: 3px solid #b45309; padding-bottom: 4px; margin-bottom: 0.15in; }}
.title {{ font-size: 18pt; font-weight: bold; color: #b45309; }}
.note {{ font-size: 9.5pt; color: #333; }}

.sheet {{ display: grid; justify-content: center; }}
.piece {{ display: grid; position: relative; outline: 2.5px solid #111; outline-offset: -1.25px; }}
.cell {{ border-right: 1px dotted #a16207; border-bottom: 1px dotted #a16207; }}
.tag {{ position: absolute; top: 1px; left: 3px; font-size: 7pt; font-weight: bold;
  color: #92400e; }}

.dock {{ display: grid; grid-template-columns: 5.2in 2.1in; gap: 0.2in; height: 6.6in; }}
.bay {{ border: 3px solid #111; border-radius: 8px; position: relative;
  background-image: repeating-linear-gradient(135deg, transparent 0 18px, #f3f4f6 18px 22px); }}
.bay.tens {{ border-color: #b45309; }}
.bay.ones {{ border-color: #1d4ed8; }}
.bay-label {{ position: absolute; bottom: 6px; left: 0; right: 0; text-align: center;
  font-size: 20pt; font-weight: bold; letter-spacing: 0.08em; }}
.bay.tens .bay-label {{ color: #b45309; }}
.bay.ones .bay-label {{ color: #1d4ed8; }}
.bay-label span {{ display: block; font-size: 9pt; letter-spacing: 0; color: #444;
  font-weight: normal; }}
.tally {{ margin-top: 0.35in; font-size: 24pt; font-weight: bold; text-align: center; }}
.blank {{ display: inline-block; width: 0.9in; height: 0.7in; border: 3px solid #111;
  border-radius: 6px; vertical-align: middle; }}
.blank.wide {{ width: 1.3in; }}
.order {{ margin-top: 0.4in; font-size: 12pt; text-align: center; }}
</style></head><body>
{long_crates}
{stack_crates}
{loose_boxes}
{dock}
</body></html>"""


def main() -> None:
    os.makedirs(OUTDIR, exist_ok=True)
    path = os.path.join(OUTDIR, "depot_cargo_cutouts.html")
    with open(path, "w") as f:
        f.write(build_html())
    print("OK:", path)


if __name__ == "__main__":
    main()
