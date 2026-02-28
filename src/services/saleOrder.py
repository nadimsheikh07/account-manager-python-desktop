from config.db import SessionLocal
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import selectinload
from src.models.sale import SaleOrder, SaleOrderProduct
from src.models.product import Product


def createSaleOrder(user_id, items):
    """
    items = [
        {"product_id": int, "quantity": int, "price": float}
    ]
    """

    if not user_id:
        raise ValueError("User is required")

    if not items:
        raise ValueError("At least one product is required")

    total_amount = 0

    for item in items:
        if item["quantity"] <= 0:
            raise ValueError("Quantity must be greater than 0")
        if item["price"] < 0:
            raise ValueError("Price must be non-negative")

        total_amount += item["quantity"] * item["price"]

    with SessionLocal() as db:
        try:
            order = SaleOrder(
                user_id=user_id,
                total_amount=total_amount,
            )
            db.add(order)
            db.flush()

            for item in items:
                order_product = SaleOrderProduct(
                    sale_order_id=order.id,
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
            raise ValueError("Invalid user or product reference")


def getAllSaleOrders(user_id=None):
    with SessionLocal() as db:
        query = db.query(SaleOrder).options(selectinload(SaleOrder.user))

        if user_id:
            query = query.filter(SaleOrder.user_id == user_id)

        return query.all()


def getSaleOrder(order_id):
    with SessionLocal() as db:
        return (
            db.query(SaleOrder)
            .options(
                selectinload(SaleOrder.user),
                selectinload(SaleOrder.products).selectinload(SaleOrderProduct.product),
            )
            .filter(SaleOrder.id == order_id)
            .first()
        )


def deleteSaleOrder(order_id):
    with SessionLocal() as db:
        order = db.get(SaleOrder, order_id)
        if order:
            db.delete(order)
            db.commit()
            return True
        return False
