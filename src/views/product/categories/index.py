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
from src.controllers.category_controller import CategoryController
from src.components.heading import createTitle
from src.views.product.categories.form import CategoryForm


class CategoryList(QWidget):
    def __init__(self):
        super().__init__()
        self.setMinimumSize(600, 400)
        self.setStyleSheet(getGlobalStylesheet())

        self.controller = CategoryController()
        self.init_ui()
        self.load_data()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        layout.addWidget(createTitle("Categories"))

        top_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText(
            "Search categories by name or description..."
        )
        self.search_input.textChanged.connect(self.load_data)
        self.add_btn = QPushButton("Add Category")
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
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["ID", "Name", "Description", "Actions"])
        self.table.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch
        )
        self.table.setColumnHidden(0, True)
        self.table.setSortingEnabled(True)
        layout.addWidget(self.table)
        layout.setStretchFactor(self.table, 1)

    def load_data(self):
        self.table.setSortingEnabled(False)
        query = self.search_input.text().strip().lower()
        categories = self.controller.get_categories(query)
        self._populate_table(categories)
        self.table.setSortingEnabled(True)

    def _populate_table(self, categories):
        self.table.setRowCount(len(categories))
        for row, cat in enumerate(categories):
            self.table.setItem(row, 0, QTableWidgetItem(str(cat["id"])))
            self.table.setItem(row, 1, QTableWidgetItem(cat["name"]))
            self.table.setItem(row, 2, QTableWidgetItem(cat["description"] or ""))
            self.table.setCellWidget(row, 3, self._create_action_buttons(cat["id"]))

    def _create_action_buttons(self, category_id):
        edit_btn = QPushButton("Edit")
        edit_btn.setProperty("class", "primary")
        edit_btn.clicked.connect(partial(self.editCategory, category_id))
        delete_btn = QPushButton("Delete")
        delete_btn.setProperty("class", "danger")
        delete_btn.clicked.connect(partial(self.deleteCategory, category_id))

        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(edit_btn)
        layout.addWidget(delete_btn)
        container = QWidget()
        container.setLayout(layout)
        return container

    def open_add_form(self):
        self.form = CategoryForm(refresh_callback=self.load_data)
        self.form.show()

    def editCategory(self, category_id):
        self.form = CategoryForm(
            refresh_callback=self.load_data, category_id=category_id
        )
        self.form.show()

    def deleteCategory(self, category_id):
        confirm = QMessageBox.question(
            self,
            "Confirm Delete",
            "Are you sure you want to delete this category?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if confirm == QMessageBox.StandardButton.Yes:
            success, message = self.controller.delete_category(category_id)
            if success:
                QMessageBox.information(self, "Deleted", message)
                self.load_data()
            else:
                QMessageBox.warning(self, "Error", message)
