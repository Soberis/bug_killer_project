import sqlite3
import os

def init_database():
    # Get the absolute path of the current file's directory
    base_dir = os.path.dirname(os.path.abspath(__file__))
    db_dir = os.path.join(base_dir, 'db')
    db_path = os.path.join(db_dir, 'bugkiller.db')
    
    # Create the db directory if it doesn't exist
    if not os.path.exists(db_dir):
        os.makedirs(db_dir)
        print(f"Created directory: {db_dir}")
    
    # Connect to the database
    connection = sqlite3.connect(db_path)
    
    # Create a cursor object to execute SQL commands
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
    
    try:
        cursor.execute(create_table_sql)
        # Commit the changes and close the connection
        connection.commit()
        print(f"Successfully initialized database at: {db_path}")
    except Exception as e:
        print(f"Error occurred: {e}")
    finally:
        connection.close()

if __name__ == '__main__':
    init_database()
