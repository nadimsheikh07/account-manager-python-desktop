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
from pages.customer_account.index import CustomerAccountList
from services.auth import logout
from config.theme import get_global_stylesheet
from config.app import APP_NAME


class MainApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(APP_NAME)
        self.sidebar_expanded = True

        # Apply global stylesheet
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

        # Menu buttons config: (label, icon, callback)
        self.menu_buttons = [
            ("☰", None, self.toggle_sidebar),
            ("Dashboard", QStyle.StandardPixmap.SP_ComputerIcon, self.show_dashboard),
            ("Customers", QStyle.StandardPixmap.SP_FileIcon, self.show_customers),
            (
                "Accounts",
                QStyle.StandardPixmap.SP_DirOpenIcon,
                self.show_customer_accounts,
            ),
            ("Logout", QStyle.StandardPixmap.SP_DialogCloseButton, self.handle_logout),
        ]

        self.buttons = {}
        for label, icon_enum, callback in self.menu_buttons:
            btn = QPushButton(label)
            if icon_enum:
                btn.setIcon(self.style().standardIcon(icon_enum))
                btn.setIconSize(QSize(20, 20))
                btn.setMinimumHeight(40)
            btn.clicked.connect(callback)
            sidebar_layout.addWidget(btn)
            self.buttons[label] = btn

        sidebar_layout.addStretch()
        self.sidebar.setLayout(sidebar_layout)

        # ================= Content Area =================
        self.content = QFrame()
        self.content_layout = QVBoxLayout()
        self.content.setLayout(self.content_layout)

        main_layout.addWidget(self.sidebar)
        main_layout.addWidget(self.content)

        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        self.setLayout(main_layout)

        self.show_dashboard()

    # ==================================================
    # Sidebar Toggle
    # ==================================================
    def toggle_sidebar(self):
        if self.sidebar_expanded:
            self.sidebar.setFixedWidth(60)
            for label in ["Dashboard", "Customers", "Accounts", "Logout"]:
                self.buttons[label].setText("")
        else:
            self.sidebar.setFixedWidth(200)
            for label in ["Dashboard", "Customers", "Accounts", "Logout"]:
                self.buttons[label].setText(label)
        self.sidebar_expanded = not self.sidebar_expanded

    # ==================================================
    # Utility
    # ==================================================
    def set_active_menu(self, active_label):
        for label in ["Dashboard", "Customers", "Accounts"]:
            btn = self.buttons[label]
            btn.setProperty("active", label == active_label)
            btn.style().unpolish(btn)
            btn.style().polish(btn)

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
        self.set_active_menu("Dashboard")
        self.content_layout.addWidget(Dashboard())

    def show_customers(self):
        self.clear_content()
        self.set_active_menu("Customers")
        self.content_layout.addWidget(CustomerList())

    def show_customer_accounts(self):
        self.clear_content()
        self.set_active_menu("Accounts")
        self.content_layout.addWidget(CustomerAccountList())

    # ==================================================
    # Login Handling
    # ==================================================
    def launch_login(self):
        self.login_window = LoginForm()
        self.login_window.login_successful.connect(self.show_main)
        self.login_window.show()

    def show_main(self):
        self.show()

    def handle_logout(self):
        logout()
        self.hide()
        self.launch_login()
