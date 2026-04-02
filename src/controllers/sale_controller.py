from src.services.saleOrder import (
    createSaleOrder,
    getAllSaleOrders,
    getSaleOrder,
    deleteSaleOrder,
)


class SaleController:
    def get_all_orders(self, user_id=None):
        """Fetches all sale orders, optionally filtered by user."""
        try:
            return getAllSaleOrders(user_id)
        except Exception:
            return []

    def get_order_by_id(self, order_id):
        """Fetches a specific sale order by its ID."""
        try:
            return getSaleOrder(order_id)
        except Exception:
            return None

    def save_order(self, user_id, items):
        """Creates a new sale order."""
        try:
            order_id = createSaleOrder(user_id, items)
            return True, f"Sale order #{order_id} created successfully.", order_id
        except ValueError as e:
            return False, str(e), None
        except Exception as e:
            return False, f"Failed to create sale order: {str(e)}", None

    def delete_order(self, order_id):
        """Deletes a sale order."""
        try:
            if deleteSaleOrder(order_id):
                return True, "Sale order deleted successfully."
            return False, "Sale order not found."
        except Exception as e:
            return False, f"Failed to delete sale order: {str(e)}"
