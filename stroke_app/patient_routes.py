"""
patient_routes.py

This module contains all routes related to patient data:

- /patients/dashboard      -> analytics dashboard (counts + charts)
- /patients/               -> patient list with filter + search
- /patients/<id>           -> patient detail view
- /patients/add            -> add a new patient
- /patients/<id>/edit      -> edit an existing patient
- /patients/<id>/delete    -> delete a patient

All routes are protected with @login_required to ensure that only
authenticated users can access clinical information.
"""

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

# ---------------------------------------------------------------------------
# Blueprint definition
# ---------------------------------------------------------------------------
# All routes in this file will be prefixed with "/patients"
# e.g. "/patients/dashboard", "/patients/123", "/patients/add"
patient_bp = Blueprint("patient", __name__, url_prefix="/patients")


# ---------------------------------------------------------------------------
# DASHBOARD ROUTE
# ---------------------------------------------------------------------------
# URL: /patients/dashboard
# Purpose:
#   - Display high-level analytics:
#       * Total number of patients
#       * Stroke cases
#       * Hypertension cases
#       * Heart disease cases
#   - Provide data to the front-end to render:
#       * Heart disease doughnut chart
#       * Stroke by gender bar chart
# Security:
#   - Protected with @login_required so only logged-in users can see it.
# ---------------------------------------------------------------------------
@patient_bp.route("/dashboard")
@login_required
def dashboard():
    """Analytics dashboard for patient data."""

    # --- Summary counts for the four cards at the top ---

    # Total number of patient records in the system
    total_patients = Patient.query.count()

    # Number of patients who have had a stroke
    stroke_cases = Patient.query.filter_by(stroke=1).count()

    # Number of patients diagnosed with hypertension
    hypertension_cases = Patient.query.filter_by(hypertension=1).count()

    # Number of patients with heart disease
    heart_disease_cases = Patient.query.filter_by(heart_disease=1).count()

    # --- Data for heart disease doughnut chart ---

    # "Yes" slice = patients with heart disease
    heart_yes = heart_disease_cases

    # "No" slice = total minus heart disease cases
    # max(..., 0) avoids negative values if something goes wrong
    heart_no = max(total_patients - heart_disease_cases, 0)

    # --- Data for stroke-by-gender bar chart ---

    # We query the database for all patients with stroke == 1 and group by gender.
    # The result looks like:
    #   [("Male", 120), ("Female", 130)]
    gender_rows = (
        db.session.query(Patient.gender, func.count(Patient.id))
        .filter(Patient.stroke == 1)
        .group_by(Patient.gender)
        .all()
    )

    # Convert rows into two simple Python lists that can be passed into the template.
    stroke_gender_labels = [row[0] or "Unknown" for row in gender_rows]
    stroke_gender_counts = [int(row[1]) for row in gender_rows]

    # If there are no stroke cases at all, the lists will be empty.
    # The template handles this and shows a small dummy chart instead.
    if not stroke_gender_labels:
        stroke_gender_labels = []
        stroke_gender_counts = []

    # Pass everything into the Jinja2 template.
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
# PATIENT LIST ROUTE
# ---------------------------------------------------------------------------
# URL: /patients
# Optional query parameters:
#   - filter = "stroke" | "hypertension" | "heart_disease"
#   - search = <patient_id> (numeric)
#
# Example URLs:
#   /patients?filter=stroke
#   /patients?search=101
#
# This route powers the main patient list page. It allows:
#   - Browsing all patients
#   - Filtering to specific subgroups
#   - Searching for a specific patient by ID
# ---------------------------------------------------------------------------
@patient_bp.route("/", methods=["GET"])
@login_required
def list_patients():
    """List patients with optional filter and search criteria."""

    # Read optional filter and search terms from the query string.
    filter_type = request.args.get("filter")
    search_id = request.args.get("search")

    # Start with a base query for all patients; we will apply filters gradually.
    query = Patient.query

    # --- Apply filter by condition (stroke / hypertension / heart disease) ---

    if filter_type == "stroke":
        query = query.filter_by(stroke=1)
    elif filter_type == "hypertension":
        query = query.filter_by(hypertension=1)
    elif filter_type == "heart_disease":
        query = query.filter_by(heart_disease=1)
    # If filter_type is None or unrecognised, we leave the query as "all patients".

    # --- Apply search by patient ID (if provided) ---

    if search_id:
        try:
            pid = int(search_id)
            # Filter by dataset patient_id column.
            # If your model uses a different column for the external ID,
            # update "patient_id" accordingly.
            query = query.filter_by(patient_id=pid)
        except ValueError:
            # If the user types a non-numeric ID, show a gentle warning.
            flash("Please enter a valid numeric Patient ID.", "warning")

    # Sort results by patient_id for consistent ordering.
    patients = query.order_by(Patient.patient_id).all()

    # Render the table template.
    return render_template(
        "patients_list.html",
        patients=patients,
        filter_type=filter_type,
        search_id=search_id,
    )


