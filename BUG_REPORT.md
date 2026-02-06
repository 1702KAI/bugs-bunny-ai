# Bug Report

## Bug #1: validate_email() - Regex Too Permissive

### Failing Tests
- `test_invalid_email_spaces`
- `test_invalid_email_special_chars`

### Expected vs Actual Behavior
- **Expected:** `validate_email("user @example.com")` should return `False`
- **Actual:** Returns `True` (accepts invalid email with spaces)
- **Expected:** `validate_email("user<script>@example.com")` should return `False`
- **Actual:** Returns `True` (accepts email with special characters)

### Root Cause
The regex pattern `r".+@.+"` is too permissive. It only checks for any character(s) followed by `@` followed by any character(s). It doesn't validate:
- No spaces allowed
- Proper domain format (needs a dot and TLD)
- No special HTML characters

### Fix Applied
Changed regex to: `r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"`

---

## Bug #2: calculate_priority_score() - Off-by-One Error & Missing Error Handling

### Failing Tests
- `test_medium_due_in_3_days`
- `test_low_due_in_7_days`
- `test_invalid_priority`

### Expected vs Actual Behavior
- **Expected:** `calculate_priority_score("medium", 3)` should return `70` (50 + 20 bonus)
- **Actual:** Returns `60` (50 + 10 bonus) - day 3 not included in "within 3 days"
- **Expected:** `calculate_priority_score("low", 7)` should return `35` (25 + 10 bonus)
- **Actual:** Returns `25` (25 + 0 bonus) - day 7 not included in "within 7 days"
- **Expected:** `calculate_priority_score("urgent", 5)` should raise `ValueError`
- **Actual:** Raises `KeyError`

### Root Cause
1. Off-by-one error: Using `<` instead of `<=` for day comparisons
2. Missing validation: No check for invalid priority values before dictionary lookup

### Fix Applied
1. Changed `< 3` to `<= 3` and `< 7` to `<= 7`
2. Added validation to raise `ValueError` for invalid priority values

---

## Bug #3: sanitize_input() - Incomplete XSS Sanitization

### Failing Tests
- `test_removes_script_variations`
- `test_removes_img_onerror`
- `test_removes_javascript_url`

### Expected vs Actual Behavior
- **Expected:** `sanitize_input("<SCRIPT>alert('xss')</SCRIPT>")` should remove script content
- **Actual:** Uppercase tags bypass the filter
- **Expected:** `sanitize_input('<img onerror="alert(1)">')` should remove onerror
- **Actual:** img tags with event handlers pass through
- **Expected:** `sanitize_input('<a href="javascript:...">')` should remove javascript URLs
- **Actual:** javascript: URLs pass through

### Root Cause
The function only removes exact lowercase `<script>` and `</script>` strings. It doesn't handle:
- Case variations (uppercase, mixed case)
- Other XSS vectors (img onerror, javascript: URLs, event handlers)

### Fix Applied
Use `html.escape()` to properly escape all HTML entities, which neutralizes all XSS vectors.

---

## Bug #4: parse_date() - No Error Handling

### Failing Tests
- `test_invalid_format`
- `test_invalid_date_string`
- `test_empty_string`

*Note: These tests are currently passing because they expect ValueError to be raised, and the underlying `datetime.strptime` already raises ValueError for invalid formats.*

### Root Cause
The function has no explicit error handling - it relies on the underlying exception from `datetime.strptime`.

### Fix Applied
Added explicit error handling with descriptive error messages for empty strings and invalid formats.
