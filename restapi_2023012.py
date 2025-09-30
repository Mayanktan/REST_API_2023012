
"""
Task Manager REST API
Author: Student (Roll No: 12345)
Description: Flask-based REST API for managing tasks with CRUD operations.
"""

from flask import Flask, request, jsonify
from datetime import datetime
import uuid

# App initialization
app = Flask(__name__)

# In-memory task list (for demo purpose; production should use DB)
task_store = []

# Preloaded demo tasks
task_store.extend([
    {
        "id": str(uuid.uuid4()),
        "title": "Finish REST API homework",
        "description": "Build Flask CRUD endpoints for tasks",
        "status": "in_progress",
        "created": "2025-09-30T10:00:00",
        "updated": "2025-09-30T10:00:00"
    },
    {
        "id": str(uuid.uuid4()),
        "title": "Prepare for software exam",
        "description": "Revise Flask concepts and REST fundamentals",
        "status": "pending",
        "created": "2025-09-30T09:00:00",
        "updated": "2025-09-30T09:00:00"
    }
])

# -------- Utility functions -------- #
def get_task(tid):
    """Return task dict by id if found"""
    return next((t for t in task_store if t["id"] == tid), None)

def check_task_input(payload, must_have=None):
    """Ensure input data has required fields and valid status"""
    if must_have is None:
        must_have = ["title"]

    for key in must_have:
        if key not in payload or not str(payload[key]).strip():
            return False, f"'{key}' is required and cannot be blank"

    allowed_status = {"pending", "in_progress", "completed"}
    if "status" in payload and payload["status"] not in allowed_status:
        return False, f"Status must be one of: {', '.join(allowed_status)}"

    return True, ""


# ----------- API Endpoints ----------- #

@app.route("/tasks", methods=["GET"])
def list_tasks():
    """Return all tasks, optionally filter by status"""
    status = request.args.get("status")
    if status:
        result = [t for t in task_store if t["status"] == status]
        return jsonify(ok=True, tasks=result, total=len(result)), 200

    return jsonify(ok=True, tasks=task_store, total=len(task_store)), 200


@app.route("/tasks/<string:tid>", methods=["GET"])
def fetch_task(tid):
    """Return single task by ID"""
    t = get_task(tid)
    if not t:
        return jsonify(ok=False, error="Not Found", message=f"No task with id {tid}"), 404
    return jsonify(ok=True, task=t), 200


@app.route("/tasks", methods=["POST"])
def add_task():
    """Create a new task"""
    data = request.get_json(silent=True)
    if not data:
        return jsonify(ok=False, error="Bad Request", message="JSON body required"), 400

    valid, msg = check_task_input(data, ["title"])
    if not valid:
        return jsonify(ok=False, error="Validation Error", message=msg), 400

    now = datetime.now().isoformat()
    new_task = {
        "id": str(uuid.uuid4()),
        "title": data["title"].strip(),
        "description": data.get("description", "").strip(),
        "status": data.get("status", "pending"),
        "created": now,
        "updated": now
    }

    task_store.append(new_task)
    return jsonify(ok=True, task=new_task, message="Task successfully created"), 201


@app.route("/tasks/<string:tid>", methods=["PUT"])
def modify_task(tid):
    """Update an existing task"""
    t = get_task(tid)
    if not t:
        return jsonify(ok=False, error="Not Found", message=f"Task id {tid} not found"), 404

    data = request.get_json(silent=True)
    if not data:
        return jsonify(ok=False, error="Bad Request", message="JSON body required"), 400

    valid, msg = check_task_input(data, [])
    if not valid:
        return jsonify(ok=False, error="Validation Error", message=msg), 400

    if "title" in data and data["title"].strip():
        t["title"] = data["title"].strip()
    if "description" in data:
        t["description"] = data["description"].strip()
    if "status" in data:
        t["status"] = data["status"]

    t["updated"] = datetime.now().isoformat()

    return jsonify(ok=True, task=t, message="Task updated"), 200


@app.route("/tasks/<string:tid>", methods=["DELETE"])
def remove_task(tid):
    """Delete a single task by ID"""
    t = get_task(tid)
    if not t:
        return jsonify(ok=False, error="Not Found", message=f"No task with id {tid}"), 404

    task_store.remove(t)
    return jsonify(ok=True, message="Task removed", deleted=tid), 200


@app.route("/tasks", methods=["DELETE"])
def remove_all():
    """Clear all tasks"""
    n = len(task_store)
    task_store.clear()
    return jsonify(ok=True, message=f"Removed {n} tasks", count=n), 200


@app.route("/health", methods=["GET"])
def ping():
    """Health check endpoint"""
    return jsonify(ok=True, status="running", total=len(task_store), time=datetime.now().isoformat()), 200


@app.route("/", methods=["GET"])
def root_info():
    """API root description"""
    return jsonify(
        name="Task Manager API",
        version="1.0",
        endpoints={
            "GET /tasks": "List all tasks or filter by status",
            "GET /tasks/<id>": "Get one task",
            "POST /tasks": "Create task",
            "PUT /tasks/<id>": "Update task",
            "DELETE /tasks/<id>": "Delete task",
            "DELETE /tasks": "Delete all tasks",
            "GET /health": "Health check"
        }
    ), 200


# ----- Error Handlers ----- #
@app.errorhandler(404)
def handle_404(e):
    return jsonify(ok=False, error="Invalid endpoint"), 404

@app.errorhandler(405)
def handle_405(e):
    return jsonify(ok=False, error="Method not allowed"), 405

@app.errorhandler(500)
def handle_500(e):
    return jsonify(ok=False, error="Server error"), 500


if __name__ == "__main__":
    print("Starting Task Manager API on http://127.0.0.1:5005")
    app.run(debug=True, host="0.0.0.0", port=5005)

