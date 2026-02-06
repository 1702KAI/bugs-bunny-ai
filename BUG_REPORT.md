Issues identified in `app/utils.py` - while running test suite

22 tests intotal
14 passed
8 failed


## Bug 1: validate_email()
### Failing Tests
- TestValidateEmail::test_invalid_email_spaces  
- TestValidateEmail::test_invalid_email_special_chars  

### Expected Behavior
The function should return `False` for invalid email formats, including emails containing spaces or embedded script tags.

### Actual Behavior
The function incorrectly returns `True` for invalid email strings such as `"user @example.com"` and `"user<script>@example.com"`.

### Root Cause Analysis
The regular expression used for email validation (`.+@.+`) is too permissive. It only checks for the presence of an `@` symbol and does not restrict spaces or special characters.

### Fix Applied
The validation logic was updated to use a stricter regular expression that enforces a basic email structure and rejects spaces and unsafe characters.


## Bug 2: calculate_priority_score()
### Failing Tests
- TestCalculatePriorityScore::test_medium_due_in_3_days  
- TestCalculatePriorityScore::test_low_due_in_7_days  
- TestCalculatePriorityScore::test_invalid_priority  

### Expected Behavior
The function should correctly calculate the priority score based on both priority level and days until due, and handle invalid priority values gracefully.

### Actual Behavior
- Tasks due in exactly 3 or 7 days receive a lower score than expected.
- Providing an invalid priority value causes the function to raise a `KeyError`.

### Root Cause Analysis
There are two issues:
1. Off-by-one errors in the conditional checks for days until due.
2. Direct dictionary access is used without validating whether the priority key exists.

### Fix Applied
The conditional logic was corrected to include boundary values (≤ 3 days and ≤ 7 days), and invalid priorities are now handled safely instead of causing a runtime exception.


## Bug 3: sanitize_input()
### Failing Tests
- TestSanitizeInput::test_removes_script_variations  
- TestSanitizeInput::test_removes_img_onerror  
- TestSanitizeInput::test_removes_javascript_url  

### Expected Behavior
The function should remove or neutralize common XSS attack vectors such as script tags, event handlers, and JavaScript URLs.

### Actual Behavior
The function only removes lowercase `<script>` tags and fails to handle:
- Case variations (e.g. `<SCRIPT>`)
- Inline event handlers (e.g. `onerror`)
- JavaScript URLs

### Root Cause Analysis
The sanitization logic is too limited and relies on simple string replacement, which does not cover common XSS patterns.

### Fix Applied
The function was updated to apply a more robust sanitization approach by escaping potentially dangerous HTML content instead of relying on partial string replacement.


## Bug 4: parse_date()
### Failing Tests
None.

### Expected Behavior
The function should correctly parse valid dates and handle invalid or empty input safely.

### Actual Behavior
All related tests pass as expected.

### Root Cause Analysis
The existing implementation already aligns with the test expectations.

### Fix Applied
No changes were required for this function.
