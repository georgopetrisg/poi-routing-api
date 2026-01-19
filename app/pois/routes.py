from sqlalchemy import *
from app.pois import bp
from flask import jsonify, request
from app.models import Poi
import json
from app.errors import APIError

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

@bp.route("", methods=["GET"])
def list_pois():
    params_errors = {}

    q = request.args.get('q')
    category = request.args.get('category')
    raw_lat = request.args.get('lat')
    raw_lon = request.args.get('lon')
    raw_radius = request.args.get('radius')
    raw_limit = request.args.get('limit', default=100)
    raw_offset = request.args.get('offset', default=0)

    try:
        limit = int(raw_limit)
        if limit < 1 or limit > 1000:
            params_errors['limit'] = "Must be between 1 and 1000"
    except ValueError:
        params_errors['limit'] = "Must be an integer"

    try:
        offset = int(raw_offset)
        if offset < 0:
            params_errors['offset'] = "Must be a possitive integer"
    except ValueError:
        params_errors['offset'] = "Must be an integer"

    lat, lon, radius = None, None, None

    if raw_lat:
        try:
            lat = float(raw_lat)
            if not -90 <= lat <= 90:
                params_errors['lat'] = "Must be between -90 and 90"
        except ValueError:
            params_errors['lat'] = "Must be a float"
    if raw_lon:
        try:
            lon = float(raw_lon)
            if not -180 <= lon <= 180:
                params_errors['lon'] = "Must be between -180 and 180"
        except ValueError:
            params_errors['lon'] = "Must be a float"
    if raw_radius:
        try:
            radius = float(raw_radius)
            if radius <= 0:
                params_errors['radius'] = "Must be a positive integer"
        except ValueError:
            params_errors['radius'] = "Must be an integer"

    has_lat = lat is not None
    has_lon = lon is not None

    if has_lat and not has_lon:
        params_errors['lon'] = "Longitude is required when latitude is provided"
    if has_lon and not has_lat:
        params_errors['lat'] = "Latitude is required when longitude is provided"

    if params_errors:
        raise APIError(
            message="Invalid query parameters.",
            status_code=400,
            details=params_errors
        )

    query_echo = {
        "q": q,
        "category": category,
        "lat": lat,
        "lon": lon,
        "radius": radius,
        "limit": limit,
        "offset": offset
    }

    query_echo = {k: v for k, v in query_echo.items() if v is not None}
    
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
            poi_lat = poi.location.get('lat')
            poi_lon = poi.location.get('lon')
            d = haversine(lon, lat, poi_lon, poi_lat)
            if d <= radius:
                nearby_results.append(poi)
        results = nearby_results

    start = offset
    end = offset + limit
    paginated_results = results[start:end]

    return jsonify({
        "query": query_echo,
        "count": len(paginated_results),
        "results": [p.to_dict() for p in paginated_results]
    }), 200

@bp.route("/<string:poi_id>", methods=["GET"])
def get_poi(poi_id):
    poi = Poi.query.get(poi_id)
    
    if poi is None:
        raise APIError(
            message=f"The POI with id '{poi_id}' does not exist.", 
            status_code=404,
            details={f"{poi_id}": "Not found"}
        )
        
    return jsonify(poi.to_dict()), 200