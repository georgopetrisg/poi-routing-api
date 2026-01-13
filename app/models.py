from app.database import db
import datetime
import json
from werkzeug.security import generate_password_hash, check_password_hash
import uuid

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
    vehicle = db.Column(db.String(50), nullable=True)
    owner_id = db.Column(db.String(50), db.ForeignKey('users.id'), nullable=True)

    # Saving complex data (json, dicts, lists) as text (JSON string)
    _poi_sequence = db.Column('poi_sequence', db.Text, nullable=True)
    _geometry = db.Column('geometry', db.Text, nullable=True)

    encoded_polyline = db.Column(db.Text, nullable=True)
    
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

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
            "vehicle": self.vehicle,
            "ownerId": self.owner_id,
            "poiSequence": self.poi_sequence,
            "geometry": self.geometry,
            "encodedPolyline": self.encoded_polyline,
            "createdAt": self.created_at.isoformat() if self.created_at else None,
            "updatedAt": self.updated_at.isoformat() if self.updated_at else None
        }
    
class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.String(50), primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    api_token = db.Column(db.String(100), unique=True) 

    routes = db.relationship('Route', backref='owner', lazy='dynamic')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def generate_token(self):
        self.api_token = str(uuid.uuid4())