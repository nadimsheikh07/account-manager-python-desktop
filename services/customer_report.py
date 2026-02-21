import sqlite3
from config.db import DB_FILE
from PySide6.QtGui import QPdfWriter, QPainter, QFont, QPageSize
from PySide6.QtWidgets import QFileDialog


def get_customer_with_accounts(customer_id):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM customers WHERE id=?", (customer_id,))
    customer = cursor.fetchone()

    if not customer:
        conn.close()
        return None

    cursor.execute(
        """
        SELECT type, amount, description, date
        FROM customer_accounts
        WHERE customer_id=?
        ORDER BY date ASC
        """,
        (customer_id,),
    )

    accounts = cursor.fetchall()
    conn.close()

    total_cr = sum(a[1] for a in accounts if a[0] == "CR")
    total_dr = sum(a[1] for a in accounts if a[0] == "DR")
    balance = total_cr - total_dr

    return customer, accounts, total_cr, total_dr, balance


def export_customer_pdf(parent, customer_id):
    data = get_customer_with_accounts(customer_id)

    if not data:
        return

    customer, accounts, total_cr, total_dr, balance = data

    file_path, _ = QFileDialog.getSaveFileName(
        parent,
        "Save PDF",
        f"{customer[1]}_report.pdf",
        "PDF Files (*.pdf)",
    )

    if not file_path:
        return

    pdf = QPdfWriter(file_path)
    pdf.setPageSize(QPageSize(QPageSize.PageSizeId.A4))
    pdf.setResolution(300)

    painter = QPainter(pdf)
    painter.setFont(QFont("Arial", 10))

    y = 100

    # Title
    painter.setFont(QFont("Arial", 14))
    painter.drawText(100, y, "Customer Ledger Report")
    y += 60

    painter.setFont(QFont("Arial", 10))

    # Customer Info
    painter.drawText(100, y, f"Name: {customer[1]}")
    y += 25
    painter.drawText(100, y, f"Email: {customer[2]}")
    y += 25
    painter.drawText(100, y, f"Contact: {customer[3] or ''}")
    y += 40

    # Table Header
    painter.drawText(100, y, "Date")
    painter.drawText(250, y, "Type")
    painter.drawText(320, y, "Amount")
    painter.drawText(420, y, "Description")
    y += 20
    painter.drawLine(100, y, 800, y)
    y += 25

    # Table Rows
    for acc in accounts:
        painter.drawText(100, y, str(acc[3]))
        painter.drawText(250, y, acc[0])
        painter.drawText(320, y, f"{acc[1]:.2f}")
        painter.drawText(420, y, acc[2] or "")
        y += 20

        if y > 1100:
            pdf.newPage()
            y = 100

    y += 30
    painter.drawLine(100, y, 800, y)
    y += 30

    painter.drawText(100, y, f"Total Credit: {total_cr:.2f}")
    y += 20
    painter.drawText(100, y, f"Total Debit: {total_dr:.2f}")
    y += 20
    painter.drawText(100, y, f"Balance: {balance:.2f}")

    painter.end()
