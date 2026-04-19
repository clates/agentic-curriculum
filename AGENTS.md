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
