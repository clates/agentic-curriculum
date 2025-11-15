# Error Handling and Weekly Overview Updates

## Overview
This document describes the improvements made to error handling and response structure based on the latest code review feedback.

## Changes Made

### 1. Improved Exception Handling (Comment on line 219)

**Problem**: Generic `Exception` handling didn't distinguish between different types of errors, making debugging harder.

**Solution**: Separated JSON parsing errors from other exceptions.

#### Before:
```python
except Exception as e:
    # If LLM call fails, provide a basic fallback
    lesson_plan = { ... }
```

#### After:
```python
except json.JSONDecodeError as e:
    # JSON parsing error from LLM - log and use fallback
    print(f"Warning: Failed to parse lesson plan JSON for {day}: {e}")
    lesson_plan = { ... }
except Exception as e:
    # Other errors (API, network, etc.) - log and use fallback
    print(f"Warning: Failed to generate lesson plan for {day}: {e}")
    lesson_plan = { ... }
```

#### Benefits:
- **Better Debugging**: Clearly identifies if the issue is LLM response format vs infrastructure
- **Targeted Logging**: Different log messages for different error types
- **Appropriate Handling**: Both errors use fallback, but with context-specific messages
- **Production Monitoring**: Easier to track and alert on specific error types

#### Error Types:
1. **`json.JSONDecodeError`**: LLM returned invalid JSON
   - Could indicate prompt issues
   - Might need prompt refinement
   - Log includes the malformed response

2. **Other `Exception`**: API errors, network issues, rate limits
   - Infrastructure or configuration problems
   - API key issues
   - Network connectivity problems

### 2. Added Weekly Overview to Response (Comment on line 246)

**Problem**: The weekly overview created during scaffolding was not included in the final response.

**Solution**: Added `weekly_overview` field to the final weekly plan.

#### Updated Response Structure:
```json
{
  "plan_id": "plan_student_01_2025-11-10",
  "student_id": "student_01",
  "week_of": "2025-11-10",
  "weekly_overview": "Progressive introduction to multiplication...",  // NEW
  "daily_plan": [
    {
      "day": "Monday",
      "lesson_plan": { ... },
      "standard": { ... },
      "standards": [ ... ],
      "focus": "..."
    },
    ...
  ]
}
```

#### Benefits:
- **Context**: Provides high-level understanding of the week's pedagogical approach
- **Transparency**: Shows how the LLM planned the week's progression
- **User Value**: Helps teachers/parents understand the learning arc
- **Planning Visibility**: Makes the scaffolding strategy explicit

#### Example Weekly Overviews:
- "Progressive introduction to multiplication starting with repeated addition, building to times tables"
- "Foundation week for reading comprehension, starting with letter recognition and building to simple words"
- "Review week combining counting, shapes, and basic addition for reinforcement"

### 3. Consistent Error Handling Pattern

Both the scaffold generation AND daily lesson generation now follow the same pattern:

```python
try:
    # LLM call
    response = client.chat.completions.create(...)
    result = json.loads(response.choices[0].message.content)
except json.JSONDecodeError as e:
    # Specific handling for JSON errors
    print(f"Warning: Failed to parse JSON: {e}")
    # Appropriate fallback
except Exception as e:
    # Handling for other errors
    print(f"Warning: Failed to generate: {e}")
    # Appropriate fallback
```

## Testing Recommendations

### Test JSON Errors:
1. Mock OpenAI to return invalid JSON
2. Verify specific error message appears
3. Confirm fallback plan is used
4. Check that other functionality continues

### Test API Errors:
1. Mock OpenAI to raise connection error
2. Verify different error message appears
3. Confirm fallback plan is used
4. Check that other functionality continues

### Test Weekly Overview:
1. Generate a plan with valid API key
2. Verify `weekly_overview` field is present
3. Check content is meaningful
4. Confirm it matches the scaffolding logic

### Test Fallback Behavior:
1. When scaffold fails, verify fallback overview is used
2. When lesson generation fails, verify fallback lessons are used
3. Confirm final plan still has valid structure

## Backward Compatibility

✅ **Maintained**: The new `weekly_overview` field is an addition, not a breaking change.

Existing code that doesn't check for `weekly_overview` will continue to work:
- `daily_plan` structure unchanged
- All existing fields still present
- Validation scripts continue to work

## Error Monitoring Recommendations

For production deployments, consider:

1. **Log Aggregation**: Send error logs to centralized system
2. **Alerting**: Set up alerts for high rates of either error type
3. **Metrics**: Track ratio of JSON errors vs API errors
4. **Response Times**: Monitor for degraded LLM performance
5. **Fallback Usage**: Track how often fallbacks are used

## Related Documentation

- See `ARCHITECTURE_IMPROVEMENTS.md` for overall architecture
- See `CHUNK4_COMPLETION.md` for setup and usage instructions
