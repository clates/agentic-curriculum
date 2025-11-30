"""
feedback_processor.py

Module for processing parent feedback on weekly packets.
Handles mastery feedback (per-standard) and quantity feedback (overall lesson density).
"""

from datetime import UTC, datetime
from typing import Dict, Any
import json


# Feedback rating constants
MASTERY_RATINGS = {"NOT_STARTED", "DEVELOPING", "MASTERED", "BENCHED"}
QUANTITY_RATINGS = {-2, -1, 0, 1, 2}

# Configuration constants
MAX_COOLDOWN_WEEKS = 12
BENCHED_COOLDOWN_WEEKS = 8
ACTIVITY_BIAS_CLAMP = 1.0


def validate_mastery_feedback(mastery_feedback: Dict[str, str]) -> None:
    """
    Validate mastery feedback ratings.

    Args:
        mastery_feedback: Dictionary mapping standard_id to rating

    Raises:
        ValueError: If any rating is invalid
    """
    for standard_id, rating in mastery_feedback.items():
        if rating not in MASTERY_RATINGS:
            raise ValueError(
                f"Invalid mastery rating '{rating}' for standard {standard_id}. "
                f"Must be one of: {MASTERY_RATINGS}"
            )


def validate_quantity_feedback(quantity_feedback: int) -> None:
    """
    Validate quantity feedback rating.

    Args:
        quantity_feedback: Integer rating from -2 to 2

    Raises:
        ValueError: If rating is invalid
    """
    if quantity_feedback not in QUANTITY_RATINGS:
        raise ValueError(
            f"Invalid quantity rating {quantity_feedback}. " f"Must be one of: {QUANTITY_RATINGS}"
        )


def process_mastery_feedback(
    progress_blob: str, mastery_feedback: Dict[str, str], feedback_date: str
) -> str:
    """
    Update progress_blob based on mastery feedback.

    Args:
        progress_blob: JSON string of current progress
        mastery_feedback: Dictionary mapping standard_id to rating
        feedback_date: ISO timestamp of feedback submission

    Returns:
        Updated progress_blob as JSON string
    """
    progress = json.loads(progress_blob)

    # Initialize standard_metadata if it doesn't exist
    if "standard_metadata" not in progress:
        progress["standard_metadata"] = {}

    mastered = set(progress.get("mastered_standards", []))
    developing = set(progress.get("developing_standards", []))

    for standard_id, rating in mastery_feedback.items():
        # Get or create metadata for this standard
        metadata = progress["standard_metadata"].get(standard_id, {})
        if "feedback_history" not in metadata:
            metadata["feedback_history"] = []

        # Add feedback to history
        metadata["feedback_history"].append({"date": feedback_date, "rating": rating})
        metadata["last_seen"] = feedback_date
        metadata["last_feedback"] = rating

        # Update cooldown and lists based on rating
        if rating == "NOT_STARTED":
            # Reset - needs immediate re-introduction
            mastered.discard(standard_id)
            developing.add(standard_id)
            metadata["cooldown_weeks"] = 0

        elif rating == "DEVELOPING":
            # Keep practicing with short cooldown
            mastered.discard(standard_id)
            developing.add(standard_id)
            metadata["cooldown_weeks"] = 1

        elif rating == "MASTERED":
            # Move to mastered list
            developing.discard(standard_id)
            mastered.add(standard_id)

            # Increase cooldown if consecutive mastered
            cooldown = metadata.get("cooldown_weeks", 2)
            if len(metadata["feedback_history"]) >= 2:
                last_two = metadata["feedback_history"][-2:]
                if all(f["rating"] == "MASTERED" for f in last_two):
                    cooldown = min(cooldown + 1, MAX_COOLDOWN_WEEKS)
            metadata["cooldown_weeks"] = cooldown

        elif rating == "BENCHED":
            # Remove from active rotation
            mastered.discard(standard_id)
            developing.discard(standard_id)
            metadata["cooldown_weeks"] = BENCHED_COOLDOWN_WEEKS

        progress["standard_metadata"][standard_id] = metadata

    progress["mastered_standards"] = list(mastered)
    progress["developing_standards"] = list(developing)

    return json.dumps(progress)


def process_quantity_feedback(
    plan_rules_blob: str, quantity_feedback: int, feedback_date: str
) -> str:
    """
    Update plan_rules_blob based on quantity feedback.

    Args:
        plan_rules_blob: JSON string of current plan rules
        quantity_feedback: Integer rating from -2 to 2
        feedback_date: ISO timestamp of feedback submission

    Returns:
        Updated plan_rules_blob as JSON string
    """
    plan_rules = json.loads(plan_rules_blob)

    # Initialize quantity_preferences if it doesn't exist
    if "quantity_preferences" not in plan_rules:
        plan_rules["quantity_preferences"] = {"activity_bias": 0.0, "feedback_history": []}

    prefs = plan_rules["quantity_preferences"]

    # Add to history
    prefs["feedback_history"].append({"date": feedback_date, "rating": quantity_feedback})

    # Update activity bias
    current_bias = prefs.get("activity_bias", 0.0)

    if quantity_feedback == -2:
        current_bias -= 0.3
    elif quantity_feedback == -1:
        current_bias -= 0.15
    elif quantity_feedback == 0:
        # Decay toward 0 when content is "just right"
        current_bias *= 0.9
    elif quantity_feedback == 1:
        current_bias += 0.15
    elif quantity_feedback == 2:
        current_bias += 0.3

    # Clamp to [-1.0, 1.0]
    prefs["activity_bias"] = max(-ACTIVITY_BIAS_CLAMP, min(current_bias, ACTIVITY_BIAS_CLAMP))

    return json.dumps(plan_rules)


def is_standard_eligible(standard_metadata: Dict[str, Any], reference_date: str = None) -> bool:
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
