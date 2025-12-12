import csv

from stroke_app import create_app, db
from stroke_app.models import Patient

CSV_FILE = "healthcare-dataset-stroke-data (1).csv"

app = create_app()

def safe_float(v):
    try:
        return float(v) if v not in ("", None) else None
    except ValueError:
        return None

with app.app_context():
    db.create_all()  # ensures tables exist

    imported = 0
    with open(CSV_FILE, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            # use dataset id as patient_id if you want
            dataset_id = int(row["id"])
            if Patient.query.filter_by(patient_id=dataset_id).first():
                continue  # already imported

            p = Patient(
                patient_id=dataset_id,
                gender=row.get("gender"),
                age=safe_float(row.get("age")),
                hypertension=int(row.get("hypertension", 0)),
                heart_disease=int(row.get("heart_disease", 0)),
                ever_married=row.get("ever_married"),
                work_type=row.get("work_type"),
                residence_type=row.get("Residence_type") or row.get("residence_type"),
                avg_glucose_level=safe_float(row.get("avg_glucose_level")),
                bmi=safe_float(row.get("bmi")),
                smoking_status=row.get("smoking_status"),
                stroke=int(row.get("stroke", 0)),
            )
            db.session.add(p)
            imported += 1

    db.session.commit()
    print(f"✅ Imported {imported} patients into instance/users.db")
