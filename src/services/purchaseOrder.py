from config.db import SessionLocal
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import selectinload
from src.models.purchase import PurchaseOrder, PurchaseOrderProduct


def createPurchaseOrder(supplier_id, items):
    """
    Create a purchase order.

    :param supplier_id: int
    :param items: list of dicts -> [
        {"product_id": int, "quantity": int, "price": float}
    ]
    """

    if not supplier_id:
        raise ValueError("Supplier ID is required")

    if not items or not isinstance(items, list):
        raise ValueError("At least one product item is required")

    total_amount = 0

    for item in items:
        if item["quantity"] <= 0:
            raise ValueError("Quantity must be greater than 0")
        if item["price"] < 0:
            raise ValueError("Price must be non-negative")

        total_amount += item["quantity"] * item["price"]

    with SessionLocal() as db:
        try:
            order = PurchaseOrder(
                supplier_id=supplier_id,
                total_amount=total_amount,
            )
            db.add(order)
            db.flush()  # get order.id before commit

            for item in items:
                order_product = PurchaseOrderProduct(
                    purchase_order_id=order.id,
                    product_id=item["product_id"],
                    quantity=item["quantity"],
                    price=item["price"],
                )
                db.add(order_product)

            db.commit()
            db.refresh(order)
            return order.id

        except IntegrityError:
            db.rollback()
            raise ValueError("Invalid supplier or product reference")


def getPurchaseOrder(order_id):
    """Fetch purchase order with products eagerly loaded"""
    with SessionLocal() as db:
        return (
            db.query(PurchaseOrder)
            .options(
                selectinload(PurchaseOrder.supplier),
                selectinload(PurchaseOrder.products).selectinload(
                    PurchaseOrderProduct.product
                )
            )
            .filter(PurchaseOrder.id == order_id)
            .first()
        )


from sqlalchemy.orm import selectinload
from src.models.user import User


def getAllPurchaseOrders(supplier_id=None):
    """Fetch all purchase orders with supplier eagerly loaded"""
    with SessionLocal() as db:
        query = db.query(PurchaseOrder).options(
            selectinload(PurchaseOrder.supplier)
        )  # 🔥 FIX

        if supplier_id:
            query = query.filter(PurchaseOrder.supplier_id == supplier_id)

        return query.all()


def deletePurchaseOrder(order_id):
    """Delete purchase order (cascade deletes items)"""
    with SessionLocal() as db:
        order = db.get(PurchaseOrder, order_id)
        if order:
            db.delete(order)
            db.commit()
            return True
        return False
