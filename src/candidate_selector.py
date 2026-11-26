"""Deterministic standards selector (M6.1): WHICH skills next week must carry.

The curriculum engine, not the parent, decides the week's skills. ``select_week_standards`` is a
pure function of the child's progress (mastery, review due dates), the grade-level standards and
a tie-break seed: no clock, no randomness, no I/O, and no parent input. The same inputs always
give the same set; the three week topics the parent chooses between all wrap this one set.

What goes in, in this order, up to ``PER_SET`` skills:

* due review: mastered or benched skills that have fallen due (``review_policy``), at most two
* the gap: skills the child is working on or last marked shaky, up to two more
* the new core: new skills at the child's own grade, then one grade below, taken round-robin
  across subjects so a week is not one subject
* a measured step up: ``step_up_slots`` (0 or 1) skills one grade above, only when the child's
  mastery says they are ready (several mastered, at most one shaky skill)

Mastered skills are never new work. A skill is blocked while one of its prerequisites is known
weak; the weak prerequisite is offered first. A prerequisite the child has no record for is
assumed known: placement by grade is the evidence, and a new child with no history must still
get a week.
"""

from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass
from typing import Any, Collection, Iterable, Mapping, Sequence

try:  # Prefer package-relative import when available
    from .review_policy import review_due, review_schedule  # type: ignore
except ImportError:  # Fallback for direct script execution / top-level import
    from review_policy import review_due, review_schedule  # type: ignore

PER_SET = 4
MAX_REVIEWS = 2
MAX_GAP = 2
STEP_UP_MIN_MASTERED = 3
STEP_UP_MAX_WEAK = 1
WEAK_RATINGS = ("STRUGGLING", "NOT_STARTED", "DEVELOPING")

REASON_REVIEW = "review"
REASON_WORKING_ON = "working_on"
REASON_NEW = "new"
REASON_NEXT_STEP = "next_step"  # a measured step above the child's grade


class NoCandidates(ValueError):
    """There is nothing to plan next week from (no standards at or near the child's grade)."""


@dataclass(frozen=True)
class StandardInfo:
    standard_id: str
    subject: str
    grade: int
    description: str


@dataclass(frozen=True)
class Candidate:
    standard_id: str
    subject: str
    grade: int
    description: str
    reason: str  # review | working_on | new | next_step


@dataclass(frozen=True)
class StandardsSet:
    """The one set of skills the week carries. Every topic option offers exactly this."""

    items: tuple[Candidate, ...]

    def ids(self) -> list[str]:
        return [c.standard_id for c in self.items]


def step_up_slots(mastered_count: int, weak_count: int) -> int:
    """How many skills above the child's grade this week may hold, from mastery alone."""
    return 1 if mastered_count >= STEP_UP_MIN_MASTERED and weak_count <= STEP_UP_MAX_WEAK else 0


def _digest(seed: str, standard_id: str) -> str:
    return hashlib.sha256(f"{seed}|{standard_id}".encode()).hexdigest()


def _round_robin(ordered: Sequence[StandardInfo], limit: int) -> list[StandardInfo]:
    """Take up to ``limit`` skills, rotating through subjects in order of first appearance."""
    if limit <= 0:
        return []
    buckets: dict[str, list[StandardInfo]] = {}
    for s in ordered:
        buckets.setdefault(s.subject, []).append(s)
    out: list[StandardInfo] = []
    while len(out) < limit and any(buckets.values()):
        for subject in list(buckets):
            if buckets[subject] and len(out) < limit:
                out.append(buckets[subject].pop(0))
    return out


