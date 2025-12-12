# stroke_app/main_routes.py
from flask import Blueprint, render_template
from flask_login import login_required
from .models import Patient

main_bp = Blueprint("main", __name__)


@main_bp.route("/")
def home():
    return render_template("home.html")


@main_bp.route("/dashboard")
@login_required
def dashboard():
    total = Patient.query.count()
    strokes = Patient.query.filter_by(stroke=1).count()
    hypertension = Patient.query.filter_by(hypertension=1).count()
    heart_disease = Patient.query.filter_by(heart_disease=1).count()

    male = Patient.query.filter_by(gender="Male").count()
    female = Patient.query.filter_by(gender="Female").count()

    return render_template(
        "dashboard.html",
        total=total,
        strokes=strokes,
        hypertension=hypertension,
        heart_disease=heart_disease,
        male=male,
        female=female
    )
