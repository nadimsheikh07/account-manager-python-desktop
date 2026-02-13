import sys
import sqlite3
from PyQt6.QtWidgets import QApplication, QWidget, QLabel, QVBoxLayout
from login import LoginForm, DB_FILE


class MainApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Main App")
        self.setGeometry(200, 200, 400, 300)
        layout = QVBoxLayout()
        layout.addWidget(QLabel("Welcome! You are logged in."))
        self.setLayout(layout)


def is_authenticated():
    """Check if any user exists in DB (for demo purposes)"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users")
    user = cursor.fetchone()
    conn.close()
    return bool(user)


def main():
    app = QApplication(sys.argv)

    def launch_main():
        main_window = MainApp()
        main_window.show()
        sys.exit(app.exec())

    # Check if authenticated, else show login
    if is_authenticated():
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
