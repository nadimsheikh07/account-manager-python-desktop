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
    QTabWidget,
)
from PySide6.QtCore import Qt
from functools import partial
from config.theme import getGlobalStylesheet
from src.services.user import getAllUsers, delete_user, exportToExcel
from src.services.userAccount import getUserBalance
from src.services.userLedger import exportUserPdf
from src.components.heading import createTitle
from src.views.user.form import UserForm


class UserList(QWidget):
    TYPE_MAP = {
        "users": "user",
        "employees": "employee",
        "customers": "customer",
        "suppliers": "supplier",
    }

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
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        layout.addWidget(createTitle("Users"))

        # ===== Top Bar =====
        top_layout = QHBoxLayout()

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText(
            "Search by name, email, contact, address, or date..."
        )
        self.search_input.setMinimumHeight(36)
        self.search_input.textChanged.connect(self.load_data)

        self.add_btn = QPushButton("Add User")
        self.add_btn.setProperty("class", "primary")
        self.add_btn.clicked.connect(self.open_add_form)

        self.export_btn = QPushButton("Export to Excel")
        self.export_btn.setProperty("class", "primary")
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

        # ===== Tabs =====
        self.tabs = QTabWidget()
        for label in self.TYPE_MAP.keys():
            self.tabs.addTab(QWidget(), label.capitalize())

        self.tabs.currentChanged.connect(self.load_data)
        layout.addWidget(self.tabs)

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

        self.table.setColumnHidden(0, True)
        layout.addWidget(self.table)
        layout.setStretchFactor(self.table, 1)

    # =========================
    # Data Loading
    # =========================
    def load_data(self):
        self.table.setSortingEnabled(False)

        selected_type = self._get_selected_type()
        users = getAllUsers(selected_type)  # returns ORM objects
        users = [self._orm_to_dict(u) for u in users]

        filtered_users = self._filter_users(users)
        self._populate_table(filtered_users)

        self.table.setSortingEnabled(True)

    def _orm_to_dict(self, user):
        """Convert ORM User object to dict for table population"""
        return {
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "contact": user.contact,
            "address": user.address,
            "date": user.date.strftime("%Y-%m-%d %H:%M:%S") if user.date else "",
            "type": user.type,
        }

    def _get_selected_type(self):
        tab_text = self.tabs.tabText(self.tabs.currentIndex()).lower()
        return self.TYPE_MAP.get(tab_text, "user")

    def _filter_users(self, users):
        query = self.search_input.text().strip().lower()
        if not query:
            return users

        def matches(user):
            fields = ["name", "email", "contact", "address", "date"]
            return any(query in str(user.get(field, "")).lower() for field in fields)

        return [user for user in users if matches(user)]

    def _populate_table(self, users):
        self.table.setRowCount(len(users))

        for row, user in enumerate(users):
            user_id = user.get("id")
            balance = getUserBalance(user_id)  # ORM-based

            row_data = [
                user_id,
                user.get("name", ""),
                user.get("email", ""),
                user.get("contact", ""),
                user.get("address", ""),
                user.get("date", ""),
                f"{balance:.2f}",
            ]

            for col, value in enumerate(row_data):
                item = QTableWidgetItem(str(value))
                item.setFlags(Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEnabled)
                self.table.setItem(row, col, item)

            self.table.setCellWidget(row, 7, self._create_action_buttons(user_id))

    def _create_action_buttons(self, user_id):
        edit_btn = QPushButton("Edit")
        edit_btn.setProperty("class", "primary")
        edit_btn.clicked.connect(partial(self.edit_user, user_id))

        delete_btn = QPushButton("Delete")
        delete_btn.setProperty("class", "danger")
        delete_btn.clicked.connect(partial(self.delete_user, user_id))

        pdf_btn = QPushButton("PDF")
        pdf_btn.setProperty("class", "primary")
        pdf_btn.clicked.connect(partial(exportUserPdf, self, user_id))

        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(edit_btn)
        layout.addWidget(delete_btn)
        layout.addWidget(pdf_btn)

        container = QWidget()
        container.setLayout(layout)
        return container

    # =========================
    # Actions
    # =========================
    def open_add_form(self):
        user_type = self._get_selected_type()
        self.user_form = UserForm(refresh_callback=self.load_data, user_type=user_type)
        self.user_form.show()

    def edit_user(self, user_id):
        user_type = self._get_selected_type()
        self.user_form = UserForm(
            refresh_callback=self.load_data, user_type=user_type, user_id=user_id
        )
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
