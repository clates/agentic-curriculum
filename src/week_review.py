"""Checks on an authored week, for a person deciding whether it is well formed and well curated.

``review_week`` reads a ``WeekDoc`` (and, when there is one, the authoring run record) and returns
plain facts plus a short list of flags. It does not change anything and makes no model call.

The reading levels are Flesch-Kincaid ESTIMATES from a syllable heuristic: good at spotting a
passage that is two grades too hard, not precise to a tenth. Word budgets per grade are guidelines
for a day's worth of child-facing text, not rules. The same functions are meant to back an
authoring gate later, so a week that fails here can be sent back for a rewrite automatically.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any

# Child-facing words a day should stay under (a guideline, by grade; 0 = kindergarten).
WORD_BUDGET = {0: 250, 1: 400, 2: 550, 3: 700, 4: 850}
DEFAULT_WORD_BUDGET = 1000
PASSAGE_KEYS = {"passage", "text", "story", "article"}
PROMPT_KEYS = {"prompt", "question", "instructions", "directions"}
ADULT_KEYS = {"answer", "answers", "solution", "solutions", "answer_key"}
MIN_PASSAGE_WORDS = 30
MIN_PROMPT_WORDS = 6
MIN_PROMPT_SAMPLE = 40  # words of questions/instructions before a day's level is judged
READ_ALOUD = re.compile(
    r"\bread(ing)?\b[^.!?]{0,60}\baloud\b"  # "read the passage aloud", "reading it aloud"
    r"|\bread(ing)?[ -]aloud\b"
    r"|\bread (it |this |them )?(to|with) (your|the) (child|student|learner)",
    re.IGNORECASE,
)


def word_budget(grade: int) -> int:
    return WORD_BUDGET.get(grade, DEFAULT_WORD_BUDGET)


def _syllables(word: str) -> int:
    word = word.lower()
    count = len(re.findall(r"[aeiouy]+", word))
    if word.endswith("e") and count > 1:
        count -= 1
    return max(1, count)


def reading_grade(text: str) -> float | None:
    """Flesch-Kincaid grade estimate, or None for text too short to judge."""
    words = re.findall(r"[A-Za-z]+", text)
    if len(words) < MIN_PROMPT_WORDS:
        return None
    sentences = max(1, len(re.findall(r"[.!?]+", text)))
    syllables = sum(_syllables(w) for w in words)
    return round(0.39 * len(words) / sentences + 11.8 * syllables / len(words) - 15.59, 1)


def _strings(obj: Any, key: str = ""):
    """Every (field name, text) inside a worksheet's data, leaving out adult-only answer keys."""
    if isinstance(obj, dict):
        for k, v in obj.items():
            if k.lower() in ADULT_KEYS:
                continue
            yield from _strings(v, k)
    elif isinstance(obj, list):
        for v in obj:
            yield from _strings(v, key)
    elif isinstance(obj, str):
        yield key.lower(), obj


@dataclass
class Flag:
    level: str  # "warn" (worth fixing) or "info" (worth a look)
    message: str


@dataclass
class DayFacts:
    day: str
    title: str
    skills: list[dict[str, str]]
    kinds: list[str]
    words: int
    passage_grade: float | None
    prompt_grade: float | None


@dataclass
class Review:
    title: str
    grade: int
    word_budget: int
    days: list[DayFacts]
    skills: list[dict[str, Any]]
    subjects: list[str]
    prep_checks: int
    flags: list[Flag] = field(default_factory=list)
    run: dict[str, Any] | None = None

    def to_dict(self) -> dict[str, Any]:
        warns = sum(1 for f in self.flags if f.level == "warn")
        return {
            "title": self.title,
            "grade": self.grade,
            "word_budget": self.word_budget,
            "verdict": (
                "Looks good" if not warns else f"{warns} thing{'s' if warns != 1 else ''} to fix"
            ),
            "days": [vars(d) for d in self.days],
            "skills": self.skills,
            "subjects": self.subjects,
            "prep_checks": self.prep_checks,
            "flags": [vars(f) for f in self.flags],
            "run": self.run,
        }


def _grade_label(grade: int) -> str:
    return "kindergarten" if grade == 0 else f"grade {grade}"


