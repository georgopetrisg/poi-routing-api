from functools import wraps
from flask import request, jsonify, g
from app.models import User

def require_api_key(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = request.headers.get('X-API-KEY')

        if not token:
            return jsonify({"error": "Missing API Key"}), 401

        user = User.query.filter_by(api_token=token).first()

        if not user:
            return jsonify({"error": "Invalid API Key"}), 401

        g.current_user = user

        return f(*args, **kwargs)
    return decorated_function