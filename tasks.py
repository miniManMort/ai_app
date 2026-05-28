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
    users = list(models.User.select().order_by(models.User.username))
    jobs = list(models.Job.select().order_by(models.Job.job_name))
    status_value = models.Task.STATUS_NEW
    job_id = ""
    if request.method == "POST":
        summary = request.form.get("summary", "").strip()
        full_description = request.form.get("full_description", "").strip()
        due_date_str = request.form.get("due_date", "").strip()
        status_value = request.form.get("status", models.Task.STATUS_NEW).strip()
        assigned_to_id = request.form.get("assigned_to", "").strip()
        job_id = request.form.get("job_id", "").strip()

        if not summary or not full_description or not due_date_str or not status_value:
            error = "All fields are required."
        elif status_value not in models.Task.STATUS_CHOICES:
            error = "Invalid status selected."
        else:
            try:
                due_date = datetime.strptime(due_date_str, "%Y-%m-%d").date()
                current_user = models.get_user(session["username"])
                if current_user is None:
                    abort(400)

                assigned_to = None
                if assigned_to_id:
                    assigned_to = models.User.get_or_none(models.User.id == int(assigned_to_id))
                    if assigned_to is None:
                        error = "Selected assignee does not exist."

                job = None
                if job_id:
                    job = models.Job.get_or_none(models.Job.id == int(job_id))
                    if job is None:
                        error = "Selected job does not exist."

                if not error:
                    models.Task.create(
                        summary=summary,
                        full_description=full_description,
                        due_date=due_date,
                        status=status_value,
                        created_by=current_user,
                        assigned_to=assigned_to,
                        job_id=job,
                    )
                    return redirect(url_for("index"))
            except ValueError:
                error = "Due date must be in YYYY-MM-DD format."

    return render_template(
        "tasks/create.html",
        error=error,
        username=session.get("username"),
        users=users,
        jobs=jobs,
        statuses=models.Task.STATUS_CHOICES,
        status_value=status_value,
        job_id=job_id,
    )


@tasks_bp.route("/tasks/<int:task_id>/edit", methods=["GET", "POST"])
@login_required
def edit_task(task_id):
    task = models.Task.get_or_none(models.Task.id == task_id)
    if task is None:
        abort(404)

    users = list(models.User.select().order_by(models.User.username))
    jobs = list(models.Job.select().order_by(models.Job.job_name))
    error = None
    status_value = task.status
    job_id = str(task.job_id.id) if task.job_id else ""
    if request.method == "POST":
        summary = request.form.get("summary", "").strip()
        full_description = request.form.get("full_description", "").strip()
        due_date_str = request.form.get("due_date", "").strip()
        status_value = request.form.get("status", task.status).strip()
        assigned_to_id = request.form.get("assigned_to", "").strip()
        job_id = request.form.get("job_id", job_id).strip()

        if not summary or not full_description or not due_date_str or not status_value:
            error = "All fields are required."
        elif status_value not in models.Task.STATUS_CHOICES:
            error = "Invalid status selected."
        else:
            try:
                task.summary = summary
                task.full_description = full_description
                task.due_date = datetime.strptime(due_date_str, "%Y-%m-%d").date()

                assigned_to = None
                if assigned_to_id:
                    assigned_to = models.User.get_or_none(models.User.id == int(assigned_to_id))
                    if assigned_to is None:
                        error = "Selected assignee does not exist."

                job = None
                if job_id:
                    job = models.Job.get_or_none(models.Job.id == int(job_id))
                    if job is None:
                        error = "Selected job does not exist."

                if not error:
                    task.assigned_to = assigned_to
                    task.status = status_value
                    task.job_id = job
                    task.save()
                    return redirect(url_for("index"))
            except ValueError:
                error = "Due date must be in YYYY-MM-DD format."

    return render_template(
        "tasks/edit.html",
        task=task,
        error=error,
        username=session.get("username"),
        users=users,
        jobs=jobs,
        statuses=models.Task.STATUS_CHOICES,
        status_value=status_value,
        job_id=job_id,
    )
