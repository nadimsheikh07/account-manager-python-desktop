from PySide6.QtWidgets import QLabel


# =============================
# Title Component
# =============================
def create_title(text: str) -> QLabel:
    title = QLabel(text)
    title.setStyleSheet(
        """
        font-size: 22px;
        font-weight: bold;
    """
    )
    return title
