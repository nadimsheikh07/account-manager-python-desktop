from alembic import command
from alembic.config import Config
from sqlalchemy.exc import IntegrityError
from config.db import SessionLocal
import src.models
import bcrypt
from pathlib import Path


def run_migrations():
    """Run all pending Alembic migrations."""
    # Locate the repository root (two levels up from src/services)
    repo_root = Path(__file__).resolve().parents[2]
    alembic_cfg = Config(str(repo_root / "alembic.ini"))

    command.upgrade(alembic_cfg, "head")


def init_db():
    """Run migrations and create default admin user."""

    # Run migrations
    run_migrations()

    db = SessionLocal()

    try:
        default_name = "Nadim Sheikh"
        default_username = "admin"
        default_email = "nadim.sheikh.07@gmail.com"
        default_password = "admin"

        existing_user = (
            db.query(src.models.User)
            .filter(src.models.User.username == default_username)
            .first()
        )

        if existing_user is None:
            hashed = bcrypt.hashpw(
                default_password.encode(),
                bcrypt.gensalt(),
            ).decode()

            admin = src.models.User(
                name=default_name,
                username=default_username,
                email=default_email,
                password=hashed,
                type="user",
            )

            db.add(admin)
            db.commit()

            print("✓ Default admin user created.")
        else:
            print("✓ Default admin already exists.")

    except IntegrityError:
        db.rollback()
        print("✗ Integrity error while creating admin.")

    finally:
        db.close()
