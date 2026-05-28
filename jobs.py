from functools import wraps
from flask import Blueprint, render_template, request, redirect, url_for, session, abort
import models

jobs_bp = Blueprint("jobs", __name__, template_folder="templates")


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get("username"):
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated_function


@jobs_bp.route("/jobs/create", methods=["GET", "POST"])
@login_required
def create_job():
    error = None
    users = list(models.User.select().order_by(models.User.username))
    current_user = models.get_user(session["username"])
    owner_id = str(current_user.id) if current_user else ""

    if request.method == "POST":
        job_name = request.form.get("job_name", "").strip()
        short_code = request.form.get("short_code", "").strip()
        full_description = request.form.get("full_description", "").strip()
        owner_id = request.form.get("owner", "").strip()

        if not job_name or not short_code or not full_description or not owner_id:
            error = "All fields are required."
        else:
            owner = models.User.get_or_none(models.User.id == int(owner_id))
            if owner is None:
                error = "Selected owner does not exist."

            if not error:
                job = models.Job.create(
                    job_name=job_name,
                    short_code=short_code,
                    full_description=full_description,
                    owner=owner,
                )
                return redirect(url_for("jobs.job_summary", job_id=job.id))

    return render_template(
        "jobs/create.html",
        error=error,
        username=session.get("username"),
        users=users,
        owner_id=owner_id,
    )


@jobs_bp.route("/jobs/<int:job_id>/edit", methods=["GET", "POST"])
@login_required
def edit_job(job_id):
    job = models.Job.get_or_none(models.Job.id == job_id)
    if job is None:
        abort(404)

    users = list(models.User.select().order_by(models.User.username))
    error = None
    owner_id = str(job.owner.id) if job.owner else ""

    if request.method == "POST":
        job_name = request.form.get("job_name", "").strip()
        short_code = request.form.get("short_code", "").strip()
        full_description = request.form.get("full_description", "").strip()
        owner_id = request.form.get("owner", "").strip()

        if not job_name or not short_code or not full_description or not owner_id:
            error = "All fields are required."
        else:
            owner = models.User.get_or_none(models.User.id == int(owner_id))
            if owner is None:
                error = "Selected owner does not exist."

            if not error:
                job.job_name = job_name
                job.short_code = short_code
                job.full_description = full_description
                job.owner = owner
                job.save()
                return redirect(url_for("jobs.job_summary", job_id=job.id))

    return render_template(
        "jobs/edit.html",
        job=job,
        error=error,
        username=session.get("username"),
        users=users,
        owner_id=owner_id,
    )


@jobs_bp.route("/jobs/<int:job_id>")
@login_required
def job_summary(job_id):
    job = models.Job.get_or_none(models.Job.id == job_id)
    if job is None:
        abort(404)

    return render_template(
        "jobs/summary.html",
        job=job,
        username=session.get("username"),
    )
