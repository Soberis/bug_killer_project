import os
from database import DatabaseManager

def init_database():
    # Use MySQL if DATABASE_URL is present, otherwise fallback to SQLite
    db_url = os.getenv('DATABASE_URL')
    
    if db_url:
        print(f"Initializing MySQL database...")
        db_manager = DatabaseManager(db_url)
        # Use %s for MySQL
        db_manager.execute_query('DROP TABLE IF EXISTS bugs')
        db_manager.execute_query('CREATE TABLE bugs (id INT AUTO_INCREMENT PRIMARY KEY, title VARCHAR(255) NOT NULL, status VARCHAR(50) DEFAULT "New")')
        db_manager.execute_query('INSERT INTO bugs (title, status) VALUES (%s, %s)', ('First Sample Bug', 'New'))
        print("MySQL database initialized.")
        return

    # Legacy SQLite path (for local dev)
    import sqlite3
    print("Initializing local SQLite database...")
    base_dir = os.path.dirname(os.path.abspath(__file__))
    db_dir = os.path.join(base_dir, 'db')
    db_path = os.path.join(db_dir, 'bugkiller.db')
    
    if not os.path.exists(db_dir):
        os.makedirs(db_dir)
    
    connection = sqlite3.connect(db_path)
    cursor = connection.cursor()
    
    # SQL command to create the bugs table
    # id: Unique identifier, auto-increments
    # title: The description of the bug
    # status: Current state of the bug
    # created_at: Automatically store the time of entry
    create_table_sql = """
    CREATE TABLE IF NOT EXISTS bugs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        status TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """
    
    create_users_sql = """
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL
    )
    """
    
    try:
        cursor.execute(create_table_sql)
        cursor.execute(create_users_sql)
        
        # Seed admin user if not exists
        cursor.execute("SELECT COUNT(*) FROM users")
        if cursor.fetchone()[0] == 0:
            from werkzeug.security import generate_password_hash
            hashed_pw = generate_password_hash('admin123')
            cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", ('admin', hashed_pw))
            
        connection.commit()
        print(f"Successfully initialized database at: {db_path}")
    except Exception as e:
        print(f"Error occurred: {e}")
    finally:
        connection.close()

if __name__ == '__main__':
    init_database()
