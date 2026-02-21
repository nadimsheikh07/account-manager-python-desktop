from PySide6.QtWidgets import QWidget, QLabel, QVBoxLayout, QFrame
from PySide6.QtCore import Qt
from PySide6.QtCharts import QChart, QChartView, QBarSeries, QBarSet, QBarCategoryAxis
from PySide6.QtGui import QPainter
from services.auth import get_user_from_session
from services.customer import get_monthly_customer_entries
from datetime import datetime


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
        layout.addWidget(self.create_monthly_chart())

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

    # =============================
    # Monthly Customers Chart Component
    # =============================
    def create_monthly_chart(self) -> QChartView:
        monthly_data = get_monthly_customer_entries()

        bar_set = QBarSet("New Customers")
        categories = []

        for year_month, total in monthly_data:
            dt = datetime.strptime(year_month, "%Y-%m")
            categories.append(dt.strftime("%B %Y"))
            bar_set.append(total)

        series = QBarSeries()
        series.append(bar_set)

        chart = QChart()
        chart.addSeries(series)
        chart.setTitle("Monthly Customer Entries")
        chart.setAnimationOptions(QChart.AnimationOption.SeriesAnimations)

        axis_x = QBarCategoryAxis()
        axis_x.append(categories)
        chart.addAxis(axis_x, Qt.AlignmentFlag.AlignBottom)
        series.attachAxis(axis_x)

        chart.createDefaultAxes()

        chart_view = QChartView(chart)
        chart_view.setRenderHint(QPainter.RenderHint.Antialiasing)
        return chart_view
