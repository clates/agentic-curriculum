# Worksheet Generation Guide (AGENTS.md)

This document outlines the architecture, constraints, and "Instructional Pair" strategy used to generate high-fidelity educational worksheets for various age groups in this repository.

---

## 1. Core Architecture
The system is built on a modular Python framework:
*   **`src/worksheets/`**: Logic for specific data structures (e.g., `MatchingWorksheet`, `ReadingWorksheet`).
*   **`src/worksheets/factory.py`**: A unified entry point to create worksheet objects from dictionary payloads. Required for PIL rendering; **not needed** for HTML rendering.
*   **`src/worksheet_renderer.py`**: The visual (PIL/Pillow) engine. Use for image-heavy types (handwriting, pixel copy, alphabet) or when PNG/PDF output is explicitly needed. Render functions follow the pattern `render_X_to_image(ws, path)` / `render_X_to_pdf(ws, path)`.
*   **`src/worksheet_html_renderer.py`**: The preferred engine for printable worksheet packets. Produces clean, browser-printable HTML with day-colour theming. Two key functions:
    *   `render_worksheet_html(kind, data, day_label) -> str | None` — renders one worksheet to an HTML fragment. `kind` uses **camelCase** strings (e.g. `"readingWorksheet"`, `"featureMatrixWorksheet"`). `data` is a plain dict — **do not pass a WorksheetFactory object**.
    *   `build_print_packet_html(pages, packet_title) -> str` — assembles a list of `(day_label, fragment)` tuples into a single printable HTML document that auto-opens the browser print dialog on load.

### Choosing a renderer
| Situation | Use |
|-----------|-----|
| Single printable packet for a student | **HTML** (`render_worksheet_html` + `build_print_packet_html`) |
| Pixel art, handwriting, or alphabet sheets | PIL (`worksheet_renderer.py`) |
| PNG/PDF files needed for individual download | PIL |
| Embedding in the API weekly-plan flow | HTML (agent.py already uses this) |

---

## 2. Instructional Strategies
### The "Instructional Pair" Pattern (Ages 5+)
For complex subjects (like Civics or Government), always generate two related pages:
1.  **Instructional Reading**: A high-level passage explaining concepts, including vocabulary definitions and comprehension questions.
2.  **Application Activity**: A corresponding classification or comparison sheet (Venn Diagram, Feature Matrix, or Tree Map) that uses terms from the reading.

### Phonics Constraint (Ages 3-4)
Stick strictly to **CVC** (Cat, Pig), **CCVC** (Snow, Frog), and **CVCC** (Raft, Bird) words. Words can be "flexibly applied" to character art (e.g., using **CAT** for Simba) to maintain engagement while sticking to decodable patterns.

---

## 3. Supported Worksheet Types

20 types are registered in `WorksheetFactory`. The table below shows the factory key (snake_case), the HTML renderer kind (camelCase, for `render_worksheet_html`), and which renderer supports each type.

| Factory key | HTML kind | HTML | PIL |
|-------------|-----------|------|-----|
| `reading_comprehension` | `readingWorksheet` | ✓ | ✓ |
| `feature_matrix` | `featureMatrixWorksheet` | ✓ | ✓ |
| `tree_map` | `treeMapWorksheet` | ✓ | ✓ |
| `odd_one_out` | `oddOneOutWorksheet` | ✓ | ✓ |
| `matching` | `matchingWorksheet` | ✓ | ✓ |
| `cause_effect` | `causeEffectWorksheet` | ✓ | ✓ |
| `frayer_model` | `frayerModelWorksheet` | ✓ | ✓ |
| `word_sort` | `wordSortWorksheet` | ✓ | ✓ |
| `writing_scaffold` | `writingScaffoldWorksheet` | ✓ | ✓ |
| `t_chart` | `tChartWorksheet` | ✓ | ✓ |
| `handwriting` | — | — | ✓ |
| `pixel_copy` | — | — | ✓ |
| `alphabet` | — | — | ✓ |
| `fill_in_the_blank` | — | — | ✓ |
| `sequencing` | — | — | ✓ |
| `venn_diagram` | — | — | ✓ |
| `story_map` | — | — | ✓ |
| `number_line` | — | — | ✓ |
| `labeled_diagram` | — | — | ✓ |
| `two_operand` | — | — | ✓ |

### Critical data-format difference: `feature_matrix`
The **HTML renderer** expects `items` as a **list of plain strings** (row labels). The **PIL factory** expects `items` as a list of dicts with `name` and `checked_properties` keys. Mixing these up produces broken output with no error.

```python
# HTML path — items are strings
add("featureMatrixWorksheet", {
    "items": ["Dog", "Fish", "Tree"],
    "properties": ["Needs Food", "Needs Water"],
})

# PIL path — items are dicts
WorksheetFactory.create("feature_matrix", {
    "items": [{"name": "Dog", "checked_properties": ["Needs Food"]}],
    "properties": ["Needs Food", "Needs Water"],
    "show_answers": False,
})
```

---

## 4. Pedagogical Best Practices

