from flask import request, jsonify
from app.database import db
from app.models import User
import uuid
from app.auth import bp

@bp.route('/register', methods=['POST'])
def register():
    data = request.get_json() or {}
    
    if not data.get('username') or not data.get('password'):
        return jsonify({"error": "Username and password required"}), 400

    if User.query.filter_by(username=data['username']).first():
        return jsonify({"error": "Username already exists"}), 400

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
        return jsonify({"error": str(e)}), 500

    return jsonify({
        "message": "User registered successfully",
        "username": new_user.username,
        "apiKey": new_user.api_token
    }), 201

@bp.route('/login', methods=['POST'])
def login():
    data = request.get_json() or {}
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
    
    return jsonify({"error": "Invalid credentials"}), 401