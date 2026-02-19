import sqlite3
from config.db import DB_FILE


def init_customer_table():
    """Initialize the customer table if it doesn't exist"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
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
    conn.commit()
    conn.close()


def add_customer(name, email, contact=None, address=None):
    """Add a new customer"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO customers (name, email, contact, address) VALUES (?, ?, ?, ?)",
            (name, email, contact, address),
        )
        conn.commit()
        return cursor.lastrowid
    except sqlite3.IntegrityError:
        raise ValueError("Email already exists")
    finally:
        conn.close()


def get_customer(customer_id):
    """Fetch customer by ID"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM customers WHERE id=?", (customer_id,))
    row = cursor.fetchone()
    conn.close()
    return row  # (id, name, email, contact, address, date) or None


def get_all_customers():
    """Fetch all customers ordered by newest first"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM customers ORDER BY date DESC")
    rows = cursor.fetchall()
    conn.close()
    return rows


def update_customer(customer_id, name=None, email=None, contact=None, address=None):
    """Update customer details. Only provided fields are updated"""
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

    if not fields:
        conn.close()
        return False  # nothing to update

    values.append(customer_id)
    query = f"UPDATE customers SET {', '.join(fields)} WHERE id=?"

    try:
        cursor.execute(query, tuple(values))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        raise ValueError("Email already exists")
    finally:
        conn.close()


def delete_customer(customer_id):
    """Delete a customer by ID"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM customers WHERE id=?", (customer_id,))
    conn.commit()
    conn.close()


def get_monthly_customer_entries():
    """Return list of (YYYY-MM, count)"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT strftime('%Y-%m', date) as month,
               COUNT(*) as total
        FROM customers
        WHERE date IS NOT NULL
        GROUP BY month
        ORDER BY month
        """
    )

    rows = cursor.fetchall()
    conn.close()
    return rows
