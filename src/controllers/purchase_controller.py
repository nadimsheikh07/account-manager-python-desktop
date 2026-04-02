from src.services.purchaseOrder import (
    createPurchaseOrder,
    getPurchaseOrder,
    getAllPurchaseOrders,
    deletePurchaseOrder,
)


class PurchaseController:
    def get_all_orders(self, supplier_id=None):
        """Fetches all purchase orders, optionally filtered by supplier."""
        try:
            return getAllPurchaseOrders(supplier_id)
        except Exception:
            return []

    def get_order_by_id(self, order_id):
        """Fetches a specific purchase order by its ID."""
        try:
            return getPurchaseOrder(order_id)
        except Exception:
            return None

    def save_order(self, supplier_id, items):
        """Creates a new purchase order."""
        try:
            order_id = createPurchaseOrder(supplier_id, items)
            return True, f"Purchase order #{order_id} created successfully.", order_id
        except ValueError as e:
            return False, str(e), None
        except Exception as e:
            return False, f"Failed to create purchase order: {str(e)}", None

    def delete_order(self, order_id):
        """Deletes a purchase order."""
        try:
            if deletePurchaseOrder(order_id):
                return True, "Purchase order deleted successfully."
            return False, "Purchase order not found."
        except Exception as e:
            return False, f"Failed to delete purchase order: {str(e)}"
