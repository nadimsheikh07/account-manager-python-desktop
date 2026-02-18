from PyQt6.QtWidgets import QSplashScreen, QApplication
from PyQt6.QtGui import QPixmap, QPainter, QColor, QFont, QIcon
from PyQt6.QtCore import Qt, QTimer
from config.theme import PRIMARY_COLOR, TEXT_DARK


def show_splash(app, duration=2000, logo_path="icon.ico"):
    """Show a themed splash screen with logo for `duration` milliseconds"""
    width, height = 500, 300

    # Create pixmap
    pixmap = QPixmap(width, height)
    pixmap.fill(Qt.GlobalColor.transparent)

    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)

    # Draw background with rounded corners
    painter.setBrush(QColor(PRIMARY_COLOR))
    painter.setPen(Qt.PenStyle.NoPen)
    painter.drawRoundedRect(0, 0, width, height, 20, 20)

    # Draw logo
    try:
        logo = QPixmap(logo_path).scaled(
            100,
            100,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation,
        )
        painter.drawPixmap((width - logo.width()) // 2, 50, logo)
    except Exception as e:
        print(f"Could not load logo: {e}")

    # Draw message text
    painter.setPen(QColor(TEXT_DARK))
    font = QFont("Segoe UI", 16, QFont.Weight.Bold)
    painter.setFont(font)
    painter.drawText(
        0,
        height - 80,
        width,
        50,
        Qt.AlignmentFlag.AlignCenter,
        "Loading Application...",
    )

    painter.end()

    # Create splash screen
    splash = QSplashScreen(pixmap, Qt.WindowType.FramelessWindowHint)
    splash.setMask(pixmap.mask())  # for rounded corners
    splash.show()

    # Set window icon (optional, for taskbar)
    app.setWindowIcon(QIcon(logo_path))

    # Timer to close
    QTimer.singleShot(duration, splash.close)
    app.processEvents()  # force rendering
    return splash
