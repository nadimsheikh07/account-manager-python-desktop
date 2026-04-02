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
from PySide6.QtCore import Qt
from functools import partial
from config.theme import getGlobalStylesheet
from src.controllers.product_controller import ProductController
from src.components.heading import createTitle
from src.views.product.products.form import ProductForm


class ProductList(QWidget):
    def __init__(self):
        super().__init__()
        self.controller = ProductController()
        self.setMinimumSize(700, 400)
        self.setStyleSheet(getGlobalStylesheet())

        self.init_ui()
        self.load_data()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        layout.addWidget(createTitle("Products"))

        top_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText(
            "Search products by name, SKU, or price..."
        )
        self.search_input.textChanged.connect(self.load_data)
        self.add_btn = QPushButton("Add Product")
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
            ["ID", "Name", "SKU", "Price", "Category", "Actions"]
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
        products = self.controller.get_products(self.search_input.text())
        self._populate_table(products)
        self.table.setSortingEnabled(True)

    def _populate_table(self, products):
        self.table.setRowCount(len(products))
        for row, prod in enumerate(products):
            self.table.setItem(row, 0, QTableWidgetItem(str(prod["id"])))
            self.table.setItem(row, 1, QTableWidgetItem(prod["name"]))
            self.table.setItem(row, 2, QTableWidgetItem(prod["sku"] or ""))
            self.table.setItem(row, 3, QTableWidgetItem(f"{prod['price']:.2f}"))
            self.table.setItem(row, 4, QTableWidgetItem(prod["category"]))
            self.table.setCellWidget(row, 5, self._create_action_buttons(prod["id"]))

    def _create_action_buttons(self, product_id):
        edit_btn = QPushButton("Edit")
        edit_btn.setProperty("class", "primary")
        edit_btn.clicked.connect(partial(self.editProduct, product_id))
        delete_btn = QPushButton("Delete")
        delete_btn.setProperty("class", "danger")
        delete_btn.clicked.connect(partial(self.deleteProduct, product_id))

        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(edit_btn)
        layout.addWidget(delete_btn)
        container = QWidget()
        container.setLayout(layout)
        return container

    def open_add_form(self):
        self.form = ProductForm(refresh_callback=self.load_data)
        self.form.show()

    def editProduct(self, product_id):
        self.form = ProductForm(refresh_callback=self.load_data, product_id=product_id)
        self.form.show()

    def deleteProduct(self, product_id):
        confirm = QMessageBox.question(
            self,
            "Confirm Delete",
            "Are you sure you want to delete this product?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if confirm == QMessageBox.StandardButton.Yes:
            _, message = self.controller.delete_product(product_id)
            QMessageBox.information(self, "Deleted", message)
            self.load_data()
