from app.pois import bp
from flask import jsonify, request
from app.models import Poi
import json

with open('data/pois_updated.json', 'r', encoding='utf-8') as f:
    data = json.load(f)
    features = data['features']

@bp.route("", methods=["GET"])
def list_pois():
    all_pois = Poi.query.all()

    results = [p.to_dict() for p in all_pois]

    return jsonify({
        "count": len(results),
        "results": results
    })


@bp.route("/<string:poi_id>", methods=["GET"])
def get_poi(poi_id):
    poi = Poi.query.get(poi_id)
    
    if poi is None:
        return jsonify({"message": "POI not found"}), 404
        
    return jsonify(poi.to_dict())