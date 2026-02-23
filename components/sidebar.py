from PySide6.QtWidgets import (
    QFrame,
    QVBoxLayout,
    QPushButton,
    QStyle,
)
from PySide6.QtCore import Qt, QSize, Signal


class Sidebar(QFrame):
    dashboard_clicked = Signal()
    customers_clicked = Signal()
    accounts_clicked = Signal()
    logout_clicked = Signal()
    toggle_clicked = Signal()

    def __init__(self):
        super().__init__()

        self.sidebar_expanded = True
        self.setFixedWidth(200)
        self.setObjectName("Sidebar")

        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        self.menu_buttons = [
            ("☰", None, self.toggle_sidebar),
            (
                "Dashboard",
                QStyle.StandardPixmap.SP_ComputerIcon,
                self.dashboard_clicked.emit,
            ),
            (
                "Customers",
                QStyle.StandardPixmap.SP_FileIcon,
                self.customers_clicked.emit,
            ),
            (
                "Accounts",
                QStyle.StandardPixmap.SP_DirOpenIcon,
                self.accounts_clicked.emit,
            ),
            (
                "Logout",
                QStyle.StandardPixmap.SP_DialogCloseButton,
                self.logout_clicked.emit,
            ),
        ]

        self.buttons = {}

        for label, icon_enum, callback in self.menu_buttons:
            btn = QPushButton(label)
            btn.setMinimumHeight(40)

            if icon_enum:
                btn.setIcon(self.style().standardIcon(icon_enum))
                btn.setIconSize(QSize(20, 20))

            btn.clicked.connect(callback)
            layout.addWidget(btn)
            self.buttons[label] = btn

        layout.addStretch()

    # ========================================
    # Toggle
    # ========================================
    def toggle_sidebar(self):
        if self.sidebar_expanded:
            self.setFixedWidth(60)
            for label in ["Dashboard", "Customers", "Accounts", "Logout"]:
                self.buttons[label].setText("")
        else:
            self.setFixedWidth(200)
            for label in ["Dashboard", "Customers", "Accounts", "Logout"]:
                self.buttons[label].setText(label)

        self.sidebar_expanded = not self.sidebar_expanded

    # ========================================
    # Active Highlight
    # ========================================
    def set_active(self, active_label):
        for label in ["Dashboard", "Customers", "Accounts"]:
            btn = self.buttons[label]
            btn.setProperty("active", label == active_label)
            btn.style().unpolish(btn)
            btn.style().polish(btn)
