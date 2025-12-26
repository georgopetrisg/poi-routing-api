from app.database import db
import datetime
import json

class Poi(db.Model):
    __tablename__ = 'pois'

    id = db.Column(db.String(50), primary_key=True)
    name = db.Column(db.String(100), nullable=True)
    category = db.Column(db.String(50), nullable=True)
    description = db.Column(db.Text, nullable=True)
    lat = db.Column(db.Float, nullable=False)
    lon = db.Column(db.Float, nullable=False)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "category": self.category,
            "description": self.description,
            "location": {"lat": self.lat, "lon": self.lon},
        }

class Route(db.Model):
    __tablename__ = 'routes'

    id = db.Column(db.String(50), primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    public = db.Column(db.Boolean, default=False)
    owner_id = db.Column(db.String(50), nullable=True)
    
    # Saving complex data (json, dicts, lists) as text (JSON string)
    _geometry = db.Column('geometry', db.Text, nullable=True)
    _poi_sequence = db.Column('poi_sequence', db.Text, nullable=True)
    
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)

    @property
    def geometry(self):
        return json.loads(self._geometry) if self._geometry else {}

    @geometry.setter
    def geometry(self, value):
        self._geometry = json.dumps(value)

    @property
    def poi_sequence(self):
        return json.loads(self._poi_sequence) if self._poi_sequence else {}

    @poi_sequence.setter
    def poi_sequence(self, value):
        self._poi_sequence = json.dumps(value)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "public": self.public,
            "geometry": self.geometry,
            "owner_id": self.owner_id,
            "poiSequence": self.poi_sequence,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }