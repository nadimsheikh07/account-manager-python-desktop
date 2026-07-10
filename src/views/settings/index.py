from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QFormLayout,
    QLineEdit,
    QPushButton,
    QLabel,
    QMessageBox,
    QFileDialog,
    QHBoxLayout,
    QTextEdit,
    QSizePolicy,
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap

from src.components.heading import createTitle
from src.services.company_settings import (
    get_company_settings,
    save_company_settings,
)


class CompanySettingsView(QWidget):
    def __init__(self):
        super().__init__()
        self.setMinimumSize(800, 600)
        self.init_ui()
        self.load_settings()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(18)

        layout.addWidget(createTitle("Company Settings"))
        layout.addWidget(
            QLabel("Manage your business profile details that appear in reports and documents.")
        )

        form_layout = QFormLayout()
        form_layout.setLabelAlignment(Qt.AlignmentFlag.AlignRight)
        form_layout.setFieldGrowthPolicy(QFormLayout.FieldGrowthPolicy.ExpandingFieldsGrow)

        self.company_name_input = QLineEdit()
        self.company_name_input.setPlaceholderText("Your Company")
        form_layout.addRow("Company Name:", self.company_name_input)

        self.company_address_input = QTextEdit()
        self.company_address_input.setFixedHeight(80)
        form_layout.addRow("Company Address:", self.company_address_input)

        self.registration_input = QLineEdit()
        form_layout.addRow("Registration Number:", self.registration_input)

        self.gst_input = QLineEdit()
        form_layout.addRow("GST Number:", self.gst_input)

        self.phone_input = QLineEdit()
        form_layout.addRow("Phone:", self.phone_input)

        self.email_input = QLineEdit()
        form_layout.addRow("Email:", self.email_input)

        self.website_input = QLineEdit()
        form_layout.addRow("Website:", self.website_input)

        self.logo_path_label = QLabel("No logo selected")
        self.logo_path_label.setWordWrap(True)

        logo_row = QHBoxLayout()
        self.choose_logo_btn = QPushButton("Choose Logo")
        self.choose_logo_btn.clicked.connect(self.choose_logo)
        self.clear_logo_btn = QPushButton("Remove Logo")
        self.clear_logo_btn.clicked.connect(self.clear_logo)
        logo_row.addWidget(self.choose_logo_btn)
        logo_row.addWidget(self.clear_logo_btn)
        logo_row.addStretch()

        logo_container = QVBoxLayout()
        logo_container.addWidget(QLabel("Company Logo:"))
        logo_container.addLayout(logo_row)
        logo_container.addWidget(self.logo_path_label)
        self.logo_preview = QLabel()
        self.logo_preview.setFixedSize(180, 180)
        self.logo_preview.setStyleSheet("border: 1px solid #cccccc; background: white;")
        self.logo_preview.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.logo_preview.setText("Logo Preview")
        logo_container.addWidget(self.logo_preview)

        form_layout.addRow(logo_container)

        layout.addLayout(form_layout)

        buttons = QHBoxLayout()
        buttons.addStretch()
        self.save_btn = QPushButton("Save Settings")
        self.save_btn.setProperty("class", "primary")
        self.save_btn.clicked.connect(self.save_settings)
        buttons.addWidget(self.save_btn)
        layout.addLayout(buttons)

        self.setLayout(layout)

    def choose_logo(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Company Logo",
            "",
            "Images (*.png *.jpg *.jpeg *.bmp *.gif *.webp)",
        )
        if file_path:
            self.selected_logo_path = file_path
            self.logo_path_label.setText(file_path)
            self._show_logo_preview(file_path)

    def clear_logo(self):
        self.selected_logo_path = None
        self.logo_path_label.setText("No logo selected")
        self.logo_preview.setPixmap(QPixmap())
        self.logo_preview.setText("Logo Preview")

    def _show_logo_preview(self, path):
        pixmap = QPixmap(path)
        if pixmap.isNull():
            self.logo_preview.setText("Unable to preview")
            return
        scaled = pixmap.scaled(
            self.logo_preview.size(),
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation,
        )
        self.logo_preview.setPixmap(scaled)

    def load_settings(self):
        settings = get_company_settings()
        if not settings:
            return

        self.company_name_input.setText(settings.company_name or "")
        self.company_address_input.setPlainText(settings.company_address or "")
        self.registration_input.setText(settings.company_registration_number or "")
        self.gst_input.setText(settings.gst_number or "")
        self.phone_input.setText(settings.company_phone or "")
        self.email_input.setText(settings.company_email or "")
        self.website_input.setText(settings.website or "")

        if settings.company_logo_path:
            self.logo_path_label.setText(settings.company_logo_path)
            self._show_logo_preview(settings.company_logo_path)

    def save_settings(self):
        logo_path = getattr(self, "selected_logo_path", None)
        try:
            save_company_settings(
                company_name=self.company_name_input.text(),
                company_address=self.company_address_input.toPlainText(),
                company_registration_number=self.registration_input.text(),
                gst_number=self.gst_input.text(),
                company_phone=self.phone_input.text(),
                company_email=self.email_input.text(),
                website=self.website_input.text(),
                company_logo_path=logo_path,
            )
            QMessageBox.information(self, "Success", "Company settings saved successfully.")
        except Exception as exc:
            QMessageBox.warning(self, "Error", f"Unable to save settings: {exc}")
