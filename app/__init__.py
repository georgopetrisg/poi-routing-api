from flask import Flask, app
from config import config
from app.database import db
from flasgger import Swagger
import os
import logging
from logging.handlers import RotatingFileHandler

def create_app(config_name=None):
    app = Flask(__name__)
    app.json.sort_keys = False

    if config_name is None:
        config_name = os.environ.get('FLASK_CONFIG') or 'default'

    app.config.from_object(config[config_name])

    db.init_app(app)

    log = logging.getLogger('werkzeug')
    log.setLevel(logging.ERROR)

    if not os.path.exists('logs'):
        os.mkdir('logs')
    
    file_handler = RotatingFileHandler('logs/app.log', maxBytes=100000, backupCount=10)

    file_handler.setFormatter(logging.Formatter('%(message)s'))
    file_handler.setLevel(logging.INFO)
    root_logger = logging.getLogger()

    if root_logger.handlers:
        root_logger.handlers = []

    root_logger.addHandler(file_handler)
    root_logger.setLevel(logging.INFO)

    if not app.debug or os.environ.get("WERKZEUG_RUN_MAIN") == "true":
        root_logger.info('API Server Started')

    basedir = os.path.abspath(os.path.dirname(__file__))
    yaml = os.path.join(basedir, '..', 'openapi.yml')

    swagger_config = {
        "openapi": "3.0.3",
        "headers": [],
        "specs": [
            {
                "endpoint": 'apispec',
                "route": '/apispec.json',
                "rule_filter": lambda rule: True,
                "model_filter": lambda tag: True,
            }
        ],
        "static_url_path": "/flasgger_static",
        "swagger_ui": True,
        "specs_route": "/apidocs/"
    }

    Swagger(app, template_file=yaml, config=swagger_config)

    # Import blueprints
    from app.main import bp as main_bp
    from app.pois import bp as pois_bp
    from app.routes_api import bp as routes_bp
    from app.auth import bp as auth_bp

    # Register them
    app.register_blueprint(main_bp, url_prefix="/")
    app.register_blueprint(pois_bp, url_prefix="/pois")
    app.register_blueprint(routes_bp, url_prefix="/routes")
    app.register_blueprint(auth_bp, url_prefix="/auth")

    # Register error handlers and middleware
    from app.errors import register_error_handlers
    from app.middleware import setup_middleware

    register_error_handlers(app)
    setup_middleware(app)

    with app.app_context():
        db.create_all()

    return app