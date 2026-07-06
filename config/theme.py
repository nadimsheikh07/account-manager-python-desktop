PRIMARY_COLOR = "#1abc9c"
PRIMARY_DARK_COLOR = "#21a288"
SECONDARY_COLOR = "#3498db"
DANGER_COLOR = "#e74c3c"
DANGER_DARK_COLOR = "#c0392b"

SIDEBAR_COLOR = "#2c3e50"
BACKGROUND_COLOR = "#f4f6f9"

DISABLE_BACKGROUND_COLOR = "#bdc3c7"
DISABLE_COLOR = "#7f8c8d"

TEXT_LIGHT = "#ffffff"
TEXT_DARK = "#2c3e50"

BORDER_COLOR = "#dcdde1"


def _button_style(name, bg, hover):
    return f"""
    QPushButton[class="{name}"] {{
        background-color: {bg};
        color: {TEXT_LIGHT};
        border: none;
        border-radius: 6px;
        padding: 8px 16px;
        font-weight: 600;
    }}

    QPushButton[class="{name}"]:hover {{
        background-color: {hover};
    }}

    QPushButton[class="{name}"]:pressed {{
        padding-top: 9px;
        padding-bottom: 7px;
    }}

    QPushButton[class="{name}"]:disabled {{
        background-color: {DISABLE_BACKGROUND_COLOR};
        color: {DISABLE_COLOR};
    }}
    """


def getGlobalStylesheet():
    return f"""
    /* ================= GLOBAL ================= */

    QWidget {{
        background: {BACKGROUND_COLOR};
        color: {TEXT_DARK};
        font-family: "Segoe UI";
        font-size: 10pt;
    }}

    QFrame#Sidebar {{
        background: {SIDEBAR_COLOR};
    }}

    /* ================= INPUT ================= */

    QLineEdit,
    QTextEdit,
    QPlainTextEdit,
    QComboBox {{
        background: white;
        border: 1px solid {BORDER_COLOR};
        border-radius: 6px;
        padding: 6px 8px;
    }}

    QLineEdit:focus,
    QTextEdit:focus,
    QPlainTextEdit:focus,
    QComboBox:focus {{
        border: 1px solid {PRIMARY_COLOR};
    }}

    QLineEdit[error="true"],
    QTextEdit[error="true"],
    QComboBox[error="true"] {{
        border: 2px solid {DANGER_COLOR};
    }}

    /* ================= COMBOBOX ================= */

    QComboBox::drop-down {{
        border: none;
        width: 24px;
    }}

    QComboBox QAbstractItemView {{
        background: white;
        border: 1px solid {BORDER_COLOR};
        selection-background-color: {PRIMARY_COLOR};
        selection-color: white;
        outline: 0;
    }}

    /* ================= BUTTON BASE ================= */

    QPushButton {{
        border: none;
        border-radius: 6px;
        padding: 8px 16px;
    }}

    {_button_style("primary", PRIMARY_COLOR, PRIMARY_DARK_COLOR)}

    {_button_style("secondary", SECONDARY_COLOR, PRIMARY_COLOR)}

    {_button_style("danger", DANGER_COLOR, DANGER_DARK_COLOR)}

    /* ================= SIDEBAR BUTTON ================= */

    QPushButton[class="sidebar"] {{
        background: transparent;
        color: {TEXT_LIGHT};
        text-align: left;
        padding: 10px 14px;
        border-radius: 0px;
    }}

    QPushButton[class="sidebar"]:hover {{
        background: {SECONDARY_COLOR};
    }}

    QPushButton[class="sidebar"][active="true"] {{
        background: {PRIMARY_COLOR};
        font-weight: bold;
    }}

    QPushButton[class="sidebar"]:disabled {{
        color: #95a5a6;
    }}

    /* ================= LABEL ================= */

    QLabel[title="true"] {{
        font-size: 18px;
        font-weight: bold;
        color: {TEXT_DARK};
    }}

    QLabel[muted="true"] {{
        color: #7f8c8d;
    }}

    /* ================= TABLE ================= */

    QTableWidget,
    QTableView {{
        background: white;
        border: 1px solid {BORDER_COLOR};
        gridline-color: #ecf0f1;
        selection-background-color: {PRIMARY_COLOR};
        selection-color: white;
    }}

    QHeaderView::section {{
        background: #ecf0f1;
        border: none;
        padding: 8px;
        font-weight: bold;
    }}
    """