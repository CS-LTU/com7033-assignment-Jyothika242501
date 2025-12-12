# stroke_app/__init__.py
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_pymongo import PyMongo

db = SQLAlchemy()
mongo = PyMongo()
login_manager = LoginManager()


def create_app():
    app = Flask(__name__)

    # SECRET KEY
    app.config["SECRET_KEY"] = "supersecretkey"

    # SQLITE DB for patients
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///patients.db"
    db.init_app(app)

    # MONGO DB for users
    app.config["MONGO_URI"] = "mongodb://localhost:27017/stroke_users"
    mongo.init_app(app)
    app.mongo = mongo

    # LOGIN MANAGER
    login_manager.init_app(app)
    login_manager.login_view = "auth.login"

    # Import User
    from .models import Patient
    from .auth_routes import auth_bp
    from .main_routes import main_bp
    from .patients_routes import patient_bp, import_patients_csv

    @login_manager.user_loader
    def load_user(user_id):
        from .models import User
        return User(user_id)
    from .patients_routes import patient_bp, import_patients_csv


    with app.app_context():
        db.create_all()
        import_patients_csv()


    # REGISTER BLUEPRINTS
    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(main_bp)
    app.register_blueprint(patient_bp)

    # ------------------------------------------------------
    # DATABASE INIT + CSV IMPORT (STEP 2 LOCATION)
    # ------------------------------------------------------
    with app.app_context():
        db.create_all()                 # Create SQLite tables
        import_patients_csv()           # Import CSV into DB

    return app
