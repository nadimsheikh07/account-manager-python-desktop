from PySide6.QtWidgets import (
    QWidget,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QGridLayout,
    QComboBox,
    QLineEdit,
    QMessageBox,
    QHBoxLayout,
)
from PySide6.QtCore import Qt
from config.theme import getGlobalStylesheet
from src.services.product import getAllProducts
from src.services.user import getAllUsers  # must exist
from src.services.purchaseOrder import createPurchaseOrder


class PurchaseOrderForm(QWidget):
    def __init__(self, refresh_callback):
        super().__init__()
        self.refresh_callback = refresh_callback
        self.setWindowTitle("Create Purchase Order")
        self.setMinimumSize(600, 450)
        self.setStyleSheet(getGlobalStylesheet())

        self.products = getAllProducts()
        self.suppliers = getAllUsers("supplier")

        self.items = []

        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)

        # Supplier
        layout.addWidget(QLabel("Supplier:"))
        self.supplier_combo = QComboBox()
        self.supplier_combo.addItem("Select Supplier", None)
        for s in self.suppliers:
            self.supplier_combo.addItem(s.name, s.id)
        layout.addWidget(self.supplier_combo)

        # Product section
        self.products_layout = QVBoxLayout()
        layout.addLayout(self.products_layout)

        self.add_product_row()

        add_row_btn = QPushButton("Add Product")
        add_row_btn.clicked.connect(self.add_product_row)
        layout.addWidget(add_row_btn)

        # Total label
        self.total_label = QLabel("Total: 0.00")
        self.total_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        layout.addWidget(self.total_label)

        # Save
        self.save_btn = QPushButton("Create Order")
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
        supplier_id = self.supplier_combo.currentData()
        if not supplier_id:
            QMessageBox.warning(self, "Error", "Select a supplier.")
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
            createPurchaseOrder(supplier_id, order_items)
            QMessageBox.information(self, "Success", "Purchase order created.")
            self.refresh_callback()
            self.close()
        except ValueError as e:
            QMessageBox.warning(self, "Error", str(e))
