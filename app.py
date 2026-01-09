import os
import time
import sqlite3
import pymysql
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from init_db import init_database
from prometheus_flask_exporter import PrometheusMetrics

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
    conn = get_db_connection()
    user = None
    if DB_TYPE == 'mysql':
        with conn.cursor() as cursor:
            cursor.execute('SELECT id, username FROM users WHERE id = %s', (user_id,))
            row = cursor.fetchone()
            if row:
                user = User(row['id'], row['username'])
    else:
        row = conn.execute('SELECT id, username FROM users WHERE id = ?', (user_id,)).fetchone()
        if row:
            user = User(row[0], row[1])
    conn.close()
    return user

# Database Configuration from Environment Variables
DB_TYPE = os.environ.get('DATABASE_TYPE', 'mysql')
DB_HOST = os.environ.get('DB_HOST', 'localhost')
DB_USER = os.environ.get('DB_USER', 'root')
DB_PASSWORD = os.environ.get('DB_PASSWORD', 'root')
DB_NAME = os.environ.get('DB_NAME', 'bugkiller')

# SQLite path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SQLITE_PATH = os.path.join(BASE_DIR, 'db', 'bugkiller.db')

def get_db_connection(connect_to_db=True):
    """
    Helper function to create a database connection.
    Supports both SQLite and MySQL based on environment.
    If connect_to_db is False, connects to MySQL server without selecting a DB.
    """
    if DB_TYPE == 'mysql':
        # Retry logic for MySQL as it takes time to boot up in Docker
        retries = 10
        while retries > 0:
            try:
                conn = pymysql.connect(
                    host=DB_HOST,
                    user=DB_USER,
                    password=DB_PASSWORD,
                    database=DB_NAME if connect_to_db else None,
                    cursorclass=pymysql.cursors.DictCursor,
                    connect_timeout=10
                )
                return conn
            except Exception as e:
                # If database doesn't exist, we need to connect without DB first
                if "Unknown database" in str(e) and connect_to_db:
                    app.logger.warning(f"Database {DB_NAME} not found. Will create it.")
                    return get_db_connection(connect_to_db=False)
                
                retries -= 1
                app.logger.warning(f"Waiting for MySQL ({DB_HOST})... {retries} retries left. Error: {e}")
                time.sleep(5)
        raise Exception("Could not connect to MySQL after several retries.")
    else:
        # Fallback to SQLite
        conn = sqlite3.connect(SQLITE_PATH)
        conn.row_factory = sqlite3.Row
        return conn

def init_db_schema():
    """Ensure database and tables exist."""
    if DB_TYPE == 'sqlite':
        init_database()
    else:
        # 1. Connect to MySQL Server (without DB)
        conn = get_db_connection(connect_to_db=False)
        try:
            with conn.cursor() as cursor:
                # 2. Create Database if not exists
                cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DB_NAME}")
                app.logger.info(f"Database {DB_NAME} ensured.")
            conn.commit()
        finally:
            conn.close()

        # 3. Connect to the specific DB and create tables
        conn = get_db_connection(connect_to_db=True)
        try:
            with conn.cursor() as cursor:
                # Create bugs table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS bugs (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        title VARCHAR(255) NOT NULL,
                        status VARCHAR(50) DEFAULT 'New',
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                # Create users table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS users (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        username VARCHAR(100) UNIQUE NOT NULL,
                        password VARCHAR(255) NOT NULL
                    )
                ''')
            conn.commit()
            app.logger.info("Tables 'bugs' and 'users' ensured.")
            
            # 4. Auto Seeding: If tables are empty, add sample data
            with conn.cursor() as cursor:
                # Seed bugs
                cursor.execute("SELECT COUNT(*) as count FROM bugs")
                if cursor.fetchone()['count'] == 0:
                    app.logger.info("Seeding sample bugs...")
                    sample_bugs = [
                        ('Login page crashing on Chrome', 'Open'),
                        ('UI button color is wrong', 'In Progress'),
                        ('API returning 500 error on /search', 'New')
                    ]
                    cursor.executemany("INSERT INTO bugs (title, status) VALUES (%s, %s)", sample_bugs)
                
                # Seed admin user (password: admin123)
                cursor.execute("SELECT COUNT(*) as count FROM users")
                if cursor.fetchone()['count'] == 0:
                    app.logger.info("Seeding admin user...")
                    hashed_pw = generate_password_hash('admin123')
                    cursor.execute("INSERT INTO users (username, password) VALUES (%s, %s)", ('admin', hashed_pw))
            conn.commit()
            app.logger.info("Sample data seeded successfully.")
        finally:
            conn.close()

# Initialize database before first request
with app.app_context():
    init_db_schema()

@app.route('/health')
def health_check():
    """Health check endpoint for K8s."""
    return {"status": "healthy"}, 200

# Define the root route
@app.route('/')
def index():
    conn = get_db_connection()
    if DB_TYPE == 'mysql':
        with conn.cursor() as cursor:
            cursor.execute('SELECT * FROM bugs ORDER BY created_at DESC')
            bugs = cursor.fetchall()
    else:
        bugs = conn.execute('SELECT * FROM bugs ORDER BY created_at DESC').fetchall()
    conn.close()
    return render_template('index.html', bugs=bugs)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        conn = get_db_connection()
        user_row = None
        if DB_TYPE == 'mysql':
            with conn.cursor() as cursor:
                cursor.execute('SELECT * FROM users WHERE username = %s', (username,))
                user_row = cursor.fetchone()
        else:
            user_row = conn.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
        conn.close()

        if user_row:
            # Handle different row formats (Dict for MySQL, Tuple/Row for SQLite)
            stored_pw = user_row['password'] if DB_TYPE == 'mysql' else user_row[2]
            user_id = user_row['id'] if DB_TYPE == 'mysql' else user_row[0]
            
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
            conn = get_db_connection()
            if DB_TYPE == 'mysql':
                with conn.cursor() as cursor:
                    cursor.execute('INSERT INTO bugs (title, status) VALUES (%s, %s)', (title, status))
            else:
                conn.execute('INSERT INTO bugs (title, status) VALUES (?, ?)', (title, status))
            conn.commit()
            conn.close()
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
        conn = get_db_connection()
        if DB_TYPE == 'mysql':
            with conn.cursor() as cursor:
                cursor.execute('DELETE FROM bugs WHERE id = %s', (bug_id,))
        else:
            conn.execute('DELETE FROM bugs WHERE id = ?', (bug_id,))
        conn.commit()
        conn.close()
    except Exception as e:
        app.logger.error(f"Error deleting bug {bug_id}: {e}")
        flash(f"Error deleting bug: {str(e)}")
        
    return redirect(url_for('index'))

if __name__ == '__main__':
    # Start the Flask development server
    # host='0.0.0.0' is REQUIRED for Docker access
    app.run(host='0.0.0.0', port=5000, debug=True)
