import sqlite3
from config.db import DB_FILE


def authenticate_user(username, password):
    """Check SQLite for user"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute(
        "CREATE TABLE IF NOT EXISTS users (username TEXT UNIQUE, password TEXT)"
    )
    cursor.execute(
        "SELECT * FROM users WHERE username=? AND password=?", (username, password)
    )
    user = cursor.fetchone()
    conn.close()
    return bool(user)


def create_session(username):
    """Store current logged-in user in session table"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS session (username TEXT UNIQUE)")
    cursor.execute("DELETE FROM session")  # remove old session
    cursor.execute("INSERT INTO session (username) VALUES (?)", (username,))
    conn.commit()
    conn.close()


def get_current_session():
    """Return username if session exists, else None"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS session (username TEXT UNIQUE)")
    cursor.execute("SELECT username FROM session LIMIT 1")
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else None
