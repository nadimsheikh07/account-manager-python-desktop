PRIMARY_COLOR = "#1abc9c"  # teal
SECONDARY_COLOR = "#3498db"  # blue
SIDEBAR_COLOR = "#2c3e50"
BACKGROUND_COLOR = "#f4f6f9"
TEXT_LIGHT = "#ffffff"
TEXT_DARK = "#2c3e50"


def get_global_stylesheet():
    return f"""
        QWidget {{
            background-color: {BACKGROUND_COLOR};
            font-family: Segoe UI, Arial;
        }}

        QFrame#Sidebar {{
            background-color: {SIDEBAR_COLOR};
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
            background-color: {SECONDARY_COLOR};
        }}

        QPushButton.primary:disabled {{
            background-color: #bdc3c7;
            color: #7f8c8d;
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
    """
