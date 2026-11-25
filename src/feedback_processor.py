"""
feedback_processor.py

Module for processing parent feedback on weekly packets.
Handles mastery feedback (per-standard) and quantity feedback (overall lesson density).
"""

from datetime import UTC, datetime
from typing import Any
import json

# Feedback rating constants
MASTERY_RATINGS = {"NOT_STARTED", "DEVELOPING", "MASTERED", "BENCHED", "STRUGGLING"}
QUANTITY_RATINGS = {-2, -1, 0, 1, 2}

# Configuration constants
MAX_COOLDOWN_WEEKS = 12
BENCHED_COOLDOWN_WEEKS = 8
ACTIVITY_BIAS_CLAMP = 1.0


def validate_mastery_feedback(mastery_feedback: dict[str, str]) -> None:
    """ValueError if the feedback is empty or any rating is not a MASTERY_RATINGS value."""
    if not mastery_feedback:
        raise ValueError("Mastery feedback must not be empty")
    for standard_id, rating in mastery_feedback.items():
        if rating not in MASTERY_RATINGS:
            raise ValueError(
                f"Invalid mastery rating '{rating}' for standard {standard_id}. "
                f"Must be one of: {MASTERY_RATINGS}"
            )


def validate_quantity_feedback(quantity_feedback: int) -> None:
    """ValueError unless the rating is an integer from -2 to 2."""
    if quantity_feedback not in QUANTITY_RATINGS:
        raise ValueError(
            f"Invalid quantity rating {quantity_feedback}. " f"Must be one of: {QUANTITY_RATINGS}"
        )


# Cooldown a freshly MASTERED standard gets, and the one-week bump for repeated mastery.
DEFAULT_MASTERED_COOLDOWN_WEEKS = 2


def _base_snapshot(progress: dict[str, Any], standard_id: str) -> dict[str, Any]:
    """Capture what we knew about a standard before any packet feedback touched it."""
    existing = progress["standard_metadata"].get(standard_id)
    if standard_id in progress.get("mastered_standards", []):
        state = "MASTERED"
    elif standard_id in progress.get("developing_standards", []):
        state = "DEVELOPING"
    else:
        state = None
    existing = existing or {}
    return {
        "state": state,
        "cooldown_weeks": existing.get("cooldown_weeks"),
        "last_seen": existing.get("last_seen"),
        "last_feedback": existing.get("last_feedback"),
        "had_metadata": bool(existing),
        # Untagged history from before packet tagging is already folded into this snapshot.
        "skip": len(existing.get("feedback_history", [])),
        "prev_rating": (existing.get("feedback_history") or [{}])[-1].get("rating"),
    }


def _replay(base: dict[str, Any], history: list[dict[str, Any]]) -> dict[str, Any]:
    """Derive a standard's state purely from its pre-feedback base plus ordered history."""
    state = base.get("state")
    cooldown = base.get("cooldown_weeks")
    previous = base.get("prev_rating")
    for entry in history:
        rating = entry["rating"]
        if rating in ("NOT_STARTED", "STRUGGLING"):
            state, cooldown = "DEVELOPING", 0  # needs immediate re-introduction
        elif rating == "DEVELOPING":
            # Shaky: keep practising, and do not hide it. Spaced review is the job of review_due().
            state, cooldown = "DEVELOPING", 0
        elif rating == "MASTERED":
            if previous == "MASTERED" and cooldown:
                cooldown = min(cooldown + 1, MAX_COOLDOWN_WEEKS)
            else:
                cooldown = DEFAULT_MASTERED_COOLDOWN_WEEKS
            state = "MASTERED"
        elif rating == "BENCHED":
            state, cooldown = None, BENCHED_COOLDOWN_WEEKS
        previous = rating
    return {"state": state, "cooldown_weeks": cooldown}


