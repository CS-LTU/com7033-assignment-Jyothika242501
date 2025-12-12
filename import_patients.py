import pandas as pd
from stroke_app import create_app, db
from stroke_app.models import Patient

app = create_app()

with app.app_context():
    df = pd.read_csv("healthcare-dataset-stroke-data.csv")

    db.session.query(Patient).delete()

    for _, row in df.iterrows():
        patient = Patient(
            gender=row["gender"],
            age=row["age"],
            hypertension=row["hypertension"],
            heart_disease=row["heart_disease"],
            ever_married=row["ever_married"],
            work_type=row["work_type"],
            Residence_type=row["Residence_type"],
            avg_glucose_level=row["avg_glucose_level"],
            bmi=row["bmi"],
            smoking_status=row["smoking_status"],
            stroke=row["stroke"],
        )
        db.session.add(patient)

    db.session.commit()

    print("Imported all patients into patients.db")
