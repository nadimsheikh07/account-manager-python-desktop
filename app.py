import sys
import sqlite3
from PyQt6.QtWidgets import QApplication, QWidget, QLabel, QVBoxLayout, QPushButton
from login import LoginForm, DB_FILE


class MainApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Main App")
        self.setGeometry(200, 200, 400, 300)

        layout = QVBoxLayout()
        self.label = QLabel("Welcome! You are logged in.")
        layout.addWidget(self.label)

        # Logout button
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
        # Relaunch login
        self.launch_login()

    def launch_login(self):
        self.login_window = LoginForm(on_login_success=self.show_main)
        self.login_window.show()

    def show_main(self):
        self.show()


def get_current_session():
    """Return username if session exists, else None"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS session (username TEXT UNIQUE)")
    cursor.execute("SELECT username FROM session LIMIT 1")
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else None


def main():
    app = QApplication(sys.argv)

    def launch_main():
        main_window = MainApp()
        main_window.show()
        sys.exit(app.exec())

    current_user = get_current_session()
    if current_user:
        launch_main()
    else:
        login_window = LoginForm(on_login_success=launch_main)
        login_window.show()
        sys.exit(app.exec())


if __name__ == "__main__":
    # For demo: create default user if DB empty
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute(
        "CREATE TABLE IF NOT EXISTS users (username TEXT UNIQUE, password TEXT)"
    )
    cursor.execute(
        "INSERT OR IGNORE INTO users (username, password) VALUES (?, ?)",
        ("admin", "1234"),
    )
    conn.commit()
    conn.close()

    main()
