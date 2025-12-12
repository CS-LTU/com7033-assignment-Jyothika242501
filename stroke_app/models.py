# stroke_app/models.py

"""
models.py
---------
Contains database models for:
1. SQLite Patient table (SQLAlchemy)
2. MongoDB User model wrapper (Flask-Login compatible)

This separation allows:
- SQL database for structured medical records
- MongoDB for flexible authentication storage
"""

from flask_login import UserMixin
from . import db, mongo


# -----------------------------------------------------------
# SQLALCHEMY PATIENT MODEL  (SQLite)
# -----------------------------------------------------------
# stroke_app/models.py

from . import db

class Patient(db.Model):
    __tablename__ = "patients"

    # Primary Key
    id = db.Column(db.Integer, primary_key=True)

    # Basic fields exactly matching CSV
    gender = db.Column(db.String(10))
    age = db.Column(db.Float)
    hypertension = db.Column(db.Integer)
    heart_disease = db.Column(db.Integer)

    ever_married = db.Column(db.String(10))
    work_type = db.Column(db.String(50))

    # FIXED FIELD — must match the CSV name logically
    residence_type = db.Column(db.String(20))

    avg_glucose_level = db.Column(db.Float)
    bmi = db.Column(db.Float)
    smoking_status = db.Column(db.String(20))

    stroke = db.Column(db.Integer)

    def __repr__(self):
        return f"<Patient {self.id}>"



# -----------------------------------------------------------
# MONGODB USER MODEL (Flask-Login Compatible)
# -----------------------------------------------------------
class User(UserMixin):
    """
    User class wraps a MongoDB document so Flask-Login
    can manage authentication sessions.
    """

    def __init__(self, user_id, email=None):
        self.id = user_id
        self.email = email

    @staticmethod
    def get_user_by_email(email):
        """Fetch a MongoDB user by email."""
        users = mongo.db.users
        return users.find_one({"email": email})

    @staticmethod
    def create_user(email, hashed_password):
        """Creates new MongoDB user."""
        users = mongo.db.users
        users.insert_one({"email": email, "password": hashed_password})
