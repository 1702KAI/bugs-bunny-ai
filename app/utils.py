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
    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
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

    BUG #2: There's an off-by-one error and missing case
    """
    priority_weights = {
        "critical": 100,
        "high": 75,
        "medium": 50,
        "low": 25
    }

    if priority not in priority_weights:
        raise ValueError(f"Invalid priority: {priority}")

    base_score = priority_weights[priority]

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

    BUG #3: This function is dangerously incomplete!
    It only handles a few cases and misses critical ones.
    """
    if not text:
        return ""

    # Remove script tags and their content
    sanitized = re.sub(r'<script[^>]*>.*?</script>', '', text, flags=re.IGNORECASE | re.DOTALL)
    # Remove all remaining HTML tags
    sanitized = re.sub(r'<[^>]*>', '', sanitized, flags=re.IGNORECASE)
    # Remove javascript: URLs
    sanitized = re.sub(r'javascript:', '', sanitized, flags=re.IGNORECASE)
    # Remove event handlers
    sanitized = re.sub(r'\bon\w+\s*=\s*["\'][^"\']*["\']', '', sanitized, flags=re.IGNORECASE)

    return sanitized


def parse_date(date_string: str) -> datetime:
    """
    Parse a date string in format YYYY-MM-DD.

    BUG #4: No error handling for invalid dates
    """
    if not date_string:
        raise ValueError("Date string cannot be empty")
    try:
        return datetime.strptime(date_string, "%Y-%m-%d")
    except ValueError:
        raise ValueError(f"Invalid date format: '{date_string}'. Expected YYYY-MM-DD")


def get_days_until_due(due_date_str: str) -> int:
    """
    Calculate days until a task is due.
    Negative number means overdue.
    """
    due_date = parse_date(due_date_str)
    today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    delta = due_date - today
    return delta.days
