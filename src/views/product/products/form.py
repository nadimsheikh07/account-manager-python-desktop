from PySide6.QtWidgets import (
    QWidget,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QGridLayout,
    QMessageBox,
    QComboBox,
    QSizePolicy,
)
from PySide6.QtCore import Qt
from src.services.product import addProduct, getProduct, updateProduct
from src.services.category import getAllCategories
from config.theme import getGlobalStylesheet
from utils.formUtils import setError


class ProductForm(QWidget):
    def __init__(self, refresh_callback, product_id=None):
        super().__init__()
        self.product_id = product_id
        self.refresh_callback = refresh_callback

        self.setWindowTitle("Product Form")
        self.setMinimumSize(400, 300)
        self.setStyleSheet(getGlobalStylesheet())
        self.init_ui()

        if self.product_id:
            self.load_product()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)

        grid = QGridLayout()
        grid.setVerticalSpacing(8)
        grid.setHorizontalSpacing(10)

        # Name
        grid.addWidget(QLabel("Name:"), 0, 0)
        self.name_input, self.name_error = self.create_input()
        grid.addWidget(self.name_input, 0, 1)
        grid.addWidget(self.name_error, 1, 1)

        # SKU
        grid.addWidget(QLabel("SKU:"), 2, 0)
        self.sku_input, self.sku_error = self.create_input()
        grid.addWidget(self.sku_input, 2, 1)
        grid.addWidget(self.sku_error, 3, 1)

        # Price
        grid.addWidget(QLabel("Price:"), 4, 0)
        self.price_input, self.price_error = self.create_input()
        grid.addWidget(self.price_input, 4, 1)
        grid.addWidget(self.price_error, 5, 1)

        # Category
        grid.addWidget(QLabel("Category:"), 6, 0)
        self.category_combo = QComboBox()
        self.categories = getAllCategories()
        self.category_combo.addItem("Select Category", None)
        for c in self.categories:
            self.category_combo.addItem(c.name, c.id)
        grid.addWidget(self.category_combo, 6, 1)

        layout.addLayout(grid)

        self.save_btn = QPushButton("Save Product")
        self.save_btn.setProperty("class", "primary")
        self.save_btn.setMinimumHeight(36)
        self.save_btn.setEnabled(False)
        self.save_btn.clicked.connect(self.save_product)
        self.save_btn.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed
        )
        layout.addWidget(self.save_btn, alignment=Qt.AlignmentFlag.AlignCenter)

        for input_field, error_label in [
            (self.name_input, self.name_error),
            (self.sku_input, self.sku_error),
            (self.price_input, self.price_error),
        ]:
            input_field.textChanged.connect(self.validate_form)
            input_field.textChanged.connect(
                lambda _, f=input_field, e=error_label: self.clear_error(f, e)
            )

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
        name = self.name_input.text().strip()
        if not name:
            setError(True, self.name_input)
            self.name_error.setText("Name is required")
            self.name_error.setVisible(True)
            valid = False

        price_text = self.price_input.text().strip()
        try:
            price = float(price_text)
            if price < 0:
                raise ValueError
        except ValueError:
            setError(True, self.price_input)
            self.price_error.setText("Invalid price")
            self.price_error.setVisible(True)
            valid = False

        cat_id = self.category_combo.currentData()
        if not cat_id:
            valid = False

        self.save_btn.setEnabled(valid)

    def load_product(self):
        product = getProduct(self.product_id)
        if not product:
            QMessageBox.warning(self, "Error", "Product not found.")
            self.close()
            return
        self.name_input.setText(product.name or "")
        self.sku_input.setText(product.sku or "")
        self.price_input.setText(str(product.price))
        index = self.category_combo.findData(product.category_id)
        if index >= 0:
            self.category_combo.setCurrentIndex(index)

    def save_product(self):
        self.validate_form()
        if not self.save_btn.isEnabled():
            QMessageBox.warning(self, "Validation Error", "Please fix errors.")
            return
        name = self.name_input.text().strip()
        sku = self.sku_input.text().strip() or None
        price = float(self.price_input.text().strip())
        category_id = self.category_combo.currentData()
        try:
            if self.product_id:
                updateProduct(
                    self.product_id,
                    name=name,
                    sku=sku,
                    price=price,
                    category_id=category_id,
                )
                QMessageBox.information(
                    self, "Success", "Product updated successfully."
                )
            else:
                addProduct(name, category_id, price, sku)
                QMessageBox.information(self, "Success", "Product added successfully.")
            self.refresh_callback()
            self.close()
        except ValueError as e:
            QMessageBox.warning(self, "Error", str(e))
