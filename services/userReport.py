import sqlite3
from config.db import DB_FILE
from utils.pdfUtils import PDFExporter


def getUserWithAccounts(user_id):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM users WHERE id=?", (user_id,))
    user = cursor.fetchone()

    if not user:
        conn.close()
        return None

    cursor.execute(
        """
        SELECT type, amount, description, date
        FROM user_accounts
        WHERE user_id=?
        ORDER BY date ASC
        """,
        (user_id,),
    )

    accounts = cursor.fetchall()
    conn.close()

    total_cr = sum(a[1] for a in accounts if a[0] == "CR")
    total_dr = sum(a[1] for a in accounts if a[0] == "DR")
    balance = total_cr - total_dr

    return user, accounts, total_cr, total_dr, balance


def exportUserPdf(parent, user_id):
    data = getUserWithAccounts(user_id)
    if not data:
        return

    user, accounts, total_cr, total_dr, balance = data

    pdf = PDFExporter(parent, filename=f"{user[1]}_report.pdf")

    # Title
    pdf.draw_title("user Ledger Report")

    # user Info
    pdf.draw_user_info(
        {
            "Name": user[1],
            "Email": user[2],
            "Contact": user[3],
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
