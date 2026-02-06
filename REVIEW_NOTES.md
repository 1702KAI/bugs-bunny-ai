## Security Review

### What happens if priority is provided in uppercase?
Priority values are converted to lowercase during validation. This means inputs such as "HIGH" or "High" are accepted and stored consistently as "high".

### What happens if the title is 10,000 characters long?
Titles are required to be non-empty, but there is currently no maximum length enforced. As a result, a very long title would be accepted and stored. In a real production system, adding a length limit would help prevent storage or performance issues.

### Is user input properly sanitized?
User input is received as JSON, validated before use, and written in a controlled manner to JSON files. No user input is executed as code. While this provides basic safety at the backend level, additional sanitization or encoding would typically be handled at the frontend to fully prevent XSS.
