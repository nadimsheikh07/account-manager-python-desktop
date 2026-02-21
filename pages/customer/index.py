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
from config.theme import get_global_stylesheet
from services.customer import get_all_customers, delete_customer
from pages.customer.form import CustomerForm
import pandas as pd
from datetime import datetime
from PySide6.QtWidgets import QFileDialog
from services.customer_account import get_customer_balance  # import balance function
from services.customer_report import export_customer_pdf


class CustomerList(QWidget):
    def __init__(self):
        super().__init__()
        self.setMinimumSize(600, 400)
        self.setStyleSheet(get_global_stylesheet())

        self.init_ui()
        self.load_data()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # ===== Top Bar =====
        top_layout = QHBoxLayout()
        top_layout.setSpacing(10)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText(
            "Search by name, email, contact, address..."
        )
        self.search_input.setMinimumHeight(36)

        self.add_btn = QPushButton("Add Customer")
        self.add_btn.setProperty("class", "primary")
        self.add_btn.setMinimumHeight(36)
        self.add_btn.clicked.connect(self.open_add_form)

        self.export_btn = QPushButton("Export to Excel")
        self.export_btn.setProperty("class", "primary")
        self.export_btn.setMinimumHeight(36)
        self.export_btn.clicked.connect(self.export_to_excel)

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

        all_customers = get_all_customers()
        query = self.search_input.text().lower()

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

            # Get current balance
            balance = get_customer_balance(customer_id)

            row_values = [customer_id, name, email, contact, address, f"{balance:.2f}"]

            for col_idx, value in enumerate(row_values):
                item = QTableWidgetItem(str(value))
                item.setFlags(Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEnabled)
                self.table.setItem(row_idx, col_idx, item)

            # ===== Action Buttons =====
            edit_btn = QPushButton("Edit")
            edit_btn.setProperty("class", "primary")
            edit_btn.clicked.connect(partial(self.edit_customer, customer_id))

            delete_btn = QPushButton("Delete")
            delete_btn.setProperty("class", "danger")
            delete_btn.clicked.connect(partial(self.delete_customer, customer_id))

            pdf_btn = QPushButton("PDF")
            pdf_btn.setProperty("class", "primary")
            pdf_btn.clicked.connect(partial(export_customer_pdf, self, customer_id))

            action_layout = QHBoxLayout()
            action_layout.addWidget(edit_btn)
            action_layout.addWidget(delete_btn)
            action_layout.addWidget(pdf_btn)
            action_layout.setContentsMargins(0, 0, 0, 0)

            action_widget = QWidget()
            action_widget.setLayout(action_layout)

            self.table.setCellWidget(row_idx, 6, action_widget)  # new column index
            self.table.setSortingEnabled(True)

    # =========================
    # Actions
    # =========================
    def open_add_form(self):
        """Open form for creating new customer"""
        self.customer_form = CustomerForm(
            refresh_callback=self.load_data,
            customer_id=None,
        )
        self.customer_form.show()

    def edit_customer(self, customer_id):
        """Open form for editing"""
        self.customer_form = CustomerForm(
            refresh_callback=self.load_data,
            customer_id=customer_id,
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

    def export_to_excel(self):
        all_customers = get_all_customers()
        if not all_customers:
            QMessageBox.warning(self, "No Data", "There are no customers to export.")
            return

        # Add balance for each customer
        export_rows = []
        for c in all_customers:
            customer_id, name, email, contact, address, date = c
            balance = get_customer_balance(customer_id)
            export_rows.append(
                {
                    "ID": customer_id,
                    "Name": name,
                    "Email": email,
                    "Contact": contact,
                    "Address": address,
                    "Date": date,
                    "Balance": balance,
                }
            )

        df = pd.DataFrame(export_rows)

        now = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save Excel File",
            f"customers_{now}.xlsx",
            "Excel Files (*.xlsx)",
        )
        if file_path:
            df.to_excel(file_path, index=False)
            QMessageBox.information(
                self, "Exported", f"Customers exported successfully to:\n{file_path}"
            )