# ---------------------------------------------------------------------------
# PATIENT DETAIL ROUTE
# ---------------------------------------------------------------------------
# URL: /patients/<int:patient_id>
#
# Shows the full record for a single patient. This is reached when the user
# clicks the "View" button in the patients list.
# ---------------------------------------------------------------------------
@patient_bp.route("/<int:patient_id>")
@login_required
def patient_detail(patient_id):
    """Display details for a single patient identified by patient_id."""
    # Look up the patient by their external dataset ID.
    # first_or_404() will return a 404 page if no record is found.
    patient = Patient.query.filter_by(patient_id=patient_id).first_or_404()
    return render_template("patient_detail.html", patient=patient)


# ---------------------------------------------------------------------------
# ADD NEW PATIENT ROUTE
# ---------------------------------------------------------------------------
# URL: /patients/add
#
# Purpose:
#   - Allow authorised users to add a new patient record.
# Note:
#   - This version uses request.form for simplicity.
#   - If you already have a WTForms-based PatientForm, you can replace
#     this implementation with that form logic.
# ---------------------------------------------------------------------------
@patient_bp.route("/add", methods=["GET", "POST"])
@login_required
def add_patient():
    """Create a new patient record."""
    if request.method == "POST":
        try:
            # Build a new Patient object from submitted form fields.
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

            # Save to database
            db.session.add(patient)
            db.session.commit()
            flash("Patient added successfully.", "success")

            # Redirect back to the patient list page
            return redirect(url_for("patient.list_patients"))

        except Exception as exc:
            # If anything goes wrong (e.g. missing field, invalid type),
            # roll back the transaction and display an error message.
            db.session.rollback()
            flash(f"Error adding patient: {exc}", "danger")

    # For GET requests, simply render the blank form.
    return render_template("patient_form.html", patient=None)


# ---------------------------------------------------------------------------
# EDIT PATIENT ROUTE
# ---------------------------------------------------------------------------
# URL: /patients/<int:patient_id>/edit
#
# Purpose:
#   - Allow editing of an existing patient record.
# Behaviour:
#   - Prefills the form with the existing data on GET.
#   - Updates the record on POST.
# ---------------------------------------------------------------------------
@patient_bp.route("/<int:patient_id>/edit", methods=["GET", "POST"])
@login_required
def edit_patient(patient_id):
    """Edit an existing patient record."""
    # Retrieve the patient or show 404 if not found
    patient = Patient.query.filter_by(patient_id=patient_id).first_or_404()

    if request.method == "POST":
        try:
            # Update fields from the submitted form values.
            # For optional fields, we fall back to the existing value.
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

            # After editing, go back to the detail view
            return redirect(url_for("patient.patient_detail", patient_id=patient.patient_id))

        except Exception as exc:
            db.session.rollback()
            flash(f"Error updating patient: {exc}", "danger")

    # For GET requests, show the form pre-filled with the patient data.
    return render_template("patient_form.html", patient=patient)


# ---------------------------------------------------------------------------
# DELETE PATIENT ROUTE
# ---------------------------------------------------------------------------
# URL: /patients/<int:patient_id>/delete
#
# Purpose:
#   - Permanently remove a patient record from the database.
# Behaviour:
#   - Only accepts POST requests (to avoid accidental deletions via link).
# ---------------------------------------------------------------------------
@patient_bp.route("/<int:patient_id>/delete", methods=["POST"])
@login_required
def delete_patient(patient_id):
    """Delete a patient record."""
    # Look up the patient we want to delete.
    patient = Patient.query.filter_by(patient_id=patient_id).first_or_404()

    # Delete and commit
    db.session.delete(patient)
    db.session.commit()
    flash("Patient deleted.", "info")

    # Return to patient list after deletion
    return redirect(url_for("patient.list_patients"))
