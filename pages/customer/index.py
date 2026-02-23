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
from services.customer import getAllCustomers, delete_customer, exportToExcel
from pages.customer.form import CustomerForm
from services.customerAccount import getCustomerBalance
from services.customerReport import exportCustomerPdf
from components.heading import createTitle


class CustomerList(QWidget):
    def __init__(self):
        super().__init__()
        self.setMinimumSize(600, 400)
        self.setStyleSheet(getGlobalStylesheet())

        self.init_ui()
        self.load_data()

    # =========================
    # UI Setup
    # =========================
    def init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        layout.addWidget(createTitle("Customers"))

        # ===== Top Bar =====
        top_layout = QHBoxLayout()
        top_layout.setSpacing(10)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText(
            "Search by name, email, contact, address, or date..."
        )
        self.search_input.setMinimumHeight(36)
        self.search_input.textChanged.connect(self.load_data)

        self.add_btn = QPushButton("Add Customer")
        self.add_btn.setProperty("class", "primary")
        self.add_btn.setMinimumHeight(36)
        self.add_btn.clicked.connect(self.open_add_form)

        self.export_btn = QPushButton("Export to Excel")
        self.export_btn.setProperty("class", "primary")
        self.export_btn.setMinimumHeight(36)
        self.export_btn.clicked.connect(lambda: exportToExcel(self))

        top_layout.addWidget(self.search_input)
        top_layout.addWidget(self.add_btn)
        top_layout.addWidget(self.export_btn)
        layout.addLayout(top_layout)

        # ===== Table =====
        self.table = QTableWidget()
        self.table.setColumnCount(8)
        self.table.setHorizontalHeaderLabels(
            ["ID", "Name", "Email", "Contact", "Address", "Date", "Balance", "Actions"]
        )
        self.table.setSortingEnabled(True)
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch
        )

        # Hide ID column
        self.table.setColumnHidden(0, True)

        layout.addWidget(self.table)
        self.setLayout(layout)

    # =========================
    # Load Data
    # =========================
    def load_data(self):
        self.table.setSortingEnabled(False)
        all_customers = getAllCustomers()
        query = self.search_input.text().lower()

        # Filter by name, email, contact, address, or date
        filtered = [
            c
            for c in all_customers
            if query in str(c[1]).lower()
            or query in str(c[2]).lower()
            or query in str(c[3]).lower()
            or query in str(c[4]).lower()
            or query in str(c[5]).lower()
        ]

        self.table.setRowCount(len(filtered))

        for row_idx, customer in enumerate(filtered):
            customer_id, name, email, contact, address, date = customer
            balance = getCustomerBalance(customer_id)

            row_values = [
                customer_id,
                name,
                email,
                contact,
                address,
                date,
                f"{balance:.2f}",
            ]

            for col_idx, value in enumerate(row_values):
                item = QTableWidgetItem(str(value))
                item.setFlags(Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEnabled)
                self.table.setItem(row_idx, col_idx, item)

            # ===== Action Buttons (last column) =====
            edit_btn = QPushButton("Edit")
            edit_btn.setProperty("class", "primary")
            edit_btn.clicked.connect(partial(self.edit_customer, customer_id))

            delete_btn = QPushButton("Delete")
            delete_btn.setProperty("class", "danger")
            delete_btn.clicked.connect(partial(self.delete_customer, customer_id))

            pdf_btn = QPushButton("PDF")
            pdf_btn.setProperty("class", "primary")
            pdf_btn.clicked.connect(partial(exportCustomerPdf, self, customer_id))

            action_layout = QHBoxLayout()
            action_layout.addWidget(edit_btn)
            action_layout.addWidget(delete_btn)
            action_layout.addWidget(pdf_btn)
            action_layout.setContentsMargins(0, 0, 0, 0)

            action_widget = QWidget()
            action_widget.setLayout(action_layout)
            self.table.setCellWidget(row_idx, 7, action_widget)  # last column

        self.table.setSortingEnabled(True)

    # =========================
    # Actions
    # =========================
    def open_add_form(self):
        self.customer_form = CustomerForm(
            refresh_callback=self.load_data, customer_id=None
        )
        self.customer_form.show()

    def edit_customer(self, customer_id):
        self.customer_form = CustomerForm(
            refresh_callback=self.load_data, customer_id=customer_id
        )
        self.customer_form.show()

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
