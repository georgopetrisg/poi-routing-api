from flask import Flask
from config import Config
from app.database import db

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)

    # Import blueprints
    from app.main import bp as main_bp
    from app.pois import bp as pois_bp
    from app.routes_api import bp as routes_bp

    # Register them
    app.register_blueprint(main_bp, url_prefix="/")
    app.register_blueprint(pois_bp, url_prefix="/pois")
    app.register_blueprint(routes_bp, url_prefix="/routes")

    # Register error handlers and middleware
    from app.errors import register_error_handlers
    from app.middleware import setup_middleware

    register_error_handlers(app)
    setup_middleware(app)

    with app.app_context():
        db.create_all()

    return app