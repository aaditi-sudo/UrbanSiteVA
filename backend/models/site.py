from backend.database import db


class Site(db.Model):
    __tablename__ = "sites"

    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(
        db.String(200),
        nullable=False
    )

    location = db.Column(
        db.String(300),
        nullable=False
    )

    latitude = db.Column(
        db.Float,
        nullable=False
    )

    longitude = db.Column(
        db.Float,
        nullable=False
    )

    area = db.Column(
        db.Float,
        nullable=True
    )

    green_cover = db.relationship(
        "GreenCover",
        backref="site",
        lazy=True,
        cascade="all, delete-orphan"
    )

    climate = db.relationship(
        "ClimateData",
        backref="site",
        lazy=True,
        cascade="all, delete-orphan"
    )

    carbon = db.relationship(
        "CarbonData",
        backref="site",
        lazy=True,
        cascade="all, delete-orphan"
    )
    population_data = db.relationship(
        "PopulationData",
        backref="site",
        lazy=True
    )
    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "location": self.location,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "area": self.area
        }





