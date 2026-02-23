import sqlite3
from config.db import DB_FILE
import bcrypt


def authenticateUser(username, password):
    """Authenticate user and create session if valid"""

    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    cursor.execute(
        "SELECT id, password FROM users WHERE username=?",
        (username,),
    )
    row = cursor.fetchone()
    conn.close()

    if not row:
        return False

    user_id = row[0]
    stored_hash = row[1]

    if bcrypt.checkpw(password.encode("utf-8"), stored_hash.encode("utf-8")):
        createSession(user_id)
        return True

    return False


def createUser(username, password):
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


def createSession(user_id):
    """Store current logged-in user in session table"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM session")  # remove old session
    cursor.execute("INSERT INTO session (user_id) VALUES (?)", (user_id,))
    conn.commit()
    conn.close()


def getCurrentSession():
    """Return user_id if session exists, else None"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT user_id FROM session LIMIT 1")
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


def getUserFromSession():
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
            SELECT u.id, u.name, u.email
            FROM users u
            INNER JOIN session s ON u.id = s.user_id
            LIMIT 1
        """
        )

        row = cursor.fetchone()

        if row:
            return {
                "name": row["name"],
                "email": row["email"],
            }

        return None

    except sqlite3.Error as e:
        print("Database error:", e)
        return None

    finally:
        conn.close()
