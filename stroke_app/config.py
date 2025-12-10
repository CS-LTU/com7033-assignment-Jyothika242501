import os
from datetime import timedelta

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-change-me")

    
    SQLALCHEMY_DATABASE_URI = os.environ.get(
    "DATABASE_URL", "sqlite:///users.db"
    )


    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Default Mongo URI (will be overridden in create_app just in case)
    MONGO_URI = MONGO_URI = "mongodb://localhost:27017/stroke_app"


    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    REMEMBER_COOKIE_HTTPONLY = True
    PERMANENT_SESSION_LIFETIME = timedelta(minutes=30)
    WTF_CSRF_TIME_LIMIT = None
