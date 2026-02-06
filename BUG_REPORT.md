# Bug Report

## Task 3.2: Bug Documentation

**Date:** 2026-02-06  
**Test Command:** `pytest tests/test_utils.py -v`  
**Result:** 8 failed, 14 passed

---

## Bug #1: Invalid Email Validation - No @ Symbol

### Failing Test

`TestValidateEmail::test_invalid_email_no_at_symbol`

### Expected Behavior

`validate_email("userexample.com")` should return `False` because the email lacks an `@` symbol.

### Actual Behavior

Returns `True` - the email is incorrectly accepted as valid.

### Root Cause Analysis

The regex pattern `r".+@.+"` uses `re.match()` which only matches from the beginning of the string. However, the pattern `.+` matches any character including nothing before `@`. The real issue is that the test string `"userexample.com"` doesn't contain `@`, but the pattern is too permissive.

**Location:** `app/utils.py`, line 19

```python
pattern = r".+@.+"  # Too permissive - doesn't validate proper email structure
```

### Fix Description

Use a stricter regex pattern that properly validates email format:

```python
pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
```

---

## Bug #2: Invalid Email Validation - Missing Domain

### Failing Test

`TestValidateEmail::test_invalid_email_no_domain`

### Expected Behavior

`validate_email("user@")` should return `False` because there's no domain after `@`.

### Actual Behavior

Returns `True` - the incomplete email is accepted.

### Root Cause Analysis

The pattern `.+@.+` requires at least one character after `@`, but `re.match()` doesn't require the pattern to match the entire string. The `user@` passes because `user@` matches the pattern partially.

**Location:** `app/utils.py`, line 19

### Fix Description

The stricter regex with `$` anchor and domain validation will fix this.

---

## Bug #3: Invalid Email Validation - Spaces in Email

### Failing Test

`TestValidateEmail::test_invalid_email_spaces`

### Expected Behavior

`validate_email("user @example.com")` should return `False` because emails cannot contain spaces.

### Actual Behavior

Returns `True` - email with space is accepted.

### Root Cause Analysis

The `.+` pattern matches any character including spaces. The regex doesn't exclude whitespace characters.

**Location:** `app/utils.py`, line 19

### Fix Description

Use a character class that excludes whitespace: `[a-zA-Z0-9._%+-]+`

---

## Bug #4: Priority Score - Off-by-One Error (3 days)

### Failing Test

`TestCalculatePriorityScore::test_medium_due_in_3_days`

### Expected Behavior

`calculate_priority_score("medium", 3)` should return `70` (50 base + 20 bonus for "within 3 days").

### Actual Behavior

Returns `60` (50 base + 10 bonus) - the 3-day boundary is not included.

### Root Cause Analysis

The condition uses `< 3` instead of `<= 3`. When `days_until_due` is exactly 3, it falls through to the next condition.

**Location:** `app/utils.py`, line 57

```python
elif days_until_due < 3:  # BUG: Should be <= 3
    urgency_bonus = 20
```

### Fix Description

Change `< 3` to `<= 3`:

```python
elif days_until_due <= 3:
    urgency_bonus = 20
```

---

## Bug #5: Priority Score - Off-by-One Error (7 days)

### Failing Test

`TestCalculatePriorityScore::test_low_due_in_7_days`

### Expected Behavior

`calculate_priority_score("low", 7)` should return `35` (25 base + 10 bonus for "within 7 days").

### Actual Behavior

Returns `25` (25 base + 0 bonus) - the 7-day boundary is not included.

### Root Cause Analysis

The condition uses `< 7` instead of `<= 7`. When `days_until_due` is exactly 7, it falls through to the else clause.

**Location:** `app/utils.py`, line 59

```python
elif days_until_due < 7:  # BUG: Should be <= 7
    urgency_bonus = 10
```

### Fix Description

Change `< 7` to `<= 7`:

```python
elif days_until_due <= 7:
    urgency_bonus = 10
```

---

## Bug #6: Priority Score - Invalid Priority Handling

### Failing Test

`TestCalculatePriorityScore::test_invalid_priority`

### Expected Behavior

`calculate_priority_score("urgent", 5)` should raise a `ValueError` for an invalid priority.

### Actual Behavior

Raises `KeyError` when trying to access `priority_weights["urgent"]`.

### Root Cause Analysis

The function directly accesses the dictionary without checking if the key exists, causing an unhandled `KeyError`.

**Location:** `app/utils.py`, line 50

```python
base_score = priority_weights[priority]  # Raises KeyError if invalid
```

### Fix Description

Add validation before dictionary access:

```python
if priority not in priority_weights:
    raise ValueError(f"Invalid priority: {priority}. Must be one of: {list(priority_weights.keys())}")
base_score = priority_weights[priority]
```

---

## Bug #7: Sanitize Input - Case Sensitivity

### Failing Test

`TestSanitizeInput::test_removes_script_variations`

### Expected Behavior

`sanitize_input("<SCRIPT>alert('xss')</SCRIPT>")` should remove the script content.

### Actual Behavior

Returns `"<SCRIPT>alert('xss')</SCRIPT>"` unchanged - uppercase tags are not sanitized.

### Root Cause Analysis

The `replace()` function is case-sensitive. Only exact matches of `<script>` and `</script>` (lowercase) are removed.

**Location:** `app/utils.py`, lines 78-79

```python
sanitized = text.replace("<script>", "")
sanitized = sanitized.replace("</script>", "")
```

### Fix Description

Use case-insensitive replacement or HTML escaping:

```python
import html
def sanitize_input(text: str) -> str:
    if not text:
        return ""
    return html.escape(text)
```

---

## Bug #8: Sanitize Input - Incomplete XSS Protection

### Failing Tests

- `TestSanitizeInput::test_removes_img_onerror`
- `TestSanitizeInput::test_removes_javascript_url`

### Expected Behavior

- `sanitize_input('<img src="x" onerror="alert(1)">')` should remove `onerror` attribute
- `sanitize_input('<a href="javascript:alert(1)">click</a>')` should remove `javascript:` URL

### Actual Behavior

Both inputs are returned unchanged - only `<script>` tags are targeted.

### Root Cause Analysis

The sanitization function only handles `<script>` tags. XSS attacks can occur through:

- Event handlers (`onerror`, `onload`, `onclick`, etc.)
- JavaScript URLs (`javascript:`)
- Other HTML elements (`<svg>`, `<iframe>`, etc.)

**Location:** `app/utils.py`, lines 77-80

### Fix Description

Use proper HTML escaping to neutralize all HTML:

```python
import html

def sanitize_input(text: str) -> str:
    if not text:
        return ""
    return html.escape(text)
```

This converts `<` to `&lt;`, `>` to `&gt;`, etc., making all HTML tags inert.

---

## Summary

| Bug # | Test                                                   | Root Cause              | Severity |
| ----- | ------------------------------------------------------ | ----------------------- | -------- |
| 1     | test_invalid_email_no_at_symbol                        | Permissive regex        | Medium   |
| 2     | test_invalid_email_no_domain                           | Permissive regex        | Medium   |
| 3     | test_invalid_email_spaces                              | Permissive regex        | Medium   |
| 4     | test_medium_due_in_3_days                              | Off-by-one (`< 3`)      | Low      |
| 5     | test_low_due_in_7_days                                 | Off-by-one (`< 7`)      | Low      |
| 6     | test_invalid_priority                                  | Missing key validation  | Medium   |
| 7     | test_removes_script_variations                         | Case-sensitive replace  | Critical |
| 8     | test_removes_img_onerror / test_removes_javascript_url | Incomplete sanitization | Critical |
