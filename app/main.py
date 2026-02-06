#Details:
#Name: Prabhashan
#Date: 06/02/2026

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

VALID_PRIORITIES = ["low", "medium", "high", "critical"]

@app.route("/tasks", methods=["POST"])
def create_task():
    """Create a new task"""
    global task_counter
    
    data = request.get_json()
    
    # Check for required fields
    if not data:
        return jsonify({"error": "Missing request body"}), 400
    
    if "title" not in data or "user_email" not in data or "priority" not in data:
        return jsonify({"error": "Missing required fields: title, user_email, priority"}), 400
    
    title = data["title"]
    user_email = data["user_email"]
    priority = data["priority"].lower() if isinstance(data["priority"], str) else data["priority"]
    
    # Validate priority
    if priority not in VALID_PRIORITIES:
        return jsonify({"error": f"Invalid priority. Must be one of: {', '.join(VALID_PRIORITIES)}"}), 400
    
    # Check if user exists
    if user_email not in users:
        return jsonify({"error": "User not found"}), 404
    
    # Generate unique task ID
    task_counter += 1
    task_id = task_counter
    
    # Create task
    task = Task(
        id=task_id,
        title=sanitize_input(title),
        description=sanitize_input(data.get("description", "")),
        user_email=user_email,
        priority=priority,
        status=data.get("status", "pending"),
        due_date=data.get("due_date")
    )
    
    tasks[task_id] = task
    
    return jsonify(task.to_dict()), 201


@app.route("/tasks", methods=["GET"])
def get_tasks():
    """Get tasks with optional filtering and sorting"""
    from app.utils import get_days_until_due
    
    # Get filter parameters
    user_email = request.args.get("user_email")
    status = request.args.get("status")
    priority = request.args.get("priority")
    
    # Get sort parameter
    sort_by = request.args.get("sort_by")  # priority_score, due_date, created_at
    
    # Start with all tasks
    filtered_tasks = list(tasks.values())
    
    # Apply filters
    if user_email:
        filtered_tasks = [t for t in filtered_tasks if t.user_email == user_email]
    
    if status:
        filtered_tasks = [t for t in filtered_tasks if t.status == status]
    
    if priority:
        filtered_tasks = [t for t in filtered_tasks if t.priority == priority.lower()]
    
    # Apply sorting
    if sort_by == "priority_score":
        def get_priority_score(task):
            priority_weights = {"critical": 100, "high": 75, "medium": 50, "low": 25}
            base = priority_weights.get(task.priority, 0)
            if task.due_date:
                try:
                    days = get_days_until_due(task.due_date)
                    if days < 0:
                        return base + 50
                    elif days == 0:
                        return base + 30
                    elif days <= 3:
                        return base + 20
                    elif days <= 7:
                        return base + 10
                except:
                    pass
            return base
        filtered_tasks.sort(key=get_priority_score, reverse=True)
    
    elif sort_by == "due_date":
        # Tasks with no due date go to the end
        filtered_tasks.sort(key=lambda t: t.due_date if t.due_date else "9999-99-99")
    
    elif sort_by == "created_at":
        filtered_tasks.sort(key=lambda t: t.created_at, reverse=True)
    
    return jsonify([task.to_dict() for task in filtered_tasks]), 200


if __name__ == "__main__":
    app.run(debug=True, port=5000)
