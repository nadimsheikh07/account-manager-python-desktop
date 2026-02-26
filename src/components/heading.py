from PySide6.QtWidgets import QLabel


# =============================
# Title Component
# =============================
def createTitle(text: str) -> QLabel:
    title = QLabel(text)
    title.setStyleSheet(
        """
        font-size: 22px;
        font-weight: bold;
    """
    )
    return title
