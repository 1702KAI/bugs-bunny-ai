# app/utils.py
import json
import os
from typing import List

# Resolve project root and data directory
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")

USERS_FILE = os.path.join(DATA_DIR, "users.json")
TASKS_FILE = os.path.join(DATA_DIR, "tasks.json")


def _read_json(path: str) -> List[dict]:
    """
    Read a JSON file and return a list.
    If the file does not exist or is empty/invalid, return an empty list.
    """
    if not os.path.exists(path):
        return []

    try:
        with open(path, "r") as f:
            return json.load(f)
    except (json.JSONDecodeError, ValueError):
        return []


def _write_json(path: str, data: List[dict]) -> None:
    """
    Write a list of dictionaries to a JSON file.
    """
    with open(path, "w") as f:
        json.dump(data, f, indent=2)


def load_tasks() -> List[dict]:
    """
    Load all tasks from data/tasks.json.
    """
    return _read_json(TASKS_FILE)


def save_tasks(tasks: List[dict]) -> None:
    """
    Persist the full task list to data/tasks.json.
    """
    _write_json(TASKS_FILE, tasks)


def user_exists(email: str) -> bool:
    """
    Check whether a user with the given email exists in data/users.json.
    """
    users = _read_json(USERS_FILE)
    return any(user.get("email") == email for user in users)



# # app/utils.py
# """
# Utility functions for the task management API.
# WARNING: This file contains bugs that need to be found and fixed!
# """

# import re
# from datetime import datetime


# def validate_email(email: str) -> bool:
#     """
#     Validate email format.
#     Returns True if valid, False otherwise.

#     BUG #1: This regex is too permissive - it accepts invalid emails
#     """
#     # This pattern has a bug - can you find it?
#     pattern = r".+@.+"
#     return bool(re.match(pattern, email))


# def calculate_priority_score(priority: str, days_until_due: int) -> int:
#     """
#     Calculate a numeric priority score for sorting tasks.
#     Higher score = more urgent.

#     Priority weights:
#     - critical: 100
#     - high: 75
#     - medium: 50
#     - low: 25

#     Days until due modifier:
#     - Overdue (negative days): +50
#     - Due today (0 days): +30
#     - Due within 3 days: +20
#     - Due within 7 days: +10

#     BUG #2: There's an off-by-one error and missing case
#     """
#     priority_weights = {
#         "critical": 100,
#         "high": 75,
#         "medium": 50,
#         "low": 25
#     }

#     # Bug: What if priority is not in the dict?
#     base_score = priority_weights[priority]

#     # Bug: Off-by-one error in the conditions
#     if days_until_due < 0:
#         urgency_bonus = 50
#     elif days_until_due == 0:
#         urgency_bonus = 30
#     elif days_until_due < 3:  # Should be <= 3
#         urgency_bonus = 20
#     elif days_until_due < 7:  # Should be <= 7
#         urgency_bonus = 10
#     else:
#         urgency_bonus = 0

#     return base_score + urgency_bonus


# def sanitize_input(text: str) -> str:
#     """
#     Sanitize user input to prevent XSS attacks.

#     BUG #3: This function is dangerously incomplete!
#     It only handles a few cases and misses critical ones.
#     """
#     if not text:
#         return ""

#     # This is NOT sufficient sanitization!
#     sanitized = text.replace("<script>", "")
#     sanitized = sanitized.replace("</script>", "")

#     return sanitized


# def parse_date(date_string: str) -> datetime:
#     """
#     Parse a date string in format YYYY-MM-DD.

#     BUG #4: No error handling for invalid dates
#     """
#     # What happens if the format is wrong?
#     return datetime.strptime(date_string, "%Y-%m-%d")


# def get_days_until_due(due_date_str: str) -> int:
#     """
#     Calculate days until a task is due.
#     Negative number means overdue.
#     """
#     due_date = parse_date(due_date_str)
#     today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
#     delta = due_date - today
#     return delta.days
