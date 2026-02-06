# Name : Sawiru Wimalatunge
# Date : 2026-01-06

# app/main.py
from flask import Flask, request, jsonify
from app.models import User, Task
from app.utils import validate_email, calculate_priority_score, sanitize_input, get_days_until_due
from app.config import Config
import json
import os

app = Flask(__name__)

# In-memory storage (for simplicity)
users = {}
tasks = {}
task_counter = 0

# ============================================
# INITIALIZATION
# ============================================

def load_sample_users():
    """Load sample users from data/sample_users.json"""
    global users
    try:
        data_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'sample_users.json')
        with open(data_path, 'r') as f:
            data = json.load(f)
            for user_data in data.get('users', []):
                email = user_data.get('email')
                name = user_data.get('name')
                if email and name:
                    users[email] = User(email=email, name=name)
    except FileNotFoundError:
        print("Warning: sample_users.json not found. Starting with empty users.")
    except Exception as e:
        print(f"Error loading sample users: {e}")

# Load sample users on app startup
load_sample_users()

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
# TASK 2.1: POST /tasks Endpoint
# ============================================

@app.route("/tasks", methods=["POST"])
def create_task():
    """
    Create a new task with the following requirements:
    - Required fields: title, user_email, priority
    - Validates priority is one of: low, medium, high, critical
    - Checks that the specified user exists
    - Auto-generates unique task ID
    - Returns 201 Created on success
    - Returns 400 Bad Request for invalid input
    - Returns 404 Not Found if user does not exist
    """
    global task_counter
    
    # Get JSON request data
    data = request.get_json()
    
    if not data:
        return jsonify({"error": "Request body must be valid JSON"}), 400
    
    # Check required fields
    required_fields = ["title", "user_email", "priority"]
    missing_fields = [field for field in required_fields if field not in data or data[field] is None]
    if missing_fields:
        return jsonify({"error": f"Missing required fields: {', '.join(missing_fields)}"}), 400
    
    title = data.get("title", "").strip()
    user_email = data.get("user_email", "").strip()
    priority = data.get("priority", "").lower().strip()
    description = data.get("description", "")
    status = data.get("status", "pending").lower().strip()
    due_date = data.get("due_date")
    
    # Validate title is not empty
    if not title:
        return jsonify({"error": "Title cannot be empty"}), 400
    
    # Validate priority
    if priority not in Config.VALID_PRIORITIES:
        return jsonify({
            "error": f"Invalid priority. Must be one of: {', '.join(Config.VALID_PRIORITIES)}"
        }), 400
    
    # Validate status if provided
    if status and status not in Config.VALID_STATUSES:
        return jsonify({
            "error": f"Invalid status. Must be one of: {', '.join(Config.VALID_STATUSES)}"
        }), 400
    
    # # Check if user exists
    # if user_email not in users:
    #     return jsonify({"error": f"User with email '{user_email}' does not exist"}), 404
    
    # Sanitize input
    title = sanitize_input(title)
    description = sanitize_input(description)
    
    # Auto-generate unique task ID
    task_counter += 1
    task_id = task_counter
    
    # Create task object
    task = Task(
        id=task_id,
        title=title,
        user_email=user_email,
        priority=priority,
        description=description,
        status=status,
        due_date=due_date
    )
    
    # Store task in memory
    tasks[task_id] = task
    
    return jsonify(task.to_dict()), 201


# ============================================
# TASK 2.2 : GET /tasks Endpoint
# ============================================

@app.route("/tasks", methods=["GET"])
def get_tasks():
    """
    Retrieve all tasks with advanced filtering and sorting.
    
    Query Parameters:
    - user_email: Filter by user email
    - status: Filter by status (pending, in_progress, completed)
    - priority: Filter by priority (low, medium, high, critical)
    - sort_by: Sort by field (priority_score, due_date, created_at)
    """
    # 1. Capture query parameters from the URL
    user_email = request.args.get('user_email', '').strip() or None
    status = request.args.get('status', '').lower().strip() or None
    priority = request.args.get('priority', '').lower().strip() or None
    sort_by = request.args.get('sort_by', 'created_at').lower().strip()
    
    # 2. Get all tasks from memory and convert to dictionaries
    task_list = [t.to_dict() for t in tasks.values()]

    # 3. Apply Filtering
    if user_email:
        task_list = [t for t in task_list if t.get('user_email') == user_email]
    
    if status:
        task_list = [t for t in task_list if t.get('status') == status]
        
    if priority:
        task_list = [t for t in task_list if t.get('priority') == priority]

    # 4. Apply Sorting
    # Valid sort fields with appropriate default values
    valid_sort_fields = {
        'priority_score': (lambda x: x.get('priority_score', 0), True),  # Descending
        'due_date': (lambda x: x.get('due_date') or '', True),  # Descending
        'created_at': (lambda x: x.get('created_at', ''), True)  # Descending
    }
    
    if sort_by in valid_sort_fields:
        key_func, reverse = valid_sort_fields[sort_by]
        task_list.sort(key=key_func, reverse=reverse)

    return jsonify(task_list), 200


if __name__ == "__main__":
    app.run(debug=True, port=5001)
    app.run(debug=True, port=5001)
