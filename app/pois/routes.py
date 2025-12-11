from app.pois import bp
from flask import jsonify, request

# Mock POI data
POIS = [
    {"id": "poi_1023", "name": "Falassarna Beach", "category": "beach", 
     "location": {"lat": 35.49547, "lon": 23.41122}}
]

@bp.route("", methods=["GET"])
def list_pois():
    q = request.args.get("q")
    category = request.args.get("category")
    limit = int(request.args.get("limit", 50))

    results = POIS
    if category:
        results = [p for p in results if p["category"] == category]
    if q:
        results = [p for p in results if q.lower() in p["name"].lower()]

    return jsonify({
        "query": request.args.to_dict(),
        "count": len(results[:limit]),
        "results": results[:limit]
    })

@bp.route("/<string:poi_id>", methods=["GET"])
def get_poi(poi_id):
    poi = next((p for p in POIS if p["id"] == poi_id), None)
    if not poi:
        return jsonify({"code": "not_found", "message": "POI not found"}), 404
    return jsonify(poi)