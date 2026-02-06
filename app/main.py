# app/main.py
# Name: Fathima Sarah
# Date: 2026-02-06

from flask import Flask, request, jsonify
from app.models import User, Task
from app.utils import validate_email, calculate_priority_score, sanitize_input

app = Flask(__name__)

# In-memory storage (for simplicity)
users = {}
tasks = {}
task_counter = 0

# ============================================
# EXISTING ENDPOINTS (DO NOT MODIFY)
# ============================================

@app.route("/health", methods=["GET"])
def health_check():
    return jsonify({"status": "healthy", "version": "1.0.0"})


@app.route("/users", methods=["POST"])
def create_user():
    """Create a new user"""
    data = request.get_json()

    if not data or "email" not in data or "name" not in data:
        return jsonify({"error": "Missing required fields: email, name"}), 400

    email = data["email"]
    name = data["name"]

    # Validate email
    if not validate_email(email):
        return jsonify({"error": "Invalid email format"}), 400

    # Check if user exists
    if email in users:
        return jsonify({"error": "User already exists"}), 409

    user = User(email=email, name=name)
    users[email] = user

    return jsonify(user.to_dict()), 201


@app.route("/users/<email>", methods=["GET"])
def get_user(email):
    """Get user by email"""
    if email not in users:
        return jsonify({"error": "User not found"}), 404
    return jsonify(users[email].to_dict())


# ============================================
# TASK 2: ADD YOUR NEW ENDPOINT BELOW
# ============================================

# TODO: Implement POST /tasks endpoint
# TODO: Implement GET /tasks endpoint with filtering
from datetime import datetime
from app.utils import get_days_until_due

VALID_PRIORITIES = {"low", "medium", "high", "critical"}
VALID_STATUSES = {"pending", "in_progress", "completed"}


@app.route("/tasks", methods=["POST"])
def create_task():
    """Create a new task"""
    global task_counter

    data = request.get_json() or {}

    title = data.get("title")
    user_email = data.get("user_email")
    priority = data.get("priority")

    # Required fields
    if not title or not user_email or not priority:
        return jsonify({"error": "Missing required fields: title, user_email, priority"}), 400

    # Normalize priority (handles uppercase input)
    if isinstance(priority, str):
        priority = priority.lower().strip()

    if priority not in VALID_PRIORITIES:
        return jsonify({"error": "Invalid priority. Must be one of: low, medium, high, critical"}), 400

    # User must exist
    if user_email not in users:
        return jsonify({"error": "User not found"}), 404

    # Optional fields
    description = data.get("description", "")
    status = data.get("status", "pending")
    due_date = data.get("due_date")  # optional YYYY-MM-DD

    # Normalize + validate status
    if isinstance(status, str):
        status = status.lower().strip()
    if status not in VALID_STATUSES:
        return jsonify({"error": "Invalid status. Must be one of: pending, in_progress, completed"}), 400

    # Sanitize strings
    title = sanitize_input(str(title))
    description = sanitize_input(str(description))

    # Generate unique ID
    task_counter += 1
    task_id = task_counter

    task = Task(
        id=task_id,
        title=title,
        description=description,
        user_email=user_email,
        priority=priority,
        status=status,
        due_date=due_date
    )

    tasks[task_id] = task
    return jsonify(task.to_dict()), 201


@app.route("/tasks", methods=["GET"])
def list_tasks():
    """List tasks with filtering + sorting"""
    user_email = request.args.get("user_email")
    status = request.args.get("status")
    priority = request.args.get("priority")
    sort_by = request.args.get("sort_by")  # priority_score | due_date | created_at
    sort_order = request.args.get("sort_order", "asc").lower()  # asc | desc

    # Normalize filters
    if isinstance(status, str) and status:
        status = status.lower().strip()
    if isinstance(priority, str) and priority:
        priority = priority.lower().strip()

    result = list(tasks.values())

    # Filtering
    if user_email:
        result = [t for t in result if t.user_email == user_email]
    if status:
        result = [t for t in result if t.status == status]
    if priority:
        result = [t for t in result if t.priority == priority]

    # Sorting
    reverse = (sort_order == "desc")

    if sort_by == "created_at":
        result.sort(key=lambda t: t.created_at, reverse=reverse)

    elif sort_by == "due_date":
        # Put tasks without due_date at the end (stable)
        def due_key(t):
            if not t.due_date:
                return datetime.max
            try:
                return parse_date(t.due_date)
            except Exception:
                return datetime.max
        result.sort(key=due_key, reverse=reverse)

    elif sort_by == "priority_score":
        # Use util scoring + due date urgency if due_date exists
        def score_key(t):
            if t.due_date:
                try:
                    days = get_days_until_due(t.due_date)
                except Exception:
                    days = 999999
            else:
                days = 999999
            try:
                return calculate_priority_score(t.priority, days)
            except Exception:
                # If scoring fails due to util bug, fall back
                fallback = {"low": 1, "medium": 2, "high": 3, "critical": 4}
                return fallback.get(t.priority, 0)
        result.sort(key=score_key, reverse=reverse)

    return jsonify([t.to_dict() for t in result]), 200


if __name__ == "__main__":
    app.run(debug=True, port=5000)
