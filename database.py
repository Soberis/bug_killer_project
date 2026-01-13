import os
import time
import sqlite3
import pymysql
from werkzeug.security import generate_password_hash


class DatabaseManager:
    def __init__(self):
        self.db_type = os.environ.get("DATABASE_TYPE", "sqlite")
        self.host = os.environ.get("DB_HOST", "localhost")
        self.port = int(os.environ.get("DB_PORT", 3306))
        self.user = os.environ.get("DB_USER", "root")
        self.password = os.environ.get("DB_PASSWORD", "root")
        self.db_name = os.environ.get("DB_NAME", "bugkiller")

        base_dir = os.path.dirname(os.path.abspath(__file__))
        self.sqlite_path = os.path.join(base_dir, "db", "bugkiller.db")

    def get_connection(self, connect_to_db=True):
        if self.db_type == "mysql":
            retries = 5
            while retries > 0:
                try:
                    conn = pymysql.connect(
                        host=self.host,
                        port=self.port,
                        user=self.user,
                        password=self.password,
                        database=self.db_name if connect_to_db else None,
                        cursorclass=pymysql.cursors.DictCursor,
                        connect_timeout=5,
                    )
                    return conn
                except Exception as e:
                    if "Unknown database" in str(e) and connect_to_db:
                        return self.get_connection(connect_to_db=False)
                    retries -= 1
                    time.sleep(2)
            raise Exception("MySQL connection failed")
        else:
            conn = sqlite3.connect(self.sqlite_path)
            conn.row_factory = sqlite3.Row
            return conn

    def execute_query(self, query, params=(), fetch=False):
        """Execute a query with retry logic for resilience."""
        retries = 3
        last_error = None

        while retries > 0:
            try:
                conn = self.get_connection()
                try:
                    if self.db_type == "mysql":
                        query = query.replace("?", "%s")
                        with conn.cursor() as cursor:
                            cursor.execute(query, params)
                            if fetch:
                                return cursor.fetchall()
                            conn.commit()
                            return cursor.lastrowid
                    else:
                        cursor = conn.execute(query, params)
                        if fetch:
                            return cursor.fetchall()
                        conn.commit()
                        return cursor.lastrowid
                finally:
                    conn.close()
                break  # Success, exit retry loop
            except Exception as e:
                last_error = e
                retries -= 1
                if retries > 0:
                    print(
                        f"Database query failed, retrying in 2s... ({retries} retries left). Error: {e}"
                    )
                    time.sleep(2)
                else:
                    print(f"Database query failed after all retries. Error: {e}")
                    raise last_error

    def fetch_one(self, query, params=()):
        results = self.execute_query(query, params, fetch=True)
        return results[0] if results else None

    def init_db(self):
        """Standardized DB Initialization."""
        if self.db_type == "mysql":
            conn = self.get_connection(connect_to_db=False)
            with conn.cursor() as cursor:
                cursor.execute(f"CREATE DATABASE IF NOT EXISTS {self.db_name}")
            conn.commit()
            conn.close()

        # Create Tables
        self.execute_query(
            """
            CREATE TABLE IF NOT EXISTS bugs (
                id INTEGER PRIMARY KEY AUTOINCREMENT if sqlite else id INT AUTO_INCREMENT PRIMARY KEY,
                title VARCHAR(255) NOT NULL,
                status VARCHAR(50) DEFAULT 'New',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """.replace(
                "INTEGER PRIMARY KEY AUTOINCREMENT if sqlite else id INT AUTO_INCREMENT PRIMARY KEY",
                "INTEGER PRIMARY KEY AUTOINCREMENT"
                if self.db_type == "sqlite"
                else "INT AUTO_INCREMENT PRIMARY KEY",
            )
        )

        self.execute_query(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT if sqlite else id INT AUTO_INCREMENT PRIMARY KEY,
                username VARCHAR(100) UNIQUE NOT NULL,
                password VARCHAR(255) NOT NULL
            )
        """.replace(
                "INTEGER PRIMARY KEY AUTOINCREMENT if sqlite else id INT AUTO_INCREMENT PRIMARY KEY",
                "INTEGER PRIMARY KEY AUTOINCREMENT"
                if self.db_type == "sqlite"
                else "INT AUTO_INCREMENT PRIMARY KEY",
            )
        )

        # Seeding
        user_count = self.fetch_one("SELECT COUNT(*) as count FROM users")
        # Handle SQLite count result which might be tuple
        count = user_count["count"] if isinstance(user_count, dict) else user_count[0]

        if count == 0:
            hashed_pw = generate_password_hash("admin123")
            self.execute_query(
                "INSERT INTO users (username, password) VALUES (?, ?)",
                ("admin", hashed_pw),
            )


db_manager = DatabaseManager()
