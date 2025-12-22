from app.pois import bp
from flask import jsonify, request
import json

with open('data/pois_updated.json', 'r', encoding='utf-8') as f:
    data = json.load(f)
    features = data['features']

@bp.route("", methods=["GET"])
def list_pois():
    return jsonify({
        "count": len(features),
        "results": features
    })

@bp.route("/<string:poi_id>", methods=["GET"])
def get_poi(poi_id):
    poi = next((p for p in features if p["id"] == poi_id), None)
    if not poi:
        return jsonify({"code": "not_found", "message": "POI not found"}), 404
    return jsonify(poi)