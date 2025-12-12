from stroke_app import create_app, db
from stroke_app.models import Patient

app = create_app()

with app.app_context():
    db.drop_all()
    db.create_all()
    print("Database reset successful!")
