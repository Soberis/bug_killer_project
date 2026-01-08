import os
import time
import sqlite3
import pymysql
from flask import Flask, render_template, request, redirect, url_for
from init_db import init_database
from tasks import send_bug_report_email

# Create the Flask application instance
app = Flask(__name__)

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
                    print(f"Database {DB_NAME} not found. Will create it.")
                    return get_db_connection(connect_to_db=False)
                
                retries -= 1
                print(f"Waiting for MySQL ({DB_HOST})... {retries} retries left. Error: {e}")
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
                print(f"Database {DB_NAME} ensured.")
            conn.commit()
        finally:
            conn.close()

        # 3. Connect to the specific DB and create tables
        conn = get_db_connection(connect_to_db=True)
        try:
            with conn.cursor() as cursor:
                # Create bugs table if it doesn't exist for MySQL
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS bugs (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        title VARCHAR(255) NOT NULL,
                        status VARCHAR(50) DEFAULT 'New',
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
            conn.commit()
            print("Table 'bugs' ensured.")
            
            # 4. Auto Seeding: If table is empty, add sample data
            with conn.cursor() as cursor:
                cursor.execute("SELECT COUNT(*) as count FROM bugs")
                result = cursor.fetchone()
                if result['count'] == 0:
                    print("Database is empty. Seeding sample data...")
                    sample_bugs = [
                        ('Login page crashing on Chrome', 'Open'),
                        ('UI button color is wrong', 'In Progress'),
                        ('API returning 500 error on /search', 'New')
                    ]
                    cursor.executemany("INSERT INTO bugs (title, status) VALUES (%s, %s)", sample_bugs)
                    conn.commit()
                    print("Sample data seeded successfully.")
        finally:
            conn.close()

# Initialize database before first request
with app.app_context():
    init_db_schema()

# Define the root route
@app.route('/')
def home():
    conn = get_db_connection()
    if DB_TYPE == 'mysql':
        with conn.cursor() as cursor:
            cursor.execute('SELECT * FROM bugs ORDER BY created_at DESC')
            bugs = cursor.fetchall()
    else:
        bugs = conn.execute('SELECT * FROM bugs ORDER BY created_at DESC').fetchall()
    conn.close()
    return render_template('index.html', bugs=bugs)

# Route to handle adding a new bug
@app.route('/add', methods=['GET', 'POST'])
def add_bug():
    if request.method == 'POST':
        title = request.form.get('bug_title')
        status = request.form.get('bug_status')
        
        conn = get_db_connection()
        if DB_TYPE == 'mysql':
            with conn.cursor() as cursor:
                cursor.execute('INSERT INTO bugs (title, status) VALUES (%s, %s)', (title, status))
        else:
            conn.execute('INSERT INTO bugs (title, status) VALUES (?, ?)', (title, status))
        conn.commit()
        conn.close()

        # [Level 14] Trigger background task (Async)
        # We don't wait for the result here, so the user gets redirected immediately
        send_bug_report_email.delay(title, status)

        return redirect(url_for('home'))
    
    return render_template('add_bug.html')

# Route to handle deleting a bug
@app.route('/delete/<int:bug_id>')
def delete_bug(bug_id):
    conn = get_db_connection()
    if DB_TYPE == 'mysql':
        with conn.cursor() as cursor:
            cursor.execute('DELETE FROM bugs WHERE id = %s', (bug_id,))
    else:
        conn.execute('DELETE FROM bugs WHERE id = ?', (bug_id,))
    conn.commit()
    conn.close()
    return redirect(url_for('home'))

if __name__ == '__main__':
    # Start the Flask development server
    # host='0.0.0.0' is REQUIRED for Docker access
    app.run(host='0.0.0.0', port=5000, debug=True)
