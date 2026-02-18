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
from pages.customer.index import CustomerList
from services.auth import logout
from config.theme import get_global_stylesheet


class MainApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Main App")
        self.sidebar_expanded = True  # Sidebar state

        self.init_ui()
        self.showMaximized()

    def init_ui(self):
        main_layout = QHBoxLayout(self)

        # ========== Sidebar ==========
        self.sidebar = QFrame()
        self.sidebar.setFixedWidth(200)
        self.sidebar.setObjectName("Sidebar")
        self.setStyleSheet(get_global_stylesheet())

        sidebar_layout = QVBoxLayout()
        sidebar_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        # Toggle button
        self.toggle_btn = QPushButton("☰")
        self.toggle_btn.clicked.connect(self.toggle_sidebar)
        sidebar_layout.addWidget(self.toggle_btn)

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
    # Sidebar Toggle
    # =====================
    def toggle_sidebar(self):
        if self.sidebar_expanded:
            self.sidebar.setFixedWidth(50)
            self.dashboard_btn.setText("")
            self.customer_btn.setText("")
            self.logout_btn.setText("")
        else:
            self.sidebar.setFixedWidth(200)
            self.dashboard_btn.setText("Dashboard")
            self.customer_btn.setText("Customers")
            self.logout_btn.setText("Logout")
        self.sidebar_expanded = not self.sidebar_expanded

    # =====================
    # Utility
    # =====================
    def set_active_menu(self, button):
        for btn in [self.dashboard_btn, self.customer_btn]:
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

    # =====================
    # Pages
    # =====================
    def show_dashboard(self):
        self.clear_content()
        self.set_active_menu(self.dashboard_btn)
        label = QLabel("Welcome! You are logged in.")
        label.setStyleSheet("font-size: 18px;")
        self.content_layout.addWidget(label)

    def show_customers(self):
        self.clear_content()
        self.set_active_menu(self.customer_btn)
        self.customer_page = CustomerList()
        self.content_layout.addWidget(self.customer_page)

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
