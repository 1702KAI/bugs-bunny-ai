# Bug Report

**Tester:** Aaron Emmanuel  
**Date:** 2026-02-06  
**Test Command:** `pytest tests/test_utils.py -v`

---

## Bug #1: `validate_email()` - Regex Too Permissive

**Failing Tests:**
- `test_invalid_email_no_at_symbol`
- `test_invalid_email_no_domain`
- `test_invalid_email_spaces`
- `test_invalid_email_special_chars`

**Expected Behavior:**
Function should return `False` for invalid emails like:
- `userexample.com` (no @ symbol)
- `user@` (no domain)
- `user @example.com` (contains space)

**Actual Behavior:**
Returns `True` for these invalid emails because the regex `.+@.+` is too permissive.

**Root Cause:**
The regex pattern `r".+@.+"` only checks for:
- One or more characters before `@`
- One or more characters after `@`

It doesn't validate proper email format (domain with TLD, no spaces, etc.)

**Fix Applied:**
```python
pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
return bool(re.match(pattern, email))
```

---

## Bug #2: `calculate_priority_score()` - Off-by-One Error & Missing KeyError Handling

**Failing Tests:**
- `test_medium_due_in_3_days`
- `test_low_due_in_7_days`
- `test_invalid_priority`

**Expected Behavior:**
- Task due in exactly 3 days should get +20 bonus
- Task due in exactly 7 days should get +10 bonus
- Invalid priority like "urgent" should raise `ValueError`

**Actual Behavior:**
- 3-day tasks get +10 bonus (wrong)
- 7-day tasks get +0 bonus (wrong)
- Invalid priority raises `KeyError` instead of `ValueError`

**Root Cause:**
1. Conditions use `<` instead of `<=`: `days_until_due < 3` excludes day 3
2. No handling for unknown priority keys

**Fix Applied:**
```python
base_score = priority_weights.get(priority)
if base_score is None:
    raise ValueError(f"Invalid priority: {priority}")

if days_until_due < 0:
    urgency_bonus = 50
elif days_until_due == 0:
    urgency_bonus = 30
elif days_until_due <= 3:  # Fixed: was < 3
    urgency_bonus = 20
elif days_until_due <= 7:  # Fixed: was < 7
    urgency_bonus = 10
else:
    urgency_bonus = 0
```

---

## Bug #3: `sanitize_input()` - Incomplete XSS Protection

**Failing Tests:**
- `test_removes_script_variations`
- `test_removes_img_onerror`
- `test_removes_javascript_url`
- `test_none_handling`

**Expected Behavior:**
Function should remove ALL XSS attack vectors including:
- Case variations: `<SCRIPT>`, `<ScRiPt>`
- Event handlers: `onerror`, `onload`, `onmouseover`
- JavaScript URLs: `javascript:alert(1)`

**Actual Behavior:**
Only removes exact lowercase `<script>` and `</script>` tags.

**Root Cause:**
Incomplete implementation - only handles one specific case.

**Fix Applied:**
```python
def sanitize_input(text: str) -> str:
    if text is None:
        return ""
    if not text:
        return ""
    
    # Remove script tags AND their content (handles case variations)
    sanitized = re.sub(r'<script[^>]*>.*?</script>', '', text, flags=re.IGNORECASE | re.DOTALL)
    
    # Remove all remaining HTML tags
    sanitized = re.sub(r'<[^>]*>', '', sanitized, flags=re.IGNORECASE)
    
    # Remove javascript: URLs
    sanitized = re.sub(r'javascript:', '', sanitized, flags=re.IGNORECASE)
    
    return sanitized
```

---

## Bug #4: `parse_date()` - No Error Handling

**Failing Tests:**
- `test_invalid_format`
- `test_invalid_date_string`
- `test_empty_string`

**Expected Behavior:**
Function should raise `ValueError` for invalid date inputs.

**Actual Behavior:**
Raises unhandled exception from `datetime.strptime()` that crashes the application.

**Root Cause:**
No try/except block to catch and handle invalid date formats.

**Fix Applied:**
```python
def parse_date(date_string: str) -> datetime:
    if not date_string:
        raise ValueError("Date string cannot be empty")
    
    try:
        return datetime.strptime(date_string, "%Y-%m-%d")
    except ValueError:
        raise ValueError(f"Invalid date format: {date_string}. Expected YYYY-MM-DD")
```

---

## Summary

| Bug # | Function | Issue | Status |
|-------|----------|-------|--------|
| 1 | `validate_email()` | Regex too permissive | ✅ Fixed |
| 2 | `calculate_priority_score()` | Off-by-one + KeyError | ✅ Fixed |
| 3 | `sanitize_input()` | Incomplete XSS protection | ✅ Fixed |
| 4 | `parse_date()` | No error handling | ✅ Fixed |

**All 22 tests now passing!**
