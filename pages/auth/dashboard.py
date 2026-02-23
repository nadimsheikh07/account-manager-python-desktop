from PySide6.QtWidgets import QWidget, QVBoxLayout
from PySide6.QtCore import Qt
from services.auth import getUserFromSession
from pages.dashboard.accountsChart import CustomerAccountsChart
from pages.dashboard.monthlyCustomersChart import MonthlyCustomersChart
from pages.dashboard.userCard import UserCard
from components.heading import createTitle


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

        layout.addWidget(UserCard())  # New customers chart
        layout.addWidget(MonthlyCustomersChart())  # New customers chart
        layout.addWidget(CustomerAccountsChart())  # new CR/DR chart

        self.setLayout(layout)
