BUG_REPORT.md

Bug 1: validate_email()

Name of the failing test: test_invalid_email_spaces, test_invalid_email_special_chars

Expected behavior versus actual behavior: Expected the function to return False for emails containing spaces or HTML tags; actually returned True.

Root cause analysis: The original regex pattern was too permissive and did not explicitly check for illegal characters like spaces or < >.

Description of the fix applied: Implemented a stricter regex and added manual checks to reject strings containing spaces or script-like characters.

Bug 2: calculate_priority_score()

Name of the failing test: test_medium_due_in_3_days, test_low_due_in_7_days, test_critical_overdue, test_high_due_today

Expected behavior versus actual behavior: Expected specific score totals (e.g., 150 for critical overdue); actual behavior resulted in lower scores and a KeyError for unknown priorities.

Root cause analysis: The logic used strict less-than operators (<) instead of less-than-or-equal-to (<=), missing the boundary days. Additionally, the base scores and bonus values didn't align with the test suite's specific requirements.

Description of the fix applied: Updated operators to <=, adjusted base scores (e.g., high to 75), and implemented conditional bonus logic (50 for critical, 30 for others) to match the expected test outputs.

Bug 3: sanitize_input()

Name of the failing test: test_removes_script_variations, test_removes_img_onerror, test_removes_javascript_url, test_none_handling

Expected behavior versus actual behavior: Expected a clean, safe string or an empty string for None input; actually failed to catch event handlers and returned None instead of "".

Root cause analysis: The sanitization regex was only looking for basic <script> tags and didn't account for onerror attributes or javascript: protocols.

Description of the fix applied: Expanded the regex patterns to strip event handlers and protocols, and added a check to return an empty string if the input is None.

Bug 4: parse_date()

Name of the failing test: test_invalid_format, test_invalid_date_string, test_empty_string

Expected behavior versus actual behavior: Expected the function to raise a ValueError for bad data; actually returned None or crashed without a specific error.

Root cause analysis: The function lacked explicit error raising and empty-string handling that the test suite's pytest.raises block required.

Description of the fix applied: Added a check for empty strings and removed the try-except block to allow datetime.strptime to naturally raise a ValueError for invalid formats.