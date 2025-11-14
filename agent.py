"""
agent.py

LLM-based agent for generating lesson plans using OpenAI API.
"""

import os
import json
from openai import OpenAI
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
    
    # Initialize OpenAI client
    client = OpenAI(api_key=api_key)
    
    # Get student profile and parse rules
    student_profile = get_student_profile(student_id)
    if student_profile is None:
        raise ValueError(f"Student with id '{student_id}' not found")
    
    # Parse plan_rules_blob to get rules
    rules = json.loads(student_profile['plan_rules_blob'])
    
    # Get 5 filtered standards for the student
    standards = get_filtered_standards(student_id, grade_level, subject, limit=5)
    
    if len(standards) < 5:
        raise ValueError(f"Not enough standards found. Only {len(standards)} standards available.")
    
    # Days of the week
    days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
    
    # Build daily plan
    daily_plan = []
    
    for i, standard in enumerate(standards[:5]):
        day = days[i]
        
        # Create prompt for this standard
        prompt = create_lesson_plan_prompt(standard, rules)
        
        # Call OpenAI API to generate lesson plan
        try:
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
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
            
        except Exception as e:
            # If LLM call fails, provide a basic fallback
            lesson_plan = {
                "objective": f"Learn about: {standard.get('description', '')}",
                "materials_needed": rules.get('allowed_materials', [])[:2],
                "procedure": [
                    "Introduce the concept",
                    "Practice with materials",
                    "Review and assess understanding"
                ]
            }
        
        # Add to daily plan
        daily_plan.append({
            "day": day,
            "lesson_plan": lesson_plan,
            "standard": standard
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
        "daily_plan": daily_plan
    }
    
    return weekly_plan
