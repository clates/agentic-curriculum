# Database JSON Blob Schemas

This document details the structure of the JSON blobs stored in the `student_profiles` table of `curriculum.db`. These blobs allow for flexible schema evolution without altering the database structure.

## 1. Progress Blob (`progress_blob`)

Tracks the student's mastery of educational standards.

**Structure:**
```json
{
  "mastered_standards": ["string"],
  "developing_standards": ["string"],
  "standard_metadata": {
    "standard_id": {
      "last_seen": "ISO date",
      "last_feedback": "MASTERED|DEVELOPING|NOT_STARTED|BENCHED",
      "cooldown_weeks": 0,
      "feedback_history": [
        {"date": "ISO", "rating": "MASTERED"}
      ]
    }
  }
}
```

**Fields:**
- `mastered_standards` (List[str]): A list of standard IDs that the student has fully mastered.
- `developing_standards` (List[str]): A list of standard IDs that the student is currently working on or has partially learned.
- `standard_metadata` (Dict[str, Object], optional): Per-standard tracking for feedback and cooldown.
  - `last_seen` (str): ISO timestamp when standard was last used in a lesson.
  - `last_feedback` (str): Most recent feedback rating.
  - `cooldown_weeks` (int): Number of weeks before the agent may surface that standard again.
  - `feedback_history` (List[Object]): Array of all feedback submissions for this standard.
  - _Usage_: The weekly plan generator consults `cooldown_weeks` when filtering candidate standards so that recently mastered or benched standards respect parent input.

**Example:**
```json
{
  "mastered_standards": ["VA.MATH.K.1a", "VA.MATH.K.1b"],
  "developing_standards": ["VA.MATH.K.2a"],
  "standard_metadata": {
    "VA.MATH.K.1a": {
      "last_seen": "2025-11-29T20:00:00Z",
      "last_feedback": "MASTERED",
      "cooldown_weeks": 3,
      "feedback_history": [
        {"date": "2025-11-22T10:00:00Z", "rating": "DEVELOPING"},
        {"date": "2025-11-29T10:00:00Z", "rating": "MASTERED"}
      ]
    }
  }
}
```

---

## 2. Plan Rules Blob (`plan_rules_blob`)

Contains configuration and preferences for generating lesson plans. This controls how the AI agent constructs the weekly schedule.

**Structure:**
```json
{
  "allowed_materials": ["string"],
  "review_rules": {
    "no_review_mastered_for_weeks": integer
  },
  "theme_rules": {
    "force_weekly_theme": boolean,
    "theme_subjects": ["string"]
  },
  "parent_notes": "string",
  "quantity_preferences": {
    "activity_bias": 0.0,
    "feedback_history": [
      {"date": "ISO", "rating": -1}
    ]
  }
}
```

**Fields:**
- `allowed_materials` (List[str]): Materials available to the student (e.g., "Crayons", "Blocks"). The AI will restrict lesson plans to use only these items.
- `review_rules` (Object): Configuration for spaced repetition.
    - `no_review_mastered_for_weeks` (int): Number of weeks to wait before re-introducing a mastered standard for review.
- `theme_rules` (Object): Configuration for thematic learning.
    - `force_weekly_theme` (bool): If true, the AI will attempt to unify lessons under a common theme.
    - `theme_subjects` (List[str]): Preferred subjects to center themes around (e.g., "Science", "Art").
- `parent_notes` (str, optional): Free-text notes from parents that the AI should consider (e.g., "Loves dinosaurs", "Visual learner").
- `quantity_preferences` (Object, optional): Configuration for lesson quantity based on parent feedback.
    - `activity_bias` (float): Range -1.0 to 1.0. Negative values reduce activity count, positive increases.
    - `feedback_history` (List[Object]): Array of all quantity feedback submissions.
  - _Usage_: The agent scales the “activities per day” guidance using `activity_bias`, so repeated feedback immediately adjusts future lesson density.

**Example:**
```json
{
  "allowed_materials": ["Crayons", "Paper", "Legos"],
  "review_rules": {
    "no_review_mastered_for_weeks": 3
  },
  "theme_rules": {
    "force_weekly_theme": true,
    "theme_subjects": ["Nature", "Space"]
  },
  "parent_notes": "Student struggles with fine motor skills, prefers large manipulatives.",
  "quantity_preferences": {
    "activity_bias": -0.3,
    "feedback_history": [
      {"date": "2025-11-22T10:00:00Z", "rating": -1},
      {"date": "2025-11-29T10:00:00Z", "rating": -1}
    ]
  }
}
```

---

## 3. Metadata Blob (`metadata_blob`)

Stores personal details and UI-specific information about the student.

**Structure:**
```json
{
  "name": "string",
  "birthday": "string (YYYY-MM-DD)",
  "avatar_url": "string",
  "notes": "string"
}
```

**Fields:**
- `name` (str): The student's display name.
- `birthday` (str): Date of birth in ISO 8601 format (`YYYY-MM-DD`). Used for age-appropriate content adjustments.
- `avatar_url` (str, optional): URL to a profile image.
- `notes` (str, optional): General administrative notes (distinct from `parent_notes` in plan rules).

**Example:**
```json
{
  "name": "Alice Smith",
  "birthday": "2019-05-20",
  "avatar_url": "https://example.com/avatars/alice.png",
  "notes": "Enrolled in Fall 2024 cohort."
}
```
