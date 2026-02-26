from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    ForeignKey,
    DateTime,
    CheckConstraint,
)
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from config.db import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    name = Column(String)
    username = Column(String, unique=True, nullable=False)
    email = Column(String, unique=True, nullable=False, index=True)
    contact = Column(String)
    address = Column(Text)
    password = Column(String)

    type = Column(String, nullable=False, default="user")

    date = Column(DateTime, server_default=func.now())

    __table_args__ = (
        CheckConstraint(
            "type IN ('user', 'employee', 'customer', 'supplier')",
            name="check_user_type",
        ),
    )

    session = relationship("Session", back_populates="user", cascade="all, delete")
    accounts = relationship("UserAccount", back_populates="user", cascade="all, delete")
    purchase_orders = relationship("PurchaseOrder", back_populates="supplier")
    sale_orders = relationship("SaleOrder", back_populates="user")


class Session(Base):
    __tablename__ = "session"

    id = Column(Integer, primary_key=True)
    user_id = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    description = Column(Text)
    date = Column(DateTime, server_default=func.now())

    user = relationship("User", back_populates="session")


class UserAccount(Base):
    __tablename__ = "user_accounts"

    id = Column(Integer, primary_key=True)
    user_id = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )

    type = Column(String, nullable=False)
    amount = Column(Integer, nullable=False)
    description = Column(Text)
    date = Column(DateTime, server_default=func.now())

    __table_args__ = (
        CheckConstraint("type IN ('CR', 'DR')", name="check_account_type"),
        CheckConstraint("amount >= 0", name="check_account_amount"),
    )

    user = relationship("User", back_populates="accounts")
