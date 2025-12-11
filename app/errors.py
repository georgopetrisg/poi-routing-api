from flask import jsonify

def register_error_handlers(app):

    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
            "code": "bad_request",
            "message": str(error),
            "status": 400
        }), 400

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            "code": "not_found",
            "message": str(error),
            "status": 404
        }), 404

    @app.errorhandler(500)
    def internal_error(error):
        return jsonify({
            "code": "internal_error",
            "message": "An internal server error occurred",
            "status": 500
        }), 500