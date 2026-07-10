from sqlalchemy.exc import IntegrityError
from sqlalchemy import inspect, text
from config.db import Base, engine, SessionLocal
import src.models
import bcrypt


def _ensure_inventory_columns():
    """Add missing inventory columns for older SQLite databases."""
    inspector = inspect(engine)

    category_columns = {col["name"] for col in inspector.get_columns("categories")}
    product_columns = {col["name"] for col in inspector.get_columns("products")}
    purchase_item_columns = {
        col["name"] for col in inspector.get_columns("purchase_order_products")
    }
    sale_item_columns = {col["name"] for col in inspector.get_columns("sale_order_products")}

    statements = []
    if "tax" not in category_columns:
        statements.append(
            "ALTER TABLE categories ADD COLUMN tax FLOAT NOT NULL DEFAULT 0.0"
        )
    if "hsn_code" not in product_columns:
        statements.append("ALTER TABLE products ADD COLUMN hsn_code VARCHAR")
    if "tax" not in product_columns:
        statements.append(
            "ALTER TABLE products ADD COLUMN tax FLOAT NOT NULL DEFAULT 0.0"
        )
    if "cost" not in product_columns:
        statements.append(
            "ALTER TABLE products ADD COLUMN cost FLOAT NOT NULL DEFAULT 0.0"
        )
    if "tax" not in purchase_item_columns:
        statements.append(
            "ALTER TABLE purchase_order_products ADD COLUMN tax FLOAT NOT NULL DEFAULT 0.0"
        )
    if "tax" not in sale_item_columns:
        statements.append(
            "ALTER TABLE sale_order_products ADD COLUMN tax FLOAT NOT NULL DEFAULT 0.0"
        )

    if not statements:
        return

    with engine.begin() as connection:
        for statement in statements:
            connection.execute(text(statement))


def init_db():
    """
    Initialize database tables and create default admin user.
    """

    # 1️⃣ Create all tables
    Base.metadata.create_all(bind=engine)
    _ensure_inventory_columns()

    # 2️⃣ Default admin credentials
    default_name = "Nadim Sheikh"
    default_username = "admin"
    default_email = "nadim.sheikh.07@gmail.com"
    default_password = "admin"

    db = SessionLocal()

    try:
        # 3️⃣ Check if admin already exists
        existing_user = db.query(src.models.User).filter(src.models.User.username == default_username).first()

        if not existing_user:
            hashed = bcrypt.hashpw(default_password.encode(), bcrypt.gensalt()).decode()

            admin_user = src.models.User(
                name=default_name,
                username=default_username,
                email=default_email,
                password=hashed,
                type="user",  # or "employee" if needed
            )

            db.add(admin_user)
            db.commit()

            print("Default admin user created.")

    except IntegrityError:
        db.rollback()
        print("Admin already exists or integrity error.")

    finally:
        db.close()
