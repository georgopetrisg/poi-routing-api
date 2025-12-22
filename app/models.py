from app.database import db

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
