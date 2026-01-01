from sqlalchemy import *
from app.pois import bp
from flask import jsonify, request
from app.models import Poi
import json

from math import radians, cos, sin, asin, sqrt

def haversine(lon1, lat1, lon2, lat2):
    """
    Calculate the great circle distance in kilometers between two points 
    on the earth (specified in decimal degrees)
    """
    # convert decimal degrees to radians 
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])

    # haversine formula 
    dlon = lon2 - lon1 
    dlat = lat2 - lat1 
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a)) 
    r = 6371000 # Radius of earth in kilometers.
    return c * r

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

    if q:
        search = f"%{q}%"
        query = query.filter(or_(Poi.name.ilike(search), 
                                 Poi.description.ilike(search),
                                 Poi.category.ilike(search)))

    if category:
        query = query.filter(Poi.category == category)

    results = query.all()

    if lat is not None and lon is not None and radius is not None:
        nearby_results = []
        for poi in results:
            d = haversine(lon, lat, poi.lon, poi.lat)
            if d <= radius:
                nearby_results.append(poi)
        results = nearby_results

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