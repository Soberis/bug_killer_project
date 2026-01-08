from flask import Flask, render_template, request, redirect, url_for
import sqlite3
import os

# Create the Flask application instance
app = Flask(__name__)

# Database path (Using absolute path for stability)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, 'db', 'bugkiller.db')

def get_db_connection():
    """
    Helper function to create a database connection.
    row_factory allows us to access columns by name like a dictionary.
    """
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

# Define the root route to display the bug list from database
@app.route('/')
def home():
    """
    Fetch all bugs from the database and render them.
    """
    conn = get_db_connection()
    # SQL: SELECT all columns from bugs table, ordered by creation time
    bugs = conn.execute('SELECT * FROM bugs ORDER BY created_at DESC').fetchall()
    conn.close()
    
    # SDET Practice: Ensure we got a list (even if empty)
    assert isinstance(bugs, list), "Database result must be a list"
    
    return render_template('index.html', bugs=bugs)

# Route to handle adding a new bug to database
@app.route('/add', methods=['GET', 'POST'])
def add_bug():
    """
    GET: Show the add bug form.
    POST: Insert new bug into database and redirect.
    """
    if request.method == 'POST':
        title = request.form.get('bug_title')
        status = request.form.get('bug_status')
        
        assert title, "Bug title cannot be empty"
        
        # Database operation
        conn = get_db_connection()
        conn.execute('INSERT INTO bugs (title, status) VALUES (?, ?)', (title, status))
        conn.commit()
        conn.close()
        
        return redirect(url_for('home'))
    
    return render_template('add_bug.html')

# Route to handle deleting a bug
@app.route('/delete/<int:bug_id>')
def delete_bug(bug_id):
    """
    Delete a bug by its ID and redirect to home.
    <int:bug_id> is a URL variable that captures the ID from the link.
    """
    conn = get_db_connection()
    # SQL: DELETE command with a WHERE clause to target a specific row
    conn.execute('DELETE FROM bugs WHERE id = ?', (bug_id,))
    conn.commit()
    conn.close()
    
    return redirect(url_for('home'))

if __name__ == '__main__':
    # Start the Flask development server
    # host='0.0.0.0' is REQUIRED for Docker access
    app.run(host='0.0.0.0', port=5000, debug=True)
