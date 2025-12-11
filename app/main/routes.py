from app.main import bp
from flask import jsonify

@bp.route("/about", methods=["GET"])
def about():
    return jsonify({
        "team": [
            {"id": "inf2023031", "name": "Georgios Georgopetris", "role": "Undergraduate Student"},
            {"id": "inf2023012", "name": "Eleni-Maria Anthi", "role": "Undergraduate Student"},
        ]
    }), 200