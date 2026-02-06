# Mufthi - 2/6/2026
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

VALID_PRIORITIES = {"low", "medium", "high", "critical"}


@app.route("/tasks", methods=["POST"])
def create_task():
    """Create a new task"""
    global task_counter
    
    data = request.get_json()
    
    # Check for required fields
    if not data:
        return jsonify({"error": "Missing request body"}), 400
    
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
    
    # Validate priority value
    if priority not in VALID_PRIORITIES:
        return jsonify({"error": f"Invalid priority. Must be one of: {', '.join(sorted(VALID_PRIORITIES))}"}), 400
    
    # Check if user exists
    if user_email not in users:
        return jsonify({"error": "User not found"}), 404
    
    # Auto-generate unique task ID
    task_counter += 1
    task_id = task_counter
    
    # Get optional fields with defaults
    description = data.get("description", "")
    status = data.get("status", "pending")
    due_date = data.get("due_date", None)
    
    # Create the task
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
def get_tasks():
    """Get all tasks with optional filtering and sorting"""
    from app.utils import get_days_until_due, calculate_priority_score
    
    # Get query parameters for filtering
    filter_user_email = request.args.get("user_email")
    filter_status = request.args.get("status")
    filter_priority = request.args.get("priority")
    
    # Get query parameter for sorting
    sort_by = request.args.get("sort_by")  # priority_score, due_date, created_at
    sort_order = request.args.get("sort_order", "asc")  # asc or desc
    
    # Start with all tasks
    result_tasks = list(tasks.values())
    
    # Apply filters
    if filter_user_email:
        result_tasks = [t for t in result_tasks if t.user_email == filter_user_email]
    
    if filter_status:
        result_tasks = [t for t in result_tasks if t.status == filter_status]
    
    if filter_priority:
        result_tasks = [t for t in result_tasks if t.priority == filter_priority]
    
    # Apply sorting
    if sort_by:
        reverse = sort_order.lower() == "desc"
        
        if sort_by == "priority_score":
            def get_priority_score(task):
                if task.due_date:
                    try:
                        days = get_days_until_due(task.due_date)
                    except:
                        days = 999  # Default for invalid dates
                else:
                    days = 999  # No due date means low urgency
                return calculate_priority_score(task.priority, days)
            
            result_tasks.sort(key=get_priority_score, reverse=reverse)
        
        elif sort_by == "due_date":
            def get_due_date_key(task):
                if task.due_date:
                    return task.due_date
                # Tasks without due dates go to the end
                return "9999-12-31" if not reverse else "0000-01-01"
            
            result_tasks.sort(key=get_due_date_key, reverse=reverse)
        
        elif sort_by == "created_at":
            result_tasks.sort(key=lambda t: t.created_at, reverse=reverse)
    
    return jsonify([task.to_dict() for task in result_tasks])


if __name__ == "__main__":
    app.run(debug=True, port=5000)
