import os
from flask import Flask, redirect, url_for, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, current_user

db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = "auth.login"


def create_app():
    app = Flask(__name__, instance_relative_config=True)

    app.config.from_mapping(
        SECRET_KEY="change-me-in-production",
        SQLALCHEMY_DATABASE_URI="sqlite:///" + os.path.join(app.instance_path, "users.db"),
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
    )

    os.makedirs(app.instance_path, exist_ok=True)

    db.init_app(app)
    login_manager.init_app(app)

    from .patient_routes import patient_bp
    from .auth_routes import auth_bp

    app.register_blueprint(patient_bp)
    app.register_blueprint(auth_bp)

    # ---------- HOME PAGE ROUTES ----------

    @app.route("/")
    @app.route("/home")
    def home():
        """
        Public landing page.
        Logged-in users can still click Dashboard in the navbar
        to go to /patients/.
        """
        return render_template("home.html")

    return app
