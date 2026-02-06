# app/main.py
# Author: Thinal
# Date: February 6, 2026
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

# Valid priority values (from config)
VALID_PRIORITIES = ["low", "medium", "high", "critical"]
MAX_TITLE_LENGTH = 500


@app.route("/tasks", methods=["POST"])
def create_task():
    """
    Create a new task.

    Required fields: title, user_email, priority

    Returns:
        201: Task created successfully
        400: Invalid input (missing fields, invalid priority)
        404: User not found
    """
    global task_counter

    data = request.get_json()

    # Validate required fields
    if not data:
        return jsonify({"error": "Request body is required"}), 400

    missing_fields = []
    if "title" not in data:
        missing_fields.append("title")
    if "user_email" not in data:
        missing_fields.append("user_email")
    if "priority" not in data:
        missing_fields.append("priority")

    if missing_fields:
        return jsonify({"error": f"Missing required fields: {', '.join(missing_fields)}"}), 400

    title = data["title"]
    user_email = data["user_email"]
    priority = data["priority"]

    # Validate title is not empty
    if not title or not title.strip():
        return jsonify({"error": "Title cannot be empty"}), 400

    # Validate title length
    if len(title) > MAX_TITLE_LENGTH:
        return jsonify({"error": f"Title exceeds maximum length of {MAX_TITLE_LENGTH} characters"}), 400

    # Sanitize the title to prevent XSS
    title = sanitize_input(title)

    # Validate priority (case-insensitive, normalize to lowercase)
    priority_lower = priority.lower() if isinstance(priority, str) else ""
    if priority_lower not in VALID_PRIORITIES:
        return jsonify({
            "error": f"Invalid priority: '{priority}'. Must be one of: {', '.join(VALID_PRIORITIES)}"
        }), 400

    # Check if user exists
    if user_email not in users:
        return jsonify({"error": f"User not found: {user_email}"}), 404

    # Auto-generate unique task ID
    task_counter += 1
    task_id = task_counter

    # Get optional fields
    description = sanitize_input(data.get("description", ""))
    due_date = data.get("due_date")
    status = data.get("status", "pending")

    # Create the task
    task = Task(
        id=task_id,
        title=title,
        description=description,
        user_email=user_email,
        priority=priority_lower,
        status=status,
        due_date=due_date
    )

    tasks[task_id] = task

    return jsonify(task.to_dict()), 201


@app.route("/tasks", methods=["GET"])
def get_tasks():
    """
    Get tasks with optional filtering and sorting.

    Query parameters:
        - user_email: Filter by user email
        - status: Filter by status (pending, in_progress, completed)
        - priority: Filter by priority (low, medium, high, critical)
        - sort_by: Sort field (priority_score, due_date, created_at)
        - sort_order: Sort order (asc, desc) - default: desc

    Returns:
        200: List of tasks
    """
    # Get query parameters
    user_email = request.args.get("user_email")
    status = request.args.get("status")
    priority = request.args.get("priority")
    sort_by = request.args.get("sort_by", "created_at")
    sort_order = request.args.get("sort_order", "desc")

    # Start with all tasks
    result = list(tasks.values())

    # Apply filters
    if user_email:
        result = [t for t in result if t.user_email == user_email]

    if status:
        result = [t for t in result if t.status == status]

    if priority:
        # Support case-insensitive priority filtering
        priority_lower = priority.lower()
        result = [t for t in result if t.priority == priority_lower]

    # Apply sorting
    reverse = sort_order.lower() == "desc"

    if sort_by == "priority_score":
        # Calculate priority score for sorting
        def get_priority_score(task):
            days = 999  # Default for no due date
            if task.due_date:
                try:
                    from app.utils import get_days_until_due
                    days = get_days_until_due(task.due_date)
                except ValueError:
                    days = 999
            return calculate_priority_score(task.priority, days)

        result = sorted(result, key=get_priority_score, reverse=reverse)

    elif sort_by == "due_date":
        # Sort by due date (None values go to end)
        def get_due_date_key(task):
            if task.due_date is None:
                return "" if reverse else "9999-99-99"
            return task.due_date

        result = sorted(result, key=get_due_date_key, reverse=reverse)

    elif sort_by == "created_at":
        result = sorted(result, key=lambda t: t.created_at, reverse=reverse)

    # Convert to dictionaries
    return jsonify([t.to_dict() for t in result]), 200


if __name__ == "__main__":
    app.run(debug=True, port=5000)
