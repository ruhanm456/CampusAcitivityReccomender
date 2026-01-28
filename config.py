import os

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "devkey")
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL",
        "sqlite:///instance/app.db"  # fallback to SQLite
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
