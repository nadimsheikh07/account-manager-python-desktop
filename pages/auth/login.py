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


class LoginForm(QWidget):
    def __init__(self, on_login_success):
        super().__init__()
        self.on_login_success = on_login_success
        self.setWindowTitle("Login")
        self.setFixedSize(400, 300)
        self.setStyleSheet(get_global_stylesheet())
        self.init_ui()

    def init_ui(self):
        # ===== Main Layout =====
        main_layout = QVBoxLayout()
        main_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # ===== Card Frame =====
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
        card_layout.setSpacing(15)
        card_layout.setContentsMargins(25, 25, 25, 25)

        # ===== Title =====
        title = QLabel("Welcome Back")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet(
            """
            font-size: 20px;
            font-weight: bold;
        """
        )

        subtitle = QLabel("Please login to continue")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle.setStyleSheet("color: gray; font-size: 12px;")

        # ===== Inputs =====
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Username")

        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Password")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)

        # Enter key support
        self.password_input.returnPressed.connect(self.handle_login)

        # ===== Login Button =====
        self.login_button = QPushButton("Login")
        self.login_button.setProperty("class", "primary")
        self.login_button.setFixedHeight(35)
        self.login_button.clicked.connect(self.handle_login)
        self.login_button.setEnabled(False)

        # Connect validation
        self.username_input.textChanged.connect(self.validate_form)
        self.password_input.textChanged.connect(self.validate_form)

        # Add widgets to card
        card_layout.addWidget(title)
        card_layout.addWidget(subtitle)
        card_layout.addSpacing(10)
        card_layout.addWidget(self.username_input)
        card_layout.addWidget(self.password_input)
        card_layout.addSpacing(10)
        card_layout.addWidget(self.login_button)

        self.card.setLayout(card_layout)
        main_layout.addWidget(self.card)

        self.setLayout(main_layout)

        # ===== Window Background =====
        self.setStyleSheet(
            """
            QWidget {
                background-color: #f4f6f9;
            }
        """
        )

    def validate_form(self):
        if self.username_input.text().strip() and self.password_input.text().strip():
            self.login_button.setEnabled(True)
        else:
            self.login_button.setEnabled(False)

    def handle_login(self):
        username = self.username_input.text().strip()
        password = self.password_input.text().strip()

        if authenticate_user(username, password):
            create_session(username)
            QMessageBox.information(self, "Login", "Login successful!")
            self.on_login_success()
            self.close()
        else:
            QMessageBox.warning(self, "Login Failed", "Invalid username or password.")
