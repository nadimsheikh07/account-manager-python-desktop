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
            date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        )
    """
    )
    conn.commit()
    conn.close()


def add_customer(name, email, contact, address):
    """Add a new customer"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO customers (name, email, contact, address) VALUES (?, ?, ?, ?)",
            (name, email, contact, address),
        )
        conn.commit()
        return cursor.lastrowid  # return the new customer id
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
    return row  # returns tuple (id, name, email, contact, address) or None


def get_all_customers():
    """Fetch all customers"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM customers")
    rows = cursor.fetchall()
    conn.close()
    return rows  # list of tuples


def update_customer(customer_id, name=None, email=None, contact=None, address=None):
    """Update customer details. Only provided fields are updated"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    # Build dynamic query
    fields = []
    values = []
    if name:
        fields.append("name=?")
        values.append(name)
    if email:
        fields.append("email=?")
        values.append(email)
    if contact:
        fields.append("contact=?")
        values.append(contact)
    if address:
        fields.append("address=?")
        values.append(address)
    values.append(customer_id)

    if fields:
        query = f"UPDATE customers SET {', '.join(fields)} WHERE id=?"
        cursor.execute(query, tuple(values))
        conn.commit()
    conn.close()


def delete_customer(customer_id):
    """Delete a customer by ID"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM customers WHERE id=?", (customer_id,))
    conn.commit()
    conn.close()
