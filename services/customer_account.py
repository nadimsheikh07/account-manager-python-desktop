import sqlite3
from config.db import DB_FILE


def add_transaction(customer_id, amount, type, description=None):
    """Add a credit (CR) or debit (DR) transaction for a customer"""
    if type not in ("CR", "DR"):
        raise ValueError("Type must be 'CR' or 'DR'")

    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO customer_accounts (customer_id, type, amount, description) VALUES (?, ?, ?, ?)",
        (customer_id, type, amount, description),
    )
    conn.commit()
    conn.close()


def get_customer_transactions(customer_id):
    """Fetch all transactions of a customer"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, type, amount, description, date FROM customer_accounts WHERE customer_id=? ORDER BY date ASC",
        (customer_id,),
    )
    rows = cursor.fetchall()
    conn.close()
    return rows  # list of tuples


def get_customer_balance(customer_id):
    """Calculate total balance for a customer (CR - DR)"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT SUM(CASE WHEN type='CR' THEN amount ELSE 0 END) - SUM(CASE WHEN type='DR' THEN amount ELSE 0 END) FROM customer_accounts WHERE customer_id=?",
        (customer_id,),
    )
    balance = cursor.fetchone()[0]
    conn.close()
    return balance or 0.0


def delete_transaction(trx_id):
    """Delete a transaction by its ID"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM customer_accounts WHERE id=?", (trx_id,))
    conn.commit()
    conn.close()
