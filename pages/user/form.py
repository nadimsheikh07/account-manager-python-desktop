from PySide6.QtWidgets import (
    QWidget,
    QLabel,
    QLineEdit,
    QPushButton,
    QGridLayout,
    QVBoxLayout,
    QMessageBox,
)
from PySide6.QtCore import Qt
from services.user import addUser, getUser, updateUser
from config.theme import getGlobalStylesheet


class UserForm(QWidget):
    def __init__(self, refresh_callback, user_type="user", user_id=None):
        """
        user_id=None -> Create new
        refresh_callback -> function to refresh the list after save
        """
        super().__init__()
        self.user_id = user_id
        self.user_type = user_type

        self.refresh_callback = refresh_callback
        self.setWindowTitle("User Form")
        self.setMinimumSize(400, 350)
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
        grid.setVerticalSpacing(12)
        grid.setHorizontalSpacing(10)

        # Name
        grid.addWidget(QLabel("Name:"), 0, 0)
        self.name_input = QLineEdit()
        self.name_input.setMinimumHeight(30)
        grid.addWidget(self.name_input, 0, 1)

        # Email
        grid.addWidget(QLabel("Email:"), 1, 0)
        self.email_input = QLineEdit()
        self.email_input.setMinimumHeight(30)
        grid.addWidget(self.email_input, 1, 1)

        # Contact
        grid.addWidget(QLabel("Contact:"), 2, 0)
        self.contact_input = QLineEdit()
        self.contact_input.setMinimumHeight(30)
        grid.addWidget(self.contact_input, 2, 1)

        # Address
        grid.addWidget(QLabel("Address:"), 3, 0)
        self.address_input = QLineEdit()
        self.address_input.setMinimumHeight(30)
        grid.addWidget(self.address_input, 3, 1)

        layout.addLayout(grid)

        # Save button
        self.save_btn = QPushButton("Save")
        self.save_btn.setProperty("class", "primary")
        self.save_btn.setMinimumHeight(36)
        self.save_btn.clicked.connect(self.save_user)
        layout.addWidget(self.save_btn, alignment=Qt.AlignmentFlag.AlignCenter)

        self.setLayout(layout)

    def load_user(self):
        """Load user data for editing"""
        user = getUser(self.user_id)

        if not user:
            return

        self.name_input.setText(user["name"] or "")
        self.email_input.setText(user["email"] or "")
        self.contact_input.setText(user["contact"] or "")
        self.address_input.setText(user["address"] or "")

    def save_user(self):
        name = self.name_input.text().strip()
        email = self.email_input.text().strip()
        contact = self.contact_input.text().strip()
        address = self.address_input.text().strip()
        user_type = self.user_type

        if not (name and email):
            QMessageBox.warning(
                self, "Validation Error", "Name and Email are required."
            )
            return

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
