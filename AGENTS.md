# Worksheet Generation Guide (AGENTS.md)

This document outlines the architecture, constraints, and "Instructional Pair" strategy used to generate high-fidelity educational worksheets for various age groups in this repository.

---

## 1. Core Architecture
The system is built on a modular Python framework:
*   **`src/worksheets/`**: Logic for specific data structures (e.g., `MatchingWorksheet`, `ReadingWorksheet`).
*   **`src/worksheets/factory.py`**: A unified entry point to create worksheet objects from dictionary payloads.
*   **`src/worksheet_renderer.py`**: The visual engine using Pillow. It handles:
    *   **High-Contrast Layouts**: Wide gutters (~400px) and tight bullet anchors for toddlers.
    *   **Advanced Scaling**: `NEAREST` filtering for Minecraft/pixel art; `LANCZOS` for high-res icons.
    *   **Dynamic Formatting**: Text wrapping, font management (DejaVu Sans), and multi-page rendering.

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
*   **`matching`**: Image-to-word or Shadow-to-image.
*   **`handwriting`**: Traceable words with sub-labels for context.
*   **`reading_comprehension`**: Passages + Questions + Vocabulary banks.
*   **`venn_diagram`**: Overlapping circles with word banks for comparison.
*   **`feature_matrix`**: Grid-based classification (e.g., "Home Rule" vs. "Community Law").
*   **`tree_map`**: Hierarchical categorization.
*   **`odd_one_out`**: Logic-based exclusion with reasoning lines.

---

## 4. The "Great Worksheet" Prompt Template
When requesting new worksheets, providing this context ensures the best results:

> **Topic**: [e.g., Ancient Egypt, Planets, Multiplication]  
> **Target Audience**: [Age & Reading Level, e.g., 6-year-old, advanced reader]  
> **Set Structure**: [e.g., Instructional Pair: Reading + Feature Matrix]  
> **Constraint**: [e.g., Only use CVC words / Include the Three Laws of Motion]  
> **Aesthetic**: [e.g., Disney API art, OpenMoji icons, Pixel Art]  
> **Educational Goal**: [e.g., Identify the difference between a planet and a star]

---

## 5. Technical Deployment
Always run generation scripts within the project's virtual environment:
```bash
venv/bin/python3 generate_[theme]_series.py
```
Outputs are consistently routed to a `[theme]_series/` directory in both **PNG** (for quick viewing) and **PDF** (for printing) formats.

---

## 6. Git Workflow Rules

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
