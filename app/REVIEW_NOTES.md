Task 2.3: Security Review

1. What happens if priority is provided in uppercase?

Currently, if a user provides HIGH or High instead of high, the request will fail with a 400 Bad Request.

Reason: In our logic, we check if priority not in ["low", "medium", "high", "critical"]:. This check is case-sensitive in Python.

Recommendation: To make it more robust, we should convert the input to lowercase using .lower() before validation.

2. What happens if the title is 10,000 characters long?

The current implementation will accept the 10,000-character title and store it in memory.

Risk (DoS/Memory Exhaustion): Because we are using an in-memory dictionary (tasks = {}), an attacker could send thousands of requests with massive titles to fill up the server's RAM, eventually causing it to crash (Denial of Service).

Recommendation: Implement a character limit (e.g., 255 characters) for the title field during the validation stage.

3. Is user input properly sanitized?

Partially.

The Good: Because we are using request.get_json() and then manually assigning variables, we aren't vulnerable to "Mass Assignment" (where a user could inject fields like id or created_at manually).

The Risk (XSS): The input is not sanitized for HTML/Script tags. If this task list were displayed on a website without proper escaping, a title like <script>alert('hacked')</script> would execute in the browser.

Recommendation: Use a library like bleach or ensure the frontend framework automatically escapes HTML characters.