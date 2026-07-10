from sqlalchemy import (
    Column,
    Integer,
    Float,
    ForeignKey,
    DateTime,
    CheckConstraint,
    Index,
)
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from config.db import Base


class PurchaseOrder(Base):
    __tablename__ = "purchase_orders"

    id = Column(Integer, primary_key=True)
    supplier_id = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    total_amount = Column(Float, nullable=False)
    date = Column(DateTime, server_default=func.now())

    __table_args__ = (
        CheckConstraint("total_amount >= 0", name="check_purchase_total"),
    )

    supplier = relationship("User", back_populates="purchase_orders")
    products = relationship(
        "PurchaseOrderProduct", back_populates="order", cascade="all, delete"
    )


class PurchaseOrderProduct(Base):
    __tablename__ = "purchase_order_products"

    id = Column(Integer, primary_key=True)
    purchase_order_id = Column(
        Integer, ForeignKey("purchase_orders.id", ondelete="CASCADE"), nullable=False
    )
    product_id = Column(
        Integer, ForeignKey("products.id", ondelete="CASCADE"), nullable=False
    )

    quantity = Column(Integer, nullable=False)
    price = Column(Float, nullable=False)
    tax = Column(Float, nullable=False, default=0.0)

    __table_args__ = (
        CheckConstraint("quantity >= 0", name="check_purchase_quantity"),
        CheckConstraint("price >= 0", name="check_purchase_price"),
        Index("idx_purchase_order_products_order_id", "purchase_order_id"),
        Index("idx_purchase_order_products_product_id", "product_id"),
    )

    order = relationship("PurchaseOrder", back_populates="products")
    product = relationship("Product", back_populates="purchase_items")
