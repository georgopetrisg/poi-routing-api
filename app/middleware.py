def setup_middleware(app):
    @app.before_request
    def before_request():
        pass