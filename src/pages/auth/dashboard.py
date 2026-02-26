from PySide6.QtWidgets import QWidget, QVBoxLayout
from PySide6.QtCore import Qt
from src.services.auth import getUserFromSession
from src.pages.dashboard.accountsChart import UserAccountsChart
from src.pages.dashboard.monthlyUsersChart import MonthlyUsersChart
from src.pages.dashboard.userCard import UserCard
from src.components.heading import createTitle


class Dashboard(QWidget):
    def __init__(self):
        super().__init__()
        self.user = getUserFromSession() or {}
        self.init_ui()

    # =============================
    # Main Layout
    # =============================
    def init_ui(self):
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        layout.setSpacing(15)

        layout.addWidget(createTitle("Dashboard"))

        layout.addWidget(UserCard())  # New users chart
        layout.addWidget(MonthlyUsersChart())  # New users chart
        layout.addWidget(UserAccountsChart())  # new CR/DR chart

        self.setLayout(layout)
