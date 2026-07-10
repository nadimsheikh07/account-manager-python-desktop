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


class SaleOrder(Base):
    __tablename__ = "sale_orders"

    id = Column(Integer, primary_key=True)
    user_id = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    total_amount = Column(Float, nullable=False)
    date = Column(DateTime, server_default=func.now())

    __table_args__ = (CheckConstraint("total_amount >= 0", name="check_sale_total"),)

    user = relationship("User", back_populates="sale_orders")
    products = relationship(
        "SaleOrderProduct", back_populates="order", cascade="all, delete"
    )


class SaleOrderProduct(Base):
    __tablename__ = "sale_order_products"

    id = Column(Integer, primary_key=True)
    sale_order_id = Column(
        Integer, ForeignKey("sale_orders.id", ondelete="CASCADE"), nullable=False
    )
    product_id = Column(
        Integer, ForeignKey("products.id", ondelete="CASCADE"), nullable=False
    )

    quantity = Column(Integer, nullable=False)
    price = Column(Float, nullable=False)
    tax = Column(Float, nullable=False, default=0.0)

    __table_args__ = (
        CheckConstraint("quantity >= 0", name="check_sale_quantity"),
        CheckConstraint("price >= 0", name="check_sale_price"),
        Index("idx_sale_order_products_order_id", "sale_order_id"),
        Index("idx_sale_order_products_product_id", "product_id"),
    )

    order = relationship("SaleOrder", back_populates="products")
    product = relationship("Product", back_populates="sale_items")
