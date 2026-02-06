import re
from datetime import datetime

# ------------------------
# Bug 1: validate_email
# ------------------------
def validate_email(email: str) -> bool:
    if not isinstance(email, str):
        return False

    # Disallow spaces and HTML-like characters
    pattern = r"^[^@\s<>]+@[^@\s<>]+\.[^@\s<>]+$"
    return bool(re.match(pattern, email))



# ------------------------
# Bug 2: calculate_priority_score
# ------------------------
def calculate_priority_score(priority: str, days_until_due: int) -> int:
    priority_weights = {
        "critical": 100,
        "high": 75,
        "medium": 50,
        "low": 25
    }

    if priority not in priority_weights:
        raise ValueError("Invalid priority")

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


# ------------------------
# Bug 3: sanitize_input
# ------------------------
def sanitize_input(text: str) -> str:
    if not text:
        return ""

    text = re.sub(r"<\s*script[^>]*>.*?<\s*/\s*script\s*>", "", text, flags=re.IGNORECASE | re.DOTALL)
    text = re.sub(r"on\w+\s*=\s*\".*?\"", "", text, flags=re.IGNORECASE)
    text = re.sub(r"javascript:", "", text, flags=re.IGNORECASE)

    return text


# ------------------------
# Bug 4: parse_date
# ------------------------
def parse_date(date_string: str) -> datetime:
    if not date_string:
        raise ValueError("Invalid date")

    try:
        return datetime.strptime(date_string, "%Y-%m-%d")
    except Exception:
        raise ValueError("Invalid date")


def get_days_until_due(due_date_str: str) -> int:
    due_date = parse_date(due_date_str)
    today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    delta = due_date - today
    return delta.days
