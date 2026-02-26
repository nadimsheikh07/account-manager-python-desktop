import sys
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QTimer, QObject

from src.views.auth.login import LoginForm
from main import MainApp
from src.services.auth import getCurrentSession
from splash import showSplash

from config.db import Base, engine
from src.models import *  # ensures models are registered
from src.services.dbSetup import init_db

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

        QTimer.singleShot(100, self.launch_app)

    def launch_app(self):
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
    # 🔹 1. Initialize DB
    init_db()

    # 🔹 2. Create tables (SQLAlchemy)
    Base.metadata.create_all(bind=engine)

    # 🔹 3. Start Qt application
    app = QApplication(sys.argv)

    # 🔹 4. Launch app controller
    launcher = AppLauncher(app)

    sys.exit(app.exec())


if __name__ == "__main__":
    main()