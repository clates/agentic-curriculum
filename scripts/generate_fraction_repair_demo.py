"""Demo: Fraction Repair Shop — error_audit theme, Dev (grade 3, fractions).

Three specimens (halves / thirds / fourths), fix_mode=redraw with the new
"partitions" art kind: a circle cut into wedges where one piece is unequal,
the count is wrong, or the shading slips. Each redraw box carries a starter
scaffold of the CORRECT equal partitions at reduced opacity.

Outputs PNG + PDF + answer-key PNG + an HTML packet page into
docs/previews/fraction_repair/.
"""
import os

os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import sys

sys.path.insert(0, os.path.abspath("src"))

from worksheets.factory import WorksheetFactory
from worksheet_renderer import (
    render_error_audit_to_image,
    render_error_audit_to_pdf,
)
from worksheet_html_renderer import render_worksheet_html, build_print_packet_html

OUT = "docs/previews/fraction_repair"
os.makedirs(OUT, exist_ok=True)

PAYLOAD = {
    "title": "Fractions: Halves, Thirds & Fourths",
    "theme_label": "Fraction Repair Shop",
    "instructions": (
        "Pip and friends cut these fraction shapes, but every one has a bug! "
        "Circle the bug, check the suspect that did it, then redraw the shape "
        "fixed in the box. The faint starter shape shows the equal pieces "
        "you need."
    ),
    "legend": ["Unequal pieces", "Wrong count", "Shading slip"],
    "fix_mode": "redraw",
    "verify": True,
    "metadata": {
        "learner": "Dev",
        "grade": 3,
        "subject": "fractions",
        "strategy": "misconception-hunter",
        "source": "bank:dev_batch/fraction_repair_shop",
    },
    "specimens": [
        {
            "prompt": "Pip says this circle shows halves.",
            "lines": ["Study Pip's circle. What did he get wrong?"],
            "art": {"kind": "partitions", "parts": 2, "broken": 0},
            "bug_location": "The two pieces are not equal; one is much bigger, so neither is one half.",
            "diagnosis": "Unequal pieces",
        },
        {
            "prompt": "Zoe says this circle shows thirds.",
            "lines": ["Study Zoe's circle. What did she get wrong?"],
            "art": {"kind": "partitions", "parts": 4},
            "bug_location": "Zoe's circle has 4 equal pieces, not 3; each piece is one fourth, not one third.",
            "diagnosis": "Wrong count",
        },
        {
            "prompt": "Milo says the shaded part of the circle is one fourth.",
            "lines": ["Study Milo's circle. What did he get wrong?"],
            "art": {"kind": "partitions", "parts": 4, "shaded": [0, 1]},
            "bug_location": "Two pieces are shaded, so the shaded part is two fourths (one half), not one fourth.",
            "diagnosis": "Shading slip",
        },
    ],
}

# PNG + PDF + answer key via the PIL renderer.
ws = WorksheetFactory.create("error_audit", PAYLOAD)
img = render_error_audit_to_image(ws, f"{OUT}/fraction_repair.png")
pdf = render_error_audit_to_pdf(ws, f"{OUT}/fraction_repair.pdf")
key = WorksheetFactory.create("error_audit", {**PAYLOAD, "show_answers": True})
render_error_audit_to_image(key, f"{OUT}/fraction_repair_key.png")
print(f"OK {img} + {pdf} (+ key)")

# HTML packet page via the inline-SVG renderer.
html_data = {
    "title": PAYLOAD["title"],
    "theme_label": PAYLOAD["theme_label"],
    "instructions": PAYLOAD["instructions"],
    "legend": PAYLOAD["legend"],
    "fix_mode": PAYLOAD["fix_mode"],
    "verify": PAYLOAD["verify"],
    "adversarial": False,
    "fix_lines": 2,
    "specimens": PAYLOAD["specimens"],
}
frag = render_worksheet_html("errorAuditWorksheet", html_data, "Thursday")
assert frag, "no HTML fragment for fraction repair"
packet = build_print_packet_html([("Thursday", frag)], "Fraction Repair Shop (HTML)")
with open(os.path.join(OUT, "fraction_repair_packet.html"), "w") as f:
    f.write(packet)
print("OK fraction_repair_packet.html")

print("DONE:", sorted(os.listdir(OUT)))
