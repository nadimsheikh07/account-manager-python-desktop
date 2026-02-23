import sqlite3
from config.db import DB_FILE
import pandas as pd
from PySide6.QtWidgets import (
    QMessageBox,
    QFileDialog,
)
from datetime import datetime


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


def getAllCustomers():
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
        SELECT strftime('%Y-%m', date) as year_month,
               COUNT(*) as total
        FROM customers
        WHERE date IS NOT NULL
        GROUP BY year_month
        ORDER BY year_month
        """
    )

    rows = cursor.fetchall()
    conn.close()
    return rows  # [('2026-01', 12), ('2026-02', 7)]


def exportToExcel(self):
    from .customerAccount import getCustomerBalance  # import balance function

    all_customers = getAllCustomers()
    if not all_customers:
        QMessageBox.warning(self, "No Data", "There are no customers to export.")
        return

    # Add balance for each customer
    export_rows = []
    for c in all_customers:
        customer_id, name, email, contact, address, date = c
        balance = getCustomerBalance(customer_id)
        export_rows.append(
            {
                "ID": customer_id,
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
        f"customers_{now}.xlsx",
        "Excel Files (*.xlsx)",
    )
    if file_path:
        df.to_excel(file_path, index=False)
        QMessageBox.information(
            self, "Exported", f"Customers exported successfully to:\n{file_path}"
        )
