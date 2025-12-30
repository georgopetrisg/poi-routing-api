from app.pois import bp
from flask import jsonify, request
from app.models import Poi
import json

with open('data/pois_updated.json', 'r', encoding='utf-8') as f:
    data = json.load(f)
    features = data['features']

@bp.route("", methods=["GET"])
def list_pois():
    q = request.args.get('q')
    category = request.args.get('category')
    lat = request.args.get('lat', type=float)
    lon = request.args.get('lon', type=float)
    radius = request.args.get('radius', type=int)
    limit = request.args.get('limit', default=50, type=int)
    offset = request.args.get('offset', default=0, type=int)
    
    query = Poi.query

    if category:
        query = query.filter(Poi.category == category)

    results = query.all()

    start = offset
    end = offset + limit
    paginated_results = results[start:end]

    return jsonify({
        "count": len(paginated_results),
        "total": len(results),
        "results": [p.to_dict() for p in paginated_results]
    })


@bp.route("/<string:poi_id>", methods=["GET"])
def get_poi(poi_id):
    poi = Poi.query.get(poi_id)
    
    if poi is None:
        return jsonify({"message": "POI not found"}), 404
        
    return jsonify(poi.to_dict())