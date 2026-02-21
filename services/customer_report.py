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

    # ---- Page Setup ----
    margin = 80
    page_width = pdf.width()
    page_height = pdf.height()
    usable_width = page_width - (margin * 2)

    y = margin

    # ---- Title ----
    painter.setFont(QFont("Arial", 16, QFont.Weight.Bold))
    painter.drawText(margin, y, "Customer Ledger Report")
    y += 50

    painter.setFont(QFont("Arial", 10))

    # ---- Customer Info ----
    painter.drawText(margin, y, f"Name: {customer[1]}")
    y += 20
    painter.drawText(margin, y, f"Email: {customer[2]}")
    y += 20
    painter.drawText(margin, y, f"Contact: {customer[3] or ''}")
    y += 30

    painter.drawLine(margin, y, page_width - margin, y)
    y += 30

    # ---- Table Column Setup ----
    col_date = margin
    col_type = margin + 120
    col_desc = margin + 190
    col_amount = margin + usable_width - 150
    col_balance = margin + usable_width - 70

    row_height = 25

    # ---- Table Header ----
    painter.setFont(QFont("Arial", 10, QFont.Weight.Bold))

    painter.drawRect(margin, y, usable_width, row_height)
    painter.drawText(col_date, y + 17, "Date")
    painter.drawText(col_type, y + 17, "Type")
    painter.drawText(col_desc, y + 17, "Description")
    painter.drawText(col_amount, y + 17, "Amount")
    painter.drawText(col_balance, y + 17, "Balance")

    y += row_height

    painter.setFont(QFont("Arial", 9))

    running_balance = 0

    # ---- Table Rows ----
    for acc in accounts:

        if y > page_height - margin - 100:
            pdf.newPage()
            y = margin

        acc_type, amount, description, date = acc

        if acc_type == "CR":
            running_balance += amount
        else:
            running_balance -= amount

        # Draw row border
        painter.drawRect(margin, y, usable_width, row_height)

        painter.drawText(col_date, y + 17, str(date))
        painter.drawText(col_type, y + 17, acc_type)
        painter.drawText(col_desc, y + 17, description or "")

        # Right aligned amounts
        painter.drawText(col_amount, y + 17, f"{amount:,.2f}")
        painter.drawText(col_balance, y + 17, f"{running_balance:,.2f}")

        y += row_height

    y += 20
    painter.drawLine(margin, y, page_width - margin, y)
    y += 30

    # ---- Summary ----
    painter.setFont(QFont("Arial", 10, QFont.Weight.Bold))
    painter.drawText(margin, y, f"Total Credit: {total_cr:,.2f}")
    y += 20
    painter.drawText(margin, y, f"Total Debit: {total_dr:,.2f}")
    y += 20
    painter.drawText(margin, y, f"Final Balance: {balance:,.2f}")

    painter.end()
