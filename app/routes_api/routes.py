from app.routes_api import bp
from flask import jsonify, request
from app.models import Route

ROUTES = []

@bp.route("", methods=["GET"])
def list_routes():
    routes = Route.query.all()

    return jsonify({
        "count": len(routes),
        "results": [route.to_dict() for route in routes]
    })

@bp.route("/compute", methods=["POST"])
def compute_route():
    data = request.get_json()
    if not data or "locations" not in data:
        return jsonify({"code": "invalid_request", "message": "Missing locations"}), 400
    return jsonify({
        "distanceMeters": 13200.5,
        "durationMillis": 950000,
        "geometry": {
            "type": "LineString",
            "coordinates": [[23.41122, 35.49547], [23.41200, 35.49600]]
        },
        "poiSequence": data.get("locations", [])
    })

@bp.route("", methods=["POST"])
def persist_route():
    data = request.get_json()
    if not data or "name" not in data:
        return jsonify({"code": "invalid_request", "message": "Missing name"}), 400
    new_route = {
        "id": f"route_{len(ROUTES)+1}",
        "name": data["name"],
        "public": data.get("public", False),
        "geometry": data.get("geometry", {}),
    }
    ROUTES.append(new_route)
    return jsonify(new_route), 201