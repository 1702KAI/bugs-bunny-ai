# app/models.py
from datetime import datetime
from dataclasses import dataclass, field
from typing import Optional
from app.utils import calculate_priority_score, get_days_until_due

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
    user_email: str
    priority: str  # "low", "medium", "high", "critical"
    description: str = ""
    status: str = "pending"  # "pending", "in_progress", "completed"
    due_date: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)

    def get_priority_score(self):
        """Calculate priority score based on priority and days until due"""
        days_until_due = get_days_until_due(self.due_date) if self.due_date else None
        return calculate_priority_score(self.priority, days_until_due)

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "user_email": self.user_email,
            "priority": self.priority,
            "priority_score": self.get_priority_score(),
            "status": self.status,
            "due_date": self.due_date,
            "created_at": self.created_at.isoformat()
        }
