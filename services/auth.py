import sqlite3
from config.db import DB_FILE
import bcrypt
from services.customer import init_customer_table


def init_db():
    """Initialize tables if not exist and create default admin user"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    # Create tables
    cursor.execute(
        "CREATE TABLE IF NOT EXISTS users (username TEXT UNIQUE, email TEXT, password TEXT)"
    )
    cursor.execute("CREATE TABLE IF NOT EXISTS session (username TEXT UNIQUE)")

    init_customer_table()

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


def authenticate_user(username, password):
    """Check SQLite for user"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT password FROM users WHERE username=?", (username,))
    row = cursor.fetchone()
    conn.close()

    if not row:
        return False

    stored_hash = row[0]
    return bcrypt.checkpw(password.encode("utf-8"), stored_hash.encode("utf-8"))


def create_user(username, password):
    """Create a new user with hashed password"""
    hashed = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO users (username, password) VALUES (?, ?)",
            (username, hashed.decode("utf-8")),
        )
        conn.commit()
    except sqlite3.IntegrityError:
        raise ValueError("Username already exists")
    finally:
        conn.close()


def create_session(username):
    """Store current logged-in user in session table"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM session")  # remove old session
    cursor.execute("INSERT INTO session (username) VALUES (?)", (username,))
    conn.commit()
    conn.close()


def get_current_session():
    """Return username if session exists, else None"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT username FROM session LIMIT 1")
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else None


def logout():
    """Clear session and close main window"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM session")
    conn.commit()
    conn.close()


def get_user_from_session():
    """
    Return full user data from active session.
    Returns dictionary or None.
    """
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row  # allows dict-like access
    cursor = conn.cursor()

    try:
        cursor.execute(
            """
            SELECT u.username, u.email
            FROM users u
            INNER JOIN session s ON u.username = s.username
            LIMIT 1
        """
        )

        row = cursor.fetchone()

        if row:
            return {
                "username": row["username"],
                "email": row["email"],
            }

        return None

    except sqlite3.Error as e:
        print("Database error:", e)
        return None

    finally:
        conn.close()
