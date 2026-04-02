from PySide6.QtWidgets import QFrame, QVBoxLayout, QLabel
from PySide6.QtCore import Qt
from src.controllers.auth_controller import AuthController


class UserCard(QFrame):
    """
    User info card that fetches data from the current session.
    """

    def __init__(self):
        super().__init__()
        self.controller = AuthController()
        self.user = self.controller.get_current_user() or {}
        self.init_ui()

    def init_ui(self):
        self.setObjectName("UserCard")
        self.setStyleSheet(
            """
            QFrame#UserCard {
                background-color: white;
                border-radius: 10px;
                padding: 15px;
            }
            QLabel {
                font-size: 15px;
            }
        """
        )

        layout = QVBoxLayout()
        layout.setSpacing(5)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        # Fetch user info safely
        username = self.user.get("username", "Guest")
        email = self.user.get("email", "Not logged in")

        self.name_label = QLabel(f"👤 Name: {username}")
        self.name_label.setStyleSheet("font-weight: 500; font-size: 16px;")

        self.email_label = QLabel(f"📧 Email: {email}")
        self.email_label.setStyleSheet("color: gray; font-size: 14px;")

        layout.addWidget(self.name_label)
        layout.addWidget(self.email_label)
        self.setLayout(layout)
