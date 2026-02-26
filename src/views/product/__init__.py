from PySide6.QtWidgets import QWidget, QVBoxLayout, QTabWidget
from config.theme import getGlobalStylesheet
from src.views.product.categories.index import CategoryList
from src.views.product.products.index import ProductList
from src.views.product.productStocks.index import ProductStockList


class InventoryPanel(QWidget):
    """Tabbed interface for managing Categories, Products, and Product Stocks."""

    def __init__(self):
        super().__init__()
        self.setMinimumSize(800, 500)
        self.setStyleSheet(getGlobalStylesheet())

        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(10)

        self.tabs = QTabWidget()
        self.tabs.addTab(CategoryList(), "Categories")
        self.tabs.addTab(ProductList(), "Products")
        self.tabs.addTab(ProductStockList(), "Stocks")

        layout.addWidget(self.tabs)
