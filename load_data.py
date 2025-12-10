import pandas as pd
from stroke_app import create_app, mongo

def load_data(csv_path="healthcare-dataset-stroke-data (1).csv"):
    app = create_app()
    with app.app_context():
        df = pd.read_csv(csv_path)
        records = []
        for _, row in df.iterrows():
            rec = {
                "patient_id": int(row["id"]),
                "gender": row["gender"],
                "age": float(row["age"]),
                "hypertension": int(row["hypertension"]),
                "heart_disease": int(row["heart_disease"]),
                "ever_married": row["ever_married"],
                "work_type": row["work_type"],
                "residence_type": row["Residence_type"],
                "avg_glucose_level": float(row["avg_glucose_level"]),
                "bmi": float(row["bmi"]) if not pd.isna(row["bmi"]) else None,
                "smoking_status": row["smoking_status"],
                "stroke": int(row["stroke"]),
            }
            records.append(rec)
        mongo.db.patients.delete_many({})
        if records:
            mongo.db.patients.insert_many(records)
        print(f"Inserted {len(records)} records")

if __name__ == "__main__":
    load_data()
