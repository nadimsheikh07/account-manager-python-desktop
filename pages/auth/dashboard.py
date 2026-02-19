from PySide6.QtWidgets import QWidget, QLabel, QVBoxLayout, QFrame
from PySide6.QtCore import Qt
from services.auth import get_user_from_session
from PySide6.QtCharts import QChart, QChartView, QBarSeries, QBarSet, QBarCategoryAxis
from PySide6.QtGui import QPainter
from services.customer import get_monthly_customer_entries
from datetime import datetime


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

        # Fetch data
        monthly_data = get_monthly_customer_entries()

        # Prepare chart data
        bar_set = QBarSet("New Customers")
        categories = []

        for year_month, total in monthly_data:
            # Convert "YYYY-MM" to datetime
            dt = datetime.strptime(year_month, "%Y-%m")
            formatted_month = dt.strftime(
                "%B %Y"
            )  # Full month name, e.g., "January 2026"
            categories.append(formatted_month)
            bar_set.append(total)

        # Create chart
        series = QBarSeries()
        series.append(bar_set)

        chart = QChart()
        chart.addSeries(series)
        chart.setTitle("Monthly Customer Entries")
        chart.setAnimationOptions(QChart.AnimationOption.SeriesAnimations)

        axis_x = QBarCategoryAxis()
        axis_x.append(categories)  # ✅ Categories are now month names
        chart.addAxis(axis_x, Qt.AlignmentFlag.AlignBottom)
        series.attachAxis(axis_x)

        chart.createDefaultAxes()

        chart_view = QChartView(chart)
        chart_view.setRenderHint(QPainter.RenderHint.Antialiasing)

        layout.addWidget(chart_view)

        self.setLayout(layout)
