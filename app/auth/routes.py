from flask import request, jsonify
from app.database import db
from app.models import User
import uuid
from app.auth import bp
from app.errors import APIError
from app.validators import validate_auth_creds

@bp.route('/register', methods=['POST'])
def register():
    data = request.get_json(silent=True)
    if data is None:
        raise APIError(
            message="Invalid or missing JSON body.",
            status_code=400,
            details={"body": "Invalid JSON format"}
        )
    
    missing_creds = validate_auth_creds(data)
    
    if missing_creds:
        raise APIError(
            message="Missing required credentials.",
            code="registration_failed",
            status_code=400,
            details=missing_creds
        )

    if User.query.filter_by(username=data['username']).first():
        raise APIError(
            message="Username already exists.",
            code="registration_failed", 
            status_code=400,
            details={"username": "Already exists"}
        )

    new_user = User(
        id=f"user_{uuid.uuid4()}",
        username=data['username']
    )
    new_user.set_password(data['password'])
    new_user.generate_token()

    try:
        db.session.add(new_user)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        raise APIError(
            message=str(e), 
            status_code=500
        )

    return jsonify({
        "message": "User registered successfully.",
        "username": new_user.username,
        "apiKey": new_user.api_token
    }), 201

@bp.route('/login', methods=['POST'])
def login():
    data = request.get_json(silent=True)
    if data is None:
        raise APIError(
            message="Invalid or missing JSON body.",
            status_code=400,
            details={"body": "Invalid JSON format"}
        )
    
    missing_creds = validate_auth_creds(data)
    if missing_creds:
        raise APIError(
            message="Missing required credentials.",
            code="login_failed",
            status_code=400,
            details=missing_creds
        )
    
    username = data.get('username')
    password = data.get('password')

    user = User.query.filter_by(username=username).first()

    if user and user.check_password(password):
        if not user.api_token:
            user.generate_token()
            db.session.commit()
            
        return jsonify({
            "message": "Login successful",
            "apiKey": user.api_token
        }), 200

    raise APIError(
        message="Username or password is incorrect.", 
        status_code=401,
        details={"authorization": "Failed"}
    )