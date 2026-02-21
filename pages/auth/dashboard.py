from PySide6.QtWidgets import QWidget, QLabel, QVBoxLayout, QFrame
from PySide6.QtCore import Qt
from services.auth import get_user_from_session
from pages.dashboard.accounts_chart import CustomerAccountsChart
from pages.dashboard.monthly_customers_chart import MonthlyCustomersChart


class Dashboard(QWidget):
    def __init__(self):
        super().__init__()
        self.user = get_user_from_session() or {}
        self.init_ui()

    # =============================
    # Main Layout
    # =============================
    def init_ui(self):
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        layout.setSpacing(15)

        layout.addWidget(self.create_title("Dashboard"))
        layout.addWidget(self.create_user_card())
        layout.addWidget(MonthlyCustomersChart())  # New customers chart
        layout.addWidget(CustomerAccountsChart())  # new CR/DR chart

        self.setLayout(layout)

    # =============================
    # Title Component
    # =============================
    def create_title(self, text: str) -> QLabel:
        title = QLabel(text)
        title.setStyleSheet(
            """
            font-size: 22px;
            font-weight: bold;
        """
        )
        return title

    # =============================
    # User Info Card Component
    # =============================
    def create_user_card(self) -> QFrame:
        username = self.user.get("username", "Guest")
        email = self.user.get("email", "Not logged in")

        card = QFrame()
        card.setObjectName("DashboardCard")  # For global stylesheet
        card_layout = QVBoxLayout()
        card_layout.setSpacing(5)

        name_label = QLabel(f"👤 Name: {username}")
        name_label.setStyleSheet("font-size: 16px;")

        email_label = QLabel(f"📧 Email: {email}")
        email_label.setStyleSheet("font-size: 16px;")

        card_layout.addWidget(name_label)
        card_layout.addWidget(email_label)
        card.setLayout(card_layout)

        return card
