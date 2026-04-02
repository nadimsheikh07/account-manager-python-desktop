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
from src.controllers.product_controller import ProductController
from config.theme import getGlobalStylesheet
from utils.formUtils import setError


class ProductForm(QWidget):
    def __init__(self, refresh_callback, product_id=None):
        super().__init__()
        self.product_id = product_id
        self.refresh_callback = refresh_callback
        self.controller = ProductController()

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
        self.categories = self.controller.get_categories()
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
        self.category_combo.currentIndexChanged.connect(self.validate_form)

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
        is_valid, errors, _ = self.controller.validate_product_form(
            name=self.name_input.text(),
            price_text=self.price_input.text(),
            category_id=self.category_combo.currentData(),
        )

        if "name" in errors:
            setError(True, self.name_input)
            self.name_error.setText(errors["name"])
            self.name_error.setVisible(True)
        else:
            self.clear_error(self.name_input, self.name_error)

        if "price" in errors:
            setError(True, self.price_input)
            self.price_error.setText(errors["price"])
            self.price_error.setVisible(True)
        else:
            self.clear_error(self.price_input, self.price_error)

        self.save_btn.setEnabled(is_valid)

    def load_product(self):
        product = self.controller.get_product_by_id(self.product_id)
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
        success, message, errors = self.controller.save_product(
            product_id=self.product_id,
            name=self.name_input.text(),
            sku=self.sku_input.text(),
            price_text=self.price_input.text(),
            category_id=self.category_combo.currentData(),
        )

        if not success:
            if errors:
                QMessageBox.warning(self, "Validation Error", message)
            else:
                QMessageBox.warning(self, "Error", message)
            return

        QMessageBox.information(self, "Success", message)
        self.refresh_callback()
        self.close()
