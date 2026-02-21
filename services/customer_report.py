import sqlite3
from config.db import DB_FILE
from PySide6.QtGui import QPdfWriter, QPainter, QFont, QColor, QPageSize
from PySide6.QtCore import QRect, Qt
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

    # ---------------- Page Setup ----------------
    margin = 80
    page_width = pdf.width()
    page_height = pdf.height()
    usable_width = page_width - (margin * 2)

    y = margin

    # ---------------- Title ----------------
    painter.setFont(QFont("Arial", 16, QFont.Weight.Bold))
    painter.drawText(margin, y, "Customer Ledger Report")
    y += 80

    painter.setFont(QFont("Arial", 10))

    # ---------------- Customer Info ----------------
    painter.drawText(margin, y, f"Name: {customer[1]}")
    y += 50
    painter.drawText(margin, y, f"Email: {customer[2]}")
    y += 50
    painter.drawText(margin, y, f"Contact: {customer[3] or ''}")
    y += 60

    painter.drawLine(margin, y, page_width - margin, y)
    y += 60

    # ---------------- Table Setup ----------------
    row_height = 70
    running_balance = 0

    # Column widths must fit usable_width
    col_widths = [
        140,  # Date
        90,  # Type
        330,  # Description
        140,  # Amount
        140,  # Balance
    ]

    columns = ["Date", "Type", "Description", "Amount", "Balance"]

    def draw_table_header():
        nonlocal y
        painter.setFont(QFont("Arial", 10, QFont.Weight.Bold))

        x = margin
        for i, col in enumerate(columns):
            painter.drawRect(x, y, col_widths[i], row_height)
            painter.drawText(
                QRect(x + 5, y, col_widths[i] - 10, row_height),
                Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft,
                col,
            )
            x += col_widths[i]

        y += row_height
        painter.setFont(QFont("Arial", 9))

    draw_table_header()

    # ---------------- Table Rows ----------------
    for index, acc in enumerate(accounts):

        # New page check
        if y > page_height - margin - row_height:
            pdf.newPage()
            y = margin
            draw_table_header()

        acc_type, amount, description, date = acc

        if acc_type == "CR":
            running_balance += amount
        else:
            running_balance -= amount

        row_data = [
            str(date),
            acc_type,
            description or "",
            f"{amount:,.2f}",
            f"{running_balance:,.2f}",
        ]

        x = margin

        # Alternate row background
        if index % 2 == 0:
            painter.fillRect(
                margin,
                y,
                sum(col_widths),
                row_height,
                QColor(245, 245, 245),
            )

        for i, cell in enumerate(row_data):

            painter.drawRect(x, y, col_widths[i], row_height)

            # Alignment rules
            if i == 1:
                alignment = Qt.AlignmentFlag.AlignCenter
            elif i >= 3:
                alignment = Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignRight
            else:
                alignment = Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft

            painter.drawText(
                QRect(x + 5, y, col_widths[i] - 10, row_height),
                alignment,
                cell,
            )

            x += col_widths[i]

        y += row_height

    # ---------------- Summary Section ----------------
    y += 40
    painter.drawLine(margin, y, page_width - margin, y)
    y += 60

    painter.setFont(QFont("Arial", 10, QFont.Weight.Bold))

    painter.drawText(margin, y, f"Total Credit: {total_cr:,.2f}")
    y += 50
    painter.drawText(margin, y, f"Total Debit: {total_dr:,.2f}")
    y += 50
    painter.drawText(margin, y, f"Final Balance: {balance:,.2f}")

    painter.end()
