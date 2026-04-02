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
from src.controllers.user_account_controller import UserAccountController
from src.services.userAccount import (
    exportToExcel,
)
from src.views.userAccount.form import UserAccountForm
from src.components.heading import createTitle


class UserAccountList(QWidget):
    def __init__(self):
        super().__init__()
        self.setMinimumSize(700, 500)
        self.setStyleSheet(getGlobalStylesheet())
        self.controller = UserAccountController()

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

        # ===== New Refresh Button =====
        self.refresh_btn = QPushButton("Refresh")
        self.refresh_btn.setProperty("class", "secondary")
        self.refresh_btn.setMinimumHeight(36)
        self.refresh_btn.clicked.connect(self.load_data)  # reload table data

        top_layout.addWidget(self.search_input)
        top_layout.addWidget(self.add_btn)
        top_layout.addWidget(self.export_btn)
        top_layout.addWidget(self.refresh_btn)  # add to layout
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
        query = self.search_input.text()
        all_rows_data = self.controller.get_account_data(query)

        self.table.setRowCount(len(all_rows_data))

        for row_idx, data in enumerate(all_rows_data):
            trx_id = data["trx_id"]
            name = data["user_name"]
            email = data["user_email"]
            cr = data["cr"]
            dr = data["dr"]
            balance = data["balance"]
            date = data["date"]
            description = data["description"]
            user_id = data["user_id"]

            row_display = [
                trx_id,
                name,
                email,
                f"{cr:.2f}" if cr else "",
                f"{dr:.2f}" if dr else "",
                f"{balance:.2f}",
                date,
            ]

            for col_idx, value in enumerate(row_display):
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
            success, message = self.controller.delete_transaction(trx_id)
            if success:
                QMessageBox.information(self, "Success", message)
                self.load_data()
            else:
                QMessageBox.warning(self, "Error", message)
