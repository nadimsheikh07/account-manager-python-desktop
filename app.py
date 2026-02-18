import sys
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QTimer
from pages.auth.login import LoginForm
from splash import show_splash
from main import MainApp
from services.auth import init_db, get_current_session


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
    init_db()
    main()
