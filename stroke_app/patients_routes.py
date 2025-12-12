# stroke_app/patients_routes.py

import os
import pandas as pd
from flask import Blueprint, render_template, request
from .models import Patient
from . import db

patient_bp = Blueprint("patients", __name__)

CSV_PATH = os.path.join(os.getcwd(), "data", "patients.csv")


def import_patients_csv():
    """Loads patients from CSV into SQLite database with data cleaning."""
    import csv
    import os
    from .models import Patient

    csv_path = os.path.join(os.path.dirname(__file__), "patients.csv")

    print("🔄 Importing patients.csv into SQLite...")

    # If patients already exist, DO NOT import again
    if Patient.query.first():
        print("✔ Patients already imported.")
        return

    with open(csv_path, "r") as file:
        reader = csv.DictReader(file)

        for row in reader:

            # CLEAN BMI (Unknown → None)
            bmi_value = None
            if row["bmi"] not in ["Unknown", "", None]:
                try:
                    bmi_value = float(row["bmi"])
                except:
                    bmi_value = None

            # CLEAN SMOKING STATUS
            smoking_status_value = row["smoking_status"] if row["smoking_status"] != "" else "Unknown"

            # CREATE PATIENT OBJECT
            patient = Patient(
                id=int(row["id"]),
                gender=row["gender"],
                age=float(row["age"]),
                hypertension=int(row["hypertension"]),
                heart_disease=int(row["heart_disease"]),
                ever_married=row["ever_married"],
                work_type=row["work_type"],
                residence_type=row["Residence_type"],
                avg_glucose_level=float(row["avg_glucose_level"]),
                bmi=bmi_value,
                smoking_status=smoking_status_value,
                stroke=int(row["stroke"])
            )

            db.session.add(patient)

        db.session.commit()

    print("✔ CSV import completed successfully!")

@patient_bp.route("/patients")
def list_patients():
    """Show patient list page."""
    patients = Patient.query.all()
    return render_template("patients.html", patients=patients)
