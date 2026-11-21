"""Deterministic candidate selector (M6.1): which standards next week could be about.

``select_candidates`` is a pure function of its arguments (no clock, no randomness, no I/O). The
same child, week and seed always give the same answer; a different ``seed`` (for example one
that includes the regeneration count) gives a different but equally valid answer, and ids passed
in ``avoid`` (what the parent has already seen) sort last so fresh ideas are actually fresh.

It returns three pools, one per outline option, and every id in them exists in ``standards``:

* ``easier``    review that is due, then skills one grade below, then the child's own grade
* ``on_level``  skills the child is working on, then new skills at their grade
* ``stretch``   new skills one grade up whose prerequisites are not known weak

Rules, in plain terms:

* Mastered skills are never new work. A mastered or benched skill inside its cooldown is left
  alone; once it falls due (``review_policy``) it comes back as review.
* Dependencies: a skill is blocked while one of its prerequisites is known weak (being worked on
  or last marked needs-work and not yet mastered). The weak prerequisite is offered first. A
  prerequisite the child has no record for is assumed known: placement by grade is the evidence,
  and a new child with no history must still get ideas.
* Within a pool, skills the child is already working on come first, then new ones, then a stable
  hash of ``seed|id`` decides the order. Each option takes skills round-robin across subjects,
  so a week is not three versions of one subject, and no skill appears in two options unless
  the pools are too small to avoid it.
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

DIFFICULTIES = ("easier", "on_level", "stretch")
PER_OPTION = 3
WEAK_RATINGS = ("STRUGGLING", "NOT_STARTED", "DEVELOPING")

REASON_REVIEW = "review"
REASON_WORKING_ON = "working_on"
REASON_NEW = "new"


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
    reason: str  # review | working_on | new


@dataclass(frozen=True)
class CandidateSet:
    easier: tuple[Candidate, ...]
    on_level: tuple[Candidate, ...]
    stretch: tuple[Candidate, ...]

    def for_difficulty(self, difficulty: str) -> tuple[Candidate, ...]:
        return getattr(self, difficulty)

    def ids_for(self, difficulty: str) -> list[str]:
        return [c.standard_id for c in self.for_difficulty(difficulty)]

    def all_ids(self) -> set[str]:
        return {c.standard_id for d in DIFFICULTIES for c in self.for_difficulty(d)}


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


def select_candidates(
    *,
    progress: Mapping[str, Any] | str | None,
    standards: Iterable[StandardInfo],
    prereqs: Mapping[str, Collection[str]] | None = None,
    grade: int,
    seed: str,
    now: str | None = None,
    per_option: int = PER_OPTION,
    avoid: Collection[str] = frozenset(),
) -> CandidateSet:
    """Pick the standards pools for the three outline options. See the module docstring."""
    if isinstance(progress, str):
        progress = json.loads(progress or "{}")
    progress = progress or {}
    prereqs = prereqs or {}
    by_id = {s.standard_id: s for s in standards}

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
    reviews = [by_id[sid] for sid in due_ids]
    review_set = set(due_ids)

    def blocked(sid: str) -> bool:
        return any(p != sid and p in weak for p in prereqs.get(sid, ()))

    def order_key(s: StandardInfo):
        working = s.standard_id in weak
        return (
            0 if working else 1,
            1 if s.standard_id in avoid else 0,
            _digest(seed, s.standard_id),
        )

    eligible: dict[int, list[StandardInfo]] = {}
    for s in by_id.values():
        if s.standard_id in mastered or s.standard_id in cooling or s.standard_id in review_set:
            continue
        if blocked(s.standard_id):
            continue
        eligible.setdefault(s.grade, []).append(s)
    for pool in eligible.values():
        pool.sort(key=order_key)
    reviews.sort(key=lambda s: (1 if s.standard_id in avoid else 0,))  # stable: policy order

    def pool(g: int) -> list[StandardInfo]:
        return eligible.get(g, [])

    def build(head: list[StandardInfo], sources: list[list[StandardInfo]], used: set[str]):
        chosen = [s for s in head if s.standard_id not in used][: max(0, per_option - 1)]
        taken = used | {s.standard_id for s in chosen}
        for source in sources:
            if len(chosen) >= per_option:
                break
            picked = _round_robin(
                [s for s in source if s.standard_id not in taken], per_option - len(chosen)
            )
            chosen.extend(picked)
            taken |= {s.standard_id for s in picked}
        return chosen

    used: set[str] = set()
    easier = build(reviews[:2], [pool(grade - 1), pool(grade)], used)
    used |= {s.standard_id for s in easier}
    on_level = build(reviews[2:3], [pool(grade), pool(grade - 1), pool(grade + 1)], used)
    used |= {s.standard_id for s in on_level}
    stretch = build([], [pool(grade + 1), pool(grade), pool(grade + 2)], used)

    everything = [s for g in sorted(eligible) for s in eligible[g]] + reviews
    everything.sort(key=lambda s: (abs(s.grade - grade), order_key(s)))
    if not everything:
        raise NoCandidates(f"no standards available near grade {grade}")

    def fill(chosen: list[StandardInfo]) -> list[StandardInfo]:
        """An option must never be empty: borrow from anywhere (overlap beats nothing)."""
        if chosen:
            return chosen
        return _round_robin(everything, per_option)

    def convert(items: list[StandardInfo]) -> tuple[Candidate, ...]:
        out = []
        for s in fill(items):
            reason = (
                REASON_REVIEW
                if s.standard_id in review_set
                else REASON_WORKING_ON if s.standard_id in weak else REASON_NEW
            )
            out.append(Candidate(s.standard_id, s.subject, s.grade, s.description, reason))
        return tuple(out)

    return CandidateSet(
        easier=convert(easier), on_level=convert(on_level), stretch=convert(stretch)
    )


_SUB_ITEM = re.compile(r"\.[a-z]$")
MIN_DESCRIPTION_CHARS = 40


def load_candidate_inputs(
    db_path: str, grade: int, *, span: int = 2
) -> tuple[list[StandardInfo], dict[str, set[str]]]:
    """Standards near ``grade`` (whole skills, not their bullet sub-points) and their prerequisites."""
    import sqlite3

    conn = sqlite3.connect(db_path)
    try:
        rows = conn.execute(
            "SELECT standard_id, subject, grade_level, description FROM standards "
            "WHERE grade_level BETWEEN ? AND ? ORDER BY standard_id",
            (grade - span, grade + span),
        ).fetchall()
    except sqlite3.OperationalError:
        return [], {}
    finally:
        conn.close()
    standards = [
        StandardInfo(sid, subject or "", int(g), " ".join(desc.split()))
        for sid, subject, g, desc in rows
        if desc
        and len(desc.strip()) >= MIN_DESCRIPTION_CHARS
        and not _SUB_ITEM.search(sid)
        and g is not None
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
