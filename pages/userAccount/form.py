from PySide6.QtWidgets import (
    QWidget,
    QLabel,
    QLineEdit,
    QPushButton,
    QComboBox,
    QGridLayout,
    QVBoxLayout,
    QMessageBox,
)
from PySide6.QtCore import Qt
from services.userAccount import addTransaction, getUserBalance
from services.user import getAllUsers
from config.theme import getGlobalStylesheet


class UserAccountForm(QWidget):
    def __init__(self, refresh_callback, user_id=None):
        """
        user_id=None -> Optional, select user from dropdown
        refresh_callback -> function to refresh the account list after save
        """
        super().__init__()
        self.user_id = user_id
        self.refresh_callback = refresh_callback
        self.setWindowTitle("User Account Form")
        self.setMinimumSize(400, 320)
        self.setStyleSheet(getGlobalStylesheet())
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # Title
        title = QLabel("Add Transaction")
        title.setStyleSheet("font-size: 18px; font-weight: bold;")
        layout.addWidget(title, alignment=Qt.AlignmentFlag.AlignCenter)

        # Grid for inputs
        grid = QGridLayout()
        grid.setVerticalSpacing(12)
        grid.setHorizontalSpacing(10)

        # User dropdown
        grid.addWidget(QLabel("User:"), 0, 0)
        self.user_dropdown = QComboBox()
        self.load_users()
        grid.addWidget(self.user_dropdown, 0, 1)

        if self.user_id:
            # Preselect the User if provided
            index = self.user_dropdown.findData(self.user_id)
            if index != -1:
                self.user_dropdown.setCurrentIndex(index)

        # Type: CR or DR
        grid.addWidget(QLabel("Type:"), 1, 0)
        self.type_combo = QComboBox()
        self.type_combo.addItems(["CR", "DR"])
        grid.addWidget(self.type_combo, 1, 1)

        # Amount
        grid.addWidget(QLabel("Amount:"), 2, 0)
        self.amount_input = QLineEdit()
        self.amount_input.setMinimumHeight(30)
        self.amount_input.setPlaceholderText("Enter numeric amount")
        grid.addWidget(self.amount_input, 2, 1)

        # Description (optional)
        grid.addWidget(QLabel("Description:"), 3, 0)
        self.description_input = QLineEdit()
        self.description_input.setMinimumHeight(30)
        grid.addWidget(self.description_input, 3, 1)

        # Current Balance (read-only)
        grid.addWidget(QLabel("Current Balance:"), 4, 0)
        self.balance_label = QLabel("0.00")
        grid.addWidget(self.balance_label, 4, 1)

        # Update balance when selecting User
        self.user_dropdown.currentIndexChanged.connect(self.update_balance)

        layout.addLayout(grid)

        # Save button
        self.save_btn = QPushButton("Save Transaction")
        self.save_btn.setProperty("class", "primary")
        self.save_btn.setMinimumHeight(36)
        self.save_btn.clicked.connect(self.save_transaction)
        layout.addWidget(self.save_btn, alignment=Qt.AlignmentFlag.AlignCenter)

        self.setLayout(layout)

        # Initial balance
        self.update_balance()

    def load_users(self):
        """Load all Users into the dropdown"""
        self.user_dropdown.clear()
        users = getAllUsers()
        for user in users:
            user_id = user["id"]
            name = user["name"]
            email = user["email"]
            contact = user["contact"]
            address = user["address"]
            date = user["date"]
            type = user["type"]
            display_text = f"{name} ({email})"
            self.user_dropdown.addItem(display_text, user_id)

    def update_balance(self):
        """Update current balance display for selected User"""
        user_id = self.user_dropdown.currentData()
        if user_id:
            balance = getUserBalance(user_id)
            self.balance_label.setText(f"{balance:.2f}")
        else:
            self.balance_label.setText("0.00")

    def save_transaction(self):
        user_id = self.user_dropdown.currentData()
        amount_text = self.amount_input.text().strip()
        type_ = self.type_combo.currentText()
        description = self.description_input.text().strip()

        if not user_id:
            QMessageBox.warning(self, "Validation Error", "User is required.")
            return

        if not amount_text:
            QMessageBox.warning(self, "Validation Error", "Amount is required.")
            return

        try:
            amount = float(amount_text)
        except ValueError:
            QMessageBox.warning(self, "Validation Error", "Amount must be a number.")
            return

        try:
            addTransaction(user_id, amount, type_, description)
            QMessageBox.information(self, "Success", "Transaction added successfully.")
            self.refresh_callback()
            self.close()
        except Exception as e:
            QMessageBox.warning(self, "Error", str(e))
