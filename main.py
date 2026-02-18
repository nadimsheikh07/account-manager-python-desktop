from PyQt6.QtWidgets import QWidget, QLabel, QVBoxLayout, QPushButton
from pages.auth.login import LoginForm
from services.auth import logout

class MainApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Main App")
        self.setGeometry(200, 200, 400, 300)

        self.init_ui()

        # Hide main window initially
        self.hide()

    def init_ui(self):
        layout = QVBoxLayout()

        self.label = QLabel("Welcome! You are logged in.")
        layout.addWidget(self.label)

        self.logout_btn = QPushButton("Logout")
        self.logout_btn.clicked.connect(self.handle_logout)
        layout.addWidget(self.logout_btn)

        self.setLayout(layout)

    def launch_login(self):
        self.login_window = LoginForm(on_login_success=self.show_main)
        self.login_window.show()

    def show_main(self):
        self.show()

    def handle_logout(self):
        logout()
        self.hide()
        self.launch_login()
