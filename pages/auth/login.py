from PySide6.QtWidgets import (
    QWidget,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QMessageBox,
    QFrame,
    QApplication
)
from PySide6.QtCore import Qt, Signal
from services.auth import authenticateUser
from config.theme import getGlobalStylesheet
from utils.formUtils import setError


class LoginForm(QWidget):
    loginSuccessful = Signal()  # Use signal instead of callback

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Login")
        self.setFixedSize(400, 300)

        # Apply global stylesheet + base validation styles
        self.setStyleSheet(
            getGlobalStylesheet()
            + """
            QWidget { background-color: #f4f6f9; }
        """
        )

        self.init_ui()

    # ==============================
    # UI
    # ==============================
    def init_ui(self):
        main_layout = QVBoxLayout()
        main_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Card container
        self.card = QFrame()
        self.card.setFixedWidth(320)
        self.card.setStyleSheet(
            "QFrame { background-color: white; border-radius: 12px; }"
        )

        card_layout = QVBoxLayout()
        card_layout.setSpacing(8)
        card_layout.setContentsMargins(25, 25, 25, 25)

        # Title / subtitle
        title = QLabel("Welcome Back")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("font-size: 20px; font-weight: bold;")
        subtitle = QLabel("Please login to continue")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle.setStyleSheet("color: gray; font-size: 12px;")

        # Username & password inputs
        self.username_input, self.username_error_label = self.create_input("Username")
        self.password_input, self.password_error_label = self.create_input(
            "Password", echo_mode=QLineEdit.EchoMode.Password
        )

        # Login button
        self.login_button = QPushButton("Login")
        self.login_button.setProperty("class", "primary")
        self.login_button.setFixedHeight(35)
        self.login_button.setEnabled(False)

        # Connect signals
        self.username_input.textChanged.connect(self.validate_form)
        self.username_input.textChanged.connect(
            lambda: self.clear_error(self.username_input, self.username_error_label)
        )
        self.password_input.textChanged.connect(self.validate_form)
        self.password_input.textChanged.connect(
            lambda: self.clear_error(self.password_input, self.password_error_label)
        )
        self.password_input.returnPressed.connect(self.handle_login)
        self.login_button.clicked.connect(self.handle_login)

        # Add widgets to card layout
        card_layout.addWidget(title)
        card_layout.addWidget(subtitle)
        card_layout.addSpacing(10)

        for widget in [
            self.username_input,
            self.username_error_label,
            self.password_input,
            self.password_error_label,
        ]:
            card_layout.addWidget(widget)

        card_layout.addSpacing(10)
        card_layout.addWidget(self.login_button)

        self.card.setLayout(card_layout)
        main_layout.addWidget(self.card)
        self.setLayout(main_layout)

    # ==============================
    # Input helper
    # ==============================
    def create_input(self, placeholder, echo_mode=QLineEdit.EchoMode.Normal):
        input_field = QLineEdit()
        input_field.setPlaceholderText(placeholder)
        input_field.setEchoMode(echo_mode)

        error_label = QLabel()
        error_label.setStyleSheet("color: #e74c3c; font-size: 11px;")
        error_label.setVisible(False)

        return input_field, error_label

    def clear_error(self, input_field, error_label):
        setError(False, input_field)
        error_label.setVisible(False)

    # ==============================
    # Validation
    # ==============================
    def validate_form(self):
        username = self.username_input.text().strip()
        password = self.password_input.text().strip()

        valid = True

        if not username:
            setError(True, self.username_input)
            self.username_error_label.setText("Username is required")
            self.username_error_label.setVisible(True)
            valid = False

        if not password:
            setError(True, self.password_input)
            self.password_error_label.setText("Password is required")
            self.password_error_label.setVisible(True)
            valid = False

        self.login_button.setEnabled(valid)

    # ==============================
    # Login handling
    # ==============================
    def handle_login(self):
        username = self.username_input.text().strip()
        password = self.password_input.text().strip()

        if not username or not password:
            self.validate_form()
            QMessageBox.warning(self, "Validation Error", "All fields are required.")
            return

        # Loading state
        self.login_button.setEnabled(False)
        self.login_button.setText("Logging in...")
        self.login_button.setCursor(Qt.CursorShape.WaitCursor)
        QApplication.processEvents()

        # Authenticate
        success = authenticateUser(username, password)

        # Restore button
        self.login_button.setText("Login")
        self.validate_form()

        if success:
            QMessageBox.information(self, "Login", "Login successful!")
            self.loginSuccessful.emit()  # emit signal
            self.close()
        else:
            for input_field in [self.username_input, self.password_input]:
                setError(True, input_field)
            QMessageBox.warning(self, "Login Failed", "Invalid username or password.")
