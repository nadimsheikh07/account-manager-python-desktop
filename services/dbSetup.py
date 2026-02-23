import sqlite3
from config.db import DB_FILE
import bcrypt
import os


def init_db():
    """Initialize database from SQL file and create default admin user"""

    default_name = "Nadim Sheikh"
    default_username = "admin"
    default_email = "nadim.sheikh.07@gmail.com"
    default_password = "admin"

    with sqlite3.connect(DB_FILE) as conn:
        conn.execute("PRAGMA foreign_keys = ON")
        cursor = conn.cursor()

        # Load and execute SQL file
        sql_path = os.path.join("services", "database.sql")

        with open(sql_path, "r", encoding="utf-8") as f:
            conn.executescript(f.read())

        # Create default admin only if not exists
        cursor.execute("SELECT 1 FROM users WHERE username = ?", (default_username,))
        if cursor.fetchone() is None:
            hashed = bcrypt.hashpw(default_password.encode(), bcrypt.gensalt()).decode()

            cursor.execute(
                "INSERT INTO users (name, username, email, password) VALUES (?, ?, ?, ?)",
                (default_name, default_username, default_email, hashed),
            )

        conn.commit()