def select_week_standards(
    *,
    progress: Mapping[str, Any] | str | None,
    standards: Iterable[StandardInfo],
    prereqs: Mapping[str, Collection[str]] | None = None,
    grade: int,
    grade_by_subject: Mapping[str, int] | None = None,
    seed: str,
    now: str | None = None,
    per_set: int = PER_SET,
) -> StandardsSet:
    """Pick the week's standards from mastery, review dates and grade. See the module docstring."""
    if isinstance(progress, str):
        progress = json.loads(progress or "{}")
    progress = progress or {}
    prereqs = prereqs or {}
    by_id = {s.standard_id: s for s in standards}
    grades = grade_by_subject or {}

    def offset(s: StandardInfo) -> int:
        """How far the skill sits from the grade the child works at in its subject."""
        return s.grade - grades.get(s.subject, grade)

    mastered = set(progress.get("mastered_standards") or [])
    developing = set(progress.get("developing_standards") or [])
    meta = progress.get("standard_metadata") or {}
    weak = set(developing) | {
        sid for sid, m in meta.items() if (m or {}).get("last_feedback") in WEAK_RATINGS
    }
    weak -= mastered

    due_rows = review_due(progress, now)
    due_ids = [r["standard_id"] for r in due_rows if r["standard_id"] in by_id]
    cooling = {r["standard_id"] for r in review_schedule(progress)} - {
        r["standard_id"] for r in due_rows
    }
    review_set = set(due_ids)

    def blocked(sid: str) -> bool:
        return any(p != sid and p in weak for p in prereqs.get(sid, ()))

    def order_key(s: StandardInfo):
        return (0 if s.standard_id in weak else 1, _digest(seed, s.standard_id))

    eligible: dict[int, list[StandardInfo]] = {}  # keyed by offset from the subject's grade
    for s in by_id.values():
        if s.standard_id in mastered or s.standard_id in cooling or s.standard_id in review_set:
            continue
        if blocked(s.standard_id):
            continue
        eligible.setdefault(offset(s), []).append(s)
    for pool in eligible.values():
        pool.sort(key=order_key)

    def pool(g: int) -> list[StandardInfo]:
        return eligible.get(g, [])

    step_up = min(step_up_slots(len(mastered), len(weak)), max(0, per_set - 1))
    chosen: list[StandardInfo] = [by_id[sid] for sid in due_ids][: min(MAX_REVIEWS, per_set)]
    taken = {s.standard_id for s in chosen}

    def add(items: list[StandardInfo], limit: int) -> None:
        for s in _round_robin([s for s in items if s.standard_id not in taken], limit):
            chosen.append(s)
            taken.add(s.standard_id)

    room = per_set - step_up
    gap = sorted(
        [s for g in sorted(eligible) for s in eligible[g] if s.standard_id in weak],
        key=lambda s: (abs(offset(s)), order_key(s)),
    )
    add(gap, min(MAX_GAP, room - len(chosen)))
    add(pool(0) + pool(-1) + pool(1), room - len(chosen))
    before = len(chosen)
    add(pool(1), step_up)
    step_up_ids = {s.standard_id for s in chosen[before:]}

    everything = [s for g in sorted(eligible) for s in eligible[g]] + [
        by_id[sid] for sid in due_ids
    ]
    everything.sort(key=lambda s: (abs(offset(s)), order_key(s)))
    if not everything:
        raise NoCandidates(f"no standards available near grade {grade}")
    if not chosen:  # a week must never be empty: borrow from anywhere
        chosen = _round_robin(everything, per_set)

    def reason(s: StandardInfo) -> str:
        if s.standard_id in review_set:
            return REASON_REVIEW
        if s.standard_id in weak:
            return REASON_WORKING_ON
        return REASON_NEXT_STEP if s.standard_id in step_up_ids else REASON_NEW

    return StandardsSet(
        items=tuple(
            Candidate(s.standard_id, s.subject, s.grade, s.description, reason(s)) for s in chosen
        )
    )


_SUB_ITEM = re.compile(r"\.[a-z]$")
MIN_DESCRIPTION_CHARS = 40


def is_whole_skill(standard_id: str, description: str | None) -> bool:
    """A real description and not a bullet sub-point: what counts as one skill."""
    return bool(
        description and len(description.strip()) >= MIN_DESCRIPTION_CHARS
    ) and not _SUB_ITEM.search(standard_id)


def load_candidate_inputs(
    db_path: str, grade: int, *, span: int = 2, extra_grades: Iterable[int] = ()
) -> tuple[list[StandardInfo], dict[str, set[str]]]:
    """Standards near ``grade`` (whole skills, not their bullet sub-points) and their prerequisites."""
    import sqlite3

    centres = sorted({grade, *extra_grades})
    where = " OR ".join("grade_level BETWEEN ? AND ?" for _ in centres)
    params = [v for c in centres for v in (c - span, c + span)]
    conn = sqlite3.connect(db_path)
    try:
        rows = conn.execute(
            "SELECT standard_id, subject, grade_level, description FROM standards "
            f"WHERE {where} ORDER BY standard_id",
            params,
        ).fetchall()
    except sqlite3.OperationalError:
        return [], {}
    finally:
        conn.close()
    standards = [
        StandardInfo(sid, subject or "", int(g), " ".join(desc.split()))
        for sid, subject, g, desc in rows
        if is_whole_skill(sid, desc) and g is not None
    ]
    ids = {s.standard_id for s in standards}
    prereqs: dict[str, set[str]] = {}
    try:
        try:
            from .curriculum_graph import load_from_db  # type: ignore
        except ImportError:
            from curriculum_graph import load_from_db  # type: ignore
        graph = load_from_db(db_path).graph
        for node in ids & set(graph.nodes()):
            deps = {
                u
                for u, _, d in graph.in_edges(node, data=True)
                if d.get("type") == "dependency" and u in ids
            }
            if deps:
                prereqs[node] = deps
    except Exception:  # a graph fault must never stop outlines: dependencies are an extra filter
        prereqs = {}
    return standards, prereqs
