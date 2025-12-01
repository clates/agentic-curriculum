"""
LLM Prompts for Weekly and Daily Lesson Plan Generation.

This module contains all the prompt templates used for generating:
- Weekly plan scaffolds (overall week structure)
- Daily lesson plans (individual day lessons)

These prompts are the core of the curriculum generation system and are
designed to be easily modified and improved.

IMPORTANT: When modifying prompts, test thoroughly as changes can significantly
affect the quality of generated lesson plans.
"""

import json


# =============================================================================
# RESOURCE GENERATION GUIDANCE
# =============================================================================

RESOURCE_GUIDANCE = """
OPTIONAL: Create educational resources (worksheets) if they would enhance the lesson.

Available resource types (see docs/WORKSHEET_TYPES.md for full details):

1. mathWorksheet (two_operand): Vertical math worksheets for addition/subtraction
   - Required: problems (list with operand_one, operand_two, operator: "+"|"-")
   - Optional: title, instructions, metadata
   - Example: {"mathWorksheet": {"title": "Addition Practice", "problems": [{"operand_one": 5, "operand_two": 3, "operator": "+"}]}}

2. readingWorksheet (reading_comprehension): Reading passages with questions
   - Required: passage_title, passage, questions (list with prompt, optional response_lines)
   - Optional: vocabulary (list with term, optional definition/response_lines), title, instructions, metadata
   - Example: {"readingWorksheet": {"passage_title": "Story Title", "passage": "Text here...", "questions": [{"prompt": "What happened?", "response_lines": 2}]}}

3. vennDiagramWorksheet: Two-circle Venn diagram for classification/comparison
   - Required: left_label, right_label
   - Optional: both_label, word_bank, left_items, right_items, both_items, title, instructions, metadata
   - Example: {"vennDiagramWorksheet": {"left_label": "Mammals", "right_label": "Reptiles", "word_bank": ["dog", "snake", "cat"]}}

4. featureMatrixWorksheet: Grid for classifying items by properties
   - Required: items (list of names or dicts with name/checked_properties), properties (list of column headers)
   - Optional: title, instructions, show_answers, metadata
   - Example: {"featureMatrixWorksheet": {"items": ["Dog", "Fish"], "properties": ["Has Fur", "Lives in Water"]}}

5. oddOneOutWorksheet: Identify what doesn't belong and explain reasoning
   - Required: rows (list of dicts with items list, optional odd_item/explanation)
   - Optional: title, instructions, show_answers, reasoning_lines, metadata
   - Example: {"oddOneOutWorksheet": {"rows": [{"items": ["dog", "cat", "car", "bird"]}], "reasoning_lines": 2}}

6. treeMapWorksheet: Hierarchical classification tree diagram
   - Required: root_label, branches (list with label, slots or slot_count)
   - Optional: word_bank, title, instructions, metadata
   - Example: {"treeMapWorksheet": {"root_label": "Food Groups", "branches": [{"label": "Fruits", "slot_count": 3}], "word_bank": ["apple", "banana"]}}

Guidelines:
- Only include resources that directly support the lesson objective
- Choose the worksheet type that best matches the learning activity
- Keep worksheets age-appropriate and aligned with the standard
- One worksheet per day is typically sufficient (but you can include multiple if pedagogically valuable)
- If no worksheet is needed, omit the entire 'resources' key
- Only emit the fields you need for each worksheet type
"""

# Example resource for demonstrating the expected format
RESOURCE_FEW_SHOT = {
    "mathWorksheet": {
        "title": "Repeated Addition Warm-Up",
        "problems": [
            {"operand_one": 2, "operand_two": 2, "operator": "+"},
            {"operand_one": 3, "operand_two": 3, "operator": "+"},
        ],
    }
}
RESOURCE_FEW_SHOT_JSON = json.dumps(RESOURCE_FEW_SHOT, indent=2)


# =============================================================================
# WEEKLY PLAN SCAFFOLD PROMPT
# =============================================================================


def build_weekly_scaffold_prompt(
    grade_level: int,
    subject: str,
    available_standards: list[dict],
    allowed_materials: list[str],
    parent_notes: str,
    activity_guidance: str,
) -> str:
    """
    Build the prompt for generating a weekly lesson plan scaffold.

    The scaffold determines how standards are distributed across the week
    and ensures complex standards get multiple days if needed.

    Args:
        grade_level: Student's grade level (0-12, where 0 = Kindergarten)
        subject: Subject area (e.g., "Math", "English", "Science")
        available_standards: List of standard dicts with 'id' and 'description'
        allowed_materials: List of materials parent has available
        parent_notes: Parent's guidance/preferences for lessons
        activity_guidance: Guidance on number of activities per day based on feedback

    Returns:
        Formatted prompt string for the LLM
    """
    available_standards_text = json.dumps(available_standards, indent=2)

    return f"""You are an expert K-12 educator and pedagogy specialist creating a weekly lesson plan scaffold for a HOMESCHOOL environment.

CONTEXT: This is for ONE parent teaching ONE student at home.

Grade Level: {grade_level}
Subject: {subject}

Available Standards (USE ALL OF THESE):
{available_standards_text}

Parent Constraints:
- Allowed materials: {allowed_materials}
- Parent guidance: {parent_notes}

Create a weekly plan that:
1. **Uses ALL provided standards** - distribute them across Monday-Friday appropriately
2. Complex standards should span multiple days with scaffolding
3. Simpler standards can be covered in a single day
4. Each day should build on previous days
5. {activity_guidance}
6. Keep lessons engaging and hands-on when possible for homeschool setting

Respond with a JSON object in this exact format:
{{
  "weekly_overview": "Brief description of how the week progresses",
  "daily_assignments": [
    {{
      "day": "Monday",
      "standard_ids": ["standard_id_1"],
      "focus": "Brief description of this day's focus"
    }},
    ...
  ]
}}"""


