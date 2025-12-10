# stroke_app/main_routes.py

from flask import Blueprint, render_template, redirect, url_for
from flask_login import current_user

main_bp = Blueprint("main", __name__)


@main_bp.route("/")
def home():
    """
    Public landing page.

    If the user is NOT logged in -> show the NHS-style home page.
    If the user IS logged in       -> redirect straight to the dashboard.
    """
    if current_user.is_authenticated:
        # Logged-in users should not see the marketing/landing page
        return redirect(url_for("patient.dashboard"))

    # Anonymous visitors see the public home page
    return render_template("home.html")
