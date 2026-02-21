from PySide6.QtWidgets import QWidget, QLabel, QVBoxLayout, QFrame
from PySide6.QtCore import Qt
from services.auth import get_user_from_session
from pages.dashboard.accounts_chart import CustomerAccountsChart
from pages.dashboard.monthly_customers_chart import MonthlyCustomersChart
from pages.dashboard.user_card import UserCard

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
        
        layout.addWidget(UserCard())  # New customers chart
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
