# stroke_app/forms.py
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import InputRequired, Email, Length, EqualTo


# -------------------------------------------
# LOGIN FORM
# -------------------------------------------
class LoginForm(FlaskForm):
    email = StringField("Email", validators=[
        InputRequired(),
        Email(message="Enter a valid email")
    ])

    password = PasswordField("Password", validators=[
        InputRequired(),
        Length(min=6, message="Password must be at least 6 characters")
    ])

    submit = SubmitField("Login")


# -------------------------------------------
# REGISTER FORM
# -------------------------------------------
class RegisterForm(FlaskForm):
    email = StringField("Email", validators=[
        InputRequired(),
        Email()
    ])

    password = PasswordField("Password", validators=[
        InputRequired(),
        Length(min=6)
    ])

    confirm_password = PasswordField("Confirm Password", validators=[
        InputRequired(),
        EqualTo("password", message="Passwords must match")
    ])

    submit = SubmitField("Create Account")
