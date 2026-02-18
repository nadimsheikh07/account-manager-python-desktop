import sys
import sqlite3
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QTimer
from login import LoginForm
from splash import show_splash
from main import MainApp
from config.db import DB_FILE
from services.auth import get_current_session


def main():
    app = QApplication(sys.argv)

    # Show splash screen
    splash_duration = 2000  # milliseconds
    splash = show_splash(app, duration=splash_duration)

    # Keep references to avoid garbage collection
    windows = {}

    def launch_app():
        splash.close()  # ensure splash is gone

        current_user = get_current_session()
        if current_user:
            windows["main"] = MainApp()
            windows["main"].show()
        else:
            windows["login"] = LoginForm(
                on_login_success=lambda: show_main_after_login(windows)
            )
            windows["login"].show()

    def show_main_after_login(windows):
        windows["login"].close()
        windows["main"] = MainApp()
        windows["main"].show()

    QTimer.singleShot(splash_duration, launch_app)
    sys.exit(app.exec())


if __name__ == "__main__":
    # Create default user if DB empty
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
