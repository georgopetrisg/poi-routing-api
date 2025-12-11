from flask import Blueprint

bp = Blueprint('routes_api', __name__)

from app.routes_api import routes