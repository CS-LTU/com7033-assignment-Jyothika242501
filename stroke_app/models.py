from flask_login import UserMixin
from . import db, login_manager


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(db.Model, UserMixin):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)

    # MFA
    mfa_secret = db.Column(db.String(32), nullable=True)
    mfa_enabled = db.Column(db.Boolean, default=False)

    def __repr__(self):
        return f"<User {self.email}>"


class Patient(db.Model):
    # IMPORTANT: this must match the existing table name
    __tablename__ = "patient"

    id = db.Column(db.Integer, primary_key=True)
    # original dataset has "id", we map it to patient_id and keep unique
    patient_id = db.Column(db.Integer, unique=True, nullable=True)

    gender = db.Column(db.String(20), nullable=True)
    age = db.Column(db.Float, nullable=True)
    hypertension = db.Column(db.Integer, default=0)
    heart_disease = db.Column(db.Integer, default=0)
    ever_married = db.Column(db.String(10), nullable=True)
    work_type = db.Column(db.String(50), nullable=True)
    residence_type = db.Column(db.String(20), nullable=True)
    avg_glucose_level = db.Column(db.Float, nullable=True)
    bmi = db.Column(db.Float, nullable=True)
    smoking_status = db.Column(db.String(50), nullable=True)
    stroke = db.Column(db.Integer, default=0)

    def __repr__(self):
        return f"<Patient {self.patient_id}>"
