# BUG REPORT

## 1) validate_email()

### Failing tests
- TestValidateEmail::test_invalid_email_spaces
- TestValidateEmail::test_invalid_email_special_chars

### Expected vs Actual
- Expected: emails containing spaces or HTML/script-like input should be invalid (False).
- Actual: function returned True for invalid inputs.

### Root cause
Regex `.+@.+` was too permissive and did not reject whitespace or unsafe characters.

### Fix applied
Implemented stricter email validation:
- Reject whitespace and `<` / `>` characters
- Use a stricter anchored regex for typical email formats


## 2) calculate_priority_score()

### Failing tests
- TestCalculatePriorityScore::test_medium_due_in_3_days
- TestCalculatePriorityScore::test_low_due_in_7_days
- TestCalculatePriorityScore::test_invalid_priority

### Expected vs Actual
- Expected: due in exactly 3 days gets +20, due in exactly 7 days gets +10, invalid priority raises ValueError.
- Actual: off-by-one comparisons missed boundary cases; invalid priority caused KeyError.

### Root cause
Used `< 3` and `< 7` instead of `<=` boundaries and directly indexed dict without validating key.

### Fix applied
- Normalized priority to lowercase and validated membership
- Raised ValueError for invalid priority
- Corrected boundary conditions to `<= 3` and `<= 7`


## 3) sanitize_input()

### Failing tests
- TestSanitizeInput::test_removes_script_variations
- TestSanitizeInput::test_removes_img_onerror
- TestSanitizeInput::test_removes_javascript_url

### Expected vs Actual
- Expected: remove script blocks, inline event handlers, and javascript: URLs.
- Actual: only removed exact lowercase <script> tags, leaving many XSS vectors intact.

### Root cause
Sanitization was incomplete and case-sensitive, and did not address attributes like onerror or javascript URLs.

### Fix applied
Used regex-based sanitization to:
- Remove script blocks case-insensitively
- Strip inline event handlers (on*)
- Remove javascript: URL schemes
