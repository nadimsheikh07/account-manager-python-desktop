from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLineEdit,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QMessageBox,
    QHeaderView,
)
from functools import partial
from config.theme import getGlobalStylesheet
from src.services.productStock import getAllProductStocks, deleteProductStock
from src.components.heading import createTitle
from src.views.product.productStocks.form import ProductStockForm
from PySide6.QtCore import QTimer


class ProductStockList(QWidget):
    def __init__(self):
        super().__init__()
        self.setMinimumSize(700, 400)
        self.setStyleSheet(getGlobalStylesheet())

        self.init_ui()
        # Load data after the event loop starts
        QTimer.singleShot(0, self.load_data)
        self.load_data()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        layout.addWidget(createTitle("Product Stocks"))

        top_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search by product name...")
        self.search_input.textChanged.connect(self.load_data)
        self.add_btn = QPushButton("Add Stock")
        self.add_btn.setProperty("class", "primary")
        self.add_btn.clicked.connect(self.open_add_form)
        self.refresh_btn = QPushButton("Refresh")
        self.refresh_btn.setProperty("class", "secondary")
        self.refresh_btn.clicked.connect(self.load_data)

        top_layout.addWidget(self.search_input)
        top_layout.addWidget(self.add_btn)
        top_layout.addWidget(self.refresh_btn)
        layout.addLayout(top_layout)

        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(
            ["ID", "Product", "Type", "Quantity", "Last Updated", "Actions"]
        )
        self.table.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch
        )
        self.table.setColumnHidden(0, True)
        self.table.setSortingEnabled(True)
        layout.addWidget(self.table)
        layout.setStretchFactor(self.table, 1)

    def load_data(self):
        self.table.setSortingEnabled(False)
        stocks = getAllProductStocks()
        stocks = [self._orm_to_dict(s) for s in stocks]
        query = self.search_input.text().strip().lower()
        if query:
            stocks = [s for s in stocks if query in s["product"].lower()]
        self._populate_table(stocks)
        self.table.setSortingEnabled(True)

    def _orm_to_dict(self, s):
        return {
            "id": s.id,
            "product": s.product.name if s.product else "",
            "type": s.type,
            "quantity": s.quantity,
            "last_updated": (
                s.last_updated.strftime("%Y-%m-%d %H:%M:%S") if s.last_updated else ""
            ),
        }

    def _populate_table(self, stocks):
        self.table.setRowCount(len(stocks))
        for row, s in enumerate(stocks):
            self.table.setItem(row, 0, QTableWidgetItem(str(s["id"])))
            self.table.setItem(row, 1, QTableWidgetItem(s["product"]))
            self.table.setItem(row, 2, QTableWidgetItem(s["type"].name))
            self.table.setItem(row, 3, QTableWidgetItem(str(s["quantity"])))
            self.table.setItem(row, 4, QTableWidgetItem(s["last_updated"]))
            self.table.setCellWidget(row, 5, self._create_action_buttons(s["id"]))

    def _create_action_buttons(self, stock_id):
        edit_btn = QPushButton("Edit")
        edit_btn.setProperty("class", "primary")
        edit_btn.clicked.connect(partial(self.editStock, stock_id))
        delete_btn = QPushButton("Delete")
        delete_btn.setProperty("class", "danger")
        delete_btn.clicked.connect(partial(self.deleteProductStock, stock_id))

        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(edit_btn)
        layout.addWidget(delete_btn)
        container = QWidget()
        container.setLayout(layout)
        return container

    def open_add_form(self):
        self.form = ProductStockForm(refresh_callback=self.load_data)
        self.form.show()

    def editStock(self, stock_id):
        self.form = ProductStockForm(refresh_callback=self.load_data, stock_id=stock_id)
        self.form.show()

    def deleteProductStock(self, stock_id):
        confirm = QMessageBox.question(
            self,
            "Confirm Delete",
            "Are you sure you want to delete this stock?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if confirm == QMessageBox.StandardButton.Yes:
            deleteProductStock(stock_id)
            QMessageBox.information(self, "Deleted", "Stock deleted successfully.")
            self.load_data()
