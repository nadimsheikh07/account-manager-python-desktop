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
from services.user import getAllUsers, delete_user, exportToExcel
from pages.user.form import UserForm
from services.userAccount import getUserBalance
from services.userReport import exportUserPdf
from components.heading import createTitle


class UserList(QWidget):
    def __init__(self):
        super().__init__()
        self.setMinimumSize(600, 400)
        self.setStyleSheet(getGlobalStylesheet())

        self.init_ui()
        self.load_data()

    # =========================
    # UI Setup
    # =========================
    def init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        layout.addWidget(createTitle("Users"))

        # ===== Top Bar =====
        top_layout = QHBoxLayout()
        top_layout.setSpacing(10)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText(
            "Search by name, email, contact, address, or date..."
        )
        self.search_input.setMinimumHeight(36)
        self.search_input.textChanged.connect(self.load_data)

        self.add_btn = QPushButton("Add User")
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
            ["ID", "Name", "Email", "Contact", "Address", "Date", "Balance", "Actions"]
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

        self.table.setRowCount(len(filtered))

        for row_idx, user in enumerate(filtered):
            user_id = user["id"]
            name = user["name"]
            email = user["email"]
            contact = user["contact"]
            address = user["address"]
            date = user["date"]
            user_type = user["type"]

            balance = getUserBalance(user_id)

            row_values = [
                user_id,
                name,
                email,
                contact,
                address,
                date,
                f"{balance:.2f}",
            ]

            for col_idx, value in enumerate(row_values):
                item = QTableWidgetItem(str(value if value is not None else ""))
                item.setFlags(Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEnabled)
                self.table.setItem(row_idx, col_idx, item)

            # ===== Action Buttons =====
            edit_btn = QPushButton("Edit")
            edit_btn.setProperty("class", "primary")
            edit_btn.clicked.connect(partial(self.edit_user, user_id))

            delete_btn = QPushButton("Delete")
            delete_btn.setProperty("class", "danger")
            delete_btn.clicked.connect(partial(self.delete_user, user_id))

            pdf_btn = QPushButton("PDF")
            pdf_btn.setProperty("class", "primary")
            pdf_btn.clicked.connect(partial(exportUserPdf, self, user_id))

            action_layout = QHBoxLayout()
            action_layout.addWidget(edit_btn)
            action_layout.addWidget(delete_btn)
            action_layout.addWidget(pdf_btn)
            action_layout.setContentsMargins(0, 0, 0, 0)

            action_widget = QWidget()
            action_widget.setLayout(action_layout)
            self.table.setCellWidget(row_idx, 7, action_widget)

        self.table.setSortingEnabled(True)

    # =========================
    # Actions
    # =========================
    def open_add_form(self):
        self.user_form = UserForm(refresh_callback=self.load_data, user_id=None)
        self.user_form.show()

    def edit_user(self, user_id):
        self.user_form = UserForm(refresh_callback=self.load_data, user_id=user_id)
        self.user_form.show()

    def delete_user(self, user_id):
        confirm = QMessageBox.question(
            self,
            "Confirm Delete",
            "Are you sure you want to delete this user?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if confirm == QMessageBox.StandardButton.Yes:
            delete_user(user_id)
            QMessageBox.information(self, "Deleted", "User deleted successfully.")
            self.load_data()
