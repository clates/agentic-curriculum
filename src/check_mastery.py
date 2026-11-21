"""Check results to mastery states (M5.1). Pure: no I/O, no database.

A parent runs the packet's prep checks and ticks Got it / Shaky / Missed for each. This turns
those ticks into one mastery state per standard, using the states the rest of the system already
speaks (MASTERED / DEVELOPING / STRUGGLING; see feedback_processor).

Rules per standard, strongest signal first:
  1. any Missed  -> STRUGGLING   (one miss is enough: no over-crediting)
  2. any Shaky   -> DEVELOPING
  3. all Got it  -> MASTERED, but only when EVERY check for that standard was answered.
     A standard with unanswered checks is left out of the result (no change) rather than credited
     for the part that happened to be ticked.
"""

from __future__ import annotations

from typing import Iterable, Mapping, Protocol

GOT_IT = "got_it"
SHAKY = "shaky"
MISSED = "missed"
CHECK_RESULTS = (GOT_IT, SHAKY, MISSED)

MASTERED = "MASTERED"
DEVELOPING = "DEVELOPING"
STRUGGLING = "STRUGGLING"

_LABELS = {
    "got it": GOT_IT,
    "got_it": GOT_IT,
    "gotit": GOT_IT,
    "shaky": SHAKY,
    "missed": MISSED,
}


class CheckLike(Protocol):
    """What we need from a check: a PrepCheck (src.weekdoc.models) satisfies this."""

    id: str
    standard_id: str


def normalize_result(value: str) -> str:
    """Accept 'Got it' / 'got_it' / 'SHAKY' etc. and return the canonical lowercase value."""
    key = str(value).strip().lower().replace("-", " ")
    if key not in _LABELS:
        raise ValueError(f"Unknown check result {value!r}; expected one of {CHECK_RESULTS}")
    return _LABELS[key]


def map_check_results(checks: Iterable[CheckLike], results: Mapping[str, str]) -> dict[str, str]:
    """Return ``{standard_id: MASTERED | DEVELOPING | STRUGGLING}`` for the answered standards.

    Raises ValueError for a result keyed on a check id that is not in ``checks`` or for a value
    that is not Got it / Shaky / Missed.
    """
    by_id = {c.id: c for c in checks}
    clean: dict[str, str] = {}
    for check_id, value in results.items():
        if check_id not in by_id:
            raise ValueError(f"Result for unknown check {check_id!r}")
        clean[check_id] = normalize_result(value)

    per_standard: dict[str, list[str | None]] = {}
    for check in by_id.values():
        per_standard.setdefault(check.standard_id, []).append(clean.get(check.id))

    out: dict[str, str] = {}
    for standard_id, answers in per_standard.items():
        given = [a for a in answers if a is not None]
        if MISSED in given:
            out[standard_id] = STRUGGLING
        elif SHAKY in given:
            out[standard_id] = DEVELOPING
        elif given and len(given) == len(answers):  # all answered, all Got it
            out[standard_id] = MASTERED
    return out
