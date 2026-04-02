from PySide6.QtWidgets import (
    QWidget,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QComboBox,
    QLineEdit,
    QMessageBox,
    QHBoxLayout,
)
from PySide6.QtCore import Qt
from src.controllers.sale_controller import SaleController
from src.services.product import getAllProducts
from src.services.user import getAllUsers


class SaleOrderForm(QWidget):
    def __init__(self, refresh_callback):
        super().__init__()
        self.refresh_callback = refresh_callback
        self.setWindowTitle("Create Sale Order")
        self.setMinimumSize(600, 450)
        self.setStyleSheet(getGlobalStylesheet())
        self.controller = SaleController()

        self.products = getAllProducts()
        self.users = getAllUsers()

        self.items = []

        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)

        layout.addWidget(QLabel("Customer:"))
        self.user_combo = QComboBox()
        self.user_combo.addItem("Select Customer", None)
        for u in self.users:
            self.user_combo.addItem(u.name, u.id)
        layout.addWidget(self.user_combo)

        self.products_layout = QVBoxLayout()
        layout.addLayout(self.products_layout)

        self.add_product_row()

        add_row_btn = QPushButton("Add Product")
        add_row_btn.clicked.connect(self.add_product_row)
        layout.addWidget(add_row_btn)

        self.total_label = QLabel("Total: 0.00")
        self.total_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        layout.addWidget(self.total_label)

        self.save_btn = QPushButton("Create Sale")
        self.save_btn.setProperty("class", "primary")
        self.save_btn.clicked.connect(self.save_order)
        layout.addWidget(self.save_btn)

    def add_product_row(self):
        row_layout = QHBoxLayout()

        product_combo = QComboBox()
        product_combo.addItem("Select Product", None)
        for p in self.products:
            product_combo.addItem(p.name, p.id)

        qty_input = QLineEdit()
        qty_input.setPlaceholderText("Qty")

        price_input = QLineEdit()
        price_input.setPlaceholderText("Price")

        row_layout.addWidget(product_combo)
        row_layout.addWidget(qty_input)
        row_layout.addWidget(price_input)

        self.products_layout.addLayout(row_layout)

        self.items.append(
            {
                "product": product_combo,
                "quantity": qty_input,
                "price": price_input,
            }
        )

        qty_input.textChanged.connect(self.calculate_total)
        price_input.textChanged.connect(self.calculate_total)

    def calculate_total(self):
        total = 0
        for item in self.items:
            try:
                qty = int(item["quantity"].text())
                price = float(item["price"].text())
                total += qty * price
            except:
                continue
        self.total_label.setText(f"Total: {total:.2f}")

    def save_order(self):
        user_id = self.user_combo.currentData()
        if not user_id:
            QMessageBox.warning(self, "Error", "Select a customer.")
            return

        order_items = []

        for item in self.items:
            product_id = item["product"].currentData()
            if not product_id:
                continue
            try:
                qty = int(item["quantity"].text())
                price = float(item["price"].text())
            except:
                QMessageBox.warning(self, "Error", "Invalid quantity or price.")
                return

            order_items.append(
                {
                    "product_id": product_id,
                    "quantity": qty,
                    "price": price,
                }
            )

        if not order_items:
            QMessageBox.warning(self, "Error", "Add at least one product.")
            return

        try:
            success, message, _ = self.controller.save_order(user_id, order_items)
            if success:
                QMessageBox.information(self, "Success", message)
                self.refresh_callback()
                self.close()
            else:
                QMessageBox.warning(self, "Error", message)
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to save: {str(e)}")
