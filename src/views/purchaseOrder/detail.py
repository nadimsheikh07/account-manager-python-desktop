from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
    QMessageBox,
    QPushButton,
)
from config.theme import getGlobalStylesheet
from src.components.heading import createTitle
from src.controllers.purchase_controller import PurchaseController
from utils.pdfUtils import PDFExporter


class PurchaseOrderDetail(QWidget):
    def __init__(self, order_id):
        super().__init__()
        self.order_id = order_id
        self.setWindowTitle(f"Purchase Order #{order_id}")
        self.setMinimumSize(760, 460)
        self.setStyleSheet(getGlobalStylesheet())
        self.controller = PurchaseController()

        self.init_ui()
        self.load_data()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)

        layout.addWidget(createTitle("Purchase Order Detail"))

        self.summary_label = QLabel("")
        layout.addWidget(self.summary_label)

        self.export_btn = QPushButton("Export Invoice")
        self.export_btn.setProperty("class", "primary")
        self.export_btn.clicked.connect(self.export_invoice)
        layout.addWidget(self.export_btn)

        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels(
            ["Product", "Quantity", "Price", "Tax (%)", "Tax Amount", "Total", "Product ID"]
        )
        self.table.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch
        )
        self.table.setColumnHidden(6, True)
        layout.addWidget(self.table)

    def load_data(self):
        order = self.controller.get_order_by_id(self.order_id)
        if not order:
            QMessageBox.warning(self, "Not Found", "Purchase order not found.")
            self.close()
            return

        supplier_name = order.supplier.name if order.supplier else "Unknown"
        order_date = order.date.strftime("%Y-%m-%d %H:%M:%S") if order.date else "-"
        self.summary_label.setText(
            f"Supplier: {supplier_name}   |   Date: {order_date}   |   Total: {order.total_amount:.2f}"
        )

        items = order.products or []
        self.table.setRowCount(len(items))

        for row, item in enumerate(items):
            product_name = item.product.name if item.product else "Unknown Product"
            subtotal = item.quantity * item.price
            tax_percent = float(getattr(item, "tax", 0) or 0)
            tax_amount = subtotal * (tax_percent / 100)
            total = subtotal + tax_amount

            self.table.setItem(row, 0, QTableWidgetItem(product_name))
            self.table.setItem(row, 1, QTableWidgetItem(str(item.quantity)))
            self.table.setItem(row, 2, QTableWidgetItem(f"{item.price:.2f}"))
            self.table.setItem(row, 3, QTableWidgetItem(f"{tax_percent:.2f}"))
            self.table.setItem(row, 4, QTableWidgetItem(f"{tax_amount:.2f}"))
            self.table.setItem(row, 5, QTableWidgetItem(f"{total:.2f}"))
            self.table.setItem(row, 6, QTableWidgetItem(str(item.product_id)))

    def export_invoice(self):
        order = self.controller.get_order_by_id(self.order_id)
        if not order:
            QMessageBox.warning(self, "Error", "Purchase order not found.")
            return

        supplier_name = order.supplier.name if order.supplier else "Unknown"
        supplier_email = getattr(order.supplier, "email", "")
        supplier_contact = getattr(order.supplier, "contact", "")
        order_date = order.date.strftime("%Y-%m-%d %H:%M:%S") if order.date else "-"

        try:
            pdf = PDFExporter(
                self,
                filename=f"purchase_invoice_{order.id}.pdf",
            )
            pdf.draw_title("Purchase Invoice")
            pdf.draw_invoice_header(order.id, order_date)
            pdf.draw_user_info(
                {
                    "Supplier": supplier_name,
                    "Email": supplier_email,
                    "Contact": supplier_contact,
                }
            )

            table_rows = []
            subtotal_total = 0.0
            tax_total = 0.0
            for item in order.products or []:
                product_name = item.product.name if item.product else "Unknown Product"
                subtotal = item.quantity * item.price
                tax_percent = float(getattr(item, "tax", 0) or 0)
                tax_amount = subtotal * (tax_percent / 100)
                total = subtotal + tax_amount
                subtotal_total += subtotal
                tax_total += tax_amount
                table_rows.append(
                    [
                        product_name,
                        item.quantity,
                        f"{item.price:.2f}",
                        f"{tax_percent:.2f}",
                        f"{tax_amount:.2f}",
                        f"{total:.2f}",
                    ]
                )

            columns = ["Product", "Qty", "Unit Price", "Tax (%)", "Tax Amount", "Total"]
            col_widths = [
                pdf.usable_width * 0.28,
                pdf.usable_width * 0.10,
                pdf.usable_width * 0.12,
                pdf.usable_width * 0.10,
                pdf.usable_width * 0.12,
                pdf.usable_width * 0.28,
            ]
            pdf.draw_table(columns, table_rows, col_widths)
            pdf.draw_summary(
                {
                    "Subtotal": subtotal_total,
                    "Tax": tax_total,
                    "Total Amount": order.total_amount,
                }
            )
            pdf.finish()

            QMessageBox.information(
                self,
                "Exported",
                f"Purchase invoice exported successfully to:\n{pdf.file_path}",
            )
        except ValueError:
            pass
        except Exception as e:
            QMessageBox.warning(self, "Export Error", f"Failed to export invoice: {str(e)}")
