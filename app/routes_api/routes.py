from app.routes_api import bp
from flask import jsonify, request, g, current_app
from app.models import Route, User
from app.database import db
import uuid
import requests
from app.auth.decorator import require_api_key
from app.errors import APIError
from app.validators import validate_route_compute, validate_route_data, validate_route_put_patch

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
    route = Route.query.get(route_id)

    if not route:
        raise APIError(
            message="Route not found", 
            status_code=404,
            details={f"{route_id}": "Not found"}
        )
    
    token = request.headers.get('X-API-KEY')
    user = None
    
    if token:
        user = User.query.filter_by(api_token=token).first()
    
    is_owner = (user and user.id == route.owner_id)
    
    if route.public or is_owner:
        return jsonify(route.to_dict()), 200
    else:
        raise APIError(
            message="This route is private", 
            status_code=403,
            details={f"{route_id}": "Private"}
        )

@bp.route("", methods=["POST"])
@require_api_key
def persist_route():
    data = request.get_json(silent=True)
    if data is None:
        raise APIError(
            message="Invalid or missing JSON body.",
            status_code=400,
            details={"body": "Invalid JSON format"}
        )

    errors = validate_route_data(data)
    if errors:
        raise APIError(
            message="Invalid route data.",
            status_code=400,
            details=errors
        )
    
    new_id = f"route_{uuid.uuid4()}"

    new_route = Route(
        id=new_id,
        name=data.get('name'),
        public=data.get('public', False),
        vehicle=data.get('vehicle', 'car'),
        owner_id=data.get('ownerId', g.current_user.id),
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
        raise APIError(
            message=str(e), 
            status_code=500
        )
    
    return jsonify(
        message="Route created successfully.",
        route=new_route.to_dict()
    ), 201

@bp.route("/<string:route_id>", methods=["PUT", "PATCH"])
@require_api_key
def update_route(route_id):
    route = Route.query.get(route_id)
    if route is None:
        raise APIError(
            message="Route not found", 
            status_code=404,
            details={f"{route_id}": "Not found"}
        )
    
    if route.owner_id != g.current_user.id:
        raise APIError(
            message="You do not have permission to modify this route.", 
            status_code=403,
            details={f"{route_id}": "Forbidden"}
        )

    data = request.get_json(silent=True)
    if data is None:
        raise APIError(
            message="Invalid or missing JSON body.",
            status_code=400,
            details={"body": "Invalid JSON format"}
        )
    
    errors = validate_route_put_patch(data)
    if errors:
        raise APIError(
            message="Invalid route data.",
            status_code=400,
            details=errors
        )

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
        raise APIError(
            message=str(e), 
            status_code=500
        )

    return jsonify(
        message="Route updated successfully.",
        route=route.to_dict()
        ), 200

@bp.route("/<string:route_id>", methods=["DELETE"])
@require_api_key
def delete_route(route_id):
    route = Route.query.get(route_id)
    if route is None:
        raise APIError(
            message="Route not found", 
            status_code=404,
            details={f"{route_id}": "Not found"}
        )

    try:
        db.session.delete(route)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        raise APIError(
            message=str(e), 
            status_code=500
        )

    return jsonify({"message": f"Route {route_id} deleted successfully."}), 200

@bp.route("/compute", methods=["POST"])
@require_api_key
def compute_route():
    data = request.get_json(silent=True)
    if data is None:
        raise APIError(
            message="Invalid or missing JSON body.",
            status_code=400,
            details={"body": "Invalid JSON format"}
        )
    
    compute_errors = validate_route_compute(data)
    if compute_errors:
        raise APIError(
            message="Invalid route compute data.",
            status_code=400,
            details=compute_errors
        )

    locations = data.get('locations', [])

    GRAPHHOPPER_API_KEY = current_app.config.get("GRAPHHOPPER_API_KEY")

    if not GRAPHHOPPER_API_KEY:
        raise APIError(
            message="Routing service API key is not configured.", 
            status_code=500
        )

    if not locations or len(locations) < 2:
        raise APIError(
            message="At least two locations are required to compute a route.", 
            status_code=400,
            details={"locations": "At least two required"}
        )

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
            raise APIError(
                message=GRAPHHOPPER_DATA.get('message', 'Error from routing service'), 
                status_code=response.status_code
            )
        
        route_info = GRAPHHOPPER_DATA['paths'][0]

        result = {
            "distance": route_info['distance'],
            "time": route_info['time'],
            "geometry": route_info['points'],
        }

        return jsonify(result), 200
    except Exception as e:
        raise APIError(
            message=str(e), 
            status_code=500
        )