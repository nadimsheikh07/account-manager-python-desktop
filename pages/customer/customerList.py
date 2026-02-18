from PyQt6.QtWidgets import (
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
from PyQt6.QtCore import Qt
from functools import partial

from services.customer import init_customer_table, get_all_customers, delete_customer


class CustomerList(QWidget):
    def __init__(self, on_edit_callback):
        """
        on_edit_callback(customer_id or None)
        """
        super().__init__()
        self.on_edit_callback = on_edit_callback
        self.setMinimumSize(600, 400)

        init_customer_table()
        self.init_ui()
        self.load_data()

    def init_ui(self):
        layout = QVBoxLayout()

        # ===== Top Bar (Search + Add Button) =====
        top_layout = QHBoxLayout()

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText(
            "Search by name, email, contact, address..."
        )
        self.search_input.textChanged.connect(self.load_data)

        self.add_btn = QPushButton("Add Customer")
        self.add_btn.clicked.connect(self.open_add_form)

        top_layout.addWidget(self.search_input)
        top_layout.addWidget(self.add_btn)

        layout.addLayout(top_layout)

        # ===== Table =====
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(
            ["ID", "Name", "Email", "Contact", "Address", "Actions"]
        )
        self.table.setSortingEnabled(True)
        self.table.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch
        )

        layout.addWidget(self.table)

        self.setLayout(layout)

    # =========================
    # Load Data
    # =========================
    def load_data(self):
        all_customers = get_all_customers()
        query = self.search_input.text().lower()

        filtered = [
            c
            for c in all_customers
            if query in str(c[1]).lower()
            or query in str(c[2]).lower()
            or query in str(c[3]).lower()
            or query in str(c[4]).lower()
        ]

        self.table.setRowCount(len(filtered))

        for row_idx, customer in enumerate(filtered):
            for col_idx, value in enumerate(customer):
                item = QTableWidgetItem(str(value))
                item.setFlags(Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEnabled)
                self.table.setItem(row_idx, col_idx, item)

            # ===== Actions Column =====
            edit_btn = QPushButton("Edit")
            edit_btn.clicked.connect(partial(self.edit_customer, customer[0]))

            delete_btn = QPushButton("Delete")
            delete_btn.clicked.connect(partial(self.delete_customer, customer[0]))

            action_layout = QHBoxLayout()
            action_layout.addWidget(edit_btn)
            action_layout.addWidget(delete_btn)
            action_layout.setContentsMargins(0, 0, 0, 0)

            action_widget = QWidget()
            action_widget.setLayout(action_layout)

            self.table.setCellWidget(row_idx, 5, action_widget)

    # =========================
    # Actions
    # =========================
    def open_add_form(self):
        """Open form for creating new customer"""
        self.on_edit_callback(None)

    def edit_customer(self, customer_id):
        """Open form for editing"""
        self.on_edit_callback(customer_id)

    def delete_customer(self, customer_id):
        confirm = QMessageBox.question(
            self,
            "Confirm Delete",
            "Are you sure you want to delete this customer?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )

        if confirm == QMessageBox.StandardButton.Yes:
            delete_customer(customer_id)
            QMessageBox.information(self, "Deleted", "Customer deleted successfully.")
            self.load_data()
