from functools import wraps
from flask import Flask, render_template, request, redirect, url_for, session
from werkzeug.security import check_password_hash
from peewee import JOIN
import models
from tasks import tasks_bp
from jobs import jobs_bp

app = Flask(__name__)
app.secret_key = "replace-this-with-a-secure-random-value"

app.register_blueprint(tasks_bp)
app.register_blueprint(jobs_bp)


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get("username"):
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated_function


@app.route("/")
@login_required
def index():
    creator = models.User.alias()
    assignee = models.User.alias()
    tasks = list(
        models.Task.select(models.Task, creator, assignee)
        .join(creator, on=(models.Task.created_by == creator.id))
        .switch(models.Task)
        .join(assignee, JOIN.LEFT_OUTER, on=(models.Task.assigned_to == assignee.id))
        .order_by(models.Task.due_date)
        .limit(5)
    )
    jobs = list(
        models.Job.select(models.Job, models.User)
        .join(models.User, on=(models.Job.owner == models.User.id))
        .order_by(models.Job.job_name)
        .limit(5)
    )
    return render_template(
        "index.html",
        username=session.get("username"),
        tasks=tasks,
        jobs=jobs,
    )


@app.route("/logout")
def logout():
    session.pop("username", None)
    return redirect(url_for("login"))


@app.route("/login", methods=["GET", "POST"])
def login():
    error = None
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        user = models.get_user(username)
        if user and check_password_hash(user.password_hash, password):
            session["username"] = username
            return redirect(url_for("index"))
        error = "Invalid username or password"
    return render_template("login.html", error=error)


if __name__ == "__main__":
    models.init_db(seed=False)
    app.run(host="0.0.0.0", port=5000, debug=True)
