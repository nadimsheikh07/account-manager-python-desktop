from PyQt6.QtWidgets import (
    QWidget,
    QLabel,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QFrame,
)
from PyQt6.QtCore import Qt

from pages.auth.login import LoginForm
from pages.customer.customerList import CustomerList
from pages.customer.customerForm import CustomerForm
from services.auth import logout


class MainApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Main App")
        self.setGeometry(200, 200, 1000, 600)

        self.init_ui()

    def init_ui(self):
        main_layout = QHBoxLayout(self)

        # ========== Sidebar ==========
        self.sidebar = QFrame()
        self.sidebar.setFixedWidth(200)
        self.sidebar.setStyleSheet(
            """
            QFrame { background-color: #2c3e50; }
            QPushButton {
                background-color: transparent;
                color: white;
                padding: 10px;
                text-align: left;
                border: none;
            }
            QPushButton:hover { background-color: #34495e; }
        """
        )

        sidebar_layout = QVBoxLayout()
        sidebar_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        self.dashboard_btn = QPushButton("Dashboard")
        self.customer_btn = QPushButton("Customers")
        self.logout_btn = QPushButton("Logout")

        self.dashboard_btn.clicked.connect(self.show_dashboard)
        self.customer_btn.clicked.connect(self.show_customers)
        self.logout_btn.clicked.connect(self.handle_logout)

        sidebar_layout.addWidget(self.dashboard_btn)
        sidebar_layout.addWidget(self.customer_btn)
        sidebar_layout.addStretch()
        sidebar_layout.addWidget(self.logout_btn)

        self.sidebar.setLayout(sidebar_layout)

        # ========== Content Area ==========
        self.content = QFrame()
        self.content_layout = QVBoxLayout()
        self.content.setLayout(self.content_layout)

        main_layout.addWidget(self.sidebar)
        main_layout.addWidget(self.content)

        self.setLayout(main_layout)

        self.show_dashboard()

    # =====================
    # Utility
    # =====================

    def clear_content(self):
        while self.content_layout.count():
            child = self.content_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

    # =====================
    # Pages
    # =====================

    def show_dashboard(self):
        self.clear_content()
        label = QLabel("Welcome! You are logged in.")
        label.setStyleSheet("font-size: 18px;")
        self.content_layout.addWidget(label)

    def show_customers(self):
        self.clear_content()

        self.customer_page = CustomerList(on_edit_callback=self.open_edit_customer)

        self.content_layout.addWidget(self.customer_page)

    def open_edit_customer(self, customer_id):
        self.customer_form = CustomerForm(
            refresh_callback=self.customer_page.load_data,
            customer_id=customer_id,
        )
        self.customer_form.show()

    # =====================
    # Login Handling
    # =====================

    def launch_login(self):
        self.login_window = LoginForm(on_login_success=self.show_main)
        self.login_window.show()

    def show_main(self):
        self.show()

    def handle_logout(self):
        logout()
        self.hide()
        self.launch_login()
