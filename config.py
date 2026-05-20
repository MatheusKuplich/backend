import os


BASE_DIR = os.path.abspath(os.path.dirname(__file__))
INSTANCE_DIR = os.path.join(BASE_DIR, "instance")

# Database
_db_path = os.path.join(INSTANCE_DIR, "app.db").replace("\\", "/")
DATABASE_URL = f"sqlite:///{_db_path}"


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-change-me")
    SQLALCHEMY_DATABASE_URI = DATABASE_URL
    SQLALCHEMY_TRACK_MODIFICATIONS = False
