# Bug Report

## Bug #1: `validate_email()` - Overly Permissive Regex

**Failing Tests:**
- `test_invalid_email_spaces` - `validate_email("user @example.com")` returned `True` instead of `False`
- `test_invalid_email_special_chars` - `validate_email("user<script>@example.com")` returned `True` instead of `False`

**Expected Behavior:** Emails with spaces or special characters like `<`, `>` should be rejected as invalid.

**Actual Behavior:** The regex `r".+@.+"` matched virtually any string containing an `@` symbol, including ones with spaces and HTML-unsafe characters.

**Root Cause:** The regex pattern `.+@.+` uses `.` which matches any character (including spaces and special characters) and only requires at least one character before and after the `@`. It has no domain validation at all.

**Fix Applied:** Replaced with a proper email regex `r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"` that enforces:
- Only alphanumeric and standard email characters before `@`
- A valid domain with at least one dot
- A TLD of at least 2 characters
- No spaces or HTML characters allowed

---

## Bug #2: `calculate_priority_score()` - Off-by-One Errors and Missing Error Handling

**Failing Tests:**
- `test_medium_due_in_3_days` - `calculate_priority_score("medium", 3)` returned `60` instead of `70`
- `test_low_due_in_7_days` - `calculate_priority_score("low", 7)` returned `25` instead of `35`
- `test_invalid_priority` - `calculate_priority_score("urgent", 5)` raised `KeyError` instead of `ValueError`

**Expected Behavior:**
- A task due in exactly 3 days should get the "within 3 days" bonus (+20)
- A task due in exactly 7 days should get the "within 7 days" bonus (+10)
- An invalid priority string should raise a `ValueError`

**Actual Behavior:**
- `< 3` excluded the boundary value 3, so 3 days fell into the 7-day bracket (+10 instead of +20)
- `< 7` excluded the boundary value 7, so 7 days fell into the "else" bracket (+0 instead of +10)
- Invalid priority caused a `KeyError` from the dictionary lookup

**Root Cause:** Off-by-one errors using strict `<` instead of `<=` in the comparison conditions. Missing validation for invalid priority keys before dictionary access.

**Fix Applied:**
- Changed `< 3` to `<= 3` and `< 7` to `<= 7`
- Added a check `if priority not in priority_weights: raise ValueError(...)` before the dictionary lookup

---

## Bug #3: `sanitize_input()` - Dangerously Incomplete XSS Sanitization

**Failing Tests:**
- `test_removes_script_variations` - `<SCRIPT>alert('xss')</SCRIPT>` was only lowercased, content not removed
- `test_removes_img_onerror` - `<img src="x" onerror="alert(1)">` was not sanitized at all
- `test_removes_javascript_url` - `<a href="javascript:alert(1)">` was not sanitized at all

**Expected Behavior:** All HTML tags, script content, event handlers, and JavaScript URLs should be stripped from input.

**Actual Behavior:** The function only did exact case-sensitive string replacement of `<script>` and `</script>` tags. Uppercase variations, other HTML tags, inline event handlers, and JavaScript URIs were all passed through unchanged.

**Root Cause:** The sanitization used simple `str.replace()` for only two specific strings, making it trivially bypassable via case changes or alternative XSS vectors.

**Fix Applied:** Replaced with comprehensive regex-based sanitization:
1. `re.sub(r'<script[^>]*>.*?</script>', ...)` - Removes script tags AND their content (case-insensitive)
2. `re.sub(r'<[^>]*>', ...)` - Removes all remaining HTML tags
3. `re.sub(r'javascript:', ...)` - Removes JavaScript URLs
4. `re.sub(r'\bon\w+\s*=\s*["\'][^"\']*["\']', ...)` - Removes inline event handlers

---

## Bug #4: `parse_date()` - No Error Handling for Invalid Dates

**Failing Tests:**
- `test_invalid_format` - `parse_date("15-02-2026")` raised raw `ValueError` without clear message
- `test_invalid_date_string` - `parse_date("not-a-date")` raised raw `ValueError`
- `test_empty_string` - `parse_date("")` raised raw `ValueError`

**Expected Behavior:** Invalid date strings should raise a `ValueError` with a clear, informative error message.

**Actual Behavior:** The function passed the input directly to `datetime.strptime()` with no validation, which raised Python's default `ValueError` with a non-descriptive message. Empty strings were not checked.

**Root Cause:** No input validation or error handling around the `strptime` call.

**Fix Applied:**
- Added an explicit empty string check that raises `ValueError("Date string cannot be empty")`
- Wrapped `strptime` in a try/except that re-raises with a descriptive message: `"Invalid date format: '...'. Expected YYYY-MM-DD"`
