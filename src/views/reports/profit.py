import pandas as pd
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QLabel,
    QDateEdit,
    QFileDialog,
    QMessageBox,
    QHeaderView,
    QSizePolicy,
)
from PySide6.QtCore import Qt, QDate
from src.components.heading import createTitle
from src.services.profit_report import generate_profit_report
from utils.pdfUtils import PDFExporter


class ProfitReport(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        layout.addWidget(createTitle("Profit Report"))

        # Controls: start/end date selectors and action buttons
        controls = QHBoxLayout()
        self.start_input = QDateEdit(calendarPopup=True)
        self.end_input = QDateEdit(calendarPopup=True)
        self.start_input.setDisplayFormat("yyyy-MM-dd")
        self.end_input.setDisplayFormat("yyyy-MM-dd")

        today = QDate.currentDate()
        self.end_input.setDate(today)
        self.start_input.setDate(today.addDays(-30))

        refresh_btn = QPushButton("Refresh")
        refresh_btn.setProperty("class", "primary")
        refresh_btn.clicked.connect(self.refresh)

        export_excel_btn = QPushButton("Export Excel")
        export_excel_btn.setProperty("class", "secondary")
        export_excel_btn.clicked.connect(self.export_to_excel)
        export_pdf_btn = QPushButton("Export PDF")
        export_pdf_btn.setProperty("class", "secondary")
        export_pdf_btn.clicked.connect(self.export_to_pdf)

        controls.addWidget(QLabel("Start:"))
        controls.addWidget(self.start_input)
        controls.addWidget(QLabel("End:"))
        controls.addWidget(self.end_input)
        controls.addWidget(refresh_btn)
        controls.addWidget(export_excel_btn)
        controls.addWidget(export_pdf_btn)

        layout.addLayout(controls)

        # Totals
        self.totals_label = QLabel("")
        layout.addWidget(self.totals_label)

        # Breakdown table
        self.table = QTableWidget(0, 7)
        self.table.setHorizontalHeaderLabels([
            "ID",
            "SKU",
            "Name",
            "Qty",
            "Revenue",
            "COGS",
            "Profit",
        ])
        self.table.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch
        )
        self.table.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Expanding,
        )

        layout.addWidget(self.table)

        self.setLayout(layout)
        self.refresh()

    def refresh(self):
        start = self.start_input.date().toString("yyyy-MM-dd")
        end = self.end_input.date().toString("yyyy-MM-dd")

        report = generate_profit_report(start, end)

        self.totals_label.setText(
            f"Total Revenue: {report['revenue']:.2f}    Total COGS: {report['cogs']:.2f}    Gross Profit: {report['gross_profit']:.2f}"
        )

        rows = report["breakdown"]
        self.table.setRowCount(len(rows))

        for r, p in enumerate(rows):
            self.table.setItem(r, 0, QTableWidgetItem(str(p["product_id"])))
            self.table.setItem(r, 1, QTableWidgetItem(str(p.get("sku") or "")))
            self.table.setItem(r, 2, QTableWidgetItem(p.get("name") or ""))
            self.table.setItem(r, 3, QTableWidgetItem(str(p.get("quantity_sold") or 0)))
            self.table.setItem(r, 4, QTableWidgetItem(f"{p.get('revenue',0):.2f}"))
            self.table.setItem(r, 5, QTableWidgetItem(f"{p.get('cogs',0):.2f}"))
            self.table.setItem(r, 6, QTableWidgetItem(f"{p.get('profit',0):.2f}"))

    def _get_report_data(self):
        start = self.start_input.date().toString("yyyy-MM-dd")
        end = self.end_input.date().toString("yyyy-MM-dd")
        return generate_profit_report(start, end)

    def export_to_excel(self):
        report = self._get_report_data()
        rows = report["breakdown"]
        if not rows:
            QMessageBox.warning(self, "No Data", "There is no profit data to export.")
            return

        export_rows = [
            {
                "Product ID": p["product_id"],
                "SKU": p.get("sku") or "",
                "Name": p.get("name") or "",
                "Quantity": p.get("quantity_sold") or 0,
                "Revenue": f"{p.get('revenue',0):.2f}",
                "COGS": f"{p.get('cogs',0):.2f}",
                "Profit": f"{p.get('profit',0):.2f}",
            }
            for p in rows
        ]

        df = pd.DataFrame(export_rows)
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save Profit Report",
            f"profit_report_{self.start_input.date().toString('yyyyMMdd')}_{self.end_input.date().toString('yyyyMMdd')}.xlsx",
            "Excel Files (*.xlsx)",
        )

        if file_path:
            df.to_excel(file_path, index=False)
            QMessageBox.information(
                self,
                "Exported",
                f"Profit report exported successfully to:\n{file_path}",
            )

    def export_to_pdf(self):
        report = self._get_report_data()
        rows = report["breakdown"]
        if not rows:
            QMessageBox.warning(self, "No Data", "There is no profit data to export.")
            return

        try:
            pdf = PDFExporter(self, filename="profit_report.pdf")
            pdf.draw_title("Profit Report")
            pdf.draw_user_info(
                {
                    "Start Date": self.start_input.date().toString("yyyy-MM-dd"),
                    "End Date": self.end_input.date().toString("yyyy-MM-dd"),
                    "Total Revenue": f"{report['revenue']:.2f}",
                    "Total COGS": f"{report['cogs']:.2f}",
                    "Gross Profit": f"{report['gross_profit']:.2f}",
                }
            )

            columns = [
                "Product ID",
                "SKU",
                "Name",
                "Qty",
                "Revenue",
                "COGS",
                "Profit",
            ]
            table_rows = [
                [
                    p["product_id"],
                    p.get("sku") or "",
                    p.get("name") or "",
                    p.get("quantity_sold") or 0,
                    f"{p.get('revenue',0):.2f}",
                    f"{p.get('cogs',0):.2f}",
                    f"{p.get('profit',0):.2f}",
                ]
                for p in rows
            ]
            col_widths = [
                pdf.usable_width * 0.10,
                pdf.usable_width * 0.13,
                pdf.usable_width * 0.30,
                pdf.usable_width * 0.08,
                pdf.usable_width * 0.16,
                pdf.usable_width * 0.12,
                pdf.usable_width * 0.11,
            ]
            pdf.draw_table(columns, table_rows, col_widths)
            pdf.finish()

            QMessageBox.information(
                self,
                "Exported",
                f"Profit report exported successfully to:\n{pdf.file_path}",
            )
        except ValueError:
            pass
        except Exception as e:
            QMessageBox.warning(self, "Export Error", f"Failed to export PDF: {str(e)}")
