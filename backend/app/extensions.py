from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS
from flask_security import Security
from celery import Celery

db = SQLAlchemy()
migrate = Migrate()
cors = CORS()
security = Security()
celery = Celery(__name__)
