from PySide6.QtWidgets import (
    QWidget,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QMessageBox,
    QFrame,
)
from PySide6.QtCore import Qt
from services.auth import authenticate_user, create_session
from config.theme import get_global_stylesheet
from utils.form_utils import set_error


class LoginForm(QWidget):
    def __init__(self, on_login_success):
        super().__init__()
        self.on_login_success = on_login_success
        self.setWindowTitle("Login")
        self.setFixedSize(400, 300)

        # Apply global stylesheet + validation styles
        self.setStyleSheet(get_global_stylesheet())

        self.init_ui()

    # ==============================
    # UI
    # ==============================
    def init_ui(self):
        main_layout = QVBoxLayout()
        main_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.card = QFrame()
        self.card.setFixedWidth(320)
        self.card.setStyleSheet(
            """
            QFrame {
                background-color: white;
                border-radius: 12px;
            }
        """
        )

        card_layout = QVBoxLayout()
        card_layout.setSpacing(8)
        card_layout.setContentsMargins(25, 25, 25, 25)

        # Title
        title = QLabel("Welcome Back")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("font-size: 20px; font-weight: bold;")

        subtitle = QLabel("Please login to continue")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle.setStyleSheet("color: gray; font-size: 12px;")

        # Username
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Username")

        self.username_error_label = QLabel()
        self.username_error_label.setStyleSheet("color: #e74c3c; font-size: 11px;")
        self.username_error_label.setVisible(False)

        # Password
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Password")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)

        self.password_error_label = QLabel()
        self.password_error_label.setStyleSheet("color: #e74c3c; font-size: 11px;")
        self.password_error_label.setVisible(False)

        # Login button
        self.login_button = QPushButton("Login")
        self.login_button.setProperty("class", "primary")
        self.login_button.setFixedHeight(35)
        self.login_button.setEnabled(False)

        # Connections
        self.username_input.textChanged.connect(self.clear_username_error)
        self.password_input.textChanged.connect(self.clear_password_error)
        self.username_input.textChanged.connect(self.validate_form)
        self.password_input.textChanged.connect(self.validate_form)

        self.password_input.returnPressed.connect(self.handle_login)
        self.login_button.clicked.connect(self.handle_login)

        # Layout
        card_layout.addWidget(title)
        card_layout.addWidget(subtitle)
        card_layout.addSpacing(10)

        card_layout.addWidget(self.username_input)
        card_layout.addWidget(self.username_error_label)

        card_layout.addWidget(self.password_input)
        card_layout.addWidget(self.password_error_label)

        card_layout.addSpacing(10)
        card_layout.addWidget(self.login_button)

        self.card.setLayout(card_layout)
        main_layout.addWidget(self.card)
        self.setLayout(main_layout)

        self.setStyleSheet(
            self.styleSheet()
            + """
            QWidget {
                background-color: #f4f6f9;
            }
        """
        )

    # ==============================
    # Validation
    # ==============================
    def validate_form(self):
        username = self.username_input.text().strip()
        password = self.password_input.text().strip()

        is_valid = True

        if not username:
            set_error(True, self.username_input)
            self.username_error_label.setText("Username is required")
            self.username_error_label.setVisible(True)
            is_valid = False

        if not password:
            set_error(True, self.password_input)
            self.password_error_label.setText("Password is required")
            self.password_error_label.setVisible(True)
            is_valid = False

        self.login_button.setEnabled(is_valid)

    def handle_login(self):
        username = self.username_input.text().strip()
        password = self.password_input.text().strip()

        # Final validation check
        if not username or not password:
            self.validate_form()
            QMessageBox.warning(self, "Validation Error", "All fields are required.")
            return

        if authenticate_user(username, password):
            create_session(username)
            QMessageBox.information(self, "Login", "Login successful!")
            self.on_login_success()
            self.close()
        else:
            set_error(True, self.username_input)
            set_error(True, self.password_input)
            QMessageBox.warning(self, "Login Failed", "Invalid username or password.")

    def clear_username_error(self):
        set_error(False, self.username_input)
        self.username_error_label.setVisible(False)

    def clear_password_error(self):
        set_error(False, self.password_input)
        self.password_error_label.setVisible(False)
