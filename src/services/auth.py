import bcrypt
from sqlalchemy.exc import IntegrityError
from config.db import SessionLocal
from src.models.user import User, Session


# ==============================
# Authenticate User
# ==============================
def authenticateUser(username, password):
    db = SessionLocal()

    try:
        user = db.query(User).filter(User.username == username).first()

        if not user:
            return False

        if bcrypt.checkpw(password.encode(), user.password.encode()):
            createSession(user.id, db)
            return True

        return False

    finally:
        db.close()


# ==============================
# Create User
# ==============================
def createUser(username, password):
    db = SessionLocal()
    hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

    try:
        user = User(username=username, password=hashed)
        db.add(user)
        db.commit()
    except IntegrityError:
        db.rollback()
        raise ValueError("Username already exists")
    finally:
        db.close()


# ==============================
# Create Session
# ==============================
def createSession(user_id, db=None):
    close_after = False

    if db is None:
        db = SessionLocal()
        close_after = True

    try:
        db.query(Session).delete()
        db.add(Session(user_id=user_id))
        db.commit()
    finally:
        if close_after:
            db.close()


# ==============================
# Get Current Session
# ==============================
def getCurrentSession():
    db = SessionLocal()

    try:
        session = db.query(Session).first()
        return session.user_id if session else None
    finally:
        db.close()


# ==============================
# Logout
# ==============================
def logout():
    db = SessionLocal()

    try:
        db.query(Session).delete()
        db.commit()
    finally:
        db.close()


# ==============================
# Get User From Session
# ==============================
def getUserFromSession():
    db = SessionLocal()

    try:
        session = db.query(Session).first()

        if session and session.user:
            return {
                "name": session.user.name,
                "email": session.user.email,
            }

        return None

    finally:
        db.close()
