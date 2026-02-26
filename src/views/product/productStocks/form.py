from PySide6.QtWidgets import (
    QWidget,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QGridLayout,
    QComboBox,
    QMessageBox,
    QSizePolicy,
)
from PySide6.QtCore import Qt
from src.services.productStock import (
    addProductStock,
    getProductStock,
    updateProductStock,
)
from src.services.product import getAllProducts
from config.theme import getGlobalStylesheet
from utils.formUtils import setError


class ProductStockForm(QWidget):
    def __init__(self, refresh_callback, stock_id=None):
        super().__init__()
        self.stock_id = stock_id
        self.refresh_callback = refresh_callback

        self.setWindowTitle("Product Stock Form")
        self.setMinimumSize(400, 300)
        self.setStyleSheet(getGlobalStylesheet())
        self.init_ui()

        if self.stock_id:
            self.load_stock()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)

        grid = QGridLayout()
        grid.setVerticalSpacing(8)
        grid.setHorizontalSpacing(10)

        # Product
        grid.addWidget(QLabel("Product:"), 0, 0)
        self.product_combo = QComboBox()
        self.products = getAllProducts()
        self.product_combo.addItem("Select Product", None)
        for p in self.products:
            self.product_combo.addItem(p.name, p.id)
        grid.addWidget(self.product_combo, 0, 1)

        # Quantity
        grid.addWidget(QLabel("Quantity:"), 1, 0)
        self.qty_input, self.qty_error = self.create_input()
        grid.addWidget(self.qty_input, 1, 1)
        grid.addWidget(self.qty_error, 2, 1)

        # Type dropdown
        grid.addWidget(QLabel("Type:"), 3, 0)
        self.type_combo = QComboBox()
        self.type_combo.addItem("In", "in")
        self.type_combo.addItem("Out", "out")
        grid.addWidget(self.type_combo, 3, 1)

        layout.addLayout(grid)

        # Save button
        self.save_btn = QPushButton("Save Stock")
        self.save_btn.setProperty("class", "primary")
        self.save_btn.setMinimumHeight(36)
        self.save_btn.setEnabled(False)
        self.save_btn.clicked.connect(self.save_stock)
        self.save_btn.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed
        )
        layout.addWidget(self.save_btn, alignment=Qt.AlignmentFlag.AlignCenter)

        # Signals
        self.qty_input.textChanged.connect(self.validate_form)
        self.qty_input.textChanged.connect(
            lambda: self.clear_error(self.qty_input, self.qty_error)
        )
        self.product_combo.currentIndexChanged.connect(self.validate_form)
        self.type_combo.currentIndexChanged.connect(self.validate_form)

        self.setLayout(layout)

    def create_input(self):
        input_field = QLineEdit()
        input_field.setMinimumHeight(30)
        error_label = QLabel()
        error_label.setStyleSheet("color: #e74c3c; font-size: 11px;")
        error_label.setVisible(False)
        return input_field, error_label

    def clear_error(self, input_field, error_label):
        setError(False, input_field)
        error_label.setVisible(False)

    def validate_form(self):
        valid = True
        try:
            qty = int(self.qty_input.text().strip())
            if qty < 0:
                raise ValueError
        except ValueError:
            setError(True, self.qty_input)
            self.qty_error.setText("Quantity must be 0 or more")
            self.qty_error.setVisible(True)
            valid = False

        if self.product_combo.currentData() is None:
            valid = False
        if self.type_combo.currentData() not in ("in", "out"):
            valid = False

        self.save_btn.setEnabled(valid)

    def load_stock(self):
        stock = getProductStock(self.stock_id)
        if not stock:
            QMessageBox.warning(self, "Error", "Stock not found.")
            self.close()
            return

        self.qty_input.setText(str(stock.quantity))
        index = self.product_combo.findData(stock.product_id)
        if index >= 0:
            self.product_combo.setCurrentIndex(index)

        if hasattr(stock, "type") and stock.type:
            type_index = self.type_combo.findData(
                stock.type.value if hasattr(stock.type, "value") else stock.type
            )
            if type_index >= 0:
                self.type_combo.setCurrentIndex(type_index)

    def save_stock(self):
        self.validate_form()
        if not self.save_btn.isEnabled():
            QMessageBox.warning(self, "Validation Error", "Please fix errors.")
            return

        product_id = self.product_combo.currentData()
        quantity = int(self.qty_input.text().strip())
        stock_type = self.type_combo.currentData()

        try:
            if self.stock_id:
                updateProductStock(
                    self.stock_id,
                    product_id=product_id,
                    quantity=quantity,
                    type=stock_type,
                )
                QMessageBox.information(self, "Success", "Stock updated successfully.")
            else:
                addProductStock(product_id, quantity, type=stock_type)
                QMessageBox.information(self, "Success", "Stock added successfully.")

            self.refresh_callback()
            self.close()
        except ValueError as e:
            QMessageBox.warning(self, "Error", str(e))
