# app/models.py
from dataclasses import dataclass
from typing import Optional
from datetime import datetime
import uuid

# Priority mapping required by the assessment
PRIORITY_MAP = {
    "low": 1,
    "medium": 2,
    "high": 3,
    "critical": 4,
}

@dataclass
class User:
    email: str
    name: str
    created_at: datetime = datetime.now()

    def to_dict(self):
        return {
            "email": self.email,
            "name": self.name,
            "created_at": self.created_at.isoformat(),
        }


# -------- Part 2 models below --------

@dataclass
class TaskCreate:
    title: str
    user_email: str
    priority: str
    due_date: Optional[str] = None

    def validate(self):
        if not self.title or not self.title.strip():
            raise ValueError("title is required")

        if not self.user_email or not self.user_email.strip():
            raise ValueError("user_email is required")

        if not self.priority:
            raise ValueError("priority is required")

        self.priority = self.priority.lower()
        if self.priority not in PRIORITY_MAP:
            raise ValueError("invalid priority")

        return self


@dataclass
class Task:
    id: str
    title: str
    user_email: str
    priority: str
    priority_score: int
    due_date: Optional[str]
    created_at: str

    @classmethod
    def from_create(cls, task_create: TaskCreate):
        return cls(
            id=str(uuid.uuid4()),
            title=task_create.title,
            user_email=task_create.user_email,
            priority=task_create.priority,
            priority_score=PRIORITY_MAP[task_create.priority],
            due_date=task_create.due_date,
            created_at=datetime.utcnow().isoformat(),
        )

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "user_email": self.user_email,
            "priority": self.priority,
            "priority_score": self.priority_score,
            "due_date": self.due_date,
            "created_at": self.created_at,
        }




# from datetime import datetime
# from dataclasses import dataclass, field
# from typing import Optional

# @dataclass
# class User:
#     email: str
#     name: str
#     created_at: datetime = field(default_factory=datetime.now)

#     def to_dict(self):
#         return {
#             "email": self.email,
#             "name": self.name,
#             "created_at": self.created_at.isoformat()
#         }


# @dataclass
# class Task:
#     id: int
#     title: str
#     description: str
#     user_email: str
#     priority: str  # "low", "medium", "high", "critical"
#     status: str = "pending"  # "pending", "in_progress", "completed"
#     due_date: Optional[str] = None
#     created_at: datetime = field(default_factory=datetime.now)

#     def to_dict(self):
#         return {
#             "id": self.id,
#             "title": self.title,
#             "description": self.description,
#             "user_email": self.user_email,
#             "priority": self.priority,
#             "status": self.status,
#             "due_date": self.due_date,
#             "created_at": self.created_at.isoformat()
#         }
