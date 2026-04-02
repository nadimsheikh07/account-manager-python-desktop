import sys
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QTimer, QObject

from src.views.auth.login import LoginForm
from main import MainApp
from src.services.auth import getCurrentSession
from splash import showSplash
from src.services.dbSetup import init_db


class AppController(QObject):
    """
    Manages the application lifecycle:
    - Displays the splash screen
    - Orchestrates transitions between Login and Main windows based on user session state
    """

    def __init__(self, app):
        super().__init__()
        self.app = app
        self.splash = showSplash(app)
        self.main_window = None
        self.login_window = None

        # Give the splash screen a moment to stay visible
        QTimer.singleShot(100, self.launch_app)

    def launch_app(self):
        # 1. Check if user already logged in
        user_id = getCurrentSession()

        # 2. Close splash
        self.splash.close()

        # 3. Decision logic
        if user_id:
            self.show_main()
        else:
            self.show_login()

    def show_main(self):
        self.main_window = MainApp()
        self.main_window.show()

    def show_login(self):
        self.login_window = LoginForm()
        self.login_window.loginSuccessful.connect(self.on_login_success)
        self.login_window.show()

    def on_login_success(self):
        if self.login_window:
            self.login_window.close()
            self.login_window = None
        self.show_main()


def main():
    # 🔹 1. Initialize DB (creates all tables and seeds data if not exists)
    init_db()

    # 🔹 2. Create Qt application
    app = QApplication(sys.argv)

    # 🔹 3. Launch the app controller
    _controller = AppController(app)

    # 🔹 4. Run loop
    sys.exit(app.exec())


if __name__ == "__main__":
    main()