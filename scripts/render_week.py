"""Render a stored WeekDoc JSON file to a packet, teacher guide and parent prep sheet (offline).

    venv/bin/python scripts/render_week.py week.json --name Zoe --out out_dir

Without --name, {{student_name}} becomes "your child". No network, no database.
"""

import argparse
import json
import os
import sys
from pathlib import Path

ROOT = Path(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, str(ROOT))

from src.weekdoc import load_week  # noqa: E402
from src.weekdoc.render import render_packet, render_prep_sheet, render_teacher_guide  # noqa: E402


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("week", type=Path, help="WeekDoc JSON file (any supported schema_version)")
    ap.add_argument("--name", default=None, help="child's first name for {{student_name}}")
    ap.add_argument("--out", type=Path, default=Path("."), help="output directory")
    args = ap.parse_args(argv)

    week = load_week(json.loads(args.week.read_text(encoding="utf-8")))
    args.out.mkdir(parents=True, exist_ok=True)
    stem = args.week.stem
    outputs = {
        f"{stem}_packet.html": render_packet(week, args.name),
        f"{stem}_teacher_guide.html": render_teacher_guide(week, args.name),
        f"{stem}_prep_sheet.html": render_prep_sheet(week, args.name),
    }
    for name, html in outputs.items():
        (args.out / name).write_text(html, encoding="utf-8")
        print(args.out / name)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
