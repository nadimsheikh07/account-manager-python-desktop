from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLineEdit,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QMessageBox,
)
from PyQt6.QtCore import Qt
from services.customer import init_customer_table, get_all_customers, delete_customer


class CustomerList(QWidget):
    def __init__(self, on_edit_callback):
        """
        on_edit_callback: function to open CustomerForm for editing
        """
        super().__init__()
        self.on_edit_callback = on_edit_callback
        self.setWindowTitle("Customer List")
        self.setMinimumSize(600, 400)
        init_customer_table()
        self.init_ui()
        self.load_data()

    def init_ui(self):
        layout = QVBoxLayout()

        # Search bar
        search_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText(
            "Search by name, email, contact, address..."
        )
        self.search_input.textChanged.connect(self.load_data)
        search_layout.addWidget(self.search_input)
        layout.addLayout(search_layout)

        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(
            ["ID", "Name", "Email", "Contact", "Address", "Actions"]
        )
        self.table.setSortingEnabled(True)
        layout.addWidget(self.table)

        self.setLayout(layout)

    def load_data(self):
        """Load customers into table, with search filter"""
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

            # Actions column: Delete & Edit
            edit_btn = QPushButton("Edit")
            edit_btn.clicked.connect(
                lambda checked, c_id=customer[0]: self.edit_customer(c_id)
            )
            delete_btn = QPushButton("Delete")
            delete_btn.clicked.connect(
                lambda checked, c_id=customer[0]: self.delete_customer(c_id)
            )

            action_layout = QHBoxLayout()
            action_layout.addWidget(edit_btn)
            action_layout.addWidget(delete_btn)
            action_widget = QWidget()
            action_widget.setLayout(action_layout)
            self.table.setCellWidget(row_idx, 5, action_widget)

        self.table.resizeColumnsToContents()

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

    def edit_customer(self, customer_id):
        self.on_edit_callback(customer_id)
