from config.db import SessionLocal
from src.models.product import ProductStock, StockType
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import joinedload


# =============================
# CREATE / ADD STOCK
# =============================
def addProductStock(product_id, quantity, type="in"):
    """Add a new stock entry for a product"""
    if quantity < 0:
        raise ValueError("Quantity cannot be negative")

    # Validate type
    if type not in ("in", "out"):
        raise ValueError("Stock type must be 'in' or 'out'")

    with SessionLocal() as db:
        stock = ProductStock(
            product_id=product_id,
            quantity=quantity,
            type=StockType.IN if type == "in" else StockType.OUT,
        )
        db.add(stock)
        try:
            db.commit()
            db.refresh(stock)
            return stock.id
        except IntegrityError:
            db.rollback()
            raise ValueError("Error adding stock")


# =============================
# READ / FETCH STOCK
# =============================
def getProductStock(stock_id):
    """Fetch stock info by stock ID"""
    with SessionLocal() as db:
        return db.get(ProductStock, stock_id)


def getAllProductStocks(product_id=None):
    """Return all stocks, with product info, optionally filtered by product_id"""
    with SessionLocal() as db:
        # Eagerly load the product relationship
        query = db.query(ProductStock).options(joinedload(ProductStock.product))
        if product_id is not None:
            query = query.filter(ProductStock.product_id == product_id)
        return query.all()


# =============================
# UPDATE STOCK
# =============================
def updateProductStock(stock_id, product_id=None, quantity=None, type=None):
    """Update stock entry using stock ID"""
    with SessionLocal() as db:
        stock = db.get(ProductStock, stock_id)
        if not stock:
            return False

        if product_id is not None:
            stock.product_id = product_id

        if quantity is not None:
            if quantity < 0:
                raise ValueError("Quantity cannot be negative")
            stock.quantity = quantity

        if type is not None:
            if type not in ("in", "out"):
                raise ValueError("Stock type must be 'in' or 'out'")
            stock.type = StockType.IN if type == "in" else StockType.OUT

        try:
            db.commit()
            return True
        except IntegrityError:
            db.rollback()
            raise ValueError("Error updating stock")


# =============================
# DELETE STOCK
# =============================
def deleteProductStock(stock_id):
    """Delete stock entry by stock ID"""
    with SessionLocal() as db:
        stock = db.get(ProductStock, stock_id)
        if stock:
            db.delete(stock)
            db.commit()
