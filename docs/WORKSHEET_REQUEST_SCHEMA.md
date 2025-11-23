# Worksheet Request Schema

This document defines the JSON contract that daily lesson plan generators use to ask the post-processing agent for printable worksheets. Each lesson day may describe zero, one, or many resource requests. When the `resources` field contains a worksheet payload, the orchestrator has enough information to call the helpers in `src/worksheets.py` followed by the renderers in `src/worksheet_renderer.py`.

## Response Envelope

Each entry in `weekly_plan.daily_plan` augments the existing structure with a `resources` object:

```jsonc
{
  "day": "Monday",
  "lesson_plan": { "objective": "..." },
  "standards": [ ... ],
  "focus": "...",
  "resources": {
    "mathWorksheet": { /* MathWorksheetRequest */ },
    "readingWorksheet": { /* ReadingWorksheetRequest */ }
  }
}
```

- `resources` is optional; omit it (or a specific worksheet key) when no artifact is needed to keep responses sparse.
- Additional resource types can be appended later without breaking consumers because each entry is keyed by name.

## MathWorksheetRequest Schema

Shape emitted when the LLM wants `generate_two_operand_math_worksheet` + `render_worksheet_to_image/pdf` to run for that day.

| Field | Type | Required | Description |
| --- | --- | --- | --- |
| `title` | `string` | No | Overrides the worksheet heading (`"Two-Operand Practice"` default mirrors helper signature). |
| `instructions` | `string` | No | Printed under the title. Defaults to `"Solve each problem. Show your work if needed."` |
| `problems` | `TwoOperandProblem[]` | **Yes** | Ordered list of vertical problems (see below). Must contain at least one entry. |
| `metadata` | `object` | No | Forwarded to the `Worksheet.metadata` bag for downstream tracking. |

### `TwoOperandProblem`

```jsonc
{
  "operand_one": 9,
  "operand_two": 4,
  "operator": "+" // accepts "+" or "-"
}
```

- Operands must be integers (the generator coerces strings to `int`, but the LLM should emit canonical numbers).
- `operator` must match the `Operator` enum (`"+"` or `"-"`). Invalid fields cause the helper to raise `ValueError` before rendering.

**Invocation Mapping**

```python
from src.worksheets import generate_two_operand_math_worksheet

worksheet = generate_two_operand_math_worksheet(
    problems=payload["problems"],
    title=payload.get("title", "Two-Operand Practice"),
    instructions=payload.get("instructions", "Solve each problem. Show your work if needed."),
    metadata=payload.get("metadata") or {},
)
```

## ReadingWorksheetRequest Schema

Shape emitted when the LLM wants `generate_reading_comprehension_worksheet` + `render_reading_worksheet_to_image/pdf` to run.

| Field | Type | Required | Description |
| --- | --- | --- | --- |
| `passage_title` | `string` | **Yes** | Printed in the worksheet header (e.g., "The Busy Garden"). |
| `passage` | `string` | **Yes** | Body text of the reading selection. Must be non-empty after trimming whitespace. |
| `questions` | `ReadingQuestion[]` | **Yes** | Ordered set of comprehension prompts (see below). |
| `vocabulary` | `VocabularyEntry[]` | No | Optional list of vocab items for the footer section. |
| `instructions` | `string` | No | Italicized hint under the header. Defaults to the helper's stock instructions. |
| `title` | `string` | No | Logical identifier stored on the worksheet object (not rendered after layout tweaks). |
| `metadata` | `object` | No | Passed through for bookkeeping. |

### `ReadingQuestion`

```jsonc
{
  "prompt": "Why did Lina water the sprouts every day?",
  "response_lines": 3 // optional, defaults to 2 and is clamped to >= 1
}
```

### `VocabularyEntry`

```jsonc
{
  "term": "sprout",
  "definition": "A young plant just starting to grow.",
  "response_lines": 1 // optional; used when no definition is provided
}
```

**Invocation Mapping**

```python
from src.worksheets import generate_reading_comprehension_worksheet

worksheet = generate_reading_comprehension_worksheet(
    passage_title=payload["passage_title"],
    passage=payload["passage"],
    questions=payload["questions"],
    vocabulary=payload.get("vocabulary"),
    instructions=payload.get("instructions", "Read the passage carefully, then answer the questions and review the vocabulary."),
    title=payload.get("title", "Reading Comprehension"),
    metadata=payload.get("metadata") or {},
)
```

## End-to-End Example

```jsonc
{
  "day": "Tuesday",
  "focus": "Apply repeated addition to story problems",
  "lesson_plan": { "objective": "Students connect repeated addition to multiplication." },
  "resources": {
    "mathWorksheet": {
      "title": "Repeated Addition Warm-Up",
      "problems": [
        { "operand_one": 3, "operand_two": 3, "operator": "+" },
        { "operand_one": 4, "operand_two": 4, "operator": "+" }
      ],
      "metadata": { "artifact_label": "warmup" }
    },
    "readingWorksheet": {
      "passage_title": "Seeds on the Windowsill",
      "passage": "Mira planted bean seeds in a jar...",
      "questions": [
        { "prompt": "What routine helped the beans grow?", "response_lines": 3 },
        { "prompt": "How does the story show patience?" }
      ],
      "vocabulary": [
        { "term": "sprout" },
        { "term": "windowsill", "definition": "The flat part at the bottom of a window." }
      ]
    }
  }
}
```

## Implementation Notes

1. Presence of `mathWorksheet` / `readingWorksheet` is the signal that generation should occur; consumers should ignore falsy or empty objects to avoid churn.
2. Both payloads mirror the exact parameters accepted by the underlying helpers, so no additional inference is required before calling `generate_*`.
3. Input validation lives in `src/resource_models.py` (Pydantic models). Use `ResourceRequests.model_validate(...)` to parse any LLM output before invoking worksheet helpers.
4. Pass-through `metadata` fields allow the LLM to tag artifacts ("warmup", "homework", etc.) without affecting the renderers.
5. Post-processing code should render each worksheet to the desired formats (`PNG`, `PDF`, etc.) and attach the resulting artifact URIs back onto the daily plan response for the client.
