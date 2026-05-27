from functools import wraps
from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for, session, abort
import models

tasks_bp = Blueprint("tasks", __name__, template_folder="templates")


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get("username"):
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated_function


@tasks_bp.route("/tasks/create", methods=["GET", "POST"])
@login_required
def create_task():
    error = None
    if request.method == "POST":
        summary = request.form.get("summary", "").strip()
        full_description = request.form.get("full_description", "").strip()
        due_date_str = request.form.get("due_date", "").strip()

        if not summary or not full_description or not due_date_str:
            error = "All fields are required."
        else:
            try:
                due_date = datetime.strptime(due_date_str, "%Y-%m-%d").date()
                models.Task.create(
                    summary=summary,
                    full_description=full_description,
                    due_date=due_date,
                )
                return redirect(url_for("index"))
            except ValueError:
                error = "Due date must be in YYYY-MM-DD format."

    return render_template(
        "tasks/create.html",
        error=error,
        username=session.get("username"),
    )


@tasks_bp.route("/tasks/<int:task_id>/edit", methods=["GET", "POST"])
@login_required
def edit_task(task_id):
    task = models.Task.get_or_none(models.Task.id == task_id)
    if task is None:
        abort(404)

    error = None
    if request.method == "POST":
        summary = request.form.get("summary", "").strip()
        full_description = request.form.get("full_description", "").strip()
        due_date_str = request.form.get("due_date", "").strip()

        if not summary or not full_description or not due_date_str:
            error = "All fields are required."
        else:
            try:
                task.summary = summary
                task.full_description = full_description
                task.due_date = datetime.strptime(due_date_str, "%Y-%m-%d").date()
                task.save()
                return redirect(url_for("index"))
            except ValueError:
                error = "Due date must be in YYYY-MM-DD format."

    return render_template(
        "tasks/edit.html",
        task=task,
        error=error,
        username=session.get("username"),
    )
