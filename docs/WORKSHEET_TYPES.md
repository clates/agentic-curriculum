# Worksheet Types Reference

This document provides comprehensive documentation for each worksheet type supported by the system. It includes descriptions, parameter details, and both typical and exotic usage examples.

---

## Table of Contents

1. [Two-Operand Math Worksheet (`two_operand`)](#two-operand-math-worksheet)
2. [Reading Comprehension Worksheet (`reading_comprehension`)](#reading-comprehension-worksheet)
3. [Using the WorksheetFactory](#using-the-worksheetfactory)

---

## Two-Operand Math Worksheet

**Type identifier:** `two_operand`  
**Class:** `MathWorksheet` (alias: `Worksheet`)  
**Generator:** `generate_two_operand_math_worksheet`

### Description

Creates printable math worksheets for early elementary grades (K-2) featuring vertical addition and subtraction problems. Problems are displayed in a traditional stacked format with operands aligned by place value and a horizontal line for students to write their answers.

### Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `problems` | `List[TwoOperandProblem \| dict]` | **Yes** | — | List of math problems to include. Each problem requires `operand_one`, `operand_two`, and `operator`. |
| `title` | `str` | No | `"Two-Operand Practice"` | Title displayed at the top of the worksheet. |
| `instructions` | `str` | No | `"Solve each problem. Show your work if needed."` | Instructions printed below the title. |
| `metadata` | `dict \| None` | No | `{}` | Arbitrary metadata for tracking (not rendered). |

### Problem Structure

Each problem in the `problems` list requires:

| Field | Type | Description |
|-------|------|-------------|
| `operand_one` | `int` | The top number in the vertical problem. |
| `operand_two` | `int` | The bottom number in the vertical problem. |
| `operator` | `str` | Either `"+"` for addition or `"-"` for subtraction. |

### Typical Usage Examples

#### Example 1: Basic Addition Practice

A simple worksheet for kindergarten addition within 10.

```python
from src.worksheets import generate_two_operand_math_worksheet

worksheet = generate_two_operand_math_worksheet(
    problems=[
        {"operand_one": 3, "operand_two": 2, "operator": "+"},
        {"operand_one": 5, "operand_two": 4, "operator": "+"},
        {"operand_one": 6, "operand_two": 1, "operator": "+"},
        {"operand_one": 2, "operand_two": 7, "operator": "+"},
    ],
    title="Addition Facts to 10",
    instructions="Add the numbers. Write your answer on the line.",
)
```

**JSON payload:**
```json
{
  "type": "two_operand",
  "title": "Addition Facts to 10",
  "instructions": "Add the numbers. Write your answer on the line.",
  "problems": [
    {"operand_one": 3, "operand_two": 2, "operator": "+"},
    {"operand_one": 5, "operand_two": 4, "operator": "+"},
    {"operand_one": 6, "operand_two": 1, "operator": "+"},
    {"operand_one": 2, "operand_two": 7, "operator": "+"}
  ]
}
```

#### Example 2: Subtraction Practice

First-grade subtraction within 20.

```python
worksheet = generate_two_operand_math_worksheet(
    problems=[
        {"operand_one": 15, "operand_two": 7, "operator": "-"},
        {"operand_one": 18, "operand_two": 9, "operator": "-"},
        {"operand_one": 12, "operand_two": 5, "operator": "-"},
    ],
    title="Subtraction Within 20",
)
```

#### Example 3: Mixed Operations

Combining addition and subtraction for variety.

```python
worksheet = generate_two_operand_math_worksheet(
    problems=[
        {"operand_one": 8, "operand_two": 5, "operator": "+"},
        {"operand_one": 14, "operand_two": 6, "operator": "-"},
        {"operand_one": 7, "operand_two": 9, "operator": "+"},
        {"operand_one": 17, "operand_two": 8, "operator": "-"},
    ],
    title="Mixed Practice",
    instructions="Solve each problem. Pay attention to the operation sign!",
)
```

### Exotic Usage Examples

#### Example 4: Large Numbers for Advanced Practice

Two-digit addition for second graders working on regrouping.

```python
worksheet = generate_two_operand_math_worksheet(
    problems=[
        {"operand_one": 47, "operand_two": 35, "operator": "+"},
        {"operand_one": 68, "operand_two": 24, "operator": "+"},
        {"operand_one": 89, "operand_two": 56, "operator": "+"},
    ],
    title="Two-Digit Addition with Regrouping",
    instructions="Add carefully. Regroup when the ones column is 10 or more.",
    metadata={"skill": "regrouping", "difficulty": "advanced"},
)
```

#### Example 5: Themed Worksheet with Metadata

Holiday-themed worksheet with tracking metadata.

```python
worksheet = generate_two_operand_math_worksheet(
    problems=[
        {"operand_one": 10, "operand_two": 2, "operator": "+"},
        {"operand_one": 12, "operand_two": 3, "operator": "+"},
    ],
    title="🎄 Holiday Math Fun 🎄",
    instructions="Santa needs help counting presents! Solve each problem.",
    metadata={
        "theme": "winter_holiday",
        "artifact_label": "holiday_math",
        "week_of": "2024-12-16",
    },
)
```

#### Example 6: Programmatic Problem Generation

Generating problems algorithmically for a timed drill.

```python
import random

# Generate 20 random addition problems within 20
problems = [
    {
        "operand_one": random.randint(1, 10),
        "operand_two": random.randint(1, 10),
        "operator": "+",
    }
    for _ in range(20)
]

worksheet = generate_two_operand_math_worksheet(
    problems=problems,
    title="Speed Drill: Addition",
    instructions="Complete as many problems as you can in 3 minutes!",
    metadata={"drill_type": "timed", "time_limit_seconds": 180},
)
```

---

## Reading Comprehension Worksheet

**Type identifier:** `reading_comprehension`  
**Class:** `ReadingWorksheet`  
**Generator:** `generate_reading_comprehension_worksheet`

### Description

Creates reading comprehension worksheets featuring a passage, comprehension questions, and optional vocabulary section. Designed for elementary literacy practice, these worksheets support multi-paragraph passages, configurable response space, and vocabulary with or without provided definitions.

### Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `passage_title` | `str` | **Yes** | — | Title of the reading passage, displayed prominently. |
| `passage` | `str` | **Yes** | — | The reading text. Supports multiple paragraphs. |
| `questions` | `List[ReadingQuestion \| dict]` | **Yes** | — | Comprehension questions with configurable response lines. |
| `vocabulary` | `List[VocabularyEntry \| dict] \| None` | No | `[]` | Optional vocabulary words with optional definitions. |
| `title` | `str` | No | `"Reading Comprehension"` | Worksheet title (stored in metadata). |
| `instructions` | `str` | No | `"Read the passage carefully, then answer the questions and review the vocabulary."` | Instructions displayed in italics. |
| `metadata` | `dict \| None` | No | `{}` | Arbitrary metadata for tracking. |

### Question Structure

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `prompt` | `str` | **Yes** | — | The question text. |
| `response_lines` | `int` | No | `2` | Number of lines provided for the answer (minimum 1). |

### Vocabulary Entry Structure

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `term` | `str` | **Yes** | — | The vocabulary word. |
| `definition` | `str \| None` | No | `None` | Optional definition. If omitted, response lines are provided. |
| `response_lines` | `int` | No | `1` | Lines for student-written definition (when no definition provided). |

### Typical Usage Examples

#### Example 1: Basic Reading Comprehension

A simple passage with straightforward questions.

```python
from src.worksheets import generate_reading_comprehension_worksheet

worksheet = generate_reading_comprehension_worksheet(
    passage_title="The Busy Squirrel",
    passage="""
    Sam the squirrel was very busy. He ran up and down the oak tree all day.
    He was collecting acorns for winter. Sam hid the acorns in a hole near
    the roots of the tree. By evening, Sam was tired but happy.
    """,
    questions=[
        {"prompt": "What was Sam doing all day?"},
        {"prompt": "Where did Sam hide the acorns?"},
        {"prompt": "How did Sam feel at the end of the day?"},
    ],
)
```

**JSON payload:**
```json
{
  "type": "reading_comprehension",
  "passage_title": "The Busy Squirrel",
  "passage": "Sam the squirrel was very busy...",
  "questions": [
    {"prompt": "What was Sam doing all day?"},
    {"prompt": "Where did Sam hide the acorns?"},
    {"prompt": "How did Sam feel at the end of the day?"}
  ]
}
```

#### Example 2: With Vocabulary Section

Adding vocabulary words with definitions.

```python
worksheet = generate_reading_comprehension_worksheet(
    passage_title="A Day at the Beach",
    passage="""
    Maria loved the beach. She built sandcastles near the shore.
    The waves gently lapped at her feet. Seagulls flew overhead,
    calling to each other. It was a perfect summer day.
    """,
    questions=[
        {"prompt": "What did Maria build at the beach?"},
        {"prompt": "Describe the waves in the story."},
    ],
    vocabulary=[
        {"term": "shore", "definition": "The land along the edge of the water."},
        {"term": "lapped", "definition": "Gently touched or washed against."},
    ],
)
```

#### Example 3: Questions with Varied Response Space

Adjusting line count for different question types.

```python
worksheet = generate_reading_comprehension_worksheet(
    passage_title="The Lost Puppy",
    passage="A small brown puppy wandered through the park...",
    questions=[
        {"prompt": "Who is the main character?", "response_lines": 1},
        {"prompt": "What problem did the puppy face?", "response_lines": 2},
        {"prompt": "Write about a time you helped an animal.", "response_lines": 5},
    ],
)
```

### Exotic Usage Examples

#### Example 4: Multi-Paragraph Literary Passage

A longer passage for advanced readers with inferential questions.

```python
worksheet = generate_reading_comprehension_worksheet(
    passage_title="The Secret Garden",
    passage="""
    Maya discovered the old garden behind the stone wall on a rainy Tuesday.
    The gate was hidden by ivy, and the hinges creaked when she pushed it open.

    Inside, flowers grew wild among the weeds. A stone path, nearly invisible
    under years of leaves, wound through the center. Maya felt like she had
    stepped into another world.

    She decided to keep the garden a secret. Every day after school, she would
    come to pull weeds and plant new seeds. Slowly, the garden began to bloom again.
    """,
    questions=[
        {"prompt": "How did Maya find the garden?", "response_lines": 2},
        {"prompt": "What details show the garden had been abandoned?", "response_lines": 3},
        {"prompt": "Why do you think Maya kept the garden a secret?", "response_lines": 4},
        {"prompt": "Predict what might happen next in the story.", "response_lines": 4},
    ],
    vocabulary=[
        {"term": "discovered", "definition": "Found something for the first time."},
        {"term": "invisible"},  # Student defines
        {"term": "bloom", "definition": "To produce flowers."},
    ],
    instructions="Read the passage carefully. Use evidence from the text to support your answers.",
    metadata={"genre": "fiction", "reading_level": "3rd_grade"},
)
```

#### Example 5: Vocabulary-Focused Worksheet

Heavy emphasis on vocabulary building with student-defined terms.

```python
worksheet = generate_reading_comprehension_worksheet(
    passage_title="The Water Cycle",
    passage="""
    Water is always moving on Earth. The sun heats water in oceans and lakes.
    The water evaporates and rises into the sky. High up, it condenses into
    clouds. When clouds get heavy, precipitation falls as rain or snow.
    The water flows back to oceans, and the cycle begins again.
    """,
    questions=[
        {"prompt": "What causes water to evaporate?", "response_lines": 2},
        {"prompt": "Explain the water cycle in your own words.", "response_lines": 5},
    ],
    vocabulary=[
        {"term": "evaporates", "response_lines": 2},
        {"term": "condenses", "response_lines": 2},
        {"term": "precipitation", "response_lines": 2},
        {"term": "cycle", "response_lines": 2},
    ],
    instructions="Read about the water cycle. Then define each vocabulary word using context clues from the passage.",
    title="Science Reading: Water Cycle",
)
```

#### Example 6: Non-Fiction with Comprehension Levels

Bloom's taxonomy-aligned questions from recall to synthesis.

```python
worksheet = generate_reading_comprehension_worksheet(
    passage_title="Honeybees at Work",
    passage="""
    Honeybees are amazing insects. A single hive can have up to 60,000 bees.
    Each bee has a job. Worker bees collect nectar from flowers. Guard bees
    protect the hive entrance. The queen bee lays eggs.

    Bees communicate through dance. When a worker finds flowers, it returns
    to the hive and does a special wiggle dance. This tells other bees where
    to find the food.
    """,
    questions=[
        # Remember
        {"prompt": "How many bees can live in one hive?", "response_lines": 1},
        # Understand  
        {"prompt": "What are three jobs bees can have?", "response_lines": 2},
        # Apply
        {"prompt": "If you were a bee, which job would you want? Why?", "response_lines": 3},
        # Analyze
        {"prompt": "Why is the wiggle dance important for the hive?", "response_lines": 3},
        # Create
        {"prompt": "Design your own dance to share a message. Describe it.", "response_lines": 4},
    ],
    vocabulary=[
        {"term": "hive", "definition": "A structure where bees live together."},
        {"term": "nectar", "definition": "A sweet liquid in flowers that bees collect."},
        {"term": "communicate"},
    ],
    metadata={
        "subject": "science",
        "topic": "insects",
        "question_levels": ["remember", "understand", "apply", "analyze", "create"],
    },
)
```

#### Example 7: Bilingual Support via Metadata

Using metadata to track language learning contexts.

```python
worksheet = generate_reading_comprehension_worksheet(
    passage_title="Mi Familia",
    passage="""
    My family is big. I have two brothers and one sister. My grandmother
    lives with us. She tells the best stories. On Sundays, we all cook
    together and eat a big meal.
    """,
    questions=[
        {"prompt": "How many siblings does the narrator have?", "response_lines": 1},
        {"prompt": "What does the family do on Sundays?", "response_lines": 2},
        {"prompt": "Draw a picture of your family on the back of this paper.", "response_lines": 1},
    ],
    vocabulary=[
        {"term": "siblings", "definition": "Brothers and sisters."},
        {"term": "narrator"},
    ],
    metadata={
        "language_focus": "ELL",
        "home_language_support": "Spanish",
        "theme": "family",
    },
)
```

---

## Using the WorksheetFactory

The `WorksheetFactory` provides a unified interface for creating worksheets from JSON payloads, making it easy to dispatch to the correct generator based on type.

### Basic Usage

```python
from src.worksheets import WorksheetFactory

# Create a math worksheet
math_ws = WorksheetFactory.create("two_operand", {
    "title": "Quick Practice",
    "problems": [
        {"operand_one": 5, "operand_two": 3, "operator": "+"},
    ],
})

# Create a reading worksheet
reading_ws = WorksheetFactory.create("reading_comprehension", {
    "passage_title": "My Story",
    "passage": "Once upon a time...",
    "questions": [{"prompt": "What happened?"}],
})
```

### Checking Supported Types

```python
from src.worksheets import WorksheetFactory

# Get list of supported worksheet types
supported = WorksheetFactory.get_supported_types()
print(supported)  # ['two_operand', 'reading_comprehension']
```

### Registering Custom Types

The factory supports extension through registration:

```python
from src.worksheets import WorksheetFactory, BaseWorksheet

def create_custom_worksheet(payload: dict) -> BaseWorksheet:
    # Custom creation logic
    ...

WorksheetFactory.register("custom_type", create_custom_worksheet)
```

---

## Rendering Worksheets

After creating a worksheet, use the rendering functions to generate printable files:

```python
from src.worksheets import generate_two_operand_math_worksheet
from src.worksheet_renderer import render_worksheet_to_pdf, render_worksheet_to_image

worksheet = generate_two_operand_math_worksheet(
    problems=[{"operand_one": 3, "operand_two": 2, "operator": "+"}],
)

# Generate PNG
render_worksheet_to_image(worksheet, "output/worksheet.png")

# Generate PDF
render_worksheet_to_pdf(worksheet, "output/worksheet.pdf")
```

For reading worksheets:

```python
from src.worksheets import generate_reading_comprehension_worksheet
from src.worksheet_renderer import (
    render_reading_worksheet_to_pdf,
    render_reading_worksheet_to_image,
)

worksheet = generate_reading_comprehension_worksheet(
    passage_title="Story",
    passage="Content...",
    questions=[{"prompt": "Question?"}],
)

render_reading_worksheet_to_image(worksheet, "output/reading.png")
render_reading_worksheet_to_pdf(worksheet, "output/reading.pdf")
```

---

## Error Handling

Both generators perform validation and raise appropriate exceptions:

| Error | Cause |
|-------|-------|
| `ValueError("At least one problem is required")` | Empty problems list for math worksheet. |
| `ValueError("Missing required key: ...")` | Problem dict missing required field. |
| `ValueError("At least one reading question is required")` | Empty questions list for reading worksheet. |
| `ValueError("Reading passage text is required")` | Empty or whitespace-only passage. |
| `ValueError("ReadingQuestion requires a prompt")` | Question without prompt text. |
| `ValueError("VocabularyEntry requires a term")` | Vocabulary entry without term. |

---

## Best Practices

1. **Keep problems age-appropriate**: Match operand sizes to grade level expectations.
2. **Use metadata for tracking**: Tag worksheets with themes, skills, or dates for organization.
3. **Vary question complexity**: Mix recall, comprehension, and open-ended questions.
4. **Balance vocabulary**: Include both defined terms (for reference) and undefined terms (for practice).
5. **Test with rendering**: Always render to PNG/PDF to verify layout before distribution.
