# Name: Chanumi Pelawatte
# Date: 2026-02-06


# app/main.py
from flask import Flask, request, jsonify
from app.models import User, TaskCreate, Task
from app.utils import load_tasks, save_tasks, user_exists

app = Flask(__name__)

# In-memory storage for users ONLY (existing behavior)
users = {}

# ============================================
# EXISTING ENDPOINTS (DO NOT MODIFY)
# ============================================

@app.route("/health", methods=["GET"])
def health_check():
    return jsonify({"status": "healthy", "version": "1.0.0"})


def _validate_email_basic(email: str) -> bool:
    # Minimal validation to preserve existing endpoint behavior
    return isinstance(email, str) and "@" in email


@app.route("/users", methods=["POST"])
def create_user():
    """Create a new user"""
    data = request.get_json()

    if not data or "email" not in data or "name" not in data:
        return jsonify({"error": "Missing required fields: email, name"}), 400

    email = data["email"]
    name = data["name"]

    if not _validate_email_basic(email):
        return jsonify({"error": "Invalid email format"}), 400

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
# PART 2: TASK ENDPOINTS
# ============================================

@app.route("/tasks", methods=["POST"])
def create_task():
    data = request.get_json()
    if not data:
        return jsonify({"error": "Invalid JSON body"}), 400

    try:
        task_create = TaskCreate(
            title=data.get("title"),
            user_email=data.get("user_email"),
            priority=data.get("priority"),
            due_date=data.get("due_date"),
        ).validate()
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

    if task_create.user_email not in users:
        return jsonify({"error": "User not found"}), 404


    task = Task.from_create(task_create)

    tasks = load_tasks()
    tasks.append(task.to_dict())
    save_tasks(tasks)

    return jsonify(task.to_dict()), 201


@app.route("/tasks", methods=["GET"])
def get_tasks():
    tasks = load_tasks()

    user_email = request.args.get("user_email")
    status = request.args.get("status")  # accepted but optional
    priority = request.args.get("priority")
    sort_by = request.args.get("sort_by", "created_at")
    order = request.args.get("order", "desc")

    if priority:
        priority = priority.lower()

    if user_email:
        tasks = [t for t in tasks if t.get("user_email") == user_email]

    if status:
        tasks = [t for t in tasks if t.get("status") == status]

    if priority:
        tasks = [t for t in tasks if t.get("priority") == priority]

    allowed_sort_fields = {"priority_score", "due_date", "created_at"}
    if sort_by not in allowed_sort_fields:
        return jsonify({"error": "Invalid sort_by field"}), 400

    reverse = order == "desc"

    tasks.sort(
        key=lambda t: t.get(sort_by) or "",
        reverse=reverse,
    )

    return jsonify(tasks), 200


if __name__ == "__main__":
    app.run(debug=True, port=5000)




# # app/main.py
# from flask import Flask, request, jsonify
# from app.models import User, Task
# from app.utils import validate_email, calculate_priority_score, sanitize_input

# app = Flask(__name__)

# # In-memory storage (for simplicity)
# users = {}
# tasks = {}
# task_counter = 0

# # ============================================
# # EXISTING ENDPOINTS (DO NOT MODIFY)
# # ============================================

# @app.route("/health", methods=["GET"])
# def health_check():
#     return jsonify({"status": "healthy", "version": "1.0.0"})


# @app.route("/users", methods=["POST"])
# def create_user():
#     """Create a new user"""
#     data = request.get_json()

#     if not data or "email" not in data or "name" not in data:
#         return jsonify({"error": "Missing required fields: email, name"}), 400

#     email = data["email"]
#     name = data["name"]

#     # Validate email
#     if not validate_email(email):
#         return jsonify({"error": "Invalid email format"}), 400

#     # Check if user exists
#     if email in users:
#         return jsonify({"error": "User already exists"}), 409

#     user = User(email=email, name=name)
#     users[email] = user

#     return jsonify(user.to_dict()), 201


# @app.route("/users/<email>", methods=["GET"])
# def get_user(email):
#     """Get user by email"""
#     if email not in users:
#         return jsonify({"error": "User not found"}), 404
#     return jsonify(users[email].to_dict())


# # ============================================
# # TASK 2: ADD YOUR NEW ENDPOINT BELOW
# # ============================================

# # TODO: Implement POST /tasks endpoint
# # TODO: Implement GET /tasks endpoint with filtering


# if __name__ == "__main__":
#     app.run(debug=True, port=5000)
