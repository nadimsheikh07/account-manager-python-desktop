import sys
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QTimer, QObject
from pages.auth.login import LoginForm
from main import MainApp
from services.auth import get_current_session
from services.dbSetup import init_db
from splash import show_splash


class AppLauncher(QObject):
    """
    Handles app startup logic:
    - Shows splash screen
    - Determines whether to show login or main window
    """

    def __init__(self, app):
        super().__init__()
        self.app = app
        self.splash = show_splash(app)
        self.main_window = None
        self.login_window = None

        # Delay a single shot to allow splash to render
        QTimer.singleShot(100, self.launch_app)

    def launch_app(self):
        # Check current session
        user = get_current_session()
        self.splash.close()

        if user:
            self.show_main()
        else:
            self.show_login()

    def show_main(self):
        self.main_window = MainApp()
        self.main_window.show()

    def show_login(self):
        self.login_window = LoginForm()
        self.login_window.login_successful.connect(self.on_login_success)
        self.login_window.show()

    def on_login_success(self):
        self.login_window.close()
        self.show_main()


def main():
    init_db()  # ensure DB is ready
    app = QApplication(sys.argv)
    launcher = AppLauncher(app)
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
