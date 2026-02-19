from PySide6.QtWidgets import QWidget, QLabel, QVBoxLayout, QFrame
from PySide6.QtCore import Qt
from services.auth import get_user_from_session


class Dashboard(QWidget):
    def __init__(self):
        super().__init__()

        self.user = get_user_from_session() or {}
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        layout.setSpacing(15)

        # Extract user safely
        username = self.user.get("username", "Guest")
        email = self.user.get("email", "Not logged in")

        # Title
        title = QLabel("Dashboard")
        title.setStyleSheet(
            """
            font-size: 22px;
            font-weight: bold;
        """
        )

        # User Name
        name_label = QLabel(f"👤 Name: {username}")
        name_label.setStyleSheet("font-size: 16px;")

        # Email
        email_label = QLabel(f"📧 Email: {email}")
        email_label.setStyleSheet("font-size: 16px;")

        # Card container
        card = QFrame()
        card.setObjectName("DashboardCard")  # Better for styling via global theme

        card_layout = QVBoxLayout()
        card_layout.addWidget(name_label)
        card_layout.addWidget(email_label)
        card.setLayout(card_layout)

        layout.addWidget(title)
        layout.addWidget(card)

        self.setLayout(layout)
