from flask import Flask
from config import Config

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

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

    return app