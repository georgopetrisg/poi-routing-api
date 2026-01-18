def validate_geojson_linestring(geometry):
    if not geometry:
        return "Geometry is required."
    if not isinstance(geometry, dict):
        return "Geometry must be a JSON object."
    if geometry.get('type') != 'LineString':
        return "Geometry type must be 'LineString'."
    
    coords = geometry.get('coordinates')
    if not isinstance(coords, list) or len(coords) < 2:
        return "Coordinates must be a list with at least two points."
    
    for point in coords:
        if not isinstance(point, list) or len(point) != 2:
            return "Each coordinate must be a [lon, lat] pair."
        if not (isinstance(point[0], (int, float)) and isinstance(point[1], (int, float))):
            return "Coordinates must be numeric."
        
    return None

def validate_poi_sequence(poi_sequence):
    if not isinstance(poi_sequence, list):
        return "POI Sequence must be a list."
    for poi in poi_sequence:
        if not isinstance(poi, dict):
            return "Each POI in the sequence must be a dictionary."
        if 'poiId' not in poi or not isinstance(poi['poiId'], str):
            return "Each POI must have a 'poiId' of type string."
        if 'name' not in poi or not isinstance(poi['name'], str):
            return "Each POI must have a 'name' of type string."
    return None

def validate_compute_locations(locations):
    if not isinstance(locations, list) or len(locations) < 2:
        return "At least two locations are required."
    for loc in locations:
        if not isinstance(loc, list) or len(loc) != 2:
            return "Each location must be a [lat, lon] pair."
        if not (isinstance(loc[0], (int, float)) and isinstance(loc[1], (int, float))):
            return "Location coordinates must be numeric."
        lat, lon = loc
        if not (-90 <= lat <= 90):
            return "Latitude must be between -90 and 90."
        if not (-180 <= lon <= 180):
            return "Longitude must be between -180 and 180."
    return None

def validate_route_data(data):
    errors = {}
    
    name = data.get('name')
    if not name or not isinstance(name, str) or not name.strip():
        errors['name'] = "Name is required and must be a string."
    
    public = data.get('public')
    if public is not None and not isinstance(public, bool):
        errors['public'] = "Public must be a boolean."

    vehicle = data.get('vehicle')
    if vehicle and (not isinstance(vehicle, str) or not vehicle.strip()):
        errors['vehicle'] = "Vehicle must be a string."
    
    poi_seq_error = validate_poi_sequence(data.get('poiSequence'))
    if poi_seq_error:
        errors['poiSequence'] = poi_seq_error

    geo_error = validate_geojson_linestring(data.get('geometry'))
    if geo_error:
        errors['geometry'] = geo_error
    
    encodedPolyline = data.get('encodedPolyline')
    if encodedPolyline and (not isinstance(encodedPolyline, str) or not encodedPolyline.strip()):
        errors['encodedPolyline'] = "Encoded polyline must be a string."

    ownerId = data.get('ownerId')
    if ownerId and (not isinstance(data.get('ownerId'), str) or not data.get('ownerId').strip()):
        errors['ownerId'] = "Owner ID must be a string."

    return errors

def validate_route_compute(data):
    errors = {}

    loc_error = validate_compute_locations(data.get('locations', []))
    if loc_error:
        errors['locations'] = loc_error

    vehicle = data.get('vehicle')
    if vehicle and (not isinstance(vehicle, str) or not vehicle.strip()):
        errors['vehicle'] = "Vehicle must be a string."
    
    algorithm = data.get('algorithm')
    if algorithm and (not isinstance(algorithm, str) or not algorithm.strip()):
        errors['algorithm'] = "Algorithm must be a string."
    
    format = data.get('format')
    if format and (not isinstance(format, str) or not format.strip()):
        errors['format'] = "Format must be a string."
    
    return errors

def validate_route_put_patch(data):
    errors = {}

    if 'name' in data:
        name = data.get('name')
        if not name or not isinstance(name, str) or not name.strip():
            errors['name'] = "Name must be a non-empty string."

    if 'public' in data:
        public = data.get('public')
        if not isinstance(public, bool):
            errors['public'] = "Public must be a boolean."

    if 'vehicle' in data:
        vehicle = data.get('vehicle')
        if vehicle and (not isinstance(vehicle, str) or not vehicle.strip()):
            errors['vehicle'] = "Vehicle must be a string."

    if 'poiSequence' in data:
        poi_seq_error = validate_poi_sequence(data.get('poiSequence'))
        if poi_seq_error:
            errors['poiSequence'] = poi_seq_error

    if 'geometry' in data:
        geo_error = validate_geojson_linestring(data.get('geometry'))
        if geo_error:
            errors['geometry'] = geo_error

    if 'encodedPolyline' in data:
        encodedPolyline = data.get('encodedPolyline')
        if encodedPolyline and (not isinstance(encodedPolyline, str) or not encodedPolyline.strip()):
            errors['encodedPolyline'] = "Encoded polyline must be a string."

    if 'ownerId' in data:
        ownerId = data.get('ownerId')
        if ownerId and (not isinstance(ownerId, str) or not ownerId.strip()):
            errors['ownerId'] = "Owner ID must be a string."

    return errors

def validate_auth_creds(data):
    errors = {}

    if not data.get('username'):
        errors['username'] = 'Required'
    if not data.get('password'):
        errors['password'] = 'Required'
    
    return errors