from src.services.productStock import (
    addProductStock,
    deleteProductStock,
    getAllProductStocks,
    getProductStock,
    updateProductStock,
)
from src.services.product import getAllProducts


class ProductStockController:
    def get_products(self):
        """Fetch all products for the stock form selection."""
        return getAllProducts()

    def get_stocks(self, query=""):
        """Fetch all stocks and filter by product name."""
        stocks = getAllProductStocks()
        rows = [self._orm_to_dict(s) for s in stocks]

        normalized_query = (query or "").strip().lower()
        if normalized_query:
            rows = [
                item
                for item in rows
                if normalized_query in item["product"].lower()
            ]
        return rows

    def get_stock_by_id(self, stock_id):
        """Fetch stock info by stock ID."""
        return getProductStock(stock_id)

    def validate_stock_form(self, product_id, quantity_text, stock_type):
        """Validate stock form data."""
        errors = {}

        if not product_id:
            errors["product"] = "Product is required"

        cleaned_qty_text = (str(quantity_text) or "").strip()
        parsed_qty = None
        try:
            parsed_qty = int(cleaned_qty_text)
            if parsed_qty < 0:
                raise ValueError
        except ValueError:
            errors["quantity"] = "Quantity must be 0 or more"

        if stock_type not in ("in", "out"):
            errors["type"] = "Invalid stock type"

        payload = {
            "product_id": product_id,
            "quantity": parsed_qty,
            "type": stock_type,
        }
        return len(errors) == 0, errors, payload

    def save_stock(self, stock_id, product_id, quantity_text, stock_type):
        """Save (add or update) stock entry."""
        is_valid, errors, payload = self.validate_stock_form(
            product_id=product_id, quantity_text=quantity_text, stock_type=stock_type
        )
        if not is_valid:
            return False, "Please fix errors.", errors

        try:
            if stock_id:
                updateProductStock(stock_id, **payload)
                return True, "Stock updated successfully.", {}
            
            addProductStock(
                payload["product_id"],
                payload["quantity"],
                payload["type"],
            )
            return True, "Stock added successfully.", {}
        except ValueError as exc:
            return False, str(exc), {}

    def delete_stock(self, stock_id):
        """Delete stock entry by ID."""
        try:
            deleteProductStock(stock_id)
            return True, "Stock deleted successfully."
        except Exception as exc:
            return False, str(exc)

    def _orm_to_dict(self, stock):
        """Convert ProductStock ORM object to dictionary."""
        return {
            "id": stock.id,
            "product": stock.product.name if stock.product else "Unknown",
            "product_id": stock.product_id,
            "type": stock.type.value if hasattr(stock.type, "value") else stock.type,
            "quantity": stock.quantity,
            "last_updated": (
                stock.last_updated.strftime("%Y-%m-%d %H:%M:%S")
                if stock.last_updated
                else ""
            ),
        }
