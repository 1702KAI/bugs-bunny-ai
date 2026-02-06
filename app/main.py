# Name : Sawiru Wimalatunge
# Date : 2026-01-06

# app/main.py
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


# ============================================
# TASK 2.2 : GET /tasks Endpoint
# ============================================

@app.route("/tasks", methods=["GET"])
def get_tasks():
    """Retrieve all tasks with advanced filtering and sorting"""
    # 1. Capture query parameters from the URL
    user_email = request.args.get('user_email')
    status = request.args.get('status')
    priority = request.args.get('priority')
    
    sort_by = request.args.get('sort_by')  # Options: priority_score, due_date, created_at

    # 2. Get all tasks from memory
    task_list = [t.to_dict() for t in tasks.values()]

    # 3. Apply Filtering
    if user_email:
        task_list = [t for t in task_list if t.get('user_email') == user_email]
    
    if status:
        task_list = [t for t in task_list if t.get('status') == status]
        
    if priority:
        task_list = [t for t in task_list if t.get('priority') == priority]

    # 4. Apply Sorting
    # We use .get(sort_by) with a default (None) to avoid errors if the key is missing
    if sort_by in ['priority_score', 'due_date', 'created_at']:
        task_list.sort(key=lambda x: x.get(sort_by) if x.get(sort_by) is not None else "", reverse=True)

    return jsonify(task_list), 200

if __name__ == "__main__":
    app.run(debug=True, port=5001)
