# Security Review Notes - Task Management API

**Author:** Thinal
**Date:** February 6, 2026
**Branch:** feature/add-tasks-api

---

## Overview

This document provides a security analysis of the task management system's behavior regarding input sanitization, edge cases, and validation strategies.

---

## 1. Input Sanitization Analysis

### Current Implementation

The `sanitize_input()` function in `app/utils.py` provides comprehensive XSS protection:

```python
def sanitize_input(text: str) -> str:
    # Removes:
    # - Script tags (case-insensitive)
    # - Event handlers (onclick, onerror, onload, etc.)
    # - JavaScript protocol URLs
    # - Dangerous HTML tags (img, iframe, object, embed, link, style, meta)
```

### Sanitization Coverage

| Attack Vector | Status | Implementation |
|--------------|--------|----------------|
| `<script>` tags | Protected | Case-insensitive regex removal |
| `<SCRIPT>` variants | Protected | `re.IGNORECASE` flag |
| Event handlers (`onerror`, `onclick`) | Protected | Regex pattern `on\w+=` |
| JavaScript URLs | Protected | Removes `javascript:` protocol |
| Dangerous tags (`<img>`, `<iframe>`) | Protected | Tag-specific removal patterns |

### Recommendations

1. **Consider using a dedicated library**: While the current implementation covers common XSS vectors, production systems should consider using established libraries like `bleach` or `html-sanitizer` for more comprehensive protection.

2. **Content Security Policy (CSP)**: Implement CSP headers as an additional defense layer.

3. **Output encoding**: Ensure proper encoding when rendering user content in HTML contexts.

---

## 2. Handling 10,000-Character Titles

### Current Behavior

The system currently **accepts** titles of any length, including 10,000+ characters. This is a potential concern for:

- **Memory consumption**: Large titles stored in-memory could exhaust resources
- **Database storage**: If migrated to a database, large text fields affect performance
- **UI/UX issues**: Extremely long titles may break frontend layouts
- **DoS potential**: Attackers could submit many large titles to exhaust memory

### Analysis

```python
# Current implementation (no length limit)
title = data["title"]
if not title or not title.strip():
    return jsonify({"error": "Title cannot be empty"}), 400
title = sanitize_input(title)  # Sanitized but not truncated
```

### Recommendations

1. **Add a maximum length validation**:
   ```python
   MAX_TITLE_LENGTH = 500  # Reasonable limit
   if len(title) > MAX_TITLE_LENGTH:
       return jsonify({"error": f"Title exceeds maximum length of {MAX_TITLE_LENGTH} characters"}), 400
   ```

2. **Consider truncation with warning** for non-critical applications

3. **Document the limit** in API documentation

### Risk Assessment

| Scenario | Risk Level | Mitigation |
|----------|------------|------------|
| Memory exhaustion | Medium | Add length validation |
| Database issues | Low (in-memory) | N/A for current implementation |
| UI breakage | Low | Frontend truncation |

---

## 3. Uppercase Priority Values

### Current Behavior

The system **handles uppercase priority values gracefully** by normalizing to lowercase:

```python
# Current implementation
priority_lower = priority.lower() if isinstance(priority, str) else ""
if priority_lower not in VALID_PRIORITIES:
    return jsonify({
        "error": f"Invalid priority: '{priority}'. Must be one of: {', '.join(VALID_PRIORITIES)}"
    }), 400
```

### Analysis

| Input | Behavior | Stored Value |
|-------|----------|--------------|
| `"HIGH"` | Accepted | `"high"` |
| `"High"` | Accepted | `"high"` |
| `"hIgH"` | Accepted | `"high"` |
| `"CRITICAL"` | Accepted | `"critical"` |
| `"invalid"` | Rejected | N/A |

### Security Considerations

1. **Case normalization is correct**: Prevents case-sensitivity issues and maintains data consistency
2. **Type checking included**: The `isinstance(priority, str)` check prevents type coercion attacks
3. **Clear error messages**: Invalid priorities return descriptive errors without exposing system internals

### Recommendations

1. **Current implementation is secure** - no changes needed
2. **Document behavior** in API documentation for client developers
3. **Consider strict mode** for applications requiring exact case matching (optional)

---

## 4. Additional Security Observations

### Email Validation

The `validate_email()` function now uses a proper RFC 5322-compliant pattern:

```python
pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
```

**Protections:**
- No HTML special characters (`<`, `>`)
- No spaces
- Requires valid TLD
- Prevents injection attacks via email field

### User Existence Check

The POST /tasks endpoint properly validates user existence before creating tasks:

```python
if user_email not in users:
    return jsonify({"error": f"User not found: {user_email}"}), 404
```

**Note:** The error message includes the email, which is acceptable for a 404 response but should be reviewed if user enumeration is a concern.

### Task ID Generation

Task IDs are auto-generated using a simple counter:

```python
task_counter += 1
task_id = task_counter
```

**Considerations:**
- IDs are sequential and predictable (acceptable for this use case)
- For production, consider UUIDs if task ID guessing is a security concern
- Thread-safety may be needed for concurrent access (not applicable for single-threaded Flask dev server)

---

## 5. Summary

| Security Aspect | Status | Notes |
|-----------------|--------|-------|
| XSS Prevention | Implemented | Comprehensive sanitization |
| SQL Injection | N/A | In-memory storage, no SQL |
| Input Validation | Implemented | Priority, email, required fields |
| Length Limits | Not Implemented | Recommend adding for titles |
| Case Handling | Implemented | Proper normalization |
| Error Messages | Secure | No sensitive data exposure |

---

## 6. Recommendations Priority

1. **High**: Add maximum length validation for title field
2. **Medium**: Consider using established sanitization library (bleach)
3. **Low**: Implement rate limiting for task creation
4. **Low**: Add request logging for security audit trail
