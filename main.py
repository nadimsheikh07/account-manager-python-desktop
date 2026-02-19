from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QFrame,
    QStyle,
)
from PySide6.QtCore import Qt, QSize
from pages.auth.login import LoginForm
from pages.auth.dashboard import Dashboard
from pages.customer.index import CustomerList
from services.auth import logout
from config.theme import get_global_stylesheet
from pages.customer_account.index import CustomerAccountList
from config.app import APP_NAME


class MainApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(APP_NAME)
        self.sidebar_expanded = True

        # Apply global stylesheet once
        self.setStyleSheet(get_global_stylesheet())

        self.init_ui()
        self.showMaximized()

    def init_ui(self):
        main_layout = QHBoxLayout(self)

        # ================= Sidebar =================
        self.sidebar = QFrame()
        self.sidebar.setFixedWidth(200)
        self.sidebar.setObjectName("Sidebar")

        sidebar_layout = QVBoxLayout()
        sidebar_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        # Toggle button
        self.toggle_btn = QPushButton("☰")
        self.toggle_btn.clicked.connect(self.toggle_sidebar)
        sidebar_layout.addWidget(self.toggle_btn)

        # Menu buttons
        self.dashboard_btn = QPushButton("Dashboard")
        self.customer_btn = QPushButton("Customers")
        self.customer_account_btn = QPushButton("Accounts")
        self.logout_btn = QPushButton("Logout")

        # Set icons (Proper enum usage)
        self.dashboard_btn.setIcon(
            self.style().standardIcon(QStyle.StandardPixmap.SP_ComputerIcon)
        )
        self.customer_btn.setIcon(
            self.style().standardIcon(QStyle.StandardPixmap.SP_FileIcon)
        )
        self.customer_account_btn.setIcon(
            self.style().standardIcon(QStyle.StandardPixmap.SP_DirOpenIcon)
        )
        self.logout_btn.setIcon(
            self.style().standardIcon(QStyle.StandardPixmap.SP_DialogCloseButton)
        )

        # Optional: consistent icon size
        for btn in [
            self.dashboard_btn,
            self.customer_btn,
            self.customer_account_btn,
            self.logout_btn,
        ]:
            btn.setIconSize(QSize(20, 20))
            btn.setMinimumHeight(40)

        # Connect buttons
        self.dashboard_btn.clicked.connect(self.show_dashboard)
        self.customer_btn.clicked.connect(self.show_customers)
        self.customer_account_btn.clicked.connect(self.show_customer_accounts)
        self.logout_btn.clicked.connect(self.handle_logout)

        sidebar_layout.addWidget(self.dashboard_btn)
        sidebar_layout.addWidget(self.customer_btn)
        sidebar_layout.addWidget(self.customer_account_btn)
        sidebar_layout.addStretch()
        sidebar_layout.addWidget(self.logout_btn)

        self.sidebar.setLayout(sidebar_layout)

        # ================= Content Area =================
        self.content = QFrame()
        self.content_layout = QVBoxLayout()

        self.content.setLayout(self.content_layout)

        main_layout.addWidget(self.sidebar)
        main_layout.addWidget(self.content)

        main_layout.setContentsMargins(0, 0, 0, 0)  # remove extra padding
        main_layout.setSpacing(0)  # remove spacing between pages
        self.setLayout(main_layout)

        self.show_dashboard()

    # ==================================================
    # Sidebar Toggle
    # ==================================================
    def toggle_sidebar(self):
        if self.sidebar_expanded:
            self.sidebar.setFixedWidth(60)
            self.dashboard_btn.setText("")
            self.customer_btn.setText("")
            self.customer_account_btn.setText("")
            self.logout_btn.setText("")
        else:
            self.sidebar.setFixedWidth(200)
            self.dashboard_btn.setText("Dashboard")
            self.customer_btn.setText("Customers")
            self.customer_account_btn.setText("Accounts")
            self.logout_btn.setText("Logout")

        self.sidebar_expanded = not self.sidebar_expanded

    # ==================================================
    # Utility
    # ==================================================
    def set_active_menu(self, button):
        for btn in [self.dashboard_btn, self.customer_btn, self.customer_account_btn]:
            btn.setProperty("active", False)
            btn.style().unpolish(btn)
            btn.style().polish(btn)

        button.setProperty("active", True)
        button.style().unpolish(button)
        button.style().polish(button)

    def clear_content(self):
        while self.content_layout.count():
            child = self.content_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

    # ==================================================
    # Pages
    # ==================================================
    def show_dashboard(self):
        self.clear_content()
        self.set_active_menu(self.dashboard_btn)
        self.dashboard_page = Dashboard()
        self.content_layout.addWidget(self.dashboard_page)

    def show_customers(self):
        self.clear_content()
        self.set_active_menu(self.customer_btn)
        self.customer_page = CustomerList()
        self.content_layout.addWidget(self.customer_page)

    def show_customer_accounts(self):
        self.clear_content()
        self.set_active_menu(self.customer_account_btn)
        self.customer_account_page = CustomerAccountList()
        self.content_layout.addWidget(self.customer_account_page)

    # ==================================================
    # Login Handling
    # ==================================================
    def launch_login(self):
        self.login_window = LoginForm(on_login_success=self.show_main)
        self.login_window.show()

    def show_main(self):
        self.show()

    def handle_logout(self):
        logout()
        self.hide()
        self.launch_login()
