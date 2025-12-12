# import_patients.py

"""
Run manually to import CSV:
> python import_patients.py
"""

from stroke_app import create_app, db
from stroke_app.patients_routes import import_patients_csv

app = create_app()

with app.app_context():
    db.create_all()
    import_patients_csv()
