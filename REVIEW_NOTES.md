# Security Review Notes

**Reviewer:** Aaron Emmanuel  
**Date:** 2026-02-06

---

## Question 1: What happens if priority is provided in uppercase?

**Behavior:** The task creation will fail with a **400 Bad Request** error.

**Analysis:**
- The `VALID_PRIORITIES` set contains lowercase values only: `{"low", "medium", "high", "critical"}`
- Priority validation uses exact string matching: `if priority not in VALID_PRIORITIES`
- Passing `"HIGH"` or `"High"` will not match and returns:
  ```json
  {"error": "Invalid priority. Must be one of: critical, high, low, medium"}
  ```

**Recommendation:** Consider normalizing priority to lowercase before validation:
```python
priority = data["priority"].lower()
```

---

## Question 2: What happens if the title is 10,000 characters long?

**Behavior:** The task will be created successfully - **no length validation exists**.

**Analysis:**
- There is no maximum length check on the `title` field
- This could lead to:
  - **Database storage issues** (if using a DB with column limits)
  - **Memory consumption** for in-memory storage
  - **UI rendering problems** on the frontend
  - **Potential DoS attack vector** via resource exhaustion

**Recommendation:** Add a maximum length validation:
```python
MAX_TITLE_LENGTH = 500
if len(title) > MAX_TITLE_LENGTH:
    return jsonify({"error": f"Title must be under {MAX_TITLE_LENGTH} characters"}), 400
```

---

## Question 3: Is user input properly sanitized?

**Behavior:** **NO** - Input sanitization is dangerously incomplete.

**Analysis of `sanitize_input()` function:**
The current implementation only removes exact `<script>` and `</script>` tags:

```python
sanitized = text.replace("<script>", "")
sanitized = sanitized.replace("</script>", "")
```

**Vulnerabilities NOT addressed:**

| Attack Vector | Example | Blocked? |
|--------------|---------|----------|
| Uppercase script tags | `<SCRIPT>alert(1)</SCRIPT>` | ❌ No |
| Mixed case | `<ScRiPt>alert(1)</sCrIpT>` | ❌ No |
| Image onerror XSS | `<img src=x onerror=alert(1)>` | ❌ No |
| JavaScript URLs | `<a href="javascript:alert(1)">` | ❌ No |
| Event handlers | `<div onmouseover="alert(1)">` | ❌ No |
| SVG XSS | `<svg onload=alert(1)>` | ❌ No |
| Encoded attacks | `%3Cscript%3E` | ❌ No |

**Recommendation:** Use a proper HTML sanitization library like `bleach` or `html-sanitizer`:
```python
import bleach
sanitized = bleach.clean(text, tags=[], strip=True)
```

---

## Summary

| Issue | Severity | Status |
|-------|----------|--------|
| Uppercase priority rejected | Low | By Design (could enhance) |
| No title length limit | Medium | ⚠️ Needs Fix |
| Incomplete XSS sanitization | **Critical** | 🔴 Needs Immediate Fix |
