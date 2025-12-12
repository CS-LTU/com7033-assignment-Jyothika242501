# stroke_app/auth_routes.py
from flask import Blueprint, render_template, redirect, request, url_for, flash, current_app
from flask_login import login_user, logout_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash

from .forms import LoginForm, RegisterForm
from .models import User

auth_bp = Blueprint("auth", __name__)


# -------------------------------------------
# USER LOGIN
# -------------------------------------------
@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()

    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data

        # Find user in MongoDB
        users = current_app.mongo.db.users
        user_data = users.find_one({"email": email})

        if user_data and check_password_hash(user_data["password"], password):
            user = User(str(user_data["_id"]))
            login_user(user)
            return redirect(url_for("main.dashboard"))
        else:
            flash("Invalid email or password", "danger")

    return render_template("login.html", form=form)


# -------------------------------------------
# USER REGISTER
# -------------------------------------------
@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    form = RegisterForm()

    if form.validate_on_submit():

        email = form.email.data
        password = form.password.data

        users = current_app.mongo.db.users

        # Check if user already exists
        if users.find_one({"email": email}):
            flash("Email already registered!", "danger")
            return redirect(url_for("auth.register"))

        hashed_pw = generate_password_hash(password)

        users.insert_one({"email": email, "password": hashed_pw})

        flash("Account created successfully! Please log in.", "success")
        return redirect(url_for("auth.login"))

    return render_template("register.html", form=form)


# -------------------------------------------
# LOGOUT
# -------------------------------------------
@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Logged out successfully", "info")
    return redirect(url_for("auth.login"))
