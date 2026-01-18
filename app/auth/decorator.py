from functools import wraps
from flask import request, jsonify, g
from app.models import User
from app.errors import APIError

def require_api_key(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = request.headers.get('X-API-KEY')

        if not token:
            raise APIError(
                message="API key is required.",
                status_code=401,
                details={"api_key": "Missing"})

        user = User.query.filter_by(api_token=token).first()

        if not user:
           raise APIError(
               message="API key is invalid.", 
               status_code=403,
               details={"api_key": "Invalid"})

        g.current_user = user

        return f(*args, **kwargs)
    return decorated_function