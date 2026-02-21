from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PySide6.QtCharts import QChart, QChartView, QBarSeries, QBarSet, QBarCategoryAxis
from PySide6.QtCore import Qt
from PySide6.QtGui import QPainter
from services.customer import get_monthly_customer_entries
from datetime import datetime


class MonthlyCustomersChart(QWidget):
    """
    Component showing monthly new customer registrations.
    """

    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        layout.setSpacing(10)

        title = QLabel("Monthly Customer Entries")
        title.setStyleSheet("font-size: 18px; font-weight: bold;")
        layout.addWidget(title)

        chart_view = self.create_chart()
        layout.addWidget(chart_view)

        self.setLayout(layout)

    def create_chart(self) -> QChartView:
        # Fetch monthly customer data
        monthly_data = get_monthly_customer_entries()  # [(YYYY-MM, total), ...]

        bar_set = QBarSet("New Customers")
        categories = []

        for year_month, total in monthly_data:
            dt = datetime.strptime(year_month, "%Y-%m")
            categories.append(dt.strftime("%B %Y"))  # e.g., "January 2026"
            bar_set.append(total)

        series = QBarSeries()
        series.append(bar_set)

        chart = QChart()
        chart.addSeries(series)
        chart.setAnimationOptions(QChart.AnimationOption.SeriesAnimations)
        chart.setTitle("Monthly Customer Entries")

        axis_x = QBarCategoryAxis()
        axis_x.append(categories)
        chart.addAxis(axis_x, Qt.AlignmentFlag.AlignBottom)
        series.attachAxis(axis_x)

        chart.createDefaultAxes()

        chart_view = QChartView(chart)
        chart_view.setRenderHint(QPainter.RenderHint.Antialiasing)
        return chart_view
