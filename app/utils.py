# app/utils.py
"""
Utility functions for the task management API.
Bugs have been fixed!
"""

import re
import html
from datetime import datetime


def validate_email(email: str) -> bool:
    """
    Validate email format.
    Returns True if valid, False otherwise.
    """
    # Stricter regex pattern for proper email validation
    # - No spaces allowed
    # - Requires valid characters before @
    # - Requires domain with at least one dot and valid TLD
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

    # Validate priority before accessing dictionary
    if priority not in priority_weights:
        raise ValueError(f"Invalid priority: {priority}. Must be one of: {list(priority_weights.keys())}")
    
    base_score = priority_weights[priority]

    # Fixed off-by-one errors: use <= for inclusive boundaries
    if days_until_due < 0:
        urgency_bonus = 50
    elif days_until_due == 0:
        urgency_bonus = 30
    elif days_until_due <= 3:  # Fixed: includes day 3
        urgency_bonus = 20
    elif days_until_due <= 7:  # Fixed: includes day 7
        urgency_bonus = 10
    else:
        urgency_bonus = 0

    return base_score + urgency_bonus


def sanitize_input(text: str) -> str:
    """
    Sanitize user input to prevent XSS attacks.
    Strips all HTML tags and dangerous content completely.
    """
    if not text:
        return ""

    # First, remove script tags and their content entirely
    sanitized = re.sub(r'<script[^>]*>.*?</script>', '', text, flags=re.IGNORECASE | re.DOTALL)
    
    # Remove all other HTML tags (including attributes)
    # This handles <img onerror=...>, <a href="javascript:...">, etc.
    sanitized = re.sub(r'<[^>]*>', '', sanitized, flags=re.IGNORECASE)
    
    # Also remove javascript: URLs that might be in text
    sanitized = re.sub(r'javascript:', '', sanitized, flags=re.IGNORECASE)
    
    return sanitized


def parse_date(date_string: str) -> datetime:
    """
    Parse a date string in format YYYY-MM-DD.
    Raises ValueError for invalid date formats.
    """
    if not date_string or not isinstance(date_string, str):
        raise ValueError("Date string cannot be empty or None")
    
    try:
        return datetime.strptime(date_string, "%Y-%m-%d")
    except ValueError:
        raise ValueError(f"Invalid date format: '{date_string}'. Expected format: YYYY-MM-DD")


def get_days_until_due(due_date_str: str) -> int:
    """
    Calculate days until a task is due.
    Negative number means overdue.
    """
    due_date = parse_date(due_date_str)
    today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    delta = due_date - today
    return delta.days
