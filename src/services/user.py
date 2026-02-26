from config.db import SessionLocal
from src.models.user import User
from src.services.userAccount import getUserBalance
from PySide6.QtWidgets import QMessageBox, QFileDialog
import pandas as pd
from datetime import datetime
from sqlalchemy.exc import IntegrityError
from sqlalchemy import func


def addUser(name, email, contact=None, address=None, user_type="user"):
    """Add a new user"""
    if not name or not name.strip():
        raise ValueError("Name is required")
    if not email or not email.strip():
        raise ValueError("Email is required")
    valid_types = {"user", "employee", "customer", "supplier"}
    if user_type not in valid_types:
        raise ValueError("Invalid user type")

    with SessionLocal() as db:
        user = User(
            name=name.strip(),
            username=name.strip(),
            email=email.strip().lower(),
            contact=contact.strip() if contact else None,
            address=address.strip() if address else None,
            type=user_type,
        )
        db.add(user)
        try:
            db.commit()
            db.refresh(user)
            return user.id
        except IntegrityError:
            db.rollback()
            raise ValueError("Email already exists")


def getUser(user_id):
    """Fetch a single user by ID"""
    with SessionLocal() as db:
        return db.get(User, user_id)


def getAllUsers(type="user"):
    """Fetch all users of a given type"""
    with SessionLocal() as db:
        users = db.query(User).filter(User.type == type).all()
        return users


def updateUser(
    user_id, name=None, email=None, contact=None, address=None, user_type=None
):
    """Update user details. Only provided fields are updated"""
    if not user_id:
        raise ValueError("User ID is required")

    valid_types = {"user", "employee", "customer", "supplier"}
    with SessionLocal() as db:
        user = db.get(User, user_id)
        if not user:
            return False

        if name is not None:
            user.name = name.strip()
            user.username = name.strip()
        if email is not None:
            user.email = email.strip().lower()
        if contact is not None:
            user.contact = contact.strip() if contact else None
        if address is not None:
            user.address = address.strip() if address else None
        if user_type is not None:
            if user_type not in valid_types:
                raise ValueError("Invalid user type")
            user.type = user_type

        try:
            db.commit()
            return True
        except IntegrityError:
            db.rollback()
            raise ValueError("Email already exists")


def delete_user(user_id):
    """Delete a user by ID"""
    with SessionLocal() as db:
        user = db.get(User, user_id)
        if user:
            db.delete(user)
            db.commit()


def getMonthlyUserEntries():
    """Return list of (YYYY-MM, count)"""
    with SessionLocal() as db:
        results = (
            db.query(
                func.strftime("%Y-%m", User.date).label("year_month"),
                func.count(User.id).label("total"),
            )
            .filter(User.date != None)
            .group_by("year_month")
            .order_by("year_month")
            .all()
        )
        return results  # [('2026-01', 12), ('2026-02', 7)]


def exportToExcel(self):
    """Export all users to Excel with balance"""
    all_users = getAllUsers()
    if not all_users:
        QMessageBox.warning(self, "No Data", "There are no users to export.")
        return

    export_rows = []
    for user in all_users:
        balance = getUserBalance(user.id)
        export_rows.append(
            {
                "ID": user.id,
                "Name": user.name,
                "Email": user.email,
                "Contact": user.contact,
                "Address": user.address,
                "Date": user.date,
                "Balance": balance,
            }
        )

    df = pd.DataFrame(export_rows)

    now = datetime.now().strftime("%Y%m%d_%H%M%S")
    file_path, _ = QFileDialog.getSaveFileName(
        self,
        "Save Excel File",
        f"users_{now}.xlsx",
        "Excel Files (*.xlsx)",
    )

    if file_path:
        df.to_excel(file_path, index=False)
        QMessageBox.information(
            self, "Exported", f"Users exported successfully to:\n{file_path}"
        )
