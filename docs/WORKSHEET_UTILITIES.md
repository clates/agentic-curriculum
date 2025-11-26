# Worksheet Utilities Reference

This document summarizes the two printable worksheet helpers included in the project. Use it as a quick guide when generating math drill sheets or longer reading comprehension activities.

> **Note:** For comprehensive documentation including detailed parameter descriptions and both typical and exotic usage examples, see [WORKSHEET_TYPES.md](./WORKSHEET_TYPES.md).

---

## `generate_two_operand_math_worksheet`

Create a structured worksheet for early math practice (addition/subtraction). The helper normalizes input, enforces valid operators, and produces a `Worksheet` object that can be rendered to Markdown, PNG, or PDF via `render_worksheet_to_image` / `render_worksheet_to_pdf`.

### Parameters

| Name | Type | Default | Description |
| --- | --- | --- | --- |
| `problems` | `Sequence[TwoOperandProblem | dict]` | **required** | Iterable of problems. Dict entries must include `operand_one`, `operand_two`, and `operator` ("+" / "-"). |
| `title` | `str` | "Two-Operand Practice" | Display title printed at the top of the worksheet. |
| `instructions` | `str` | "Solve each problem. Show your work if needed." | Optional instructions printed under the title. |
| `metadata` | `dict | None` | `{}` | Arbitrary metadata bag (not rendered but useful if you store worksheets elsewhere). |

### Callouts

- Problems render vertically with aligned ones/tens columns; no answer key is generated so adults can work through the solutions with learners.
- Rendering helper (`render_worksheet_to_image/pdf`) automatically lays out up to five columns of problems and inserts header fields for Name/Date.
- If you feed dictionaries, the helper casts values to integers and validates operators; invalid entries raise `ValueError`.

---

## `generate_reading_comprehension_worksheet`

Builds a literacy worksheet containing a passage, free-response questions, and vocabulary prompts. Pair the result with `render_reading_worksheet_to_image/pdf` to obtain a classroom-ready handout.

### Parameters

| Name | Type | Default | Description |
| --- | --- | --- | --- |
| `passage_title` | `str` | **required** | Title shown at the top-left of the page. |
| `passage` | `str` | **required** | Main reading selection; can span multiple paragraphs. Blank entries raise `ValueError`. |
| `questions` | `Sequence[ReadingQuestion | dict]` | **required** | Ordered list of comprehension prompts. Each item supports `prompt` and optional `response_lines` (defaults to 2). |
| `vocabulary` | `Sequence[VocabularyEntry | dict] | None` | `[]` | Optional vocabulary list. Entries accept `term`, optional `definition`, and optional `response_lines` (defaults to 1 when definition is omitted). |
| `title` | `str` | "Reading Comprehension" | Logical identifier stored on the object (not printed after latest layout tweaks). |
| `instructions` | `str` | "Read the passage carefully, then answer the questions and review the vocabulary." | Italicized block under the header. |
| `metadata` | `dict | None` | `{}` | Free-form metadata container. |

### Callouts

- The renderer wraps passages and instructions automatically, so multi-paragraph passages and long vocabulary lists simply extend the page height.
- Vocabulary terms print in bold with trailing colons; when no definition is provided, response lines begin immediately after the term so students can fill in meanings.
- Name and Date fields live in the top-right corner; only the passage title appears on the left, keeping the worksheet header compact.
- Questions support configurable response space (number of lines) so you can balance short recall checks with longer writing prompts.

---

## Rendering Helpers

- `render_worksheet_to_image` / `render_worksheet_to_pdf`: Accept a math `Worksheet` instance and produce PNG/PDF artifacts under `artifacts/` or any path you specify.
- `render_reading_worksheet_to_image` / `render_reading_worksheet_to_pdf`: Do the same for `ReadingWorksheet` objects, handling name/date fields, italic instructions, multi-paragraph passages, question blocks, and vocabulary sections automatically.

When generating artifacts, remember to create the `artifacts/` directory or point to another writable location. The renderers will create missing parent folders for you.

---

## Structured LLM Requests

Pair these helpers with the JSON contract in `docs/WORKSHEET_REQUEST_SCHEMA.md` when you want the lesson-planning LLM to ask for printable worksheets. That schema mirrors the signatures of `generate_two_operand_math_worksheet` and `generate_reading_comprehension_worksheet`, so any payload that validates against it can be fed directly into the corresponding generator before rendering.
