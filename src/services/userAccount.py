from sqlalchemy import func, case
from config.db import SessionLocal
from src.models.user import UserAccount
from PySide6.QtWidgets import QMessageBox, QFileDialog
import pandas as pd
from datetime import datetime


def addTransaction(user_id, amount, trx_type, description=None):
    """Add a credit (CR) or debit (DR) transaction for a user"""
    if trx_type not in ("CR", "DR"):
        raise ValueError("Type must be 'CR' or 'DR'")

    with SessionLocal() as db:
        transaction = UserAccount(
            user_id=user_id,
            type=trx_type,
            amount=amount,
            description=description,
        )
        db.add(transaction)
        db.commit()


def getUserTransactions(user_id):
    """Fetch all transactions of a user"""
    with SessionLocal() as db:
        transactions = (
            db.query(UserAccount)
            .filter(UserAccount.user_id == user_id)
            .order_by(UserAccount.date.asc())
            .all()
        )

        return transactions  # list of ORM objects


def getUserBalance(user_id):
    """Calculate total balance for a user (CR - DR)"""
    with SessionLocal() as db:
        result = (
            db.query(
                func.coalesce(
                    func.sum(
                        case(
                            (UserAccount.type == "CR", UserAccount.amount),
                            else_=0,
                        )
                    ),
                    0,
                )
                - func.coalesce(
                    func.sum(
                        case(
                            (UserAccount.type == "DR", UserAccount.amount),
                            else_=0,
                        )
                    ),
                    0,
                )
            )
            .filter(UserAccount.user_id == user_id)
            .scalar()
        )

        return result or 0.0


def deleteTransaction(trx_id):
    """Delete a transaction by its ID"""
    with SessionLocal() as db:
        transaction = db.get(UserAccount, trx_id)
        if transaction:
            db.delete(transaction)
            db.commit()


def getTransaction(trx_id):
    """Fetch a single transaction by its ID"""
    with SessionLocal() as db:
        return db.get(UserAccount, trx_id)


def updateTransaction(trx_id, user_id, amount, trx_type, description=None):
    """Update an existing transaction"""
    if trx_type not in ("CR", "DR"):
        raise ValueError("Type must be 'CR' or 'DR'")

    with SessionLocal() as db:
        transaction = db.get(UserAccount, trx_id)
        if transaction:
            transaction.user_id = user_id
            transaction.amount = amount
            transaction.type = trx_type
            transaction.description = description
            db.commit()
            return True
        return False


def getMonthlyAccountSummary():
    """
    Returns list of (YYYY-MM, total_cr, total_dr)
    """
    with SessionLocal() as db:
        results = (
            db.query(
                func.strftime("%Y-%m", UserAccount.date).label("month"),
                func.sum(
                    case((UserAccount.type == "CR", UserAccount.amount), else_=0)
                ).label("total_cr"),
                func.sum(
                    case((UserAccount.type == "DR", UserAccount.amount), else_=0)
                ).label("total_dr"),
            )
            .group_by("month")
            .order_by("month")
            .all()
        )

        return results


def exportToExcel(self):
    from .user import getAllUsers

    all_users = getAllUsers()
    query = self.search_input.text().lower()

    # Filter users
    filtered_users = [
        u
        for u in all_users
        if query in str(u.name).lower()
        or query in str(u.email).lower()
        or query in str(u.contact).lower()
    ]

    all_rows = []

    for user in filtered_users:
        user_id = user.id
        name = user.name
        email = user.email

        transactions = getUserTransactions(user_id)

        running_balance = 0.0

        for trx in transactions:
            if trx.type == "CR":
                running_balance += trx.amount
            elif trx.type == "DR":
                running_balance -= trx.amount

            all_rows.append(
                {
                    "Transaction ID": trx.id,
                    "User": name,
                    "Email": email,
                    "CR": trx.amount if trx.type == "CR" else "",
                    "DR": trx.amount if trx.type == "DR" else "",
                    "Balance": running_balance,
                    "Date": trx.date,
                    "Description": trx.description,
                }
            )

    if not all_rows:
        QMessageBox.warning(self, "No Data", "There are no transactions to export.")
        return

    df = pd.DataFrame(all_rows)

    now = datetime.now().strftime("%Y%m%d_%H%M%S")
    file_path, _ = QFileDialog.getSaveFileName(
        self,
        "Save Excel File",
        f"user_accounts_{now}.xlsx",
        "Excel Files (*.xlsx)",
    )

    if file_path:
        df.to_excel(file_path, index=False)
        QMessageBox.information(
            self,
            "Exported",
            f"User accounts exported successfully to:\n{file_path}",
        )
