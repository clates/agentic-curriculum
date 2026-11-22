"""CLI: author a week for a student, save it, print a summary.

    cd src && ../venv/bin/python -m authoring --student-json child.json \\
        --topic "Weather and seasons" --standards VA.SCIENCE.2.2.6.a,VA.SCIENCE.2.2.6.b \\
        [--model z-ai/glm-5.3] [--out-dir DIR] [--no-save]
    cd src && ../venv/bin/python -m authoring --find-standards --grade 2 --subject Science

``child.json`` holds the allowlisted fields only: first_name, grade, reading_level, interests,
parent_notes. Needs OPENROUTER_API_KEY (never printed).
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

from .context import ModelStudentContext, Tenant
from .pipeline import author_week
from .standards import search_standards


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="python -m authoring", description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--student-json")
    ap.add_argument("--topic")
    ap.add_argument("--standards", help="comma-separated standard ids from the standards DB")
    ap.add_argument("--model", help="override the author model (also LLM_MODEL_AUTHOR)")
    ap.add_argument("--family-id", default="fam_local")
    ap.add_argument("--student-id", default="stu_author_cli")
    ap.add_argument("--week-of")
    ap.add_argument("--max-cost", type=float, help="per-run cost cap in USD")
    ap.add_argument("--max-repairs", type=int, default=4)
    ap.add_argument("--out-dir", help="also write week.json and run.json here")
    ap.add_argument("--no-save", action="store_true", help="do not write to the week store")
    ap.add_argument("--find-standards", action="store_true")
    ap.add_argument("--grade", type=int)
    ap.add_argument("--subject")
    ap.add_argument("--keyword")
    a = ap.parse_args(argv)

    if a.find_standards:
        if a.grade is None:
            ap.error("--find-standards needs --grade")
        for s in search_standards(grade=a.grade, subject=a.subject, keyword=a.keyword):
            print(f"{s.standard_id}\t{s.subject}\t{s.description[:110]}")
        return 0
    if not (a.student_json and a.topic and a.standards):
        ap.error("--student-json, --topic and --standards are required")
    if a.model:
        os.environ["LLM_MODEL_AUTHOR"] = a.model
    student = ModelStudentContext.from_profile(json.loads(Path(a.student_json).read_text()))
    result = author_week(
        Tenant(a.family_id), student, a.topic, [s.strip() for s in a.standards.split(",")],
        student_id=None if a.no_save else a.student_id, week_of=a.week_of,
        max_repairs=a.max_repairs, max_cost_usd=a.max_cost,
    )
    r = result.run
    print(f"status:        {result.status}")
    print(f"model:         {r.model}   prompts: {r.prompt_version} ({r.prompt_hash})")
    for s in r.steps:
        print(f"  step {s.name:<5} ok={s.ok} calls={s.calls} repairs={s.repairs} "
              f"tokens={s.prompt_tokens}/{s.completion_tokens} cost=${s.cost_usd:.4f} wall={s.wall_s}s")
    print(f"total:         repairs={r.repairs} cost=${r.cost_usd:.4f} wall={r.wall_s}s")
    if result.week:
        w = result.week
        kinds = sorted({ws.kind for d in w.days for ws in d.worksheets})
        print(f"week:          {w.title!r}, {sum(len(d.worksheets) for d in w.days)} worksheets, "
              f"{len(kinds)} kinds, {len(w.prep_checks)} prep checks")
        if r.uncovered_standards:
            print(f"uncovered standards: {', '.join(r.uncovered_standards)}")
    if result.packet_id:
        print(f"saved packet:  {result.packet_id} (family {a.family_id}, student {a.student_id}, "
              f"saved={result.saved})")
    for e in result.errors:
        print(f"error: {e[:400]}", file=sys.stderr)
    if a.out_dir:
        out = Path(a.out_dir)
        out.mkdir(parents=True, exist_ok=True)
        (out / "run.json").write_text(json.dumps(r.to_dict(), indent=1, ensure_ascii=False))
        if result.week:
            (out / "week.json").write_text(result.week.model_dump_json(indent=1))
    return 0 if result.ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
