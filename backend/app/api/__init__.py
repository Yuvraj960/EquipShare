from flask import Blueprint

bp = Blueprint('api', __name__)

from . import auth, equipment, categories, rentals, reviews, notifications, reports, admin
