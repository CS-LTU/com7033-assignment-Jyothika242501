from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    flash,
)
from flask_login import login_required
from sqlalchemy import func

from . import db
from .models import Patient

# All routes here live under /patients/...
patient_bp = Blueprint("patient", __name__, url_prefix="/patients")


# ---------------------------------------------------------------------------
# DASHBOARD  /patients/dashboard
# ---------------------------------------------------------------------------
@patient_bp.route("/dashboard")
@login_required
def dashboard():
    """Top-level analytics dashboard with summary cards and charts."""

    # ---- Core counts for the stat cards ----
    total_patients = Patient.query.count()
    stroke_cases = Patient.query.filter_by(stroke=1).count()
    hypertension_cases = Patient.query.filter_by(hypertension=1).count()
    heart_disease_cases = Patient.query.filter_by(heart_disease=1).count()

    # Heart disease distribution for doughnut chart
    heart_yes = heart_disease_cases
    heart_no = max(total_patients - heart_disease_cases, 0)

    # ---- Stroke by gender for bar chart ----
    # Returns rows such as: [("Male", 120), ("Female", 129)]
    gender_rows = (
        db.session.query(Patient.gender, func.count(Patient.id))
        .filter(Patient.stroke == 1)
        .group_by(Patient.gender)
        .all()
    )

    stroke_gender_labels = [row[0] or "Unknown" for row in gender_rows]
    stroke_gender_counts = [int(row[1]) for row in gender_rows]

    # If there are no stroke cases at all, send empty lists;
    # the template will render a simple fallback chart.
    if not stroke_gender_labels:
        stroke_gender_labels = []
        stroke_gender_counts = []

    return render_template(
        "dashboard.html",
        total_patients=total_patients,
        stroke_cases=stroke_cases,
        hypertension_cases=hypertension_cases,
        heart_disease_cases=heart_disease_cases,
        heart_yes=heart_yes,
        heart_no=heart_no,
        stroke_gender_labels=stroke_gender_labels,
        stroke_gender_counts=stroke_gender_counts,
    )


# ---------------------------------------------------------------------------
# PATIENT LIST  /patients
#   - optional ?filter=stroke|hypertension|heart_disease
#   - optional ?search=<patient_id>
# ---------------------------------------------------------------------------
@patient_bp.route("/", methods=["GET"])
@login_required
def list_patients():
    """List patients, with optional filter and search by patient ID."""

    filter_type = request.args.get("filter")
    search_id = request.args.get("search")

    query = Patient.query

    # Filtering based on the summary cards
    if filter_type == "stroke":
        query = query.filter_by(stroke=1)
    elif filter_type == "hypertension":
        query = query.filter_by(hypertension=1)
    elif filter_type == "heart_disease":
        query = query.filter_by(heart_disease=1)

    # Optional search by patient ID (dataset ID)
    if search_id:
        try:
            pid = int(search_id)
            # NOTE: if your model uses a different column (e.g. Patient.id),
            # just change `patient_id` to that.
            query = query.filter_by(patient_id=pid)
        except ValueError:
            flash("Please enter a valid numeric Patient ID.", "warning")

    patients = query.order_by(Patient.patient_id).all()

    return render_template(
        "patients_list.html",
        patients=patients,
        filter_type=filter_type,
        search_id=search_id,
    )


# ---------------------------------------------------------------------------
# PATIENT DETAIL VIEW  /patients/<int:patient_id>
# ---------------------------------------------------------------------------
@patient_bp.route("/<int:patient_id>")
@login_required
def patient_detail(patient_id):
    """Show a single patient's record."""
    patient = Patient.query.filter_by(patient_id=patient_id).first_or_404()
    return render_template("patient_detail.html", patient=patient)


# ---------------------------------------------------------------------------
# ADD NEW PATIENT  /patients/add
# (If you already have a WTForms-based implementation, you can ignore this.)
# ---------------------------------------------------------------------------
@patient_bp.route("/add", methods=["GET", "POST"])
@login_required
def add_patient():
    """Very simple add form. If you have a WTForms version, keep that instead."""
    if request.method == "POST":
        try:
            patient = Patient(
                patient_id=int(request.form["patient_id"]),
                gender=request.form.get("gender") or None,
                age=float(request.form["age"]),
                hypertension=int(request.form.get("hypertension", 0)),
                heart_disease=int(request.form.get("heart_disease", 0)),
                ever_married=request.form.get("ever_married") or None,
                work_type=request.form.get("work_type") or None,
                residence_type=request.form.get("residence_type") or None,
                avg_glucose_level=float(request.form["avg_glucose_level"]),
                bmi=float(request.form["bmi"]),
                smoking_status=request.form.get("smoking_status") or None,
                stroke=int(request.form.get("stroke", 0)),
            )
            db.session.add(patient)
            db.session.commit()
            flash("Patient added successfully.", "success")
            return redirect(url_for("patient.list_patients"))
        except Exception as exc:  # crude but safe
            db.session.rollback()
            flash(f"Error adding patient: {exc}", "danger")

    return render_template("patient_form.html", patient=None)


# ---------------------------------------------------------------------------
# EDIT PATIENT  /patients/<int:patient_id>/edit
# ---------------------------------------------------------------------------
@patient_bp.route("/<int:patient_id>/edit", methods=["GET", "POST"])
@login_required
def edit_patient(patient_id):
    patient = Patient.query.filter_by(patient_id=patient_id).first_or_404()

    if request.method == "POST":
        try:
            patient.gender = request.form.get("gender") or patient.gender
            patient.age = float(request.form["age"])
            patient.hypertension = int(request.form.get("hypertension", 0))
            patient.heart_disease = int(request.form.get("heart_disease", 0))
            patient.ever_married = request.form.get("ever_married") or patient.ever_married
            patient.work_type = request.form.get("work_type") or patient.work_type
            patient.residence_type = request.form.get("residence_type") or patient.residence_type
            patient.avg_glucose_level = float(request.form["avg_glucose_level"])
            patient.bmi = float(request.form["bmi"])
            patient.smoking_status = request.form.get("smoking_status") or patient.smoking_status
            patient.stroke = int(request.form.get("stroke", 0))

            db.session.commit()
            flash("Patient updated successfully.", "success")
            return redirect(url_for("patient.patient_detail", patient_id=patient.patient_id))
        except Exception as exc:
            db.session.rollback()
            flash(f"Error updating patient: {exc}", "danger")

    return render_template("patient_form.html", patient=patient)


# ---------------------------------------------------------------------------
# DELETE PATIENT  /patients/<int:patient_id>/delete
# ---------------------------------------------------------------------------
@patient_bp.route("/<int:patient_id>/delete", methods=["POST"])
@login_required
def delete_patient(patient_id):
    patient = Patient.query.filter_by(patient_id=patient_id).first_or_404()
    db.session.delete(patient)
    db.session.commit()
    flash("Patient deleted.", "info")
    return redirect(url_for("patient.list_patients"))
