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
from services.customer import getAllCustomers
from services.customerAccount import (
    getCustomerTransactions,
    deleteTransaction,  # we’ll assume we add this to the service
    exportToExcel,
)
from pages.customer_account.form import CustomerAccountForm
from datetime import datetime
from components.heading import createTitle


class CustomerAccountList(QWidget):
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
        layout.addWidget(createTitle("Customer Accounts"))

        # ===== Top Bar =====
        top_layout = QHBoxLayout()
        top_layout.setSpacing(10)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText(
            "Search by customer name, email, or contact..."
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
            ["ID", "Customer", "Email", "CR", "DR", "Balance", "Date", "Actions"]
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
        all_customers = getAllCustomers()
        query = self.search_input.text().lower()

        # Filter customers
        filtered_customers = [
            c
            for c in all_customers
            if query in str(c[1]).lower()
            or query in str(c[2]).lower()
            or query in str(c[3]).lower()
        ]

        # Gather all transactions for filtered customers
        all_rows = []
        for c in filtered_customers:
            customer_id, name, email, _, _, _ = c
            transactions = getCustomerTransactions(customer_id)

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
                        customer_id,
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
                customer_id,
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
            edit_btn.clicked.connect(
                partial(self.edit_transaction, trx_id, customer_id)
            )

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
    def open_add_form(self, customer_id=None):
        """Open form for adding CR/DR transaction"""
        self.account_form = CustomerAccountForm(
            refresh_callback=self.load_data,
            customer_id=customer_id,
        )
        self.account_form.show()

    def edit_transaction(self, trx_id, customer_id):
        """Edit transaction - for now, re-use the add form"""
        self.account_form = CustomerAccountForm(
            refresh_callback=self.load_data,
            customer_id=customer_id,
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