def review_week(
    week: Any,
    *,
    grade: int,
    skills: dict[str, dict[str, str]] | None = None,
    planned: list[str] | None = None,
    run: dict[str, Any] | None = None,
) -> Review:
    """``week``: a WeekDoc (or its dict). ``skills``: standard id -> {subject, description}.
    ``planned``: the skill ids the picked idea promised. ``run``: the authoring run record."""
    doc = week.model_dump() if hasattr(week, "model_dump") else dict(week)
    skills = skills or {}
    budget = word_budget(grade)
    label = _grade_label(grade)
    flags: list[Flag] = []
    days: list[DayFacts] = []

    for d in doc.get("days", []):
        texts = [kt for ws in d.get("worksheets", []) for kt in _strings(ws.get("data", {}))]
        passages = [
            t for k, t in texts if k in PASSAGE_KEYS and len(t.split()) >= MIN_PASSAGE_WORDS
        ]
        prompts = [t for k, t in texts if k in PROMPT_KEYS and len(t.split()) >= MIN_PROMPT_WORDS]
        p_grades = [g for g in map(reading_grade, passages) if g is not None]
        # Questions are short; a one-line sentence fools the formula. Judge a day's questions
        # and instructions together, and only once there is enough text to judge.
        joined = " ".join(prompts)
        q_grade = reading_grade(joined) if len(joined.split()) >= MIN_PROMPT_SAMPLE else None
        facts = DayFacts(
            day=d.get("day", ""),
            title=d.get("title", ""),
            skills=[
                {"id": s, "subject": skills.get(s, {}).get("subject", "")}
                for s in d.get("standards", [])
            ],
            kinds=[ws.get("kind", "") for ws in d.get("worksheets", [])],
            words=sum(len(t.split()) for _, t in texts),
            passage_grade=max(p_grades) if p_grades else None,
            prompt_grade=q_grade,
        )
        days.append(facts)
        name = facts.day
        if facts.passage_grade is not None and facts.passage_grade > grade + 1.0:
            flags.append(Flag("warn", f"{name}'s reading passage reads at about grade "
                                      f"{facts.passage_grade:g}; the child is {label}."))  # fmt: skip
        if facts.prompt_grade is not None and facts.prompt_grade > grade + 1.5:
            flags.append(Flag("warn", f"{name}'s questions or instructions read at about grade "
                                      f"{facts.prompt_grade:g}; the child is {label}."))  # fmt: skip
        if facts.words > budget * 1.2:
            flags.append(Flag("warn", f"{name} has {facts.words} words on the page; a {label} day "
                                      f"is about {budget}."))  # fmt: skip
        if len(facts.skills) >= 3:
            flags.append(Flag("info", f"{name} carries {len(facts.skills)} skills at once."))

    graded = [d.passage_grade for d in days if d.passage_grade is not None]
    if len(graded) >= 2 and graded[-1] - graded[0] >= 2:
        flags.append(Flag("info", f"Reading level climbs through the week (about grade "
                                  f"{graded[0]:g} on {days[0].day} to {graded[-1]:g} by "
                                  f"{days[-1].day})."))  # fmt: skip

    # Skills: what the idea promised, and where each one is taught.
    taught: dict[str, list[str]] = {}
    for d in days:
        for s in d.skills:
            taught.setdefault(s["id"], []).append(d.day)
    wanted = list(dict.fromkeys((planned or []) + list(taught)))
    skill_rows = []
    for sid in wanted:
        info = skills.get(sid, {})
        on = taught.get(sid, [])
        skill_rows.append(
            {"id": sid, "subject": info.get("subject", ""),
             "description": info.get("description", ""), "days": on}
        )  # fmt: skip
        if planned and sid in planned and not on:
            flags.append(Flag("warn", f"{sid} ({info.get('subject') or 'skill'}) was planned but "
                                      "no day teaches it."))  # fmt: skip
        elif len(on) == 1 and len(days) > 1:
            flags.append(Flag("info", f"{sid} ({info.get('subject') or 'skill'}) is taught on "
                                      f"{on[0]} only. Check it fits the theme."))  # fmt: skip
    subjects = sorted({r["subject"] for r in skill_rows if r["subject"]})
    if len(subjects) >= 4:
        flags.append(Flag("info", f"The week spans {len(subjects)} subjects "
                                  f"({', '.join(subjects)}). Check each one fits the theme."))  # fmt: skip

    # What the adult needs.
    guide_text = " ".join(t for _, t in _strings(doc.get("teacher_guide") or {}))
    if grade <= 2 and not READ_ALOUD.search(guide_text):
        flags.append(Flag("warn", f"Nothing tells the adult what to read aloud, and the child is "
                                  f"{label}."))  # fmt: skip
    flags.append(Flag("info", "No time estimates: the week format has no place for them yet."))
    narrator = doc.get("narrator") or ""
    if len(narrator.split()) > 25:
        flags.append(Flag("info", f"The narrator description is {len(narrator.split())} words "
                                  "long."))  # fmt: skip

    # How the authoring run went.
    if run:
        if run.get("status") not in (None, "success"):
            flags.append(Flag("warn", f"Authoring ended as {run.get('status')}."))
        if run.get("uncovered_standards"):
            flags.append(Flag("warn", "The author left these skills out: "
                                      + ", ".join(run["uncovered_standards"])))  # fmt: skip
        if run.get("repairs"):
            flags.append(Flag("info", f"The author needed {run['repairs']} rewrite"
                                      f"{'s' if run['repairs'] != 1 else ''} to pass the checks."))  # fmt: skip

    # Worst first.
    flags.sort(key=lambda f: 0 if f.level == "warn" else 1)
    return Review(
        title=doc.get("title", ""),
        grade=grade,
        word_budget=budget,
        days=days,
        skills=skill_rows,
        subjects=subjects,
        prep_checks=len(doc.get("prep_checks") or []),
        flags=flags,
        run=_run_summary(run),
    )


def _run_summary(run: dict[str, Any] | None) -> dict[str, Any] | None:
    if not run:
        return None
    keys = ("status", "model", "cost_usd", "wall_s", "repairs", "prompt_version", "started_at",
            "final_errors", "topic")  # fmt: skip
    out = {k: run.get(k) for k in keys}
    out["final_errors"] = [str(e)[:200] for e in (run.get("final_errors") or [])][:5]
    return out
