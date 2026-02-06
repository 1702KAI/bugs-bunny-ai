# Project Summary

## Bugs Bunny AI - Task Management API

**Date:** 2026-02-06  
**Author:** Assisted by AI (Google Gemini - Antigravity)

---

## Implementation Summary

This project implements a Flask-based Task Management API with the following components:

### Endpoints Implemented

#### 1. POST /tasks (Task 2.1)

Creates a new task with validation.

**Required Fields:**

- `title` - Task title
- `user_email` - Email of the user (must exist)
- `priority` - One of: `low`, `medium`, `high`, `critical`

**Response Codes:**

- `201 Created` - Task successfully created
- `400 Bad Request` - Missing fields or invalid priority
- `404 Not Found` - User does not exist

**Features:**

- Auto-generates unique task IDs
- Validates priority against allowed values
- Checks user existence before task creation
- Supports optional fields: `description`, `status`, `due_date`

#### 2. GET /tasks (Task 2.2)

Retrieves tasks with filtering and sorting capabilities.

**Filtering (Query Parameters):**

- `user_email` - Filter by user
- `status` - Filter by status (`pending`, `in_progress`, `completed`)
- `priority` - Filter by priority level

**Sorting (Query Parameters):**

- `sort_by` - Options: `priority_score`, `due_date`, `created_at`
- `sort_order` - `asc` (default) or `desc`

---

## Bugs Fixed (Task 3.3)

### Bug 1: `validate_email()` - Permissive Regex

**Problem:** The regex `r".+@.+"` accepted invalid emails like `user@`, `userexample.com`, and emails with spaces.

**Fix:** Replaced with strict regex pattern:

```python
pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
```

---

### Bug 2: `calculate_priority_score()` - Off-by-One Errors & Missing Validation

**Problems:**

1. Used `< 3` and `< 7` instead of `<= 3` and `<= 7` (boundary days excluded)
2. Raised `KeyError` for invalid priorities instead of `ValueError`

**Fix:**

```python
# Added priority validation
if priority not in priority_weights:
    raise ValueError(f"Invalid priority: {priority}...")

# Fixed boundary conditions
elif days_until_due <= 3:  # Was < 3
    urgency_bonus = 20
elif days_until_due <= 7:  # Was < 7
    urgency_bonus = 10
```

---

### Bug 3: `sanitize_input()` - Incomplete XSS Protection

**Problems:**

1. Only removed exact `<script>` and `</script>` (case-sensitive)
2. Didn't handle `<SCRIPT>`, `<img onerror=...>`, `javascript:` URLs, etc.

**Fix:** Complete rewrite using regex:

```python
# Remove script tags AND their content
sanitized = re.sub(r'<script[^>]*>.*?</script>', '', text, flags=re.IGNORECASE | re.DOTALL)

# Remove all other HTML tags
sanitized = re.sub(r'<[^>]*>', '', sanitized, flags=re.IGNORECASE)

# Remove javascript: URLs
sanitized = re.sub(r'javascript:', '', sanitized, flags=re.IGNORECASE)
```

---

### Bug 4: `parse_date()` - No Error Handling

**Problem:** Invalid date strings caused unhandled exceptions.

**Fix:**

```python
if not date_string or not isinstance(date_string, str):
    raise ValueError("Date string cannot be empty or None")

try:
    return datetime.strptime(date_string, "%Y-%m-%d")
except ValueError:
    raise ValueError(f"Invalid date format: '{date_string}'. Expected format: YYYY-MM-DD")
```

---

## AI Tools Used

| Tool                            | Purpose                                                                               |
| ------------------------------- | ------------------------------------------------------------------------------------- |
| **Google Gemini (Antigravity)** | Primary AI assistant for code analysis, implementation, bug fixing, and documentation |

---

## Reflection: Where AI Was Helpful vs. Where It Struggled

### ✅ Where AI Was Helpful

1. **Rapid Implementation**
   - Quickly understood the requirements and implemented both endpoints correctly
   - Generated proper validation logic, error handling, and response codes

2. **Bug Identification & Analysis**
   - Accurately identified all bugs from the test file expectations
   - Provided clear root cause analysis for each issue
   - Generated comprehensive documentation (BUG_REPORT.md, REVIEW_NOTES.md)

3. **Security Awareness**
   - Recognized the XSS vulnerabilities in `sanitize_input()`
   - Identified that the function was imported but never called in endpoints
   - Provided multiple sanitization approaches

4. **Test-Driven Fixes**
   - Used test expectations to guide the implementation
   - Iteratively refined fixes until all 22 tests passed

5. **Documentation**
   - Created well-structured markdown documents
   - Provided code examples and fix descriptions

### ⚠️ Where AI Struggled

1. **Initial Sanitization Approach**
   - First attempt used `html.escape()` which escapes characters but keeps the text
   - Tests expected complete removal of malicious content, not escaping
   - Required iteration to understand test expectations correctly

2. **Test Output Parsing**
   - PowerShell output truncation made it difficult to see full test results
   - Had to use multiple approaches (`--tb=short`, `-q`, individual test runs) to verify fixes

3. **Assumptions About Test Behavior**
   - Initially assumed `html.escape()` was sufficient for XSS protection (it is, technically)
   - Had to adjust to match the specific test expectations (removal vs. escaping)

### Key Learnings

1. **Test expectations matter** - Even if a security approach is valid, tests define the expected behavior
2. **Iterative refinement** - Complex bugs may require multiple fix attempts
3. **Understanding context** - Reading test files early helps understand what "fixed" means for each bug

---

## Test Results

```
22 passed in 0.11s
```

All tests in `tests/test_utils.py` now pass after the bug fixes.

---

## Files Modified

| File              | Changes                                    |
| ----------------- | ------------------------------------------ |
| `app/main.py`     | Added POST /tasks and GET /tasks endpoints |
| `app/utils.py`    | Fixed all 4 utility functions              |
| `REVIEW_NOTES.md` | Security review documentation (new)        |
| `BUG_REPORT.md`   | Bug documentation for failing tests (new)  |
| `SUMMARY.md`      | This summary document (new)                |
