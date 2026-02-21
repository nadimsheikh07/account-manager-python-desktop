# pdf_utils.py
from PySide6.QtGui import QPdfWriter, QPainter, QFont, QColor, QPageSize
from PySide6.QtCore import QRect, Qt
from PySide6.QtWidgets import QFileDialog


class PDFExporter:
    def __init__(
        self,
        parent,
        filename="report.pdf",
        page_size=QPageSize.PageSizeId.A4,
        margin=80,
    ):
        self.parent = parent
        self.margin = margin
        self.filename = filename

        # Create file path dialog
        self.file_path, _ = QFileDialog.getSaveFileName(
            parent, "Save PDF", filename, "PDF Files (*.pdf)"
        )
        if not self.file_path:
            raise ValueError("No file path selected.")

        # Initialize PDF
        self.pdf = QPdfWriter(self.file_path)
        self.pdf.setPageSize(page_size)
        self.pdf.setResolution(300)

        self.painter = QPainter(self.pdf)
        self.page_width = self.pdf.width()
        self.page_height = self.pdf.height()
        self.usable_width = self.page_width - (self.margin * 2)
        self.y = self.margin

        self.row_height = 70

    def draw_title(self, title, font_size=16):
        self.painter.setFont(QFont("Arial", font_size, QFont.Weight.Bold))
        self.painter.drawText(self.margin, self.y, title)
        self.y += 80
        self.painter.setFont(QFont("Arial", 10))

    def draw_customer_info(self, customer_info: dict):
        for key, value in customer_info.items():
            self.painter.drawText(self.margin, self.y, f"{key}: {value or ''}")
            self.y += 50
        self.y += 10
        self.painter.drawLine(
            self.margin, self.y, self.page_width - self.margin, self.y
        )
        self.y += 60

    def draw_table(
        self,
        columns,
        data_rows,
        col_widths=None,
        alternate_row_color=QColor(245, 245, 245),
    ):
        # If no column widths, divide equally
        if not col_widths:
            col_widths = [self.usable_width // len(columns)] * len(columns)

        def draw_table_header():
            self.painter.setFont(QFont("Arial", 10, QFont.Weight.Bold))
            x = self.margin
            for i, col in enumerate(columns):
                self.painter.drawRect(x, self.y, col_widths[i], self.row_height)
                self.painter.drawText(
                    QRect(x + 5, self.y, col_widths[i] - 10, self.row_height),
                    Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft,
                    col,
                )
                x += col_widths[i]
            self.y += self.row_height
            self.painter.setFont(QFont("Arial", 9))

        draw_table_header()

        for idx, row in enumerate(data_rows):
            # New page check
            if self.y > self.page_height - self.margin - self.row_height:
                self.pdf.newPage()
                self.y = self.margin
                draw_table_header()

            x = self.margin

            # Alternate row background
            if idx % 2 == 0:
                self.painter.fillRect(
                    self.margin,
                    self.y,
                    sum(col_widths),
                    self.row_height,
                    alternate_row_color,
                )

            for i, cell in enumerate(row):
                self.painter.drawRect(x, self.y, col_widths[i], self.row_height)

                # Align numbers right, others left, Type center
                if i == 1:  # Type
                    alignment = Qt.AlignmentFlag.AlignCenter
                elif i >= 3:  # Amount & Balance
                    alignment = (
                        Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignRight
                    )
                else:
                    alignment = (
                        Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft
                    )

                self.painter.drawText(
                    QRect(x + 5, self.y, col_widths[i] - 10, self.row_height),
                    alignment,
                    str(cell),
                )
                x += col_widths[i]

            self.y += self.row_height

    def draw_summary(self, summary: dict):
        self.y += 40
        self.painter.drawLine(
            self.margin, self.y, self.page_width - self.margin, self.y
        )
        self.y += 60
        self.painter.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        for key, value in summary.items():
            self.painter.drawText(self.margin, self.y, f"{key}: {value:,.2f}")
            self.y += 50

    def finish(self):
        self.painter.end()
