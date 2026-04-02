from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout
from PySide6.QtCore import Qt
from src.views.dashboard.accountsChart import UserAccountsChart
from src.views.dashboard.monthlyUsersChart import MonthlyUsersChart
from src.views.dashboard.userCard import UserCard
from src.components.heading import createTitle


class Dashboard(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    # =============================
    # Main Layout
    # =============================
    def init_ui(self):
        main_layout = QVBoxLayout()
        main_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        main_layout.setSpacing(15)

        main_layout.addWidget(createTitle("Dashboard Overview"))

        # Top Section: User Info
        main_layout.addWidget(UserCard())

        # Middle Section: Charts in 2 columns
        charts_row = QHBoxLayout()
        charts_row.setSpacing(20)

        charts_row.addWidget(MonthlyUsersChart(), 1)
        charts_row.addWidget(UserAccountsChart(), 1)

        main_layout.addLayout(charts_row)

        self.setLayout(main_layout)
