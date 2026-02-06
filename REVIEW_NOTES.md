# Security Review Notes

### 1. What happens if priority is provided in uppercase?

- The implementation handles uppercase priority values correctly. In the `POST /tasks` endpoint, the priority is converted to lowercase before validation:

```python
priority = data["priority"].lower() if isinstance(data["priority"], str) else data["priority"]
```

So if a user submits `"HIGH"` or `"High"`, it will be normalized to `"high"` and accepted as valid.

---

### 2. What happens if the title is 10,000 characters long?

- Currently, there is **no validation** on title length. A 10,000-character title would be accepted and stored without any truncation or rejection.

---

### 3. Is user input properly sanitized?

- No, user input is NOT properly sanitized.\*\* The current `sanitize_input()` function is dangerously incomplete:

```python
sanitized = text.replace("<script>", "")
sanitized = sanitized.replace("</script>", "")
```

**Security Vulnerabilities:**

1. **Case Sensitivity:** `<SCRIPT>` or `<ScRiPt>` would bypass the filter
2. **Other XSS Vectors Not Handled:**
   - `<img src="x" onerror="alert(1)">`
   - `<a href="javascript:alert(1)">click</a>`
   - `<svg onload="alert(1)">`
   - Event handlers like `onclick`, `onmouseover`
3. **Partial Tag Bypass:** `<scr<script>ipt>` would become `<script>` after sanitization
