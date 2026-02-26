from config.db import SessionLocal
from src.models.product import Category
from sqlalchemy.exc import IntegrityError


def addCategory(name, description=None, parent_id=None):
    """Add a new category"""
    if not name or not name.strip():
        raise ValueError("Category name is required")

    with SessionLocal() as db:
        category = Category(
            name=name.strip(),
            description=description.strip() if description else None,
            parent_id=parent_id,
        )
        db.add(category)
        try:
            db.commit()
            db.refresh(category)
            return category.id
        except IntegrityError:
            db.rollback()
            raise ValueError("Category name already exists")


def getCategory(category_id):
    """Fetch a category by ID"""
    with SessionLocal() as db:
        return db.get(Category, category_id)


def getAllCategories():
    """Fetch all categories"""
    with SessionLocal() as db:
        return db.query(Category).all()


def updateCategory(category_id, name=None, description=None, parent_id=None):
    """Update category details"""
    if not category_id:
        raise ValueError("Category ID is required")

    with SessionLocal() as db:
        category = db.get(Category, category_id)
        if not category:
            return False

        if name is not None:
            category.name = name.strip()
        if description is not None:
            category.description = description.strip() if description else None
        if parent_id is not None:
            category.parent_id = parent_id

        try:
            db.commit()
            return True
        except IntegrityError:
            db.rollback()
            raise ValueError("Category name already exists")


def deleteCategory(category_id):
    """Delete a category by ID"""
    with SessionLocal() as db:
        category = db.get(Category, category_id)
        if category:
            db.delete(category)
            db.commit()
