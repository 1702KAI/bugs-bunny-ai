# Security Review Notes

## 1. What happens if priority is provided in uppercase?

The `POST /tasks` endpoint normalizes priority to lowercase using `.lower()` before validation:

```python
priority = data["priority"].lower()
```

So submitting `"HIGH"`, `"High"`, or `"hIgH"` all work correctly and are stored as `"high"`. This is handled properly.

However, the `GET /tasks` filter also applies `.lower()` to the priority query parameter, ensuring case-insensitive filtering works as expected.

**Verdict:** Handled correctly. Case-insensitive matching is applied on both input and filtering.

## 2. What happens if the title is 10,000 characters long?

Currently, there is **no length validation** on the `title` field. A 10,000-character title would be accepted and stored in memory without any restriction. This could lead to:

- **Memory exhaustion:** An attacker could repeatedly submit tasks with extremely long titles to consume server memory.
- **Performance degradation:** Large payloads slow down serialization and response times.
- **UI/display issues:** Downstream consumers (frontends, reports) may not handle extremely long titles gracefully.

**Recommendation:** Add a maximum length validation (e.g., 500 characters) for the title field:
```python
if len(title) > 500:
    return jsonify({"error": "Title must be 500 characters or less"}), 400
```

## 3. Is user input properly sanitized?

After the bug fixes, input sanitization has been significantly improved but still has considerations:

**What is sanitized:**
- The `title` and `description` fields are passed through `sanitize_input()` which strips HTML tags, script content, event handlers, and JavaScript URLs.
- Email validation uses a strict regex that prevents HTML injection via email fields.

**Remaining concerns:**
- **No rate limiting:** There is no protection against brute-force or flood attacks on any endpoint.
- **No input length limits:** Fields like `title` and `description` have no maximum length enforced.
- **No authentication/authorization:** Any client can create users and tasks without authentication. There's no ownership verification — any user can create tasks for any other user's email.
- **In-memory storage:** All data is lost on restart, but while running, there are no limits on the number of users or tasks that can be created (potential DoS via resource exhaustion).
- **No CSRF protection:** The API does not implement CSRF tokens.
- **Secret key in config:** The default `SECRET_KEY` is hardcoded as a fallback (`"dev-secret-key-change-in-production"`), which is acceptable for development but must be changed in production.

**Verdict:** Basic XSS sanitization is in place after fixes, but the application lacks defense-in-depth measures (rate limiting, input length validation, authentication) that would be required for a production deployment.
