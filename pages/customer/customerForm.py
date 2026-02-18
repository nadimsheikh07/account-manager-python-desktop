from PyQt6.QtWidgets import (
    QWidget,
    QLabel,
    QLineEdit,
    QPushButton,
    QGridLayout,
    QVBoxLayout,
    QMessageBox,
)
from PyQt6.QtCore import Qt
from services.customer import add_customer, get_customer, update_customer
from config.theme import get_global_stylesheet


class CustomerForm(QWidget):
    def __init__(self, refresh_callback, customer_id=None):
        """
        customer_id=None -> Create new
        refresh_callback -> function to refresh the list after save
        """
        super().__init__()
        self.customer_id = customer_id
        self.refresh_callback = refresh_callback
        self.setWindowTitle("Customer Form")
        self.setMinimumSize(400, 350)
        self.setStyleSheet(get_global_stylesheet())
        self.init_ui()

        if self.customer_id:
            self.load_customer()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # Title
        title = QLabel("Edit Customer" if self.customer_id else "Add New Customer")
        title.setStyleSheet("font-size: 18px; font-weight: bold;")
        layout.addWidget(title, alignment=Qt.AlignmentFlag.AlignCenter)

        # Grid for inputs
        grid = QGridLayout()
        grid.setVerticalSpacing(12)
        grid.setHorizontalSpacing(10)

        # Name
        grid.addWidget(QLabel("Name:"), 0, 0)
        self.name_input = QLineEdit()
        self.name_input.setMinimumHeight(30)
        grid.addWidget(self.name_input, 0, 1)

        # Email
        grid.addWidget(QLabel("Email:"), 1, 0)
        self.email_input = QLineEdit()
        self.email_input.setMinimumHeight(30)
        grid.addWidget(self.email_input, 1, 1)

        # Contact
        grid.addWidget(QLabel("Contact:"), 2, 0)
        self.contact_input = QLineEdit()
        self.contact_input.setMinimumHeight(30)
        grid.addWidget(self.contact_input, 2, 1)

        # Address
        grid.addWidget(QLabel("Address:"), 3, 0)
        self.address_input = QLineEdit()
        self.address_input.setMinimumHeight(30)
        grid.addWidget(self.address_input, 3, 1)

        layout.addLayout(grid)

        # Save button
        self.save_btn = QPushButton("Save")
        self.save_btn.setProperty("class", "primary")
        self.save_btn.setMinimumHeight(36)
        self.save_btn.clicked.connect(self.save_customer)
        layout.addWidget(self.save_btn, alignment=Qt.AlignmentFlag.AlignCenter)

        self.setLayout(layout)

    def load_customer(self):
        """Load customer data for editing"""
        customer = get_customer(self.customer_id)
        if customer:
            _, name, email, contact, address = customer
            self.name_input.setText(name)
            self.email_input.setText(email)
            self.contact_input.setText(contact)
            self.address_input.setText(address)

    def save_customer(self):
        name = self.name_input.text().strip()
        email = self.email_input.text().strip()
        contact = self.contact_input.text().strip()
        address = self.address_input.text().strip()

        if not (name and email):
            QMessageBox.warning(
                self, "Validation Error", "Name and Email are required."
            )
            return

        try:
            if self.customer_id:
                update_customer(
                    self.customer_id,
                    name=name,
                    email=email,
                    contact=contact,
                    address=address,
                )
                QMessageBox.information(
                    self, "Success", "Customer updated successfully."
                )
            else:
                add_customer(name, email, contact, address)
                QMessageBox.information(self, "Success", "Customer added successfully.")

            self.refresh_callback()
            self.close()
        except ValueError as e:
            QMessageBox.warning(self, "Error", str(e))
