from PySide6.QtWidgets import (
    QFrame,
    QVBoxLayout,
    QPushButton,
    QStyle,
)
from PySide6.QtCore import Qt, QSize, Signal


class Sidebar(QFrame):
    dashboard_clicked = Signal()
    users_clicked = Signal()
    accounts_clicked = Signal()
    inventory_clicked = Signal()
    purchase_orders_clicked = Signal()
    sale_orders_clicked = Signal()  # 🔥 NEW
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
            ("Users", QStyle.StandardPixmap.SP_FileIcon, self.users_clicked.emit),
            (
                "Accounts",
                QStyle.StandardPixmap.SP_DirOpenIcon,
                self.accounts_clicked.emit,
            ),
            (
                "Inventory",
                QStyle.StandardPixmap.SP_DriveHDIcon,
                self.inventory_clicked.emit,
            ),
            (
                "Purchase Orders",
                QStyle.StandardPixmap.SP_FileDialogDetailedView,
                self.purchase_orders_clicked.emit,
            ),
            (
                "Sale Orders",  # 🔥 NEW MENU
                QStyle.StandardPixmap.SP_FileDialogListView,
                self.sale_orders_clicked.emit,
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
        for label, _, _ in self.menu_buttons:
            if label == "☰":
                continue
            if self.sidebar_expanded:
                self.buttons[label].setText("")
            else:
                self.buttons[label].setText(label)

        self.setFixedWidth(60 if self.sidebar_expanded else 200)
        self.sidebar_expanded = not self.sidebar_expanded

    # ========================================
    # Active Highlight
    # ========================================
    def set_active(self, active_label):
        for label, _, _ in self.menu_buttons:
            if label == "☰":
                continue

            btn = self.buttons[label]
            btn.setProperty("active", label == active_label)
            btn.style().unpolish(btn)
            btn.style().polish(btn)
