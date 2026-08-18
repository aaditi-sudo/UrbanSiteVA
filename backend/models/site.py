from database import db


class Site(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String(100), nullable=False)

    location = db.Column(
        db.String(100),
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
        nullable=False
    )
    climate_data = db.relationship(
        "ClimateData",
        backref="site",
        lazy=True
    )

    green_cover = db.relationship(
        "GreenCover",
        backref="site",
        lazy=True
    )

    carbon_data = db.relationship(
        "CarbonData",
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