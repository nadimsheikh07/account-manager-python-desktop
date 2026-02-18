from PyQt6.QtWidgets import QSplashScreen, QApplication
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt, QTimer


def show_splash(app, duration=2000):
    """Show splash screen for `duration` milliseconds"""
    pixmap = QPixmap(400, 300)
    pixmap.fill(Qt.GlobalColor.white)  # plain white background, can use an image
    splash = QSplashScreen(pixmap)
    splash.showMessage("Loading Application...", alignment=Qt.AlignmentFlag.AlignCenter)
    splash.show()

    # Return a QTimer that closes the splash after duration
    timer = QTimer()
    timer.singleShot(duration, splash.close)
    app.processEvents()  # force splash to render
    return splash
