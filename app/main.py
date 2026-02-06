# app/main.py
# Aaron Emmanuel - 6/2/2026
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

# Valid priority values
VALID_PRIORITIES = {"low", "medium", "high", "critical"}


@app.route("/tasks", methods=["POST"])
def create_task():
    """
    Create a new task.
    
    Required fields: title, user_email, priority
    Optional fields: description, due_date
    
    Returns:
        201: Task created successfully
        400: Invalid input (missing fields or invalid priority)
        404: User not found
    """
    global task_counter
    
    data = request.get_json()
    
    # Validate required fields
    if not data:
        return jsonify({"error": "Request body is required"}), 400
    
    required_fields = ["title", "user_email", "priority"]
    missing_fields = [field for field in required_fields if field not in data]
    if missing_fields:
        return jsonify({"error": f"Missing required fields: {', '.join(missing_fields)}"}), 400
    
    title = data["title"]
    user_email = data["user_email"]
    priority = data["priority"]
    description = data.get("description", "")
    due_date = data.get("due_date")
    
    # Validate priority value
    if priority not in VALID_PRIORITIES:
        return jsonify({
            "error": f"Invalid priority. Must be one of: {', '.join(sorted(VALID_PRIORITIES))}"
        }), 400
    
    # Check if user exists
    if user_email not in users:
        return jsonify({"error": "User not found"}), 404
    
    # Sanitize inputs
    title = sanitize_input(title)
    description = sanitize_input(description)
    
    # Generate unique task ID
    task_counter += 1
    task_id = task_counter
    
    # Create task
    task = Task(
        id=task_id,
        title=title,
        description=description,
        user_email=user_email,
        priority=priority,
        due_date=due_date
    )
    tasks[task_id] = task
    
    return jsonify(task.to_dict()), 201


@app.route("/tasks", methods=["GET"])
def get_tasks():
    """
    Get all tasks with optional filtering and sorting.
    
    Query Parameters:
        - user_email: Filter by user email
        - status: Filter by task status (pending, in_progress, completed)
        - priority: Filter by priority (low, medium, high, critical)
        - sort_by: Sort field (priority_score, due_date, created_at)
        - order: Sort order (asc, desc) - default: desc
    
    Returns:
        200: List of tasks
    """
    from app.utils import calculate_priority_score, get_days_until_due
    
    # Get filter parameters
    filter_user_email = request.args.get("user_email")
    filter_status = request.args.get("status")
    filter_priority = request.args.get("priority")
    
    # Get sorting parameters
    sort_by = request.args.get("sort_by", "created_at")
    order = request.args.get("order", "desc")
    
    # Filter tasks
    filtered_tasks = list(tasks.values())
    
    if filter_user_email:
        filtered_tasks = [t for t in filtered_tasks if t.user_email == filter_user_email]
    
    if filter_status:
        filtered_tasks = [t for t in filtered_tasks if t.status == filter_status]
    
    if filter_priority:
        filtered_tasks = [t for t in filtered_tasks if t.priority == filter_priority]
    
    # Sort tasks
    reverse_order = (order == "desc")
    
    if sort_by == "priority_score":
        def get_priority_score(task):
            try:
                if task.due_date:
                    days = get_days_until_due(task.due_date)
                else:
                    days = 30  # Default to 30 days if no due date
                return calculate_priority_score(task.priority, days)
            except (KeyError, ValueError):
                return 0
        filtered_tasks.sort(key=get_priority_score, reverse=reverse_order)
    elif sort_by == "due_date":
        # Tasks without due_date go to the end
        def due_date_key(task):
            if task.due_date is None:
                return "" if reverse_order else "9999-99-99"
            return task.due_date
        filtered_tasks.sort(key=due_date_key, reverse=reverse_order)
    else:  # Default to created_at
        filtered_tasks.sort(key=lambda t: t.created_at, reverse=reverse_order)
    
    return jsonify([task.to_dict() for task in filtered_tasks]), 200


if __name__ == "__main__":
    app.run(debug=True, port=5000)
