import os
import time
import sqlite3
import pymysql
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from init_db import init_database
from prometheus_flask_exporter import PrometheusMetrics
from prometheus_client import Counter

from database import db_manager

# Create the Flask application instance
app = Flask(__name__)
app.config['SECRET_KEY'] = 'dev-secret-key' # Required for session/flash

# [Level 13/14] Redis Configuration from Environment
REDIS_URL = os.environ.get('REDIS_URL', 'redis://localhost:6379/0')
app.config['CELERY_BROKER_URL'] = REDIS_URL
app.config['CELERY_RESULT_BACKEND'] = REDIS_URL

# Override for testing environment
if os.environ.get('TESTING') == 'True':
    app.config['CELERY_TASK_ALWAYS_EAGER'] = True
    app.config['CELERY_BROKER_URL'] = 'memory://'
    app.config['CELERY_RESULT_BACKEND'] = 'cache+memory://'

from celery import Celery
celery = Celery(app.name, broker=app.config['CELERY_BROKER_URL'])
celery.conf.update(app.config)

# Register tasks with the configured celery instance
from tasks import register_tasks
send_bug_report_email = register_tasks(celery)

metrics = PrometheusMetrics(app)

# [Level 17] Custom Metrics for SDET Analysis
BUG_CREATED_COUNTER = Counter('bug_created_total', 'Total number of bugs reported', ['status'])

# Login Manager Setup
login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.init_app(app)

# User Model for Flask-Login
class User(UserMixin):
    def __init__(self, id, username):
        self.id = id
        self.username = username

@login_manager.user_loader
def load_user(user_id):
    row = db_manager.fetch_one('SELECT id, username FROM users WHERE id = ?', (user_id,))
    if row:
        # Handle dict vs tuple
        uid = row['id'] if isinstance(row, dict) else row[0]
        uname = row['username'] if isinstance(row, dict) else row[1]
        return User(uid, uname)
    return None

# Initialize database before first request
with app.app_context():
    db_manager.init_db()

@app.route('/health')
def health_check():
    """Health check endpoint for K8s."""
    return {"status": "healthy"}, 200

# Define the root route
@app.route('/')
def index():
    bugs = db_manager.execute_query('SELECT * FROM bugs ORDER BY created_at DESC', fetch=True)
    return render_template('index.html', bugs=bugs)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user_row = db_manager.fetch_one('SELECT * FROM users WHERE username = ?', (username,))

        if user_row:
            # Handle different row formats
            stored_pw = user_row['password'] if isinstance(user_row, dict) else user_row[2]
            user_id = user_row['id'] if isinstance(user_row, dict) else user_row[0]
            
            if check_password_hash(stored_pw, password):
                user = User(user_id, username)
                login_user(user)
                return redirect(url_for('index'))
        
        flash('Invalid username or password')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

# Route to handle adding a new bug
@app.route('/add', methods=['GET', 'POST'])
@login_required
def add_bug():
    if request.method == 'POST':
        title = request.form.get('bug_title')
        status = request.form.get('bug_status')
        
        try:
            db_manager.execute_query('INSERT INTO bugs (title, status) VALUES (?, ?)', (title, status))
            # [Level 17] Increment custom metric
            BUG_CREATED_COUNTER.labels(status=status).inc()
        except Exception as e:
            app.logger.error(f"Database error during add_bug: {e}")
            flash(f"Error saving bug to database: {str(e)}")
            return redirect(url_for('index'))

        # [Level 14] Trigger background task (Async)
        try:
            send_bug_report_email.delay(title, status)
        except Exception as e:
            app.logger.error(f"Celery task submission failed (Redis down?): {e}")

        # [Level 15] External Notification Simulation
        try:
            import requests as external_requests
            # We use a short timeout to prevent hanging the main thread
            external_requests.post("https://api.slack.com/messaging/send", json={
                "text": f"New Bug Reported: {title} (Status: {status})"
            }, timeout=0.5)
        except Exception as e:
            app.logger.error(f"External notification failed (Normal if not in Level 15): {e}")

        return redirect(url_for('index'))
    
    return render_template('add_bug.html')

# Route to handle deleting a bug
@app.route('/delete/<int:bug_id>')
@login_required
def delete_bug(bug_id):
    try:
        db_manager.execute_query('DELETE FROM bugs WHERE id = ?', (bug_id,))
    except Exception as e:
        app.logger.error(f"Error deleting bug {bug_id}: {e}")
        flash(f"Error deleting bug: {str(e)}")
        
    return redirect(url_for('index'))


if __name__ == '__main__':
    # Start the Flask development server
    # host='0.0.0.0' is REQUIRED for Docker access
    app.run(host='0.0.0.0', port=5000, debug=True)
