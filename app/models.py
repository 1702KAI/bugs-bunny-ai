# app/models.py
from datetime import datetime
from dataclasses import dataclass, field
from typing import Optional
from enum import Enum


class Priority(Enum):
    """Priority levels for tasks."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class User:
    email: str
    name: str
    created_at: datetime = field(default_factory=datetime.now)

    def to_dict(self):
        return {
            "email": self.email,
            "name": self.name,
            "created_at": self.created_at.isoformat()
        }


@dataclass
class Task:
    id: int
    title: str
    description: str
    user_email: str
    priority: Priority
    status: str = "pending"  # "pending", "in_progress", "completed"
    due_date: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "user_email": self.user_email,
            "priority": self.priority.value,  # Return string value for JSON
            "status": self.status,
            "due_date": self.due_date,
            "created_at": self.created_at.isoformat()
        }

