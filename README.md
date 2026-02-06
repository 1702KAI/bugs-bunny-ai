# Bugs Bunny AI - Task Management API

A Flask-based task management REST API built as part of the Bugs Bunny AI Hackathon technical assessment.

## Project Overview

This project implements a task management system with user and task CRUD operations, featuring:
- User management (create, retrieve)
- Task management with priority scoring
- Input validation and XSS sanitization
- Filtering and sorting capabilities

## Setup

### Prerequisites
- Python 3.8+
- pip

### Installation

```bash
# Clone the repository
git clone <repository-url>
cd bugs-bunny-ai

# Install dependencies
pip install -r requirements.txt
```

### Running the Application

```bash
python -m app.main
```

The server will start at `http://localhost:5000`

### Running Tests

```bash
pytest tests/test_utils.py -v
```

## API Endpoints

### Health Check
```
GET /health
```

### Users
```
POST /users
Body: { "email": "user@example.com", "name": "John Doe" }

GET /users/<email>
```

### Tasks
```
POST /tasks
Body: {
  "title": "Task title",
  "user_email": "user@example.com",
  "priority": "low|medium|high|critical",
  "description": "Optional description",
  "due_date": "YYYY-MM-DD"
}

GET /tasks
Query params:
  - user_email: Filter by user
  - status: Filter by status (pending, in_progress, completed)
  - priority: Filter by priority
  - sort_by: Sort field (priority_score, due_date, created_at)
  - sort_order: asc|desc
```

## Project Structure

```
bugs-bunny-ai/
├── app/
│   ├── __init__.py
│   ├── main.py          # Flask application and endpoints
│   ├── models.py        # User and Task data models
│   ├── utils.py         # Utility functions (validation, sanitization)
│   └── config.py        # Configuration settings
├── tests/
│   └── test_utils.py    # Unit tests for utilities
├── data/
│   └── sample_users.json
├── BUG_REPORT.md        # Documentation of fixed bugs
├── REVIEW_NOTES.md      # Security analysis
├── requirements.txt
└── README.md
```

## Documentation

- **BUG_REPORT.md**: Detailed documentation of all bugs discovered and fixed
- **REVIEW_NOTES.md**: Security analysis covering input sanitization, edge cases, and recommendations

## Author

- **Thinal**
- **Date**: February 6, 2026
