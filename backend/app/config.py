import os
from datetime import timedelta
from dotenv import load_dotenv

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
ENV_PATH = os.path.join(os.path.dirname(__file__), '..', '.env')
if os.path.exists(ENV_PATH):
    load_dotenv(ENV_PATH)

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'equipshare-dev-secret-key-2026')
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', f'sqlite:///{os.path.join(BASE_DIR, "equipshare.db")}')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Flask-Security
    SECURITY_PASSWORD_SALT = os.environ.get('SECURITY_PASSWORD_SALT', 'equipshare-secret-salt-2026')
    SECURITY_PASSWORD_HASH = 'pbkdf2_sha512'
    SECURITY_REGISTERABLE = True
    SECURITY_SEND_REGISTER_EMAIL = False
    SECURITY_TRACKABLE = True
    SECURITY_CSRF_PROTECT = False

    # JWT or session
    SECURITY_TOKEN_AUTHENTICATION_HEADER = 'Authentication-Token'

    # Celery
    CELERY_BROKER_URL = os.environ.get('CELERY_BROKER_URL', 'redis://localhost:6379/0')
    CELERY_RESULT_BACKEND = os.environ.get('CELERY_RESULT_BACKEND', 'redis://localhost:6379/0')

    # CORS
    CORS_ORIGINS = ['http://localhost:5173', 'http://127.0.0.1:5173', 'http://localhost:5174', 'http://127.0.0.1:5174']
