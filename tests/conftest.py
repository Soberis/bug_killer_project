import pytest
import pymysql
import os

# Database configuration (Same as app.py)
DB_HOST = os.environ.get('DB_HOST', '127.0.0.1')
DB_USER = os.environ.get('DB_USER', 'root')
DB_PASSWORD = os.environ.get('DB_PASSWORD', 'root')
DB_NAME = os.environ.get('DB_NAME', 'bugkiller')

@pytest.fixture(scope="function")
def db_conn():
    """
    Fixture to provide a clean database connection for each test.
    """
    # SETUP: Connect to DB
    conn = pymysql.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME,
        cursorclass=pymysql.cursors.DictCursor
    )
    
    try:
        yield conn  # Provide the connection to the test
    finally:
        # TEARDOWN: Clean up data after the test
        with conn.cursor() as cursor:
            # We only delete the bugs added during testing
            # For simplicity now, we'll truncate the table
            cursor.execute("TRUNCATE TABLE bugs")
            conn.commit()
        conn.close()
        print("\n[Teardown] Database cleaned up.")
