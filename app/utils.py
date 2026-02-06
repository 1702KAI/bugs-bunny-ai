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
    if not isinstance(email, str) or not email:
        return False

    # Reject spaces and obvious injection-like characters
    if any(ch.isspace() for ch in email):
        return False
    if "<" in email or ">" in email:
        return False

    # Basic but stricter email regex for tests
    pattern = r"^[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}$"
    return bool(re.match(pattern, email))



def calculate_priority_score(priority: str, days_until_due: int) -> int:
    """
    Calculate a numeric priority score for sorting tasks.
    Higher score = more urgent.
    """
    priority_weights = {
        "critical": 100,
        "high": 75,
        "medium": 50,
        "low": 25
    }

    if not isinstance(priority, str):
        raise ValueError("Invalid priority")

    priority_key = priority.lower().strip()
    if priority_key not in priority_weights:
        raise ValueError("Invalid priority")

    base_score = priority_weights[priority_key]

    # Fix off-by-one: <= 3 and <= 7
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
    Sanitize user input to reduce XSS vectors.
    """
    if text is None:
        return ""
    if not isinstance(text, str):
        text = str(text)

    # Remove script blocks (case-insensitive)
    sanitized = re.sub(r"(?is)<\s*script[^>]*>.*?<\s*/\s*script\s*>", "", text)

    # Remove common inline event handlers like onerror=, onclick= etc.
    sanitized = re.sub(r'(?i)\son\w+\s*=\s*(".*?"|\'.*?\'|[^\s>]+)', "", sanitized)

    # Remove javascript: URLs (case-insensitive)
    sanitized = re.sub(r'(?i)javascript\s*:', "", sanitized)

    return sanitized


def parse_date(date_string: str) -> datetime:
    """
    Parse a date string in format YYYY-MM-DD.

    BUG #4: No error handling for invalid dates
    """
    # What happens if the format is wrong?
    return datetime.strptime(date_string, "%Y-%m-%d")


def get_days_until_due(due_date_str: str) -> int:
    """
    Calculate days until a task is due.
    Negative number means overdue.
    """
    due_date = parse_date(due_date_str)
    today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    delta = due_date - today
    return delta.days
