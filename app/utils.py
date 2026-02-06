# app/utils.py
"""
Utility functions for the task management API.
WARNING: This file contains bugs that need to be found and fixed!
"""

import re
import html
from datetime import datetime


def validate_email(email: str) -> bool:
    """
    Validate email format.
    Returns True if valid, False otherwise.

    BUG #1: This regex is too permissive - it accepts invalid emails
    """
    # Fixed: Proper email validation regex
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

    # Fixed: Handle invalid priority
    if priority not in priority_weights:
        raise ValueError(f"Invalid priority: {priority}")
    
    base_score = priority_weights[priority]

    # Fixed: Off-by-one error - changed < to <=
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

    BUG #3: This function is dangerously incomplete!
    It only handles a few cases and misses critical ones.
    """
    if text is None:
        return ""
    
    if not text:
        return ""

    # Fixed: Comprehensive sanitization to remove dangerous content
    sanitized = text
    
    # Remove script tags (case insensitive)
    sanitized = re.sub(r'<script[^>]*>.*?</script>', '', sanitized, flags=re.IGNORECASE | re.DOTALL)
    sanitized = re.sub(r'<script[^>]*>', '', sanitized, flags=re.IGNORECASE)
    sanitized = re.sub(r'</script>', '', sanitized, flags=re.IGNORECASE)
    
    # Remove event handlers (onerror, onclick, onload, etc.)
    sanitized = re.sub(r'\s*on\w+\s*=\s*["\'][^"\']*["\']', '', sanitized, flags=re.IGNORECASE)
    sanitized = re.sub(r'\s*on\w+\s*=\s*[^\s>]+', '', sanitized, flags=re.IGNORECASE)
    
    # Remove javascript: URLs
    sanitized = re.sub(r'javascript:[^\s"\']*', '', sanitized, flags=re.IGNORECASE)
    
    # Remove img tags with dangerous attributes
    sanitized = re.sub(r'<img[^>]*>', '', sanitized, flags=re.IGNORECASE)
    
    # Remove any remaining dangerous tags
    sanitized = re.sub(r'<[^>]*javascript[^>]*>', '', sanitized, flags=re.IGNORECASE)

    return sanitized


def parse_date(date_string: str) -> datetime:
    """
    Parse a date string in format YYYY-MM-DD.

    BUG #4: No error handling for invalid dates
    """
    # Fixed: Added proper error handling
    if not date_string:
        raise ValueError("Date string cannot be empty")
    
    try:
        return datetime.strptime(date_string, "%Y-%m-%d")
    except ValueError:
        raise ValueError(f"Invalid date format: {date_string}. Expected YYYY-MM-DD")


def get_days_until_due(due_date_str: str) -> int:
    """
    Calculate days until a task is due.
    Negative number means overdue.
    """
    due_date = parse_date(due_date_str)
    today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    delta = due_date - today
    return delta.days