### "Let's Discuss" Discussion Question
Add one oral-discussion question at the **end** of every student-facing `reading_comprehension` worksheet. Use `response_lines: 0` so no write-in lines are rendered — this is a spoken activity led by the parent/teacher. The prompt should pose a tricky or surprising real-world case that applies the day's concept.

```python
{"prompt": "LET'S DISCUSS: Finn found a seed. Is it alive? What about a dead leaf?", "response_lines": 0}
```

### Word Bank / Vocabulary Shuffling
Always shuffle word banks so the display order does not match the answer key or the passage order. This applies to:
- `word_bank` lists in `tree_map` and `word_sort` worksheets
- Answer-order lists in `fill_in_the_blank`
- `vocabulary` term order in `reading_comprehension`

### Outdoor / Hands-On Activity Integration
For science or nature topics, include a brief teacher-led outdoor observation activity in the `instructions` field of each reading worksheet. Frame it as a before/during/after activity tied to that day's concept (e.g., "Before reading: go outside and find 3 living things and 3 nonliving things").

### Character Hook (Consistent Narrator)
For multi-day series, a recurring character grounding each passage improves engagement and continuity. Introduce the character explicitly on Day 1 with a "meet X" sentence before the science content begins. The character should be a living thing themselves when the topic is biology (e.g., Finn the Frog for a "What Is Life?" unit). See `generate_biomes_week_series.py` (Minecraft Steve) and `generate_life_week_series.py` (Finn the Frog) as examples.

---

## 5. The "Great Worksheet" Prompt Template
When requesting new worksheets, providing this context ensures the best results:

> **Topic**: [e.g., Ancient Egypt, Planets, Multiplication]  
> **Target Audience**: [Age & Reading Level, e.g., 6-year-old, 2nd-grade reading level]  
> **Set Structure**: [e.g., Instructional Pair: Reading + Feature Matrix]  
> **Constraint**: [e.g., Only use CVC words / Include the Three Laws of Motion]  
> **Aesthetic**: [e.g., Character hook: Finn the Frog / Pixel Art]  
> **Output Format**: [e.g., Single printable HTML packet / Individual PNG+PDF files]  
> **Educational Goal**: [e.g., Identify the difference between a planet and a star]

---

## 6. Technical Deployment
Run generation scripts from the project root:
```bash
python3 scripts/generate_[theme]_series.py
```
(If a `venv/` exists: `venv/bin/python3 scripts/generate_[theme]_series.py`)

**HTML path** (preferred for printable packets): outputs a single `[theme]_series/[theme].html`. Open in any browser — the print dialog opens automatically.

**PIL path** (image-heavy or standalone files): outputs to `[theme]_series/` as both `.png` (screen preview) and `.pdf` (print-ready), one file per worksheet.

---

## 7. Git Workflow Rules

**Never commit directly to `main`.** All changes must go through a pull request, regardless of size or urgency. This applies to agents, automated fixes, and humans alike.

The correct workflow for any change:
1. Create a branch from `origin/main`: `git checkout -b <branch-name> origin/main`
2. Make commits on that branch
3. Push the branch: `git push -u origin <branch-name>`
4. Open a PR: `gh pr create ...`
5. Do **not** push to `main` directly

**Never commit directly to `main`.** All changes must go through a pull request, regardless of size or urgency. This applies to agents, automated fixes, and humans alike.

The correct workflow for any change:
1. Create a branch from `origin/main`: `git checkout -b <branch-name> origin/main`
2. Make commits on that branch
3. Push the branch: `git push -u origin <branch-name>`
4. Open a PR: `gh pr create ...`
5. Do **not** push to `main` directly

**Before pushing any commit, always verify the current branch has not been merged:**
```bash
git fetch origin
git log origin/main --oneline -5
```
If your current branch tip appears in `origin/main`, it has been merged. **Do not push to it.** Instead:
1. Create a new branch from `origin/main`: `git checkout origin/main -b <new-branch-name>`
2. Cherry-pick only the commits that are not yet on main
3. Push the new branch and open a fresh PR

**Never accumulate multiple unrelated fixes on one branch.** Each PR should be focused on a single concern so it can be merged independently without blocking other work.

---

## 7. Automated Analysis & Fix Workflow

When an agent performs a codebase audit and creates GitHub issues, the following pattern must be followed:

1. **Analysis**: Spawn a read-only agent to identify bugs/deficiencies. Each finding must include a reproduction scenario and justification before an issue is filed.
2. **Issue creation**: File GitHub issues with the `Claude-identified` label. One issue per distinct bug.
3. **Fix branch**: Create a single branch (`fix/claude-identified-bugs` or similar) from `origin/main` **before** making any changes.
4. **Fix & commit**: Apply fixes on the branch and commit. Do not touch `main`.
5. **PR**: Push the branch and open a PR referencing the issues (e.g., `Closes #77, #78`). Do not close issues manually — let the PR merge close them via GitHub keywords.
6. **No direct-to-main commits**: Even if the fix seems trivial, it must go through a PR so the owner can review before merging.
