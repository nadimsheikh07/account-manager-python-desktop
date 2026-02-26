from sqlalchemy.exc import IntegrityError
from config.db import Base, engine, SessionLocal
from src.models import User
import bcrypt


def init_db():
    """
    Initialize database tables and create default admin user.
    """

    # 1️⃣ Create all tables
    Base.metadata.create_all(bind=engine)

    # 2️⃣ Default admin credentials
    default_name = "Nadim Sheikh"
    default_username = "admin"
    default_email = "nadim.sheikh.07@gmail.com"
    default_password = "admin"

    db = SessionLocal()

    try:
        # 3️⃣ Check if admin already exists
        existing_user = db.query(User).filter(User.username == default_username).first()

        if not existing_user:
            hashed = bcrypt.hashpw(default_password.encode(), bcrypt.gensalt()).decode()

            admin_user = User(
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
