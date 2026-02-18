import sqlite3
from PyQt6.QtWidgets import QWidget, QLabel, QVBoxLayout, QPushButton
from login import LoginForm, DB_FILE


class MainApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Main App")
        self.setGeometry(200, 200, 400, 300)

        layout = QVBoxLayout()
        self.label = QLabel("Welcome! You are logged in.")
        layout.addWidget(self.label)

        self.logout_btn = QPushButton("Logout")
        self.logout_btn.clicked.connect(self.logout)
        layout.addWidget(self.logout_btn)

        self.setLayout(layout)

    def logout(self):
        """Clear session and close main window"""
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM session")
        conn.commit()
        conn.close()
        self.close()
        self.launch_login()

    def launch_login(self):
        self.login_window = LoginForm(on_login_success=self.show_main)
        self.login_window.show()

    def show_main(self):
        self.show()
