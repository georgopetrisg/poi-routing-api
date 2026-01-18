from flask import Blueprint, jsonify
from werkzeug.exceptions import HTTPException

bp = Blueprint('errors', __name__)

class APIError(Exception):
    def __init__(self, message, status_code=400, code=None, details=None):
        super().__init__()
        self.message = message
        self.status_code = status_code
        self.details = details
        
        if code:
            self.code = code
        else:
            self.code = self._get_default_code(status_code)

    def _get_default_code(self, status):
        mapping = {
            400: 'invalid_request',
            401: 'unauthorized',
            403: 'forbidden',
            404: 'not_found',
            429: 'rate_limit_exceeded',
            500: 'internal_server_error',
            502: 'bad_gateway'
        }
        return mapping.get(status, 'unknown_error')

    def to_dict(self):
        rv = {
            "code": self.code,
            "message": self.message,
            "details": self.details
        }
        return rv

@bp.app_errorhandler(APIError)
def handle_api_error(error):
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response

@bp.app_errorhandler(404)
def not_found_error(error):
    return jsonify({
        "code": "not_found",
        "message": "The requested resource was not found.",
        "details": None
    }), 404

@bp.app_errorhandler(500)
def internal_error(error):
    return jsonify({
        "code": "internal_server_error",
        "message": "An unexpected error occurred.",
        "details": None
    }), 500
    
def register_error_handlers(app):
    app.register_blueprint(bp)