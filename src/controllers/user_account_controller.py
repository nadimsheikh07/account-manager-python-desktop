from src.services.user import getAllUsers
from src.services.userAccount import (
    getUserTransactions,
    deleteTransaction,
    addTransaction,
    getUserBalance,
)


class UserAccountController:
    def get_account_data(self, query=""):
        """
        Fetches and filters user account data, calculates running balances,
        and returns formatted rows for the view.
        """
        all_users = getAllUsers()
        normalized_query = (query or "").strip().lower()

        # Filter users
        filtered_users = [
            u
            for u in all_users
            if normalized_query in str(u.name).lower()
            or normalized_query in str(u.email).lower()
            or normalized_query in str(u.contact).lower()
            or normalized_query in str(u.address).lower()
        ]

        all_rows = []
        for user in filtered_users:
            user_id = user.id
            transactions = getUserTransactions(user_id)
            # Sort by date
            transactions.sort(key=lambda t: t.date)

            running_balance = 0.0
            for trx in transactions:
                trx_id = trx.id
                trx_type = trx.type
                amount = trx.amount
                description = trx.description
                date = trx.date.strftime("%Y-%m-%d %H:%M:%S") if trx.date else ""

                running_balance += amount if trx_type == "CR" else -amount

                all_rows.append(
                    {
                        "trx_id": trx_id,
                        "user_name": user.name,
                        "user_email": user.email,
                        "cr": amount if trx_type == "CR" else 0.0,
                        "dr": amount if trx_type == "DR" else 0.0,
                        "balance": running_balance,
                        "date": date,
                        "description": description,
                        "user_id": user_id,
                    }
                )

        return all_rows

    def delete_transaction(self, trx_id):
        """Deletes a transaction and returns status/message."""
        try:
            deleteTransaction(trx_id)
            return True, "Transaction deleted successfully."
        except Exception as e:
            return False, f"Failed to delete transaction: {str(e)}"

    def save_transaction(self, user_id, amount, trx_type, description=None):
        """Adds a new transaction."""
        try:
            addTransaction(user_id, amount, trx_type, description)
            return True, "Transaction added successfully."
        except Exception as e:
            return False, f"Failed to add transaction: {str(e)}"

    def get_user_balance(self, user_id):
        """Fetches the current balance for a user."""
        try:
            return getUserBalance(user_id)
        except Exception:
            return 0.0
