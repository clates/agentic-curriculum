"""
agent.py

LLM-based agent for generating lesson plans using OpenAI API.
"""

import os
import sys
import json
from openai import OpenAI

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(__file__))

from db_utils import get_student_profile
from logic import get_filtered_standards
from datetime import datetime, timedelta


def create_lesson_plan_prompt(standard: dict, rules: dict) -> str:
    """
    Build the system prompt for the LLM to generate a lesson plan.
    
    Args:
        standard: Dictionary containing standard information (standard_id, subject, description, etc.)
        rules: Dictionary containing parent rules (allowed_materials, parent_notes, etc.)
        
    Returns:
        A string containing the formatted prompt for the LLM
    """
    # Extract allowed materials and parent notes from rules
    allowed_materials = rules.get('allowed_materials', [])
    # Default to keeping procedures under 3 steps if parent_notes not provided
    parent_notes = rules.get('parent_notes', 'keep procedures under 3 steps')
    
    # Build the prompt
    prompt = f"""You are an expert K-12 educator. Create a lesson plan for the following educational standard.

Standard: {standard.get('description', '')}
Subject: {standard.get('subject', '')}
Grade Level: {standard.get('grade_level', 0)}

Requirements:
1. Create a lesson_plan object with the following structure:
   - objective: A clear learning objective based on the standard
   - materials_needed: A list of materials (MUST only use items from: {allowed_materials})
   - procedure: Step-by-step instructions for teaching the lesson

2. Important constraints:
   - Materials MUST ONLY come from this list: {allowed_materials}
   - Follow this parent guidance: {parent_notes}
   - Keep the lesson age-appropriate for the grade level
   - The objective should directly address the standard

Respond ONLY with a valid JSON object in this exact format:
{{
  "objective": "Clear learning objective here",
  "materials_needed": ["Material1", "Material2"],
  "procedure": ["Step 1", "Step 2", "Step 3"]
}}"""
    
    return prompt


