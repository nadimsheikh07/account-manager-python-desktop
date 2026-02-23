import sqlite3
from config.db import DB_FILE
from utils.pdfUtils import PDFExporter


def getCustomerWithAccounts(customer_id):
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


def exportCustomerPdf(parent, customer_id):
    data = getCustomerWithAccounts(customer_id)
    if not data:
        return

    customer, accounts, total_cr, total_dr, balance = data

    pdf = PDFExporter(parent, filename=f"{customer[1]}_report.pdf")

    # Title
    pdf.draw_title("Customer Ledger Report")

    # Customer Info
    pdf.draw_customer_info(
        {
            "Name": customer[1],
            "Email": customer[2],
            "Contact": customer[3],
        }
    )

    # Table
    running_balance = 0
    table_rows = []
    for acc in accounts:
        acc_type, amount, description, date = acc
        running_balance = (
            running_balance + amount if acc_type == "CR" else running_balance - amount
        )
        table_rows.append(
            [
                date,
                acc_type,
                description or "",
                f"{amount:,.2f}",
                f"{running_balance:,.2f}",
            ]
        )

    columns = ["Date", "Type", "Description", "Amount", "Balance"]
    pdf.draw_table(columns, table_rows)

    # Summary
    pdf.draw_summary(
        {
            "Total Credit": total_cr,
            "Total Debit": total_dr,
            "Final Balance": balance,
        }
    )

    pdf.finish()
