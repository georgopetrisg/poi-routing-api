from app.routes_api import bp
from flask import jsonify, request, g
from app.models import Route, User
from app.database import db
import uuid
import os
from dotenv import load_dotenv
import requests
from app.auth.decorator import require_api_key

load_dotenv()
GRAPHHOPPER_API_KEY = os.getenv("GRAPHHOPPER_API_KEY")

@bp.route("", methods=["GET"])
def list_routes():
    public = request.args.get('public', type=lambda v: v.lower() == 'true' )
    owner_id = request.args.get('ownerId')

    limit = request.args.get('limit', default=50, type=int)
    offset = request.args.get('offset', default=0, type=int)

    query = Route.query

    if public:
        query = query.filter(Route.public == True)

    if owner_id:
        query = query.filter(Route.owner_id == owner_id)
    
    total = query.count()

    routes = query.limit(limit).offset(offset).all()

    return jsonify({
        "count": len(routes),
        "total": total,
        "results": [r.to_dict() for r in routes]
    }), 200

@bp.route("/<string:route_id>", methods=["GET"])

def get_route(route_id):
    route = Route.query.get_or_404(route_id)
    
    token = request.headers.get('X-API-KEY')
    user = None
    
    if token:
        user = User.query.filter_by(api_token=token).first()
    
    is_owner = (user and user.id == route.owner_id)
    
    if route.public or is_owner:
        return jsonify(route.to_dict()), 200
    else:
        return jsonify({"error": "Forbidden: This route is private"}), 403

@bp.route("", methods=["POST"])
@require_api_key
def persist_route():
    data = request.get_json() or {}

    if 'name' not in data:
        return jsonify({"code": "invalid_request", "message": "Missing route name"}), 400

    new_id = f"route_{uuid.uuid4()}"

    new_route = Route(
        id=new_id,
        name=data.get('name'),
        public=data.get('public', False),
        vehicle=data.get('vehicle'),
        owner_id=data.get('ownerId'),
        encoded_polyline=data.get('encodedPolyline')
    )

    if 'poiSequence' in data:
        new_route.poi_sequence = data['poiSequence']

    if 'geometry' in data:
        new_route.geometry = data['geometry']

    try:
        db.session.add(new_route)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({"code": "database_error", "message": str(e)}), 500
    
    return jsonify(new_route.to_dict()), 201

@bp.route("/<string:route_id>", methods=["PUT", "PATCH"])
@require_api_key
def update_route(route_id):
    route = Route.query.get_or_404(route_id)
    data = request.get_json() or {}

    if 'name' in data:
        route.name = data['name']
    if 'public' in data:
        route.public = data['public']
    if 'vehicle' in data:
        route.vehicle = data['vehicle']
    if 'ownerId' in data:
        route.owner_id = data['ownerId']
    if 'poiSequence' in data:
        route.poi_sequence = data['poiSequence']
    if 'geometry' in data:
        route.geometry = data['geometry']
    if 'encodedPolyline' in data:
        route.encoded_polyline = data['encodedPolyline']

    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({"code": "database_error", "message": str(e)}), 500

    return jsonify(route.to_dict()), 200

@bp.route("/<string:route_id>", methods=["DELETE"])
@require_api_key
def delete_route(route_id):
    route = Route.query.get_or_404(route_id)

    try:
        db.session.delete(route)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({"code": "database_error", "message": str(e)}), 500

    return jsonify({"message": f"Route {route_id} deleted successfully."}), 200

@bp.route("/compute", methods=["POST"])
@require_api_key
def compute_route():
    data = request.get_json() or {}
    locations = data.get('locations', [])

    if not locations or len(locations) < 2:
        return jsonify({"code": "invalid_request", "message": "At least two locations are required to compute a route."}), 400
    
    vehicle = data.get('vehicle', 'car')

    GRAPHHOPPER_URL = "https://graphhopper.com/api/1/route"

    params = [
        ('key', GRAPHHOPPER_API_KEY),
        ('vehicle', vehicle),
        ('type', 'json'),
        ('points_encoded', 'false'),
        ('instructions', 'false')
    ]
    
    for loc in locations:
        lat_lon = f"{loc[1]},{loc[0]}"
        params.append(('point', lat_lon))

    try:
        response = requests.get(GRAPHHOPPER_URL, params=params)
        GRAPHHOPPER_DATA = response.json()

        if response.status_code != 200:
            return jsonify({"code": "routing_error", "message": GRAPHHOPPER_DATA.get('message', 'Error from routing service')}), response.status_code
        
        route_info = GRAPHHOPPER_DATA['paths'][0]

        result = {
            "distance": route_info['distance'],
            "time": route_info['time'],
            "geometry": route_info['points'],
        }

        return jsonify(result), 200
    except Exception as e:
        return jsonify({"error": "Failed to connect to routing service", "details": str(e)}), 500
