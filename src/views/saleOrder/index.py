from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QMessageBox,
    QHeaderView,
)
from functools import partial
from PySide6.QtCore import QTimer
from src.controllers.sale_controller import SaleController
from src.components.heading import createTitle
from src.views.saleOrder.form import SaleOrderForm
from src.views.saleOrder.detail import SaleOrderDetail
from config.theme import getGlobalStylesheet


class SaleOrderList(QWidget):
    def __init__(self):
        super().__init__()
        self.setMinimumSize(800, 450)
        self.setStyleSheet(getGlobalStylesheet())
        self.controller = SaleController()

        self.init_ui()
        QTimer.singleShot(0, self.load_data)

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        layout.addWidget(createTitle("Sale Orders"))

        top_layout = QHBoxLayout()

        self.add_btn = QPushButton("Create Sale Order")
        self.add_btn.setProperty("class", "primary")
        self.add_btn.clicked.connect(self.open_add_form)

        self.refresh_btn = QPushButton("Refresh")
        self.refresh_btn.setProperty("class", "secondary")
        self.refresh_btn.clicked.connect(self.load_data)

        top_layout.addWidget(self.add_btn)
        top_layout.addWidget(self.refresh_btn)
        layout.addLayout(top_layout)

        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(
            ["ID", "Customer", "Total Amount", "Date", "Actions"]
        )
        self.table.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch
        )
        self.table.setColumnHidden(0, True)
        layout.addWidget(self.table)

    def load_data(self):
        orders = self.controller.get_all_orders()
        self.table.setRowCount(len(orders))

        for row, order in enumerate(orders):
            self.table.setItem(row, 0, QTableWidgetItem(str(order.id)))
            self.table.setItem(
                row,
                1,
                QTableWidgetItem(order.user.name if order.user else ""),
            )
            self.table.setItem(row, 2, QTableWidgetItem(f"{order.total_amount:.2f}"))
            self.table.setItem(
                row,
                3,
                QTableWidgetItem(
                    order.date.strftime("%Y-%m-%d %H:%M:%S") if order.date else ""
                ),
            )
            self.table.setCellWidget(row, 4, self._create_action_buttons(order.id))

    def _create_action_buttons(self, order_id):
        view_btn = QPushButton("View")
        view_btn.setProperty("class", "secondary")
        view_btn.clicked.connect(partial(self.open_detail_view, order_id))

        delete_btn = QPushButton("Delete")
        delete_btn.setProperty("class", "danger")
        delete_btn.clicked.connect(partial(self.delete_order, order_id))

        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(view_btn)
        layout.addWidget(delete_btn)

        container = QWidget()
        container.setLayout(layout)
        return container

    def open_add_form(self):
        self.form = SaleOrderForm(refresh_callback=self.load_data)
        self.form.show()

    def open_detail_view(self, order_id):
        self.detail_view = SaleOrderDetail(order_id)
        self.detail_view.show()

    def delete_order(self, order_id):
        confirm = QMessageBox.question(
            self,
            "Confirm Delete",
            "Are you sure you want to delete this sale order?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if confirm == QMessageBox.StandardButton.Yes:
            success, message = self.controller.delete_order(order_id)
            if success:
                QMessageBox.information(self, "Deleted", message)
                self.load_data()
            else:
                QMessageBox.warning(self, "Error", message)
