import sys
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QTimer, QObject
from pages.auth.login import LoginForm
from main import MainApp
from services.auth import getCurrentSession
from services.dbSetup import init_db
from splash import showSplash


class AppLauncher(QObject):
    """
    Handles app startup logic:
    - Shows splash screen
    - Determines whether to show login or main window
    """

    def __init__(self, app):
        super().__init__()
        self.app = app
        self.splash = showSplash(app)
        self.main_window = None
        self.login_window = None

        # Delay a single shot to allow splash to render
        QTimer.singleShot(100, self.launch_app)

    def launch_app(self):
        # Check current session
        user = getCurrentSession()
        self.splash.close()

        if user:
            self.showMain()
        else:
            self.showLogin()

    def showMain(self):
        self.main_window = MainApp()
        self.main_window.show()

    def showLogin(self):
        self.login_window = LoginForm()
        self.login_window.loginSuccessful.connect(self.onLoginSuccess)
        self.login_window.show()

    def onLoginSuccess(self):
        self.login_window.close()
        self.showMain()


def main():
    init_db()  # ensure DB is ready
    app = QApplication(sys.argv)
    launcher = AppLauncher(app)
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
