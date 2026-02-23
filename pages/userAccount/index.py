from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLineEdit,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QMessageBox,
    QHeaderView,
)
from PySide6.QtCore import Qt
from functools import partial
from config.theme import getGlobalStylesheet
from services.user import getAllUsers
from services.userAccount import (
    getUserTransactions,
    deleteTransaction,  # we’ll assume we add this to the service
    exportToExcel,
)
from pages.userAccount.form import UserAccountForm
from datetime import datetime
from components.heading import createTitle


class UserAccountList(QWidget):
    def __init__(self):
        super().__init__()
        self.setMinimumSize(700, 500)
        self.setStyleSheet(getGlobalStylesheet())

        self.init_ui()
        self.load_data()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        layout.addWidget(createTitle("user Accounts"))

        # ===== Top Bar =====
        top_layout = QHBoxLayout()
        top_layout.setSpacing(10)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText(
            "Search by user name, email, or contact..."
        )
        self.search_input.setMinimumHeight(36)
        self.search_input.textChanged.connect(self.load_data)

        self.add_btn = QPushButton("Add Transaction")
        self.add_btn.setProperty("class", "primary")
        self.add_btn.setMinimumHeight(36)
        self.add_btn.clicked.connect(self.open_add_form)

        self.export_btn = QPushButton("Export to Excel")
        self.export_btn.setProperty("class", "primary")
        self.export_btn.setMinimumHeight(36)
        self.export_btn.clicked.connect(lambda: exportToExcel(self))
        top_layout.addWidget(self.search_input)
        top_layout.addWidget(self.add_btn)
        top_layout.addWidget(self.export_btn)

        layout.addLayout(top_layout)

        # ===== Table =====
        self.table = QTableWidget()
        self.table.setColumnCount(8)
        self.table.setHorizontalHeaderLabels(
            ["ID", "user", "Email", "CR", "DR", "Balance", "Date", "Actions"]
        )

        self.table.setSortingEnabled(True)
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)

        self.table.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch
        )

        # Hide ID column
        self.table.setColumnHidden(0, True)

        layout.addWidget(self.table)
        self.setLayout(layout)

    # =========================
    # Load Data
    # =========================
    def load_data(self):
        self.table.setSortingEnabled(False)
        all_users = getAllUsers()
        query = self.search_input.text().lower()

        # Filter safely using dictionary access
        filtered = [
            user
            for user in all_users
            if query in str(user["name"] or "").lower()
            or query in str(user["email"] or "").lower()
            or query in str(user["contact"] or "").lower()
            or query in str(user["address"] or "").lower()
            or query in str(user["date"] or "").lower()
        ]

        # Gather all transactions for filtered users
        all_rows = []
        for user in filtered:
            user_id = user["id"]
            name = user["name"]
            email = user["email"]
            contact = user["contact"]
            address = user["address"]
            date = user["date"]
            type = user["type"]
            transactions = getUserTransactions(user_id)

            # Sort transactions by date (and optionally by ID)
            transactions.sort(
                key=lambda t: datetime.strptime(t[4], "%Y-%m-%d %H:%M:%S")
            )

            running_balance = 0.0
            for t in transactions:
                trx_id, trx_type, amount, description, date = t

                if trx_type == "CR":
                    running_balance += amount
                elif trx_type == "DR":
                    running_balance -= amount

                all_rows.append(
                    (
                        trx_id,
                        name,
                        email,
                        trx_type,
                        amount,
                        running_balance,  # <-- running balance
                        date,
                        description,
                        user_id,
                    )
                )

        self.table.setRowCount(len(all_rows))

        for row_idx, row in enumerate(all_rows):
            (
                trx_id,
                name,
                email,
                trx_type,
                amount,
                balance,
                date,
                description,
                user_id,
            ) = row
            row_data = [
                trx_id,
                name,
                email,
                f"{amount:.2f}" if trx_type == "CR" else "",
                f"{amount:.2f}" if trx_type == "DR" else "",
                f"{balance:.2f}",
                date,
            ]

            for col_idx, value in enumerate(row_data):
                item = QTableWidgetItem(str(value))
                item.setFlags(Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEnabled)
                self.table.setItem(row_idx, col_idx, item)

            # ===== Actions =====
            edit_btn = QPushButton("Edit")
            edit_btn.setProperty("class", "primary")
            edit_btn.clicked.connect(partial(self.edit_transaction, trx_id, user_id))

            delete_btn = QPushButton("Delete")
            delete_btn.setProperty("class", "danger")
            delete_btn.clicked.connect(partial(self.deleteTransaction, trx_id))

            action_layout = QHBoxLayout()
            action_layout.addWidget(edit_btn)
            action_layout.addWidget(delete_btn)
            action_layout.setContentsMargins(0, 0, 0, 0)

            action_widget = QWidget()
            action_widget.setLayout(action_layout)
            self.table.setCellWidget(row_idx, 7, action_widget)

        self.table.setSortingEnabled(True)

    # =========================
    # Actions
    # =========================
    def open_add_form(self, user_id=None):
        """Open form for adding CR/DR transaction"""
        self.account_form = UserAccountForm(
            refresh_callback=self.load_data,
            user_id=user_id,
        )
        self.account_form.show()

    def edit_transaction(self, trx_id, user_id):
        """Edit transaction - for now, re-use the add form"""
        self.account_form = UserAccountForm(
            refresh_callback=self.load_data,
            user_id=user_id,
        )
        self.account_form.show()

    def deleteTransaction(self, trx_id):
        confirm = QMessageBox.question(
            self,
            "Confirm Delete",
            "Are you sure you want to delete this transaction?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if confirm == QMessageBox.StandardButton.Yes:
            deleteTransaction(trx_id)
            QMessageBox.information(
                self, "Deleted", "Transaction deleted successfully."
            )
            self.load_data()
