import os
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import (
    LoginManager,
    UserMixin,
    login_user,
    logout_user,
    login_required,
)
from werkzeug.security import check_password_hash
from prometheus_flask_exporter import PrometheusMetrics
from prometheus_client import Counter
from celery import Celery

from database import db_manager
from config import Config

# Create the Flask application instance
app = Flask(__name__)
app.config.from_object(Config)

# Celery Configuration
celery = Celery(app.name, broker=app.config["CELERY_BROKER_URL"])
celery.conf.update(app.config)

# Register tasks with the configured celery instance
from tasks import register_tasks

tasks_registry = register_tasks(celery)
send_bug_report_email = tasks_registry

# [Level 17] Prometheus Metrics Setup
metrics = PrometheusMetrics(app, path="/metrics")
BUG_CREATED_COUNTER = Counter(
    "bug_created_total", "Total number of bugs reported", ["status"]
)

# Login Manager Setup
login_manager = LoginManager()
login_manager.login_view = "login"
login_manager.init_app(app)


# User Model for Flask-Login (kept here for simplicity, models.py is optional)
class User(UserMixin):
    def __init__(self, id, username):
        self.id = id
        self.username = username


@login_manager.user_loader
def load_user(user_id):
    row = db_manager.fetch_one(
        "SELECT id, username FROM users WHERE id = ?", (user_id,)
    )
    if row:
        uid = row["id"] if isinstance(row, dict) else row[0]
        uname = row["username"] if isinstance(row, dict) else row[1]
        return User(uid, uname)
    return None


# Initialize database before first request
with app.app_context():
    db_manager.init_db()


@app.route("/health")
def health_check():
    """Health check endpoint for K8s."""
    return {"status": "healthy"}, 200


@app.route("/")
def index():
    # [L16 FIX] Added LIMIT 20 to prevent O(N) latency
    bugs = db_manager.execute_query(
        "SELECT * FROM bugs ORDER BY created_at DESC LIMIT 20", fetch=True
    )
    return render_template("index.html", bugs=bugs)


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        user_row = db_manager.fetch_one(
            "SELECT * FROM users WHERE username = ?", (username,)
        )

        if user_row:
            stored_pw = (
                user_row["password"] if isinstance(user_row, dict) else user_row[2]
            )
            user_id = user_row["id"] if isinstance(user_row, dict) else user_row[0]

            if check_password_hash(stored_pw, password):
                user = User(user_id, username)
                login_user(user)
                return redirect(url_for("index"))

        flash("Invalid username or password")
    return render_template("login.html")


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("index"))


@app.route("/add", methods=["GET", "POST"])
def add_bug():
    if request.method == "POST":
        title = request.form.get("bug_title")
        status = request.form.get("bug_status")

        try:
            db_manager.execute_query(
                "INSERT INTO bugs (title, status) VALUES (?, ?)", (title, status)
            )
            BUG_CREATED_COUNTER.labels(status=status).inc()
        except Exception as e:
            app.logger.error(f"Database error during add_bug: {e}")
            flash(f"Error saving bug to database: {str(e)}")
            return redirect(url_for("index"))

        # [Level 14] Trigger background task (Async)
        try:
            send_bug_report_email.delay(title, status)
        except Exception as e:
            app.logger.error(f"Celery task submission failed: {e}")

        # [Level 15] External Notification (Async via Celery)
        try:
            celery.send_task("tasks.send_slack_notification", args=[title, status])
        except Exception as e:
            app.logger.error(f"Failed to queue Slack task: {e}")

        return redirect(url_for("index"))

    return render_template("add_bug.html")


@app.route("/delete/<int:bug_id>")
@login_required
def delete_bug(bug_id):
    try:
        db_manager.execute_query("DELETE FROM bugs WHERE id = ?", (bug_id,))
    except Exception as e:
        app.logger.error(f"Error deleting bug {bug_id}: {e}")
        flash(f"Error deleting bug: {str(e)}")

    return redirect(url_for("index"))


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
