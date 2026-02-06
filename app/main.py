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

# TODO: Implement POST /tasks endpoint
# TODO: Implement GET /tasks endpoint with filtering


if __name__ == "__main__":
    app.run(debug=True, port=5000)
