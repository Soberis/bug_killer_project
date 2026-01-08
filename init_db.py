import sqlite3
import os

def init_database():
    # Ensure the db directory exists
    db_path = 'db/bugkiller.db'
    
    # Connect to the database (it will be created if it doesn't exist)
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
