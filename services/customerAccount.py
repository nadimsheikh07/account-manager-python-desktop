import sqlite3
from config.db import DB_FILE
from PySide6.QtWidgets import (
    QMessageBox,
    QFileDialog,
)
import pandas as pd
from datetime import datetime


def addTransaction(customer_id, amount, type, description=None):
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


def getCustomerTransactions(customer_id):
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


def getCustomerBalance(customer_id):
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


def deleteTransaction(trx_id):
    """Delete a transaction by its ID"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM customer_accounts WHERE id=?", (trx_id,))
    conn.commit()
    conn.close()


def getMonthlyAccountSummary():
    """
    Returns list of (YYYY-MM, total_cr, total_dr)
    """
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    query = """
        SELECT
            strftime('%Y-%m', date) AS month,
            SUM(CASE WHEN type='CR' THEN amount ELSE 0 END) AS total_cr,
            SUM(CASE WHEN type='DR' THEN amount ELSE 0 END) AS total_dr
        FROM customer_accounts
        GROUP BY month
        ORDER BY month ASC
    """
    cursor.execute(query)
    result = cursor.fetchall()
    conn.close()
    return result


def exportToExcel(self):
    from .customer import getAllCustomers

    all_customers = getAllCustomers()
    query = self.search_input.text().lower()

    # Filter customers
    filtered_customers = [
        c
        for c in all_customers
        if query in str(c[1]).lower()
        or query in str(c[2]).lower()
        or query in str(c[3]).lower()
    ]

    # Gather all transactions
    all_rows = []
    for c in filtered_customers:
        customer_id, name, email, _, _, _ = c
        transactions = getCustomerTransactions(customer_id)
        running_balance = 0.0
        for t in transactions:
            trx_id, trx_type, amount, description, date = t
            if trx_type == "CR":
                running_balance += amount
            elif trx_type == "DR":
                running_balance -= amount

            all_rows.append(
                {
                    "Transaction ID": trx_id,
                    "Customer": name,
                    "Email": email,
                    "CR": amount if trx_type == "CR" else "",
                    "DR": amount if trx_type == "DR" else "",
                    "Balance": running_balance,
                    "Date": date,
                    "Description": description,
                }
            )

    if not all_rows:
        QMessageBox.warning(self, "No Data", "There are no transactions to export.")
        return

    df = pd.DataFrame(all_rows)

    # Open save dialog
    now = datetime.now().strftime("%Y%m%d_%H%M%S")
    file_path, _ = QFileDialog.getSaveFileName(
        self,
        "Save Excel File",
        f"customer_accounts_{now}.xlsx",
        "Excel Files (*.xlsx)",
    )
    if file_path:
        df.to_excel(file_path, index=False)
        QMessageBox.information(
            self,
            "Exported",
            f"Customer accounts exported successfully to:\n{file_path}",
        )