# =============================================================================
# DAILY LESSON PLAN PROMPT
# =============================================================================


def build_lesson_plan_prompt(
    standard: dict,
    allowed_materials: list[str],
    parent_notes: str,
    day_focus: str = "",
) -> str:
    """
    Build the prompt for generating a single day's lesson plan.

    This prompt creates detailed lesson plans including objectives, materials,
    procedures, and optional worksheet resources.

    Args:
        standard: Dictionary containing:
            - description: The learning standard's description
            - subject: Subject area
            - grade_level: Grade level (0-12)
        allowed_materials: List of materials parent has available
        parent_notes: Parent's guidance/preferences for lessons (default: "keep procedures under 3 steps")
        day_focus: Optional specific focus for this day (e.g., "Introduction to concept")

    Returns:
        Formatted prompt string for the LLM

    Example:
        >>> standard = {
        ...     "description": "Understand place value",
        ...     "subject": "Math",
        ...     "grade_level": 2
        ... }
        >>> prompt = build_lesson_plan_prompt(
        ...     standard,
        ...     ["paper", "pencils", "counters"],
        ...     "keep lessons under 45 minutes"
        ... )
    """
    # Build resource guidance section
    resource_guidance = f"""{RESOURCE_GUIDANCE}

Example (trim fields you do not need):
{RESOURCE_FEW_SHOT_JSON}
"""

    # Build base prompt
    prompt = f"""You are an expert K-12 educator and pedagogy specialist with a knack for creating engaging and enticing lesson plans.

CONTEXT: This lesson is for a HOMESCHOOL environment where ONE parent is teaching ONE student.

Standard: {standard.get('description', '')}
Subject: {standard.get('subject', '')}
Grade Level: {standard.get('grade_level', 0)}

Requirements:
1. Create a lesson_plan object with the following structure:
   - objective: A clear, engaging learning objective based on the standard
   - materials_needed: A list of materials (MUST only use items from: {allowed_materials})
   - procedure: Step-by-step instructions for teaching the lesson

2. Important constraints:
   - Materials MUST ONLY come from this list: {allowed_materials}
   - Follow this parent guidance: {parent_notes}
   - **Include AT LEAST 3 distinct activities** in the procedure
   - **Aim for 60-75 minutes of total work** (include approximate minutes for each step)
   - Keep the lesson age-appropriate for the grade level
   - Make activities engaging, hands-on, and suitable for one-on-one homeschool instruction
   - The objective should directly address the standard

{resource_guidance}

Respond ONLY with valid JSON:
{{
    "lesson_plan": {{
        "objective": "Clear learning objective here",
        "materials_needed": ["Material1", "Material2"],
        "procedure": ["Step 1 (15 min)", "Step 2 (20 min)", "Step 3 (25 min)", "..."]
    }},
    "resources": {{
        "mathWorksheet": {{ ... }},
        "readingWorksheet": {{ ... }}
    }}
}}
If no worksheet is needed, omit the entire `resources` key.
"""

    # Add day-specific focus if provided
    if day_focus:
        prompt += f"\n\nDay Focus: {day_focus}"

    return prompt


# =============================================================================
# SYSTEM MESSAGE (Used for all LLM calls)
# =============================================================================

LLM_SYSTEM_MESSAGE = """You are a helpful K-12 education assistant and expert in pedagogy with a knack for creating engaging and enticing lesson plans.

IMPORTANT CONTEXT: You are creating materials for a HOMESCHOOL environment where:
- There is ONE parent teaching ONE student
- The parent may have limited time and resources
- Lessons should be clear, engaging, and doable at home
- Activities should be hands-on and interactive when possible

Always respond with valid JSON only."""


# =============================================================================
# PROMPT IMPROVEMENT NOTES
# =============================================================================

"""
NOTES FOR FUTURE IMPROVEMENTS:

Weekly Scaffold Prompt:
- Consider adding examples of good vs bad standard distribution
- Could include more explicit guidance on pacing complex topics
- May benefit from examples of how to scaffold multi-day lessons

Daily Lesson Plan Prompt:
- Could provide more specific structure for procedure steps
- Consider adding guidance on differentiation for different learning styles
- May want to include assessment/check-for-understanding guidance
- Could provide examples of high-quality lesson plans

Resource Generation:
- Current resource types are limited to Math and Reading worksheets
- Could expand to include: writing prompts, science experiments, art projects
- May want more explicit guidance on difficulty calibration

General:
- Test prompt variations with different models (GPT-3.5 vs GPT-4 vs o1)
- Consider A/B testing different prompt structures
- Could add few-shot examples for better consistency
"""
