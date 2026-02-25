import sqlite3
from config.db import DB_FILE
import pandas as pd
from PySide6.QtWidgets import (
    QMessageBox,
    QFileDialog,
)
from datetime import datetime


import sqlite3


def addUser(name, email, contact=None, address=None, user_type="user"):
    """Add a new user"""

    # ===== Basic Validation =====
    if not name or not name.strip():
        raise ValueError("Name is required")

    if not email or not email.strip():
        raise ValueError("Email is required")

    valid_types = {"user", "employee", "customer", "supplier"}
    if user_type not in valid_types:
        raise ValueError("Invalid user type")

    try:
        with sqlite3.connect(DB_FILE) as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO users (name, username, email, contact, address, type)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    name.strip(),
                    name.strip(),
                    email.strip().lower(),
                    contact.strip() if contact else None,
                    address.strip() if address else None,
                    user_type,
                ),
            )
            conn.commit()
            return cursor.lastrowid

    except sqlite3.IntegrityError:
        raise ValueError("Email already exists")


def getUser(user_id):
    """Fetch user by ID"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE id=?", (user_id,))
    row = cursor.fetchone()
    conn.close()
    return row  # (id, name, email, contact, address, date) or None


def getAllUsers(type="user"):
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT id, name, email, contact, address, date, type
        FROM users WHERE type=?
    """,
        (type,),
    )

    rows = cursor.fetchall()
    conn.close()
    return rows


def updateUser(
    user_id, name=None, email=None, contact=None, address=None, user_type="user"
):
    """Update user details. Only provided fields are updated"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    fields = []
    values = []

    if name is not None:
        fields.append("name=?")
        values.append(name)

    if email is not None:
        fields.append("email=?")
        values.append(email)

    if contact is not None:
        fields.append("contact=?")
        values.append(contact)

    if address is not None:
        fields.append("address=?")
        values.append(address)

    if type is not None:
        fields.append("type=?")
        values.append(user_type)

    if not fields:
        conn.close()
        return False  # nothing to update

    values.append(user_id)
    query = f"UPDATE users SET {', '.join(fields)} WHERE id=?"

    try:
        cursor.execute(query, tuple(values))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        raise ValueError("Email already exists")
    finally:
        conn.close()


def delete_user(user_id):
    """Delete a user by ID"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM users WHERE id=?", (user_id,))
    conn.commit()
    conn.close()


def getMonthlyUserEntries():
    """Return list of (YYYY-MM, count)"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT strftime('%Y-%m', date) as year_month,
               COUNT(*) as total
        FROM users
        WHERE date IS NOT NULL
        GROUP BY year_month
        ORDER BY year_month
        """
    )

    rows = cursor.fetchall()
    conn.close()
    return rows  # [('2026-01', 12), ('2026-02', 7)]


def exportToExcel(self):
    from .userAccount import getUserBalance  # import balance function

    all_users = getAllUsers()
    if not all_users:
        QMessageBox.warning(self, "No Data", "There are no users to export.")
        return

    # Add balance for each user
    export_rows = []
    for user in all_users:
        user_id = user["id"]
        name = user["name"]
        email = user["email"]
        contact = user["contact"]
        address = user["address"]
        date = user["date"]
        type = user["type"]
        balance = getUserBalance(user_id)
        export_rows.append(
            {
                "ID": user_id,
                "Name": name,
                "Email": email,
                "Contact": contact,
                "Address": address,
                "Date": date,
                "Balance": balance,
            }
        )

    df = pd.DataFrame(export_rows)

    now = datetime.now().strftime("%Y%m%d_%H%M%S")
    file_path, _ = QFileDialog.getSaveFileName(
        self,
        "Save Excel File",
        f"users_{now}.xlsx",
        "Excel Files (*.xlsx)",
    )
    if file_path:
        df.to_excel(file_path, index=False)
        QMessageBox.information(
            self, "Exported", f"users exported successfully to:\n{file_path}"
        )