def _recompute_standard(progress: dict[str, Any], standard_id: str) -> None:
    """Rewrite one standard's metadata and list membership from base + history."""
    meta = progress["standard_metadata"][standard_id]
    base = meta["base"]
    skip = base.get("skip", 0)
    full = meta.get("feedback_history", [])
    # Replay in date order (stable), so editing an older packet slots back where it belongs.
    history = sorted(full[skip:], key=lambda e: e["date"])
    meta["feedback_history"] = full[:skip] + history
    mastered = set(progress.get("mastered_standards", []))
    developing = set(progress.get("developing_standards", []))
    mastered.discard(standard_id)
    developing.discard(standard_id)

    if not history:  # fully reverted: restore exactly what was there before
        derived = {"state": base["state"], "cooldown_weeks": base["cooldown_weeks"]}
        last_seen, last_feedback = base["last_seen"], base["last_feedback"]
    else:
        derived = _replay(base, history)
        last_seen, last_feedback = history[-1]["date"], history[-1]["rating"]

    if derived["state"] == "MASTERED":
        mastered.add(standard_id)
    elif derived["state"] == "DEVELOPING":
        developing.add(standard_id)
    progress["mastered_standards"] = sorted(mastered)
    progress["developing_standards"] = sorted(developing)

    if not history and not base["had_metadata"]:  # nothing existed before: leave no trace
        del progress["standard_metadata"][standard_id]
        return
    if not history:
        meta.pop("base", None)  # back to the pre-feedback shape; a later apply re-snapshots
    meta["cooldown_weeks"] = derived["cooldown_weeks"]
    meta["last_seen"] = last_seen
    meta["last_feedback"] = last_feedback
    if meta["cooldown_weeks"] is None:
        del meta["cooldown_weeks"]
    if last_seen is None:
        del meta["last_seen"]
    if last_feedback is None:
        del meta["last_feedback"]


def _load_progress(progress_blob: str) -> dict[str, Any]:
    progress = json.loads(progress_blob)
    progress.setdefault("standard_metadata", {})
    progress.setdefault("mastered_standards", [])
    progress.setdefault("developing_standards", [])
    return progress


def _packet_ratings(progress: dict[str, Any], packet_id: str) -> dict[str, str]:
    out: dict[str, str] = {}
    for sid, meta in progress["standard_metadata"].items():
        for entry in meta.get("feedback_history", []):
            if entry.get("packet_id") == packet_id:
                out[sid] = entry["rating"]
    return out


def _revert_in_place(progress: dict[str, Any], packet_id: str) -> None:
    for sid in list(progress["standard_metadata"]):
        meta = progress["standard_metadata"][sid]
        history = meta.get("feedback_history", [])
        kept = [e for e in history if e.get("packet_id") != packet_id]
        if len(kept) == len(history):
            continue
        meta["feedback_history"] = kept
        if "base" in meta:
            _recompute_standard(progress, sid)


def revert_mastery_feedback(progress_blob: str, packet_id: str) -> str:
    """Remove everything one packet's feedback did to the progress blob (exact undo)."""
    progress = _load_progress(progress_blob)
    _revert_in_place(progress, packet_id)
    return json.dumps(progress)


def process_mastery_feedback(
    progress_blob: str,
    mastery_feedback: dict[str, str],
    feedback_date: str,
    packet_id: str | None = None,
) -> str:
    """Apply per-standard mastery ratings to a progress blob and return the new blob.

    With a ``packet_id`` the update is idempotent and editable: history entries are tagged with
    the packet, an exact repeat changes nothing, and a changed resubmit first reverts the packet's
    earlier effect and then replays, so nothing is counted twice. Without a ``packet_id`` the
    feedback is applied as an untagged one-off (it cannot be reverted).
    """
    progress = _load_progress(progress_blob)

    if packet_id is not None:
        if _packet_ratings(progress, packet_id) == dict(mastery_feedback):
            return progress_blob  # exact repeat: nothing to do
        _revert_in_place(progress, packet_id)

    for standard_id, rating in mastery_feedback.items():
        meta = progress["standard_metadata"].get(standard_id)
        if meta is None or "base" not in meta:
            base = _base_snapshot(progress, standard_id)
            meta = progress["standard_metadata"].setdefault(standard_id, {})
            meta["base"] = base
        meta.setdefault("feedback_history", [])
        entry = {"date": feedback_date, "rating": rating}
        if packet_id is not None:
            entry["packet_id"] = packet_id
        meta["feedback_history"].append(entry)
        _recompute_standard(progress, standard_id)

    return json.dumps(progress)


