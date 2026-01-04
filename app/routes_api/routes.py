from app.routes_api import bp
from flask import jsonify, request
from app.models import Route
from app.database import db
import uuid

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

    return jsonify(route.to_dict()), 200

@bp.route("", methods=["POST"])
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

@bp.route("/compute", methods=["POST"])
def compute_route():
    # data = request.get_json()
    # if not data or "locations" not in data:
    #     return jsonify({"code": "invalid_request", "message": "Missing locations"}), 400
    # return jsonify({
    #     "distanceMeters": 13200.5,
    #     "durationMillis": 950000,
    #     "geometry": {
    #         "type": "LineString",
    #         "coordinates": [[23.41122, 35.49547], [23.41200, 35.49600]]
    #     },
    #     "poiSequence": data.get("locations", [])
    # }), 200
    pass