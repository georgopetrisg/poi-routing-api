from app.main import bp
from flask import jsonify, render_template

@bp.route("/about", methods=["GET"])
def about():
    return jsonify({
        "team": [
            {"id": "inf2023031", "name": "Georgios Georgopetris", "role": "Undergraduate Student"},
            {"id": "inf2023012", "name": "Eleni-Maria Anthi", "role": "Undergraduate Student"},
        ]
    }), 200

@bp.route("/", methods=["GET"])
def index():
    return render_template("dashboard.html")

@bp.route("/login", methods=["GET"])
def login():
    return render_template("login.html")

@bp.route("/register", methods=["GET"])
def register():
    return render_template("register.html")