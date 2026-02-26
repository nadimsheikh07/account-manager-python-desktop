from sqlalchemy import func, case
from config.db import SessionLocal
from src.models.user import User
from src.models.user import UserAccount
from utils.pdfUtils import PDFExporter


def getUserWithAccounts(user_id):
    """Fetch a user and all their transactions, compute totals and balance"""
    with SessionLocal() as db:
        user = db.get(User, user_id)
        if not user:
            return None

        accounts = (
            db.query(UserAccount)
            .filter(UserAccount.user_id == user_id)
            .order_by(UserAccount.date.asc())
            .all()
        )

        total_cr = sum(acc.amount for acc in accounts if acc.type == "CR")
        total_dr = sum(acc.amount for acc in accounts if acc.type == "DR")
        balance = total_cr - total_dr

        return user, accounts, total_cr, total_dr, balance


def exportUserPdf(parent, user_id):
    """Export a single user's ledger report to PDF"""
    data = getUserWithAccounts(user_id)
    if not data:
        return

    user, accounts, total_cr, total_dr, balance = data

    pdf = PDFExporter(parent, filename=f"{user.name}_report.pdf")

    # Title
    pdf.draw_title("User Ledger Report")

    # User info
    pdf.draw_user_info(
        {
            "Name": user.name,
            "Email": user.email,
            "Contact": user.contact,
        }
    )

    # Transaction Table
    running_balance = 0
    table_rows = []
    for acc in accounts:
        running_balance += acc.amount if acc.type == "CR" else -acc.amount
        table_rows.append(
            [
                acc.date.strftime("%Y-%m-%d %H:%M:%S"),
                acc.type,
                acc.description or "",
                f"{acc.amount:,.2f}",
                f"{running_balance:,.2f}",
            ]
        )

    columns = ["Date", "Type", "Description", "Amount", "Balance"]
    pdf.draw_table(columns, table_rows)

    # Summary
    pdf.draw_summary(
        {
            "Total Credit": f"{total_cr:,.2f}",
            "Total Debit": f"{total_dr:,.2f}",
            "Final Balance": f"{balance:,.2f}",
        }
    )

    pdf.finish()
