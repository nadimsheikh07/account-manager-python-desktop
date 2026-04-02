from PySide6.QtWidgets import (
    QWidget,
    QLabel,
    QLineEdit,
    QPushButton,
    QComboBox,
    QGridLayout,
    QVBoxLayout,
    QMessageBox,
    QSizePolicy,
)
from PySide6.QtCore import Qt
from config.theme import getGlobalStylesheet
from src.controllers.user_account_controller import UserAccountController
from src.services.user import getAllUsers
from sqlalchemy.exc import SQLAlchemyError
from utils.formUtils import setError  # reuse error styling helper


class UserAccountForm(QWidget):
    def __init__(self, refresh_callback, user_id=None, trx_id=None):
        """
        user_id=None -> Optional, select user from dropdown
        trx_id=None -> Optional, if provided, load transaction for editing
        refresh_callback -> function to refresh the account list after save
        """
        super().__init__()
        self.user_id = user_id
        self.trx_id = trx_id
        self.refresh_callback = refresh_callback
        self.setWindowTitle("User Account Form")
        self.setMinimumSize(400, 350)
        self.setStyleSheet(getGlobalStylesheet())
        self.controller = UserAccountController()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # Title
        title_text = "Edit Transaction" if self.trx_id else "Add Transaction"
        title = QLabel(title_text)
        title.setStyleSheet("font-size: 18px; font-weight: bold;")
        layout.addWidget(title, alignment=Qt.AlignmentFlag.AlignCenter)

        # Grid for inputs
        grid = QGridLayout()
        grid.setVerticalSpacing(8)
        grid.setHorizontalSpacing(10)

        # User Type dropdown
        grid.addWidget(QLabel("User Type:"), 0, 0)
        self.user_type_combo = QComboBox()
        self.user_type_combo.addItems(["user", "employee", "customer", "supplier"])
        grid.addWidget(self.user_type_combo, 0, 1)

        # User dropdown
        grid.addWidget(QLabel("User:"), 1, 0)  # <-- row 1
        self.user_dropdown = QComboBox()
        grid.addWidget(self.user_dropdown, 1, 1)
        self.user_error = QLabel()
        self.user_error.setStyleSheet("color: #e74c3c; font-size: 11px;")
        self.user_error.setVisible(False)
        grid.addWidget(self.user_error, 2, 1)

        if self.user_id:
            index = self.user_dropdown.findData(self.user_id)
            if index != -1:
                self.user_dropdown.setCurrentIndex(index)

        # Type: CR or DR
        grid.addWidget(QLabel("Type:"), 2, 0)
        self.type_combo = QComboBox()
        self.type_combo.addItems(["CR", "DR"])
        grid.addWidget(self.type_combo, 2, 1)

        # Amount
        grid.addWidget(QLabel("Amount:"), 3, 0)
        self.amount_input = QLineEdit()
        self.amount_input.setMinimumHeight(30)
        self.amount_input.setPlaceholderText("Enter numeric amount")
        grid.addWidget(self.amount_input, 3, 1)
        self.amount_error = QLabel()
        self.amount_error.setStyleSheet("color: #e74c3c; font-size: 11px;")
        self.amount_error.setVisible(False)
        grid.addWidget(self.amount_error, 4, 1)

        # Description (optional)
        grid.addWidget(QLabel("Description:"), 5, 0)
        self.description_input = QLineEdit()
        self.description_input.setMinimumHeight(30)
        grid.addWidget(self.description_input, 5, 1)

        # Current Balance (read-only)
        grid.addWidget(QLabel("Current Balance:"), 6, 0)
        self.balance_label = QLabel("0.00")
        grid.addWidget(self.balance_label, 6, 1)

        # Update balance when selecting User
        self.user_dropdown.currentIndexChanged.connect(self.update_balance)

        layout.addLayout(grid)

        # Save button
        self.save_btn = QPushButton("Save Transaction")
        self.save_btn.setProperty("class", "primary")
        self.save_btn.setMinimumHeight(36)
        self.save_btn.clicked.connect(self.save_transaction)
        self.save_btn.setEnabled(False)
        # Make button full width
        self.save_btn.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed
        )

        layout.addWidget(self.save_btn, alignment=Qt.AlignmentFlag.AlignCenter)

        # Connect signals
        self.user_type_combo.currentTextChanged.connect(self.load_users)
        self.user_dropdown.currentIndexChanged.connect(self.update_balance)
        self.amount_input.textChanged.connect(
            lambda: self.clear_error(self.amount_input, self.amount_error)
        )

        # Now safe to load users and update balance
        self.load_users()
        self.setLayout(layout)
        if self.trx_id:
            self.load_transaction_data()
        self.update_balance()
        self.validate_form()

    # ==============================
    # Load Transaction Data for Edit
    # ==============================
    def load_transaction_data(self):
        if not self.trx_id:
            return

        trx = self.controller.get_transaction(self.trx_id)
        if trx:
            # Set user type and load users
            user = trx.user
            if user:
                # Block signals temporarily to prevent multiple loads
                self.user_type_combo.blockSignals(True)
                self.user_dropdown.blockSignals(True)

                self.user_type_combo.setCurrentText(user.type)
                self.load_users()  # Ensure users are loaded for this type

                index = self.user_dropdown.findData(user.id)
                if index != -1:
                    self.user_dropdown.setCurrentIndex(index)

                self.user_type_combo.blockSignals(False)
                self.user_dropdown.blockSignals(False)

            # Set other fields
            self.type_combo.setCurrentText(trx.type)
            self.amount_input.setText(str(trx.amount))
            self.description_input.setText(trx.description or "")

    # ==============================
    # Helpers
    # ==============================
    def clear_error(self, input_field, error_label):
        setError(False, input_field)
        error_label.setVisible(False)

    # ==============================
    # Load users
    # ==============================
    def load_users(self):
        """Load all Users into the dropdown based on selected type"""
        self.user_dropdown.clear()
        user_type = self.user_type_combo.currentText()  # get selected type
        try:
            users = getAllUsers(
                type=user_type
            )  # ORM service returns list of User objects
            for u in users:
                display_text = f"{u.name} ({u.email})"
                self.user_dropdown.addItem(display_text, u.id)

            # Automatically select first user if available
            if users:
                self.user_dropdown.setCurrentIndex(0)

        except SQLAlchemyError as e:
            QMessageBox.warning(self, "Error", f"Failed to load users: {str(e)}")

        self.validate_form()  # re-validate after loading

    # ==============================
    # Update balance
    # ==============================
    def update_balance(self):
        user_id = self.user_dropdown.currentData()
        if user_id:
            balance = self.controller.get_user_balance(user_id)
            self.balance_label.setText(f"{balance:.2f}")
        else:
            self.balance_label.setText("0.00")
        self.validate_form()

    # ==============================
    # Validation
    # ==============================
    def validate_form(self):
        """Enable save button only if inputs are valid"""
        valid = True
        user_id = self.user_dropdown.currentData()
        amount_text = self.amount_input.text().strip()

        # User validation
        if not user_id:
            self.user_error.setText("User is required")
            self.user_error.setVisible(True)
            valid = False
        else:
            self.user_error.setVisible(False)

        # Amount validation
        if not amount_text:
            self.amount_error.setText("Amount is required")
            self.amount_error.setVisible(True)
            setError(True, self.amount_input)
            valid = False
        else:
            try:
                amount = float(amount_text)
                if amount <= 0:
                    raise ValueError
                self.amount_error.setVisible(False)
                setError(False, self.amount_input)
            except ValueError:
                self.amount_error.setText("Enter a valid positive number")
                self.amount_error.setVisible(True)
                setError(True, self.amount_input)
                valid = False

        self.save_btn.setEnabled(valid)
        return valid

    # ==============================
    # Save transaction
    # ==============================
    def save_transaction(self):
        if not self.validate_form():
            QMessageBox.warning(
                self, "Validation Error", "Please fix the errors before saving."
            )
            return

        user_id = self.user_dropdown.currentData()
        amount = float(self.amount_input.text().strip())
        type_ = self.type_combo.currentText()
        description = self.description_input.text().strip()

        try:
            success, message = self.controller.save_transaction(
                user_id, amount, type_, description, trx_id=self.trx_id
            )
            if success:
                QMessageBox.information(self, "Success", message)
                self.refresh_callback()
                self.close()
            else:
                QMessageBox.warning(self, "Error", message)
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to save: {str(e)}")
