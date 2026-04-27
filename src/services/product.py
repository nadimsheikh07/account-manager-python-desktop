from config.db import SessionLocal
from src.models.product import Product
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import selectinload


def addProduct(
    name,
    category_id,
    price,
    cost=0.0,
    sku=None,
    description=None,
    hsn_code=None,
    tax=0.0,
):
    """Add a new product"""
    if not name or not name.strip():
        raise ValueError("Product name is required")
    if price is None or price < 0:
        raise ValueError("Price must be a positive number")
    if cost is None or cost < 0:
        raise ValueError("Cost must be a non-negative number")
    if tax is None or tax < 0:
        raise ValueError("Tax must be a non-negative number")

    with SessionLocal() as db:
        product = Product(
            name=name.strip(),
            category_id=category_id,
            price=price,
            cost=cost,
            sku=sku.strip() if sku else None,
            hsn_code=hsn_code.strip() if hsn_code else None,
            tax=tax,
            description=description.strip() if description else None,
        )
        db.add(product)
        try:
            db.commit()
            db.refresh(product)
            return product.id
        except IntegrityError:
            db.rollback()
            raise ValueError("SKU must be unique")


def getProduct(product_id):
    """Fetch a product by ID"""
    with SessionLocal() as db:
        return db.get(Product, product_id)


def getAllProducts(category_id=None):
    """Fetch all products, optionally filtered by category, with categories eagerly loaded"""
    with SessionLocal() as db:
        query = db.query(Product).options(selectinload(Product.category))
        if category_id is not None:
            query = query.filter(Product.category_id == category_id)
        products = query.all()  # category is already loaded
        return products


def updateProduct(
    product_id,
    name=None,
    category_id=None,
    price=None,
    cost=None,
    sku=None,
    description=None,
    hsn_code=None,
    tax=None,
):
    """Update product details"""
    if not product_id:
        raise ValueError("Product ID is required")

    with SessionLocal() as db:
        product = db.get(Product, product_id)
        if not product:
            return False

        if name is not None:
            product.name = name.strip()
        if category_id is not None:
            product.category_id = category_id
        if price is not None:
            if price < 0:
                raise ValueError("Price must be non-negative")
            product.price = price
        if cost is not None:
            if cost < 0:
                raise ValueError("Cost must be non-negative")
            product.cost = cost
        if sku is not None:
            product.sku = sku.strip() if sku else None
        if hsn_code is not None:
            product.hsn_code = hsn_code.strip() if hsn_code else None
        if tax is not None:
            if tax < 0:
                raise ValueError("Tax must be non-negative")
            product.tax = tax
        if description is not None:
            product.description = description.strip() if description else None

        try:
            db.commit()
            return True
        except IntegrityError:
            db.rollback()
            raise ValueError("SKU must be unique")


def deleteProduct(product_id):
    """Delete a product by ID"""
    with SessionLocal() as db:
        product = db.get(Product, product_id)
        if product:
            db.delete(product)
            db.commit()
