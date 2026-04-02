from PySide6.QtWidgets import (
    QWidget,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QGridLayout,
    QMessageBox,
    QSizePolicy,
)
from PySide6.QtCore import Qt
from src.controllers.category_controller import CategoryController
from config.theme import getGlobalStylesheet
from utils.formUtils import setError


class CategoryForm(QWidget):
    def __init__(self, refresh_callback, category_id=None):
        super().__init__()
        self.category_id = category_id
        self.refresh_callback = refresh_callback
        self.controller = CategoryController()

        self.setWindowTitle("Category Form")
        self.setMinimumSize(400, 250)
        self.setStyleSheet(getGlobalStylesheet())
        self.init_ui()

        if self.category_id:
            self.load_category()

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

        # Description
        grid.addWidget(QLabel("Description:"), 2, 0)
        self.desc_input, self.desc_error = self.create_input()
        grid.addWidget(self.desc_input, 2, 1)
        grid.addWidget(self.desc_error, 3, 1)

        layout.addLayout(grid)

        self.save_btn = QPushButton("Save Category")
        self.save_btn.setProperty("class", "primary")
        self.save_btn.setMinimumHeight(36)
        self.save_btn.setEnabled(False)
        self.save_btn.clicked.connect(self.save_category)
        self.save_btn.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed
        )
        layout.addWidget(self.save_btn, alignment=Qt.AlignmentFlag.AlignCenter)

        for input_field, error_label in [
            (self.name_input, self.name_error),
            (self.desc_input, self.desc_error),
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
        self.save_btn.setEnabled(valid)

    def load_category(self):
        category = self.controller.get_category_by_id(self.category_id)
        if not category:
            QMessageBox.warning(self, "Error", "Category not found.")
            self.close()
            return
        self.name_input.setText(category.name or "")
        self.desc_input.setText(category.description or "")

    def save_category(self):
        name = self.name_input.text().strip()
        description = self.desc_input.text().strip()

        success, message, errors = self.controller.save_category(
            self.category_id, name=name, description=description
        )

        if not success:
            if errors:
                for field, error in errors.items():
                    if field == "name":
                        setError(True, self.name_input)
                        self.name_error.setText(error)
                        self.name_error.setVisible(True)
            QMessageBox.warning(self, "Error", message)
            return

        QMessageBox.information(self, "Success", message)
        self.refresh_callback()
        self.close()
