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
from src.controllers.sale_controller import SaleController
from utils.pdfUtils import PDFExporter


class SaleOrderDetail(QWidget):
    def __init__(self, order_id):
        super().__init__()
        self.order_id = order_id
        self.setWindowTitle(f"Sale Order #{order_id}")
        self.setMinimumSize(760, 460)
        self.setStyleSheet(getGlobalStylesheet())
        self.controller = SaleController()

        self.init_ui()
        self.load_data()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)

        layout.addWidget(createTitle("Sale Order Detail"))

        self.summary_label = QLabel("")
        layout.addWidget(self.summary_label)

        self.export_btn = QPushButton("Export Invoice")
        self.export_btn.setProperty("class", "primary")
        self.export_btn.clicked.connect(self.export_invoice)
        layout.addWidget(self.export_btn)

        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(
            ["Product", "Quantity", "Price", "Subtotal", "Product ID"]
        )
        self.table.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch
        )
        self.table.setColumnHidden(4, True)
        layout.addWidget(self.table)

    def load_data(self):
        order = self.controller.get_order_by_id(self.order_id)
        if not order:
            QMessageBox.warning(self, "Not Found", "Sale order not found.")
            self.close()
            return

        customer_name = order.user.name if order.user else "Unknown"
        order_date = order.date.strftime("%Y-%m-%d %H:%M:%S") if order.date else "-"
        self.summary_label.setText(
            f"Customer: {customer_name}   |   Date: {order_date}   |   Total: {order.total_amount:.2f}"
        )

        items = order.products or []
        self.table.setRowCount(len(items))

        for row, item in enumerate(items):
            product_name = item.product.name if item.product else "Unknown Product"
            subtotal = item.quantity * item.price

            self.table.setItem(row, 0, QTableWidgetItem(product_name))
            self.table.setItem(row, 1, QTableWidgetItem(str(item.quantity)))
            self.table.setItem(row, 2, QTableWidgetItem(f"{item.price:.2f}"))
            self.table.setItem(row, 3, QTableWidgetItem(f"{subtotal:.2f}"))
            self.table.setItem(row, 4, QTableWidgetItem(str(item.product_id)))

    def export_invoice(self):
        order = self.controller.get_order_by_id(self.order_id)
        if not order:
            QMessageBox.warning(self, "Error", "Sale order not found.")
            return

        customer_name = order.user.name if order.user else "Unknown"
        customer_email = getattr(order.user, "email", "")
        customer_contact = getattr(order.user, "contact", "")
        order_date = order.date.strftime("%Y-%m-%d %H:%M:%S") if order.date else "-"

        try:
            pdf = PDFExporter(
                self,
                filename=f"sales_invoice_{order.id}.pdf",
            )
            pdf.draw_title("Sales Invoice")
            pdf.draw_invoice_header(order.id, order_date)
            pdf.draw_user_info(
                {
                    "Customer": customer_name,
                    "Email": customer_email,
                    "Contact": customer_contact,
                }
            )

            table_rows = []
            for item in order.products or []:
                product_name = item.product.name if item.product else "Unknown Product"
                subtotal = item.quantity * item.price
                table_rows.append(
                    [
                        product_name,
                        item.quantity,
                        f"{item.price:.2f}",
                        f"{subtotal:.2f}",
                    ]
                )

            columns = ["Product", "Qty", "Unit Price", "Subtotal"]
            col_widths = [pdf.usable_width * 0.40, pdf.usable_width * 0.20, pdf.usable_width * 0.20, pdf.usable_width * 0.20]
            pdf.draw_table(columns, table_rows, col_widths)
            pdf.draw_summary({"Total Amount": order.total_amount})
            pdf.finish()

            QMessageBox.information(
                self,
                "Exported",
                f"Sales invoice exported successfully to:\n{pdf.file_path}",
            )
        except ValueError:
            pass
        except Exception as e:
            QMessageBox.warning(self, "Export Error", f"Failed to export invoice: {str(e)}")
