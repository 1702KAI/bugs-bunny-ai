# app/utils.py
"""
Utility functions for the task management API.
Bugs have been fixed as part of the assessment.
"""

import re
import html
from datetime import datetime


def validate_email(email: str) -> bool:
    """
    Validate email format.
    Returns True if valid, False otherwise.

    FIX #1: Updated regex to properly validate email format
    - Requires valid characters before @
    - Requires domain with at least one dot
    - No spaces or special HTML characters allowed
    """
    # Fixed pattern: requires proper format with domain and TLD
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

    FIX #2: Fixed off-by-one error and added ValueError for invalid priority
    """
    priority_weights = {
        "critical": 100,
        "high": 75,
        "medium": 50,
        "low": 25
    }

    # FIX #2a: Handle invalid priority gracefully with ValueError
    base_score = priority_weights.get(priority)
    if base_score is None:
        raise ValueError(f"Invalid priority: {priority}. Must be one of: {', '.join(priority_weights.keys())}")

    # FIX #2b: Fixed off-by-one errors with <= instead of <
    if days_until_due < 0:
        urgency_bonus = 50
    elif days_until_due == 0:
        urgency_bonus = 30
    elif days_until_due <= 3:  # Fixed: was < 3
        urgency_bonus = 20
    elif days_until_due <= 7:  # Fixed: was < 7
        urgency_bonus = 10
    else:
        urgency_bonus = 0

    return base_score + urgency_bonus


def sanitize_input(text: str) -> str:
    """
    Sanitize user input to prevent XSS attacks.

    FIX #3: Strip all HTML tags and dangerous content
    - Removes script tags AND their content
    - Removes all other HTML tags (including attributes like onerror, onclick)
    - Removes javascript: URLs
    - Handles case variations
    """
    # FIX #3a: Handle None input
    if text is None:
        return ""
    
    if not text:
        return ""

    # FIX #3b: Remove script tags AND their content (handles case variations)
    sanitized = re.sub(r'<script[^>]*>.*?</script>', '', text, flags=re.IGNORECASE | re.DOTALL)
    
    # FIX #3c: Remove all remaining HTML tags (handles case sensitivity, attributes, etc.)
    sanitized = re.sub(r'<[^>]*>', '', sanitized, flags=re.IGNORECASE)
    
    # FIX #3d: Remove javascript: URLs
    sanitized = re.sub(r'javascript:', '', sanitized, flags=re.IGNORECASE)

    return sanitized


def parse_date(date_string: str) -> datetime:
    """
    Parse a date string in format YYYY-MM-DD.

    FIX #4: Added proper error handling for invalid dates
    Raises ValueError with clear message for invalid input.
    """
    # FIX #4a: Handle empty string
    if not date_string:
        raise ValueError("Date string cannot be empty")
    
    # FIX #4b: Wrap in try/except to provide clear error message
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
