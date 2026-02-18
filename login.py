import sqlite3
from PyQt6.QtWidgets import (
    QWidget,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QGridLayout,
    QMessageBox,
)
from PyQt6.QtCore import Qt
from services.auth import authenticate_user, create_session


class LoginForm(QWidget):
    def __init__(self, on_login_success):
        super().__init__()
        self.on_login_success = on_login_success
        self.setWindowTitle("Login")
        self.setMinimumSize(350, 200)
        self.init_ui()

    def init_ui(self):
        grid = QGridLayout()
        grid.setSpacing(10)

        # Username
        username_label = QLabel("Username:")
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Enter username")
        self.username_input.textChanged.connect(self.validate_form)
        grid.addWidget(username_label, 0, 0, alignment=Qt.AlignmentFlag.AlignRight)
        grid.addWidget(self.username_input, 0, 1)

        # Password
        password_label = QLabel("Password:")
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.setPlaceholderText("Enter password")
        self.password_input.textChanged.connect(self.validate_form)
        grid.addWidget(password_label, 1, 0, alignment=Qt.AlignmentFlag.AlignRight)
        grid.addWidget(self.password_input, 1, 1)

        # Login button
        self.login_button = QPushButton("Login")
        self.login_button.setFixedHeight(40)
        self.login_button.clicked.connect(self.handle_login)
        self.login_button.setEnabled(False)

        layout = QVBoxLayout()
        layout.addLayout(grid)
        layout.addStretch()
        layout.addWidget(self.login_button, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addStretch()
        self.setLayout(layout)

    def validate_form(self):
        """Enable login button only if both fields are filled"""
        if self.username_input.text().strip() and self.password_input.text().strip():
            self.login_button.setEnabled(True)
        else:
            self.login_button.setEnabled(False)

    def handle_login(self):
        username = self.username_input.text().strip()
        password = self.password_input.text().strip()

        if authenticate_user(username, password):
            create_session(username)  # create session
            QMessageBox.information(self, "Login", "Login successful!")
            self.on_login_success()
            self.close()
        else:
            QMessageBox.warning(self, "Login Failed", "Invalid username or password.")
