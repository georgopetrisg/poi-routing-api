import json
from app import create_app
from app.database import db
from app.models import Poi

app = create_app()

def import_data():
    with app.app_context():
        db.create_all()
        
        try:
            with open('data/pois_updated.json', 'r', encoding='utf-8') as f:
                data = json.load(f)
        except FileNotFoundError:
            print("pois.json not found.")
            return

        if isinstance(data, dict) and 'features' in data:
            items = data['features']
        elif isinstance(data, list):
            items = data
        else:
            print("Uknown JSON format.")
            return

        count = 0
        for item in items:
            properties = item.get('properties', {})
            geometry = item.get('geometry', {})
            name = properties.get('name')

            if not name:
                print(f"Skipping ID {item.get('id')} - No name found")
                continue
            
            lat = None
            lon = None
            coords = geometry.get('coordinates')

            if geometry.get('type') == 'Point':
                lon = coords[0]
                lat = coords[1]
            
            elif geometry.get('type') == 'Polygon':
                # Use the first coordinate
                first_point = coords[0][0]
                lon = first_point[0]
                lat = first_point[1]

            if lat and lon:
                poi_id = str(item.get('id')) or str(properties.get('@id'))
                
                new_poi = Poi(
                    id=poi_id,
                    name=name,
                    category=properties.get('amenity', 'cafe'),
                    lat=lat,
                    lon=lon,
                    description=properties.get('building')
                )

                db.session.merge(new_poi)
                count += 1

        db.session.commit()
        print(f"{count} POIs imported.")

if __name__ == '__main__':
    import_data()