# Worksheet Generator Meta-Prompt

Use this prompt to generate high-quality, themed worksheets for a 1st-grade level using the local generation tools.

---

**Role:** You are a curriculum developer for a 1st-grade homeschool student. 

**Task:** Generate a Python script that utilizes an existing worksheet generation framework to create a series of themed writing and reading exercises.

**Themed Topic:** [INSERT TOPIC HERE]

**Passage Requirements:**
- Each worksheet must have a reading passage of at least **two healthy paragraphs**.
- The language must be appropriate for a **1st-grade reading level** (simple sentences, common sight words, descriptive but accessible vocabulary).
- The tone should be engaging and educational, often framed as a "Quest" or "Mission."

**Technical Requirements:**
1. Use the `reading_comprehension` worksheet type.
2. The script must import `WorksheetFactory` from `worksheets.factory`.
3. The script must import `render_reading_worksheet_to_image` and `render_reading_worksheet_to_pdf` from `worksheet_renderer`.
4. Define a `generate_series()` function that creates an output directory and iterates through a list of worksheet data dictionaries.
5. Each worksheet data dictionary should include:
   - `title`: e.g., "[Theme] Quest X: [Title]"
   - `passage_title`: A catchy title for the story.
   - `passage`: Two paragraphs of themed content.
   - `instructions`: Simple instructions for the student.
   - `questions`: 3-4 comprehension questions with `response_lines` (usually 2).
   - `vocabulary`: 3 key terms with definitions.

**Output Format:** Provide a complete, runnable Python script that uses the `./venv/bin/python` environment to generate PDF and PNG files.
