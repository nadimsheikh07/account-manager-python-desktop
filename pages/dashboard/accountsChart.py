from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PySide6.QtCharts import QChart, QChartView, QBarSeries, QBarSet, QBarCategoryAxis
from PySide6.QtCore import Qt
from PySide6.QtGui import QPainter
from services.userAccount import getMonthlyAccountSummary  # custom function


class UserAccountsChart(QWidget):
    """
    Chart showing monthly Credit (CR) and Debit (DR) totals.
    """

    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        layout.setSpacing(10)

        title = QLabel("Monthly User Accounts")
        title.setStyleSheet("font-size: 18px; font-weight: bold;")
        layout.addWidget(title)

        chart_view = self.create_chart()
        layout.addWidget(chart_view)

        self.setLayout(layout)

    def create_chart(self) -> QChartView:
        # Fetch monthly account summary from DB
        # Expected format: [(YYYY-MM, total_cr, total_dr), ...]
        monthly_data = getMonthlyAccountSummary()

        cr_set = QBarSet("Credit (CR)")
        dr_set = QBarSet("Debit (DR)")
        categories = []

        for year_month, total_cr, total_dr in monthly_data:
            categories.append(year_month)  # e.g., "2026-01"
            cr_set.append(total_cr)
            dr_set.append(total_dr)

        series = QBarSeries()
        series.append(cr_set)
        series.append(dr_set)

        chart = QChart()
        chart.addSeries(series)
        chart.setTitle("Monthly Credits vs Debits")
        chart.setAnimationOptions(QChart.AnimationOption.SeriesAnimations)

        axis_x = QBarCategoryAxis()
        axis_x.append(categories)
        chart.addAxis(axis_x, Qt.AlignmentFlag.AlignBottom)
        series.attachAxis(axis_x)

        chart.createDefaultAxes()

        chart_view = QChartView(chart)
        chart_view.setRenderHint(QPainter.RenderHint.Antialiasing)
        return chart_view