def generate_weekly_plan(student_id: str, grade_level: int, subject: str) -> dict:
    """
    Generate a weekly lesson plan for a student using LLM.
    
    Args:
        student_id: Unique identifier for the student
        grade_level: Grade level for the standards
        subject: Subject area (may be overridden by theme rules)
        
    Returns:
        A dictionary containing the complete weekly plan with daily lesson plans
        
    Raises:
        ValueError: If student not found or API key not set
    """
    # Check for OpenAI API key
    api_key = os.environ.get('OPENAI_API_KEY')
    if not api_key:
        raise ValueError("OPENAI_API_KEY environment variable not set")
    
    # Get base URL and model from environment variables with defaults
    base_url = os.environ.get('OPENAI_BASE_URL', None)
    model = os.environ.get('OPENAI_MODEL', 'gpt-3.5-turbo')
    
    # Initialize OpenAI client
    client = OpenAI(api_key=api_key, base_url=base_url)
    
    # Get student profile and parse rules
    student_profile = get_student_profile(student_id)
    if student_profile is None:
        raise ValueError(f"Student with id '{student_id}' not found")
    
    # Parse plan_rules_blob to get rules
    rules = json.loads(student_profile['plan_rules_blob'])
    
    # Get standards for the student. We request more than 5 to have flexibility
    # in how they're distributed across the week. Some complex standards may need
    # multiple days, while simpler ones can be covered in a single day.
    standards = get_filtered_standards(student_id, grade_level, subject, limit=10)
    
    if len(standards) == 0:
        raise ValueError(f"No standards found for student {student_id}.")
    
    # Precompute a pretty JSON preview of the first few standards for the prompt
    available_standards_preview = [
        {"id": s.get("standard_id"), "description": s.get("description")}
        for s in standards[:5]
    ]
    available_standards_text = json.dumps(available_standards_preview, indent=2)

    # First pass: Create a weekly overview/scaffold
    # This helps ensure complex standards get multiple days if needed
    scaffold_prompt = f"""You are an expert K-12 educator creating a weekly lesson plan scaffold.

Grade Level: {grade_level}
Subject: {subject}

Available Standards (may use 1 or more):
{available_standards_text}

Parent Constraints:
- Allowed materials: {rules.get('allowed_materials', [])}
- Parent guidance: {rules.get('parent_notes', 'keep procedures under 3 steps')}

Create a weekly plan that:
1. Distributes standards across Monday-Friday appropriately
2. Complex standards should span multiple days with scaffolding
3. Simpler standards can be covered in a single day
4. Each day should build on previous days

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

    # Get the weekly scaffold from LLM
    try:
        scaffold_response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are a helpful K-12 education assistant. Always respond with valid JSON only."},
                {"role": "user", "content": scaffold_prompt}
            ],
            temperature=0.7,
            response_format={"type": "json_object"}
        )
        
        weekly_scaffold = json.loads(scaffold_response.choices[0].message.content)
        daily_assignments = weekly_scaffold.get('daily_assignments', [])
        weekly_overview = weekly_scaffold.get('weekly_overview', '')
    except json.JSONDecodeError as e:
        # JSON parsing error from LLM - log and use fallback
        print(f"Warning: Failed to parse scaffold JSON: {e}")
        weekly_overview = "Weekly plan using standard curriculum progression"
        daily_assignments = [
            {"day": day, "standard_ids": [standards[i].get('standard_id')], "focus": f"Day {i+1} focus"}
            for i, day in enumerate(["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"])
            if i < len(standards)
        ]
    except Exception as e:
        # Other errors (API, network, etc.) - log and use fallback
        print(f"Warning: Failed to generate scaffold: {e}")
        weekly_overview = "Weekly plan using standard curriculum progression"
        daily_assignments = [
            {"day": day, "standard_ids": [standards[i].get('standard_id')], "focus": f"Day {i+1} focus"}
            for i, day in enumerate(["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"])
            if i < len(standards)
        ]
    
    # Ensure we have exactly 5 days
    days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
    if len(daily_assignments) != 5:
        # Adjust to exactly 5 days
        while len(daily_assignments) < 5:
            daily_assignments.append({
                "day": days[len(daily_assignments)],
                "standard_ids": [standards[min(len(daily_assignments), len(standards)-1)].get('standard_id')],
                "focus": "Additional practice"
            })
        daily_assignments = daily_assignments[:5]
    
    # Create a lookup for standards by ID
    standards_by_id = {s.get('standard_id'): s for s in standards}
    
    # Build daily plan based on scaffold
    daily_plan = []
    
    for assignment in daily_assignments:
        day = assignment.get('day')
        standard_ids = assignment.get('standard_ids', [])
        day_focus = assignment.get('focus', '')
        
        # Get the standards for this day
        day_standards = [standards_by_id.get(sid) for sid in standard_ids if sid in standards_by_id]
        day_standards = [s for s in day_standards if s is not None]  # Filter out None values
        
        if not day_standards:
            # Fallback to first available standard if assignment references missing standards
            day_standards = [standards[0]] if standards else []
        
        # Create a combined prompt for all standards assigned to this day
        if len(day_standards) == 1:
            prompt = create_lesson_plan_prompt(day_standards[0], rules)
        else:
            # Multiple standards for this day - create combined lesson
            combined_descriptions = " AND ".join([s.get('description', '') for s in day_standards])
            combined_standard = {
                'description': combined_descriptions,
                'subject': day_standards[0].get('subject'),
                'grade_level': day_standards[0].get('grade_level')
            }
            prompt = create_lesson_plan_prompt(combined_standard, rules)
            prompt += f"\n\nDay Focus: {day_focus}"
        
        # Call OpenAI API to generate lesson plan
        try:
            response = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": "You are a helpful K-12 education assistant. Always respond with valid JSON only."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                response_format={"type": "json_object"}
            )
            
            # Parse the LLM response
            lesson_plan_json = response.choices[0].message.content
            lesson_plan = json.loads(lesson_plan_json)
            
        except json.JSONDecodeError as e:
            # JSON parsing error from LLM - log and use fallback
            print(f"Warning: Failed to parse lesson plan JSON for {day}: {e}")
            lesson_plan = {
                "objective": f"Learn about: {day_standards[0].get('description', '') if day_standards else 'the assigned topic'}",
                "materials_needed": rules.get('allowed_materials', [])[:2],
                "procedure": [
                    "Introduce the concept",
                    "Practice with materials",
                    "Review and assess understanding"
                ]
            }
        except Exception as e:
            # Other errors (API, network, etc.) - log and use fallback
            print(f"Warning: Failed to generate lesson plan for {day}: {e}")
            lesson_plan = {
                "objective": f"Learn about: {day_standards[0].get('description', '') if day_standards else 'the assigned topic'}",
                "materials_needed": rules.get('allowed_materials', [])[:2],
                "procedure": [
                    "Introduce the concept",
                    "Practice with materials",
                    "Review and assess understanding"
                ]
            }
        
        # Add to daily plan - include all standards for this day
        daily_plan.append({
            "day": day,
            "lesson_plan": lesson_plan,
            "standard": day_standards[0] if day_standards else {},  # Primary standard
            "standards": day_standards,  # All standards for this day
            "focus": day_focus
        })
    
    # Calculate week_of date (Monday of current week)
    today = datetime.now()
    monday = today - timedelta(days=today.weekday())
    week_of = monday.strftime("%Y-%m-%d")
    
    # Construct the final weekly plan
    weekly_plan = {
        "plan_id": f"plan_{student_id}_{week_of}",
        "student_id": student_id,
        "week_of": week_of,
        "weekly_overview": weekly_overview,
        "daily_plan": daily_plan
    }
    
    return weekly_plan
