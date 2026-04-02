from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QFrame,
)
from src.components.sidebar import Sidebar
from src.views.auth.login import LoginForm
from src.views.auth.dashboard import Dashboard
from src.views.product import InventoryPanel
from src.views.user.index import UserList
from src.views.purchaseOrder.index import PurchaseOrderList
from src.views.saleOrder.index import SaleOrderList
from src.views.userAccount.index import UserAccountList
from src.controllers.auth_controller import AuthController
from config.theme import getGlobalStylesheet
from config.app import APP_NAME


class MainApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(APP_NAME)

        self.setStyleSheet(getGlobalStylesheet())
        self.auth_controller = AuthController()

        self.init_ui()
        self.showMaximized()

    def init_ui(self):
        main_layout = QHBoxLayout(self)

        # ================= Sidebar =================
        self.sidebar = Sidebar()

        # Connect sidebar signals
        self.sidebar.dashboard_clicked.connect(self.show_dashboard)
        self.sidebar.users_clicked.connect(self.show_users)
        self.sidebar.accounts_clicked.connect(self.show_user_accounts)
        self.sidebar.inventory_clicked.connect(self.show_inventory)
        self.sidebar.purchase_orders_clicked.connect(self.show_purchase_orders)
        self.sidebar.sale_orders_clicked.connect(self.show_sale_orders)
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

    def show_users(self):
        self.clear_content()
        self.sidebar.set_active("Users")
        self.content_layout.addWidget(UserList())

    def show_user_accounts(self):
        self.clear_content()
        self.sidebar.set_active("Accounts")
        self.content_layout.addWidget(UserAccountList())

    def show_inventory(self):
        self.clear_content()
        self.sidebar.set_active("Inventory")
        self.content_layout.addWidget(InventoryPanel())

    def show_purchase_orders(self):
        self.clear_content()
        self.sidebar.set_active("Purchase Orders")

        self.content_layout.addWidget(PurchaseOrderList())

    def show_sale_orders(self):
        self.clear_content()
        self.sidebar.set_active("Sale Orders")

        self.content_layout.addWidget(SaleOrderList())    
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
        self.auth_controller.logout()
        self.hide()
        self.launch_login()
