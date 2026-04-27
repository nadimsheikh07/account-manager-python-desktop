from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    ForeignKey,
    DateTime,
    Float,
    CheckConstraint,
    Index,
    Enum,
)
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from config.db import Base
import enum


class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True)
    parent_id = Column(Integer, ForeignKey("categories.id", ondelete="SET NULL"))
    name = Column(String, unique=True, nullable=False)
    tax = Column(Float, nullable=False, default=0.0)
    description = Column(Text)
    date = Column(DateTime, server_default=func.now())

    products = relationship("Product", back_populates="category", cascade="all, delete")


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True)
    category_id = Column(
        Integer, ForeignKey("categories.id", ondelete="CASCADE"), nullable=False
    )

    name = Column(String, nullable=False)
    sku = Column(String, unique=True, index=True)
    hsn_code = Column(String)
    tax = Column(Float, nullable=False, default=0.0)
    price = Column(Float, nullable=False, default=0.0)
    cost = Column(Float, nullable=False, default=0.0)
    description = Column(Text)
    date = Column(DateTime, server_default=func.now())

    __table_args__ = (
        CheckConstraint("price >= 0", name="check_product_price"),
        CheckConstraint("cost >= 0", name="check_product_cost"),
        Index("idx_products_category_id", "category_id"),
    )

    category = relationship("Category", back_populates="products")
    stock = relationship(
        "ProductStock", back_populates="product", uselist=False, cascade="all, delete"
    )
    purchase_items = relationship("PurchaseOrderProduct", back_populates="product")
    sale_items = relationship("SaleOrderProduct", back_populates="product")


# Define stock type enum
class StockType(enum.Enum):
    IN = "in"
    OUT = "out"


class ProductStock(Base):
    __tablename__ = "product_stocks"

    id = Column(Integer, primary_key=True)
    product_id = Column(
        Integer, ForeignKey("products.id", ondelete="CASCADE"), nullable=False
    )
    quantity = Column(Integer, nullable=False)
    type = Column(Enum(StockType), nullable=False, server_default=StockType.IN.value)
    last_updated = Column(DateTime, server_default=func.now(), onupdate=func.now())

    __table_args__ = (
        CheckConstraint("quantity >= 0", name="check_stock_quantity"),
        Index("idx_product_stocks_product_id", "product_id"),
    )

    product = relationship("Product", back_populates="stock")
