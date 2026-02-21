PRIMARY_COLOR = "#1abc9c"  # teal
PRIMARY_DARK_COLOR = "#21a288"  # teal
SECONDARY_COLOR = "#3498db"  # blue
DANGER_COLOR = "#e74c3c"  # red
DANGER_DARK_COLOR = "#c0392b"  # red
SIDEBAR_COLOR = "#2c3e50"
BACKGROUND_COLOR = "#f4f6f9"
DISABLE_BACKGROUND_COLOR = "#bdc3c7"
DISABLE_COLOR = "#7f8c8d"
TEXT_LIGHT = "#ffffff"
TEXT_DARK = "#2c3e50"
BORDER_COLOR = "#ccc"  # light gray for borders


def get_global_stylesheet():
    return f"""
        QWidget {{
            background-color: {BACKGROUND_COLOR};
            font-family: Segoe UI, Arial;
        }}

        QFrame#Sidebar {{
            background-color: {SIDEBAR_COLOR};
        }}

        QLineEdit {{
            padding: 8px;
            border: 1px solid {BORDER_COLOR};
            border-radius: 6px;
        }}

        QLineEdit:focus {{
            border: 1px solid {PRIMARY_COLOR};
        }}

        /* ================= BUTTON BASE ================= */
        QPushButton {{
            border: none;
            padding: 8px;
            border-radius: 6px;
        }}

        /* ================= PRIMARY BUTTON ================= */
        QPushButton.primary {{
            background-color: {PRIMARY_COLOR};
            color: {TEXT_LIGHT};
            font-weight: bold;
        }}

        QPushButton.primary:hover {{
            background-color: {PRIMARY_DARK_COLOR};
        }}

        QPushButton.primary:disabled {{
            background-color: {DISABLE_BACKGROUND_COLOR};
            color: {DISABLE_COLOR};
        }}

        /* ================= DANGER BUTTON ================= */
        QPushButton.danger {{
            background-color: {DANGER_COLOR};
            color: {TEXT_LIGHT};
            font-weight: bold;
        }}

        QPushButton.danger:hover {{
            background-color: {DANGER_DARK_COLOR};
        }}

        QPushButton.danger:disabled {{
            background-color: {DISABLE_BACKGROUND_COLOR};
            color: {DISABLE_COLOR};
        }}


        /* ================= SIDEBAR BUTTON ================= */
        QPushButton.sidebar {{
            background-color: transparent;
            color: {TEXT_LIGHT};
            text-align: left;
            padding: 10px;
        }}

        QPushButton.sidebar:hover {{
            background-color: {SECONDARY_COLOR};
        }}

        QPushButton.sidebar:disabled {{
            color: #95a5a6;
        }}

        /* ================= ACTIVE MENU ================= */
        QPushButton[active="true"] {{
            background-color: {PRIMARY_COLOR};
            font-weight: bold;
        }}

        /* ================= DROPDOWN / COMBOBOX ================= */
        QComboBox {{
            border: 1px solid {BORDER_COLOR};
            border-radius: 6px;
            padding: 5px 8px;
            min-height: 28px;
            background-color: #fff;
        }}

        QComboBox:hover {{
            border: 1px solid {PRIMARY_COLOR};
        }}

        QComboBox:focus {{
            border: 1px solid {PRIMARY_COLOR};
        }}

        QComboBox::drop-down {{
            subcontrol-origin: padding;
            subcontrol-position: top right;
            width: 20px;
            border-left: 1px solid {BORDER_COLOR};
        }}

        QComboBox::down-arrow {{
            image: url(:/icons/arrow-down.png); /* optional custom arrow */
            width: 12px;
            height: 12px;
        }}

        QComboBox QAbstractItemView {{
            border: 1px solid {BORDER_COLOR};
            selection-background-color: {PRIMARY_COLOR};
            selection-color: {TEXT_LIGHT};
            background-color: #fff;
            padding: 4px;
            outline: 0;
        }}

        QLineEdit[error="true"] {{
            border: 2px solid {DANGER_COLOR};
            border-radius: 6px;
            padding: 4px;
        }}
    """
