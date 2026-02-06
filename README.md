# Task Management API - Vibe Coding Assessment

## Overview
This is a simple task management API built with Flask. Your job is to:
1. Set up the repo correctly using Git
2. Add new features using AI assistance
3. Find and fix bugs in the existing code

## Setup
```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the app
python -m app.main

# Run tests
pytest tests/ -v
```

## API Endpoints

### Existing
- `GET /health` - Health check
- `POST /users` - Create a user
- `GET /users/<email>` - Get a user

### To Implement
- `POST /tasks` - Create a task
- `GET /tasks` - List/filter tasks

## Your Tasks

See `ASSESSMENT_INSTRUCTIONS.md` for detailed requirements.
