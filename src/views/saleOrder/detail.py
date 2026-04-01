from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
    QMessageBox,
)
from config.theme import getGlobalStylesheet
from src.components.heading import createTitle
from src.services.saleOrder import getSaleOrder


class SaleOrderDetail(QWidget):
    def __init__(self, order_id):
        super().__init__()
        self.order_id = order_id
        self.setWindowTitle(f"Sale Order #{order_id}")
        self.setMinimumSize(760, 460)
        self.setStyleSheet(getGlobalStylesheet())

        self.init_ui()
        self.load_data()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)

        layout.addWidget(createTitle("Sale Order Detail"))

        self.summary_label = QLabel("")
        layout.addWidget(self.summary_label)

        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(
            ["Product", "Quantity", "Price", "Subtotal", "Product ID"]
        )
        self.table.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch
        )
        self.table.setColumnHidden(4, True)
        layout.addWidget(self.table)

    def load_data(self):
        order = getSaleOrder(self.order_id)
        if not order:
            QMessageBox.warning(self, "Not Found", "Sale order not found.")
            self.close()
            return

        customer_name = order.user.name if order.user else "Unknown"
        order_date = order.date.strftime("%Y-%m-%d %H:%M:%S") if order.date else "-"
        self.summary_label.setText(
            f"Customer: {customer_name}   |   Date: {order_date}   |   Total: {order.total_amount:.2f}"
        )

        items = order.products or []
        self.table.setRowCount(len(items))

        for row, item in enumerate(items):
            product_name = item.product.name if item.product else "Unknown Product"
            subtotal = item.quantity * item.price

            self.table.setItem(row, 0, QTableWidgetItem(product_name))
            self.table.setItem(row, 1, QTableWidgetItem(str(item.quantity)))
            self.table.setItem(row, 2, QTableWidgetItem(f"{item.price:.2f}"))
            self.table.setItem(row, 3, QTableWidgetItem(f"{subtotal:.2f}"))
            self.table.setItem(row, 4, QTableWidgetItem(str(item.product_id)))
