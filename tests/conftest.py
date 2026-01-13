import pytest

try:
    import pymysql
except ImportError:
    pymysql = None
import os
import sys

# Ensure project root is in sys.path for importing app
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Database configuration
DB_TYPE = os.environ.get("DATABASE_TYPE", "sqlite")
DB_HOST = os.environ.get("DB_HOST", "localhost")
DB_PORT = int(os.environ.get("DB_PORT", 3306))
DB_USER = os.environ.get("DB_USER", "root")
DB_PASSWORD = os.environ.get("DB_PASSWORD", "root")
DB_NAME = os.environ.get("DB_NAME", "bugkiller")


@pytest.fixture(scope="function")
def db_conn():
    """
    Fixture to provide a clean database connection for each test.
    Supports both SQLite and MySQL.
    """
    if DB_TYPE == "mysql":
        conn = pymysql.connect(
            host=DB_HOST,
            port=DB_PORT,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME,
            cursorclass=pymysql.cursors.DictCursor,
        )
    else:
        import sqlite3

        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        sqlite_path = os.path.join(base_dir, "db", "bugkiller.db")
        conn = sqlite3.connect(sqlite_path)
        conn.row_factory = sqlite3.Row

    try:
        yield conn
    finally:
        if DB_TYPE == "mysql":
            with conn.cursor() as cursor:
                cursor.execute("TRUNCATE TABLE bugs")
                conn.commit()
            conn.close()
        else:
            conn.execute("DELETE FROM bugs")
            conn.commit()
            conn.close()
