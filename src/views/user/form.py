from PySide6.QtWidgets import (
    QWidget,
    QLabel,
    QLineEdit,
    QPushButton,
    QGridLayout,
    QVBoxLayout,
    QMessageBox,
    QSizePolicy,
)
from PySide6.QtCore import Qt
from src.services.user import addUser, getUser, updateUser
from config.theme import getGlobalStylesheet
from utils.formUtils import setError  # reuse the same helper from login


class UserForm(QWidget):
    def __init__(self, refresh_callback, user_type="user", user_id=None):
        super().__init__()
        self.user_id = user_id
        self.user_type = user_type
        self.refresh_callback = refresh_callback

        self.setWindowTitle("User Form")
        self.setMinimumSize(400, 400)
        self.setStyleSheet(getGlobalStylesheet())
        self.init_ui()

        if self.user_id:
            self.load_user()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # Title
        title = QLabel("Edit User" if self.user_id else "Add New User")
        title.setStyleSheet("font-size: 18px; font-weight: bold;")
        layout.addWidget(title, alignment=Qt.AlignmentFlag.AlignCenter)

        # Grid for inputs
        grid = QGridLayout()
        grid.setVerticalSpacing(8)
        grid.setHorizontalSpacing(10)

        # Name
        grid.addWidget(QLabel("Name:"), 0, 0)
        self.name_input, self.name_error = self.create_input()
        grid.addWidget(self.name_input, 0, 1)
        grid.addWidget(self.name_error, 1, 1)

        # Email
        grid.addWidget(QLabel("Email:"), 2, 0)
        self.email_input, self.email_error = self.create_input()
        grid.addWidget(self.email_input, 2, 1)
        grid.addWidget(self.email_error, 3, 1)

        # Contact
        grid.addWidget(QLabel("Contact:"), 4, 0)
        self.contact_input, self.contact_error = self.create_input()
        grid.addWidget(self.contact_input, 4, 1)
        grid.addWidget(self.contact_error, 5, 1)

        # Address
        grid.addWidget(QLabel("Address:"), 6, 0)
        self.address_input, self.address_error = self.create_input()
        grid.addWidget(self.address_input, 6, 1)
        grid.addWidget(self.address_error, 7, 1)

        layout.addLayout(grid)

        # Save button
        self.save_btn = QPushButton("Save User")
        self.save_btn.setProperty("class", "primary")
        self.save_btn.setMinimumHeight(36)
        self.save_btn.setEnabled(False)
        self.save_btn.clicked.connect(self.save_user)

        # Make button full width
        self.save_btn.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed
        )
        layout.addWidget(self.save_btn, alignment=Qt.AlignmentFlag.AlignCenter)

        # Connect input change signals to validation
        for input_field, error_label in [
            (self.name_input, self.name_error),
            (self.email_input, self.email_error),
            (self.contact_input, self.contact_error),
            (self.address_input, self.address_error),
        ]:
            input_field.textChanged.connect(self.validate_form)
            input_field.textChanged.connect(
                lambda _, f=input_field, e=error_label: self.clear_error(f, e)
            )

        self.setLayout(layout)

    # ==============================
    # Input helpers
    # ==============================
    def create_input(self):
        input_field = QLineEdit()
        input_field.setMinimumHeight(30)

        error_label = QLabel()
        error_label.setStyleSheet("color: #e74c3c; font-size: 11px;")
        error_label.setVisible(False)

        return input_field, error_label

    def clear_error(self, input_field, error_label):
        setError(False, input_field)
        error_label.setVisible(False)

    # ==============================
    # Validation
    # ==============================
    def validate_form(self):
        """Validate required fields and enable save button if valid"""
        valid = True

        # Name validation
        name = self.name_input.text().strip()
        if not name:
            setError(True, self.name_input)
            self.name_error.setText("Name is required")
            self.name_error.setVisible(True)
            valid = False

        # Email validation (basic)
        email = self.email_input.text().strip()
        if not email:
            setError(True, self.email_input)
            self.email_error.setText("Email is required")
            self.email_error.setVisible(True)
            valid = False
        elif "@" not in email or "." not in email:
            setError(True, self.email_input)
            self.email_error.setText("Invalid email address")
            self.email_error.setVisible(True)
            valid = False

        # Optional: contact validation (digits only)
        contact = self.contact_input.text().strip()
        if contact and not contact.isdigit():
            setError(True, self.contact_input)
            self.contact_error.setText("Contact must be numeric")
            self.contact_error.setVisible(True)
            valid = False

        self.save_btn.setEnabled(valid)

    # ==============================
    # Load user
    # ==============================
    def load_user(self):
        user = getUser(self.user_id)
        if not user:
            QMessageBox.warning(self, "Error", "User not found.")
            self.close()
            return

        self.name_input.setText(user.name or "")
        self.email_input.setText(user.email or "")
        self.contact_input.setText(user.contact or "")
        self.address_input.setText(user.address or "")

    # ==============================
    # Save user
    # ==============================
    def save_user(self):
        self.validate_form()
        if not self.save_btn.isEnabled():
            QMessageBox.warning(self, "Validation Error", "Please fix the errors.")
            return

        name = self.name_input.text().strip()
        email = self.email_input.text().strip()
        contact = self.contact_input.text().strip()
        address = self.address_input.text().strip()
        user_type = self.user_type

        try:
            if self.user_id:
                updateUser(
                    self.user_id,
                    name=name,
                    email=email,
                    contact=contact,
                    address=address,
                    user_type=user_type,
                )
                QMessageBox.information(self, "Success", "User updated successfully.")
            else:
                addUser(name, email, contact, address, user_type)
                QMessageBox.information(self, "Success", "User added successfully.")

            self.refresh_callback()
            self.close()
        except ValueError as e:
            QMessageBox.warning(self, "Error", str(e))
