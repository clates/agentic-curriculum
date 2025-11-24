# Architecture Improvements - Code Review Response

## Overview
This document describes the architectural improvements made to the LLM-powered weekly lesson plan generation system based on code review feedback.

## Changes Made

### 1. Dynamic OpenAI Configuration (Comment on line 81)
**Problem**: Base URL and model were hardcoded.

**Solution**: Added environment variable support:
- `OPENAI_BASE_URL` (optional) - Supports custom OpenAI-compatible endpoints
- `OPENAI_MODEL` (optional, default: `gpt-3.5-turbo`) - Configurable model selection

**Usage**:
```bash
export OPENAI_API_KEY="your-key"
export OPENAI_BASE_URL="https://custom-endpoint.com/v1"  # Optional
export OPENAI_MODEL="gpt-4"  # Optional
```

### 2. Flexible Standard Retrieval (Comment on line 92)
**Problem**: Fixed limit of 5 standards was too rigid.

**Solution**: 
- Increased limit from 5 to 10 standards
- Provides flexibility for the scaffolding logic to distribute standards appropriately
- Allows complex standards to span multiple days while simpler ones can be covered in a single day

**Rationale**: The scaffold can now intelligently decide:
- Which standards need multiple days of instruction
- Which standards can be combined in a single day
- How to build progressive complexity throughout the week

### 3. Two-Pass Planning with Scaffolding (Comment on line 107)
**Problem**: No weekly planning - each day was generated independently.

**Solution**: Implemented a two-pass approach:

#### Pass 1: Weekly Scaffold
- LLM creates a weekly overview
- Determines how standards should be distributed across Monday-Friday
- Identifies which standards need scaffolding across multiple days
- Plans how each day builds on previous days

Example scaffold response:
```json
{
  "weekly_overview": {
    "before_you_start": "Gather counters and a math journal, preview the week's focus, and set norms for quick daily warm-ups",
    "summary": "Progressive introduction to multiplication starting with repeated addition"
  },
  "daily_assignments": [
    {
      "day": "Monday",
      "standard_ids": ["MATH.2.mul.1"],
      "focus": "Introduce repeated addition as foundation"
    },
    {
      "day": "Tuesday",
      "standard_ids": ["MATH.2.mul.1"],
      "focus": "Connect repeated addition to multiplication concept"
    },
    ...
  ]
}
```

#### Pass 2: Daily Lesson Generation
- Uses scaffold to guide lesson creation
- Generates detailed lesson plans for each day
- Ensures lessons align with the weekly progression
- Maintains consistency across the week

**Benefits**:
- Complex standards like "second grade multiplication" can span multiple days
- Each day builds on previous learning
- Better pedagogical progression
- More coherent weekly experience

### 4. Non-1:1 Standard-to-Day Mapping (Comment on line 103)
**Problem**: Standards were rigidly mapped 1:1 to days.

**Solution**: Flexible mapping based on complexity and pedagogy:

#### New Data Structure
Each daily plan item now includes:
```json
{
  "day": "Monday",
  "lesson_plan": { ... },
  "standard": { ... },          // Primary standard (backward compatible)
  "standards": [ ... ],         // All standards for this day (new)
  "focus": "Day's focus"        // Description of what this day emphasizes (new)
}
```

#### Mapping Scenarios

**Scenario 1: Complex standard spans multiple days**
- Monday: "Introduction to multiplication" (MATH.2.mul.1)
- Tuesday: "Practice multiplication patterns" (MATH.2.mul.1)
- Wednesday: "Apply multiplication to problems" (MATH.2.mul.1)

**Scenario 2: Multiple simple standards in one day**
- Friday: "Review counting + Review shapes" (MATH.K.1 + MATH.K.2)

**Scenario 3: Progressive building**
- Monday-Tuesday: Foundation concepts (Standard A)
- Wednesday-Thursday: Application (Standard B, building on A)
- Friday: Integration (Standards A+B together)

## Backward Compatibility

The changes maintain backward compatibility:
- `standard` field still present (primary standard for the day)
- All existing validation scripts will continue to work
- New fields (`standards`, `focus`) are additions, not replacements

## Testing Recommendations

1. **Test with simple standards**: Verify single-day lessons work
2. **Test with complex standards**: Verify multi-day scaffolding works
3. **Test with mixed complexity**: Verify intelligent distribution
4. **Test custom endpoints**: Verify OPENAI_BASE_URL works with compatible APIs
5. **Test different models**: Verify OPENAI_MODEL selection works

## Environment Configuration Summary

| Variable | Required | Default | Purpose |
|----------|----------|---------|---------|
| `OPENAI_API_KEY` | Yes | - | Authentication |
| `OPENAI_BASE_URL` | No | OpenAI default | Custom endpoint support |
| `OPENAI_MODEL` | No | `gpt-3.5-turbo` | Model selection |

## Impact on Validation

The validation script (`validate_chunk4.py`) will continue to work because:
1. The `standard` field is still present (backward compatible)
2. New fields are additions that don't break existing checks
3. The response structure matches expected format

Users can optionally update validation to check:
- The new `standards` array
- The `focus` field
- Multi-day scaffolding logic
