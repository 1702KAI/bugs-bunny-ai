# Security Review Notes

## Task 2.3: Security Review Findings

**Reviewer:** Automated Review  
**Date:** 2026-02-06  
**Scope:** POST /tasks and GET /tasks endpoints

---

## Question 1: What happens if priority is provided in uppercase?

### Finding: **VALIDATION FAILURE**

The current implementation uses an exact match comparison:

```python
VALID_PRIORITIES = {"low", "medium", "high", "critical"}

if priority not in VALID_PRIORITIES:
    return jsonify({"error": f"Invalid priority..."}), 400
```

**Behavior:** If a user sends `"HIGH"` or `"High"` instead of `"high"`, the request will be rejected with a 400 Bad Request error.

**Impact:** Poor user experience - users may expect case-insensitive matching.

**Recommendation:** Normalize the priority to lowercase before validation:

```python
priority = data["priority"].lower()
```

---

## Question 2: What happens if the title is 10,000 characters long?

### Finding: **NO LENGTH VALIDATION**

The current implementation does not validate the length of input fields:

```python
title = data["title"]  # No length check
```

**Behavior:** A 10,000+ character title will be accepted and stored without any restrictions.

**Impact:**

- **Memory exhaustion:** Large payloads can consume excessive memory
- **Database issues:** If persisted, could exceed column limits
- **DoS potential:** Attackers could send massive payloads to exhaust resources
- **UI/UX problems:** Extremely long titles will break display formatting

**Recommendation:** Add length validation:

```python
MAX_TITLE_LENGTH = 255

if len(title) > MAX_TITLE_LENGTH:
    return jsonify({"error": f"Title exceeds maximum length of {MAX_TITLE_LENGTH} characters"}), 400
```

---

## Question 3: Is user input properly sanitized?

### Finding: **INADEQUATE SANITIZATION**

The `sanitize_input()` function in `utils.py` is imported but **never used** in the endpoints:

```python
# In main.py - sanitize_input is imported but NOT called
from app.utils import validate_email, calculate_priority_score, sanitize_input

# Title and description are used directly without sanitization
title = data["title"]  # NOT sanitized
description = data.get("description", "")  # NOT sanitized
```

Additionally, the `sanitize_input()` function itself is dangerously incomplete:

```python
# In utils.py - THIS IS NOT SUFFICIENT
def sanitize_input(text: str) -> str:
    sanitized = text.replace("<script>", "")
    sanitized = sanitized.replace("</script>", "")
    return sanitized
```

**Vulnerabilities:**

1. **XSS attacks:** Only removes exact `<script>` tags, easily bypassed with:
   - `<SCRIPT>` (case variation)
   - `<scr<script>ipt>` (nested injection)
   - `<img onerror="alert('xss')">` (event handlers)
   - `<svg onload="...">` (SVG-based XSS)
2. **SQL Injection:** No protection if connected to a database
3. **Command Injection:** No shell character escaping

**Impact:** Critical security vulnerability allowing XSS attacks.

**Recommendation:**

1. Actually call `sanitize_input()` on user inputs:

   ```python
   title = sanitize_input(data["title"])
   description = sanitize_input(data.get("description", ""))
   ```

2. Use a proper sanitization library like `bleach` or `html.escape()`:

   ```python
   import html

   def sanitize_input(text: str) -> str:
       if not text:
           return ""
       return html.escape(text)
   ```

---

## Summary of Security Issues

| Issue                                  | Severity | Status    |
| -------------------------------------- | -------- | --------- |
| Case-sensitive priority validation     | Low      | Not Fixed |
| No input length validation             | Medium   | Not Fixed |
| sanitize_input() not called            | High     | Not Fixed |
| sanitize_input() implementation flawed | Critical | Not Fixed |

---

## Recommendations

1. **Immediate:** Use `html.escape()` for all user inputs
2. **Short-term:** Add input length validation for all string fields
3. **Short-term:** Normalize priority to lowercase
4. **Long-term:** Consider using a validation library like `marshmallow` or `pydantic`
