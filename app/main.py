# app/main.py
# Name: Nilupul | Date: 2026-02-06
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

@app.route("/tasks", methods=["POST"])
def create_task():
    """Create a new task"""
    global task_counter
    data = request.get_json()

    if not data:
        return jsonify({"error": "Request body is required"}), 400

    # Check required fields
    required_fields = ["title", "user_email", "priority"]
    for field in required_fields:
        if field not in data:
            return jsonify({"error": f"Missing required field: {field}"}), 400

    title = sanitize_input(data["title"])
    user_email = data["user_email"]
    priority = data["priority"].lower()

    # Validate priority
    valid_priorities = ["low", "medium", "high", "critical"]
    if priority not in valid_priorities:
        return jsonify({"error": f"Invalid priority. Must be one of: {', '.join(valid_priorities)}"}), 400

    # Check if user exists
    if user_email not in users:
        return jsonify({"error": "User not found"}), 404

    # Validate email
    if not validate_email(user_email):
        return jsonify({"error": "Invalid email format"}), 400

    task_counter += 1
    task = Task(
        id=task_counter,
        title=title,
        description=sanitize_input(data.get("description", "")),
        user_email=user_email,
        priority=priority,
        status=data.get("status", "pending"),
        due_date=data.get("due_date")
    )
    tasks[task.id] = task

    return jsonify(task.to_dict()), 201


@app.route("/tasks", methods=["GET"])
def get_tasks():
    """Get tasks with optional filtering and sorting"""
    result = list(tasks.values())

    # Filter by user_email
    user_email = request.args.get("user_email")
    if user_email:
        result = [t for t in result if t.user_email == user_email]

    # Filter by status
    status = request.args.get("status")
    if status:
        result = [t for t in result if t.status == status]

    # Filter by priority
    priority = request.args.get("priority")
    if priority:
        result = [t for t in result if t.priority == priority.lower()]

    # Sorting
    sort_by = request.args.get("sort_by")
    if sort_by == "priority_score":
        priority_order = {"critical": 4, "high": 3, "medium": 2, "low": 1}
        result.sort(key=lambda t: priority_order.get(t.priority, 0), reverse=True)
    elif sort_by == "due_date":
        result.sort(key=lambda t: t.due_date or "9999-12-31")
    elif sort_by == "created_at":
        result.sort(key=lambda t: t.created_at)

    return jsonify([t.to_dict() for t in result])


if __name__ == "__main__":
    app.run(debug=True, port=5000)
