from flask import (
    Blueprint,
    render_template,
    redirect,
    url_for,
    flash,
    request,
    session,
)
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash

from . import db
from .models import User
from .forms import RegisterForm, LoginForm, MFASetupForm, MFAVerifyForm

import pyotp
import qrcode
import io
import base64

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")


# ---------- Helper: create QR image as data URL ----------

def _qr_code_data_url(data: str) -> str:
    """Return a base64 data URL for a QR code from the given string."""
    img = qrcode.make(data)
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    b64 = base64.b64encode(buf.read()).decode("ascii")
    return f"data:image/png;base64,{b64}"


# ---------- Register ----------

@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("patient.dashboard"))

    form = RegisterForm()
    if form.validate_on_submit():
        existing = User.query.filter_by(email=form.email.data.lower()).first()
        if existing:
            flash("An account with that email already exists.", "danger")
            return redirect(url_for("auth.register"))

        user = User(
            email=form.email.data.lower(),
            password_hash=generate_password_hash(form.password.data),
        )
        db.session.add(user)
        db.session.commit()

        # Log them in and force MFA setup
        login_user(user)
        flash("Account created. You must set up Multi-Factor Authentication.", "info")
        return redirect(url_for("auth.setup_mfa"))

    return render_template("register.html", form=form)


# ---------- Login (password step) ----------

@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        # If already logged in, make sure MFA is done
        if not current_user.mfa_enabled or not current_user.mfa_secret:
            return redirect(url_for("auth.setup_mfa"))
        return redirect(url_for("patient.dashboard"))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data.lower()).first()
        if user and check_password_hash(user.password_hash, form.password.data):

            # 🔐 MFA MANDATORY LOGIC

            # 1) If MFA is NOT enabled, log in, but force them to MFA setup
            if not user.mfa_enabled or not user.mfa_secret:
                login_user(user)
                flash(
                    "You must set up Multi-Factor Authentication before using your account.",
                    "warning",
                )
                return redirect(url_for("auth.setup_mfa"))

            # 2) MFA enabled -> go to MFA verify step
            session["mfa_user_id"] = user.id
            flash("Enter your 6-digit code from the authenticator app.", "info")
            return redirect(url_for("auth.mfa_verify"))

        flash("Invalid email or password.", "danger")

    return render_template("login.html", form=form)


# ---------- Logout ----------

@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You have been logged out.", "info")
    return redirect(url_for("auth.login"))


# ---------- MFA Setup (after register or forced from login) ----------

@auth_bp.route("/setup-mfa", methods=["GET", "POST"])
@login_required
def setup_mfa():
    form = MFASetupForm()

    # If already enabled, nothing to do
    if current_user.mfa_enabled and current_user.mfa_secret:
        flash("Multi-Factor Authentication is already enabled.", "info")
        return redirect(url_for("patient.dashboard"))

    # If user doesn't have a secret yet, generate one ONCE
    if not current_user.mfa_secret:
        secret = pyotp.random_base32()
        current_user.mfa_secret = secret
        db.session.commit()
    else:
        secret = current_user.mfa_secret

    # Generate provisioning URI and QR code
    issuer = "HS StrokeApp"
    totp = pyotp.TOTP(secret)
    provisioning_uri = totp.provisioning_uri(
        name=current_user.email,
        issuer_name=issuer,
    )
    qr_data_url = _qr_code_data_url(provisioning_uri)

    if form.validate_on_submit():
        code = form.otp_code.data.strip()

        # 👇 more tolerant: allow slight time skew (valid_window=2)
        if totp.verify(code, valid_window=2):
            current_user.mfa_enabled = True
            db.session.commit()
            flash("Multi-Factor Authentication has been enabled.", "success")
            return redirect(url_for("patient.dashboard"))
        else:
            flash("The code you entered is not correct. Please try again.", "danger")

    return render_template(
        "mfa_setup.html",
        form=form,
        qr_data_url=qr_data_url,
        secret=secret,
    )


# ---------- MFA Verify (during login) ----------

@auth_bp.route("/mfa-verify", methods=["GET", "POST"])
def mfa_verify():
    # Only used after password is verified
    user_id = session.get("mfa_user_id")
    if not user_id:
        flash("Your login session has expired. Please log in again.", "warning")
        return redirect(url_for("auth.login"))

    user = User.query.get(user_id)
    if not user or not user.mfa_secret or not user.mfa_enabled:
        session.pop("mfa_user_id", None)
        flash("MFA is not configured for this account.", "danger")
        return redirect(url_for("auth.login"))

    form = MFAVerifyForm()
    totp = pyotp.TOTP(user.mfa_secret)

    if form.validate_on_submit():
        code = form.otp_code.data.strip()

        if totp.verify(code, valid_window=2):
            # MFA success -> complete login
            login_user(user)
            session.pop("mfa_user_id", None)
            flash("MFA verified. You are now logged in.", "success")
            next_page = request.args.get("next") or url_for("patient.dashboard")
            return redirect(next_page)
        else:
            flash("Invalid code. Please try again.", "danger")

    return render_template("mfa_verify.html", form=form, email=user.email)
