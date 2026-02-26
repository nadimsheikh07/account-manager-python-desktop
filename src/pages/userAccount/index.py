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
from datetime import datetime
from config.theme import getGlobalStylesheet
from src.services.user import getAllUsers
from src.services.userAccount import (
    getUserTransactions,
    deleteTransaction,
    exportToExcel,
)
from src.pages.userAccount.form import UserAccountForm
from src.components.heading import createTitle


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
        layout.addWidget(createTitle("User Accounts"))

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
            ["ID", "User", "Email", "CR", "DR", "Balance", "Date", "Actions"]
        )
        self.table.setSortingEnabled(True)
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch
        )
        self.table.setColumnHidden(0, True)  # Hide ID column

        layout.addWidget(self.table)
        self.setLayout(layout)

    # =========================
    # Load Data
    # =========================
    def load_data(self):
        self.table.setSortingEnabled(False)

        # Fetch all users (ORM objects) and convert to dict for filtering
        all_users = [self._orm_to_dict(u) for u in getAllUsers()]
        query = self.search_input.text().lower()

        # Filter users
        filtered = [
            u
            for u in all_users
            if query in str(u.get("name", "")).lower()
            or query in str(u.get("email", "")).lower()
            or query in str(u.get("contact", "")).lower()
            or query in str(u.get("address", "")).lower()
            or query in str(u.get("date", "")).lower()
        ]

        # Gather transactions for filtered users
        all_rows = []
        for user in filtered:
            user_id = user["id"]
            transactions = getUserTransactions(user_id)  # ORM tuples/list
            # Sort by date
            transactions.sort(key=lambda t: t.date)  # t.date is datetime

            running_balance = 0.0
            for trx in transactions:
                trx_id = trx.id
                trx_type = trx.type
                amount = trx.amount
                description = trx.description
                date = trx.date.strftime("%Y-%m-%d %H:%M:%S") if trx.date else ""

                running_balance += amount if trx_type == "CR" else -amount

                all_rows.append(
                    (
                        trx_id,
                        user["name"],
                        user["email"],
                        amount if trx_type == "CR" else 0.0,
                        amount if trx_type == "DR" else 0.0,
                        running_balance,
                        date,
                        description,
                        user_id,
                    )
                )

        self.table.setRowCount(len(all_rows))

        for row_idx, row in enumerate(all_rows):
            trx_id, name, email, cr, dr, balance, date, description, user_id = row

            row_data = [
                trx_id,
                name,
                email,
                f"{cr:.2f}" if cr else "",
                f"{dr:.2f}" if dr else "",
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
            delete_btn.clicked.connect(partial(self.delete_transaction, trx_id))

            action_layout = QHBoxLayout()
            action_layout.setContentsMargins(0, 0, 0, 0)
            action_layout.addWidget(edit_btn)
            action_layout.addWidget(delete_btn)

            action_widget = QWidget()
            action_widget.setLayout(action_layout)
            self.table.setCellWidget(row_idx, 7, action_widget)

        self.table.setSortingEnabled(True)

    # =========================
    # Helper
    # =========================
    def _orm_to_dict(self, user):
        """Convert ORM User to dict for table filtering"""
        return {
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "contact": user.contact,
            "address": user.address,
            "date": user.date.strftime("%Y-%m-%d %H:%M:%S") if user.date else "",
            "type": user.type,
        }

    # =========================
    # Actions
    # =========================
    def open_add_form(self, user_id=None):
        self.account_form = UserAccountForm(
            refresh_callback=self.load_data,
            user_id=user_id,
        )
        self.account_form.show()

    def edit_transaction(self, trx_id, user_id):
        self.account_form = UserAccountForm(
            refresh_callback=self.load_data,
            user_id=user_id,
            trx_id=trx_id,
        )
        self.account_form.show()

    def delete_transaction(self, trx_id):
        confirm = QMessageBox.question(
            self,
            "Confirm Delete",
            "Are you sure you want to delete this transaction?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if confirm == QMessageBox.StandardButton.Yes:
            deleteTransaction(trx_id)  # ORM-based
            QMessageBox.information(
                self, "Deleted", "Transaction deleted successfully."
            )
            self.load_data()
