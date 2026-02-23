from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QFrame,
)
from components.sidebar import Sidebar
from pages.auth.login import LoginForm
from pages.auth.dashboard import Dashboard
from pages.customer.index import CustomerList
from pages.customerAccount.index import CustomerAccountList
from services.auth import logout
from config.theme import getGlobalStylesheet
from config.app import APP_NAME


class MainApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(APP_NAME)

        self.setStyleSheet(getGlobalStylesheet())

        self.init_ui()
        self.showMaximized()

    def init_ui(self):
        main_layout = QHBoxLayout(self)

        # ================= Sidebar =================
        self.sidebar = Sidebar()

        # Connect sidebar signals
        self.sidebar.dashboard_clicked.connect(self.show_dashboard)
        self.sidebar.customers_clicked.connect(self.show_customers)
        self.sidebar.accounts_clicked.connect(self.show_customer_accounts)
        self.sidebar.logout_clicked.connect(self.handle_logout)

        # ================= Content =================
        self.content = QFrame()
        self.content_layout = QVBoxLayout(self.content)

        main_layout.addWidget(self.sidebar)
        main_layout.addWidget(self.content)

        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        self.show_dashboard()

    # ==========================================
    # Utility
    # ==========================================
    def clear_content(self):
        while self.content_layout.count():
            child = self.content_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

    # ==========================================
    # Pages
    # ==========================================
    def show_dashboard(self):
        self.clear_content()
        self.sidebar.set_active("Dashboard")
        self.content_layout.addWidget(Dashboard())

    def show_customers(self):
        self.clear_content()
        self.sidebar.set_active("Customers")
        self.content_layout.addWidget(CustomerList())

    def show_customer_accounts(self):
        self.clear_content()
        self.sidebar.set_active("Accounts")
        self.content_layout.addWidget(CustomerAccountList())

    # ==========================================
    # Login Handling
    # ==========================================
    def launch_login(self):
        self.login_window = LoginForm()
        self.login_window.loginSuccessful.connect(self.show_main)
        self.login_window.show()

    def show_main(self):
        self.show()

    def handle_logout(self):
        logout()
        self.hide()
        self.launch_login()