# How far each quantity rating moves activity_bias; 0 ("just right") instead decays it toward 0.
_BIAS_STEP = {-2: -0.3, -1: -0.15, 1: 0.15, 2: 0.3}
_JUST_RIGHT_DECAY = 0.9


def _clamp_bias(bias: float) -> float:
    """Clamp to [-1.0, 1.0] and round to avoid floating-point drift."""
    return round(max(-ACTIVITY_BIAS_CLAMP, min(bias, ACTIVITY_BIAS_CLAMP)), 6)


def process_quantity_feedback(
    plan_rules_blob: str, quantity_feedback: int, feedback_date: str
) -> str:
    """Record a quantity rating (-2..2) and nudge the plan's activity_bias accordingly."""
    plan_rules = json.loads(plan_rules_blob)
    if "quantity_preferences" not in plan_rules:
        plan_rules["quantity_preferences"] = {"activity_bias": 0.0, "feedback_history": []}
    prefs = plan_rules["quantity_preferences"]
    prefs["feedback_history"].append({"date": feedback_date, "rating": quantity_feedback})

    bias = prefs.get("activity_bias", 0.0)
    if quantity_feedback == 0:
        bias *= _JUST_RIGHT_DECAY
    elif quantity_feedback in _BIAS_STEP:
        bias += _BIAS_STEP[quantity_feedback]
    prefs["activity_bias"] = _clamp_bias(bias)
    return json.dumps(plan_rules)


def reverse_quantity_feedback(plan_rules_blob: str, old_quantity_feedback: int) -> str:
    """Undo a previously applied quantity rating's effect on activity_bias (used on edits)."""
    plan_rules = json.loads(plan_rules_blob)
    if "quantity_preferences" not in plan_rules:
        return plan_rules_blob
    prefs = plan_rules["quantity_preferences"]

    bias = prefs.get("activity_bias", 0.0)
    if old_quantity_feedback == 0:
        bias = round(bias / _JUST_RIGHT_DECAY, 6) if bias != 0 else 0.0
    elif old_quantity_feedback in _BIAS_STEP:
        bias -= _BIAS_STEP[old_quantity_feedback]
    prefs["activity_bias"] = _clamp_bias(bias)
    return json.dumps(plan_rules)


def is_standard_eligible(standard_metadata: dict[str, Any], reference_date: str = None) -> bool:
    """
    Check if a standard is eligible to appear in a lesson based on cooldown.

    Args:
        standard_metadata: Metadata for a specific standard
        reference_date: ISO date string to check against (defaults to today)

    Returns:
        True if standard is eligible (cooldown expired), False otherwise
    """
    if not standard_metadata:
        return True

    last_seen = standard_metadata.get("last_seen")
    cooldown_weeks = standard_metadata.get("cooldown_weeks", 0)

    if not last_seen or cooldown_weeks == 0:
        return True

    if reference_date is None:
        reference_date = datetime.now(UTC).isoformat()

    last_seen_dt = datetime.fromisoformat(last_seen.replace("Z", "+00:00"))
    reference_dt = datetime.fromisoformat(reference_date.replace("Z", "+00:00"))

    weeks_since_seen = (reference_dt - last_seen_dt).days / 7.0

    return weeks_since_seen >= cooldown_weeks
