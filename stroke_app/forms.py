from flask_wtf import FlaskForm
from wtforms import (
    StringField,
    PasswordField,
    SubmitField,
    FloatField,
    IntegerField,
    SelectField,
)
from wtforms.validators import (
    DataRequired,
    Email,
    Length,
    NumberRange,
    Optional,
    Regexp,
    EqualTo,
)


# --------------------------------------------------------
# REGISTER FORM (with confirm password + strong rules)
# --------------------------------------------------------
class RegisterForm(FlaskForm):
    email = StringField(
        "Email",
        validators=[
            DataRequired(message="Email is required."),
            Email(message="Enter a valid email address."),
        ],
    )

    password = PasswordField(
        "Password",
        validators=[
            DataRequired(message="Password is required."),
            Length(min=8, message="Password must be at least 8 characters long."),
            Regexp(
                r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&]).+$",
                message=(
                    "Password must include: one uppercase letter, one lowercase letter, "
                    "one number, and one special character (@$!%*?&)."
                ),
            ),
        ],
    )

    confirm_password = PasswordField(
        "Confirm Password",
        validators=[
            DataRequired(message="Please confirm your password."),
            EqualTo("password", message="Passwords must match."),
        ],
    )

    submit = SubmitField("Register")


# --------------------------------------------------------
# LOGIN FORM
# --------------------------------------------------------
class LoginForm(FlaskForm):
    email = StringField(
        "Email",
        validators=[
            DataRequired(message="Email is required."),
            Email(message="Enter a valid email address."),
        ],
    )
    password = PasswordField(
        "Password",
        validators=[DataRequired(message="Password is required.")],
    )

    submit = SubmitField("Login")


# --------------------------------------------------------
# PATIENT FORM
# --------------------------------------------------------
class PatientForm(FlaskForm):
    patient_id = IntegerField("Patient ID", validators=[DataRequired()])

    gender = SelectField("Gender", choices=["Male", "Female", "Other"])

    age = FloatField(
        "Age", validators=[DataRequired(), NumberRange(min=0, max=120)]
    )

    hypertension = SelectField(
        "Hypertension",
        choices=[("0", "No"), ("1", "Yes")],
    )

    heart_disease = SelectField(
        "Heart Disease",
        choices=[("0", "No"), ("1", "Yes")],
    )

    ever_married = SelectField(
        "Ever Married",
        choices=["Yes", "No"],
    )

    work_type = SelectField(
        "Work Type",
        choices=[
            "Private",
            "Self-employed",
            "Govt_job",
            "children",
            "Never_worked",
        ],
    )

    residence_type = SelectField(
        "Residence Type",
        choices=["Urban", "Rural"],
    )

    avg_glucose_level = FloatField(
        "Average Glucose Level", validators=[DataRequired()]
    )

    bmi = FloatField(
        "BMI", validators=[Optional()]
    )

    smoking_status = SelectField(
        "Smoking Status",
        choices=[
            "formerly smoked",
            "never smoked",
            "smokes",
            "Unknown",
        ],
    )

    stroke = SelectField(
        "Stroke",
        choices=[("0", "No"), ("1", "Yes")],
    )

    submit = SubmitField("Save")
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email, Length

# ... your existing RegisterForm, LoginForm, PatientForm, etc.

class MFASetupForm(FlaskForm):
    otp_code = StringField(
        "Authenticator Code",
        validators=[DataRequired(), Length(min=6, max=6, message="Enter the 6-digit code")],
    )
    submit = SubmitField("Verify & Enable MFA")


class MFAVerifyForm(FlaskForm):
    otp_code = StringField(
        "Authenticator Code",
        validators=[DataRequired(), Length(min=6, max=6, message="Enter the 6-digit code")],
    )
    submit = SubmitField("Verify Login")
