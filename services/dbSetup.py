import sqlite3
from config.db import DB_FILE
import bcrypt


def init_db():
    """Initialize tables if not exist and create default admin user"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    # Create tables
    cursor.execute(
        "CREATE TABLE IF NOT EXISTS users (username TEXT UNIQUE, email TEXT, password TEXT)"
    )
    cursor.execute("CREATE TABLE IF NOT EXISTS session (username TEXT UNIQUE)")

    cursor.execute(
        """
            CREATE TABLE IF NOT EXISTS customers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                contact TEXT,
                address TEXT,
                date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """
    )

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS customer_accounts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_id INTEGER NOT NULL,
            type TEXT CHECK(type IN ('CR', 'DR')) NOT NULL,
            amount REAL NOT NULL,
            description TEXT,
            date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (customer_id) REFERENCES customers(id) ON DELETE CASCADE
        )
        """
    )

    # Hash default password
    default_username = "admin"
    default_email = "nadim.sheikh.07@gmail.com"
    default_password = "1234"
    hashed = bcrypt.hashpw(default_password.encode("utf-8"), bcrypt.gensalt())

    # Insert default admin user if not exists
    cursor.execute(
        "INSERT OR IGNORE INTO users (username, email, password) VALUES (?, ?, ?)",
        (default_username, default_email, hashed.decode("utf-8")),
    )

    conn.commit()
    conn.close()
