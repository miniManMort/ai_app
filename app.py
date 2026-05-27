from flask import Flask, render_template, request
from werkzeug.security import check_password_hash
import models

app = Flask(__name__)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    error = None
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        user = models.get_user(username)
        if user and check_password_hash(user.password_hash, password):
            return render_template("welcome.html", username=username)
        error = "Invalid username or password"
    return render_template("login.html", error=error)


if __name__ == "__main__":
    models.init_db(seed=False)
    app.run(host="0.0.0.0", port=5000, debug=True)
