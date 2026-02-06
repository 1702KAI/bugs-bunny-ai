# app/utils.py
"""
Utility functions for the task management API.
WARNING: This file contains bugs that need to be found and fixed!
"""

import re
from datetime import datetime


def validate_email(email: str) -> bool:
    """
    Validate email format.
    Returns True if valid, False otherwise.
    """
    if not email:
        return False
    # Proper RFC 5322 compliant email pattern
    # - No spaces allowed
    # - No special HTML characters like < > allowed
    # - Must have valid local part, @ symbol, and domain with TLD
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def calculate_priority_score(priority: str, days_until_due: int) -> int:
    """
    Calculate a numeric priority score for sorting tasks.
    Higher score = more urgent.

    Priority weights:
    - critical: 100
    - high: 75
    - medium: 50
    - low: 25

    Days until due modifier:
    - Overdue (negative days): +50
    - Due today (0 days): +30
    - Due within 3 days: +20
    - Due within 7 days: +10
    """
    priority_weights = {
        "critical": 100,
        "high": 75,
        "medium": 50,
        "low": 25
    }

    # Handle invalid priority values gracefully
    if priority not in priority_weights:
        raise ValueError(f"Invalid priority: {priority}. Must be one of: {list(priority_weights.keys())}")

    base_score = priority_weights[priority]

    # Fixed off-by-one errors: use <= instead of <
    if days_until_due < 0:
        urgency_bonus = 50
    elif days_until_due == 0:
        urgency_bonus = 30
    elif days_until_due <= 3:
        urgency_bonus = 20
    elif days_until_due <= 7:
        urgency_bonus = 10
    else:
        urgency_bonus = 0

    return base_score + urgency_bonus


def sanitize_input(text: str) -> str:
    """
    Sanitize user input to prevent XSS attacks.
    Removes dangerous HTML tags, event handlers, and javascript URLs.
    """
    if not text:
        return ""

    sanitized = text

    # Remove script tags (case-insensitive)
    sanitized = re.sub(r'<script[^>]*>.*?</script>', '', sanitized, flags=re.IGNORECASE | re.DOTALL)
    sanitized = re.sub(r'<script[^>]*>', '', sanitized, flags=re.IGNORECASE)
    sanitized = re.sub(r'</script>', '', sanitized, flags=re.IGNORECASE)

    # Remove event handlers (onclick, onerror, onload, etc.)
    sanitized = re.sub(r'\s*on\w+\s*=\s*["\'][^"\']*["\']', '', sanitized, flags=re.IGNORECASE)
    sanitized = re.sub(r'\s*on\w+\s*=\s*[^\s>]+', '', sanitized, flags=re.IGNORECASE)

    # Remove javascript: URLs
    sanitized = re.sub(r'javascript\s*:', '', sanitized, flags=re.IGNORECASE)

    # Remove dangerous tags entirely
    dangerous_tags = ['img', 'iframe', 'object', 'embed', 'link', 'style', 'meta']
    for tag in dangerous_tags:
        sanitized = re.sub(rf'<{tag}[^>]*>', '', sanitized, flags=re.IGNORECASE)
        sanitized = re.sub(rf'</{tag}>', '', sanitized, flags=re.IGNORECASE)

    return sanitized


def parse_date(date_string: str) -> datetime:
    """
    Parse a date string in format YYYY-MM-DD.
    Raises ValueError for invalid or improperly formatted dates.
    """
    if not date_string:
        raise ValueError("Date string cannot be empty")

    try:
        return datetime.strptime(date_string, "%Y-%m-%d")
    except ValueError as e:
        raise ValueError(f"Invalid date format: '{date_string}'. Expected format: YYYY-MM-DD") from e


def get_days_until_due(due_date_str: str) -> int:
    """
    Calculate days until a task is due.
    Negative number means overdue.
    """
    due_date = parse_date(due_date_str)
    today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    delta = due_date - today
    return delta.days
