from flask import Blueprint

bp = Blueprint('pois', __name__)

from app.pois import routes