from backend.database import db


class PopulationData(db.Model):

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    site_id = db.Column(
        db.Integer,
        db.ForeignKey("sites.id"),
        nullable=False
    )

    total_population = db.Column(
        db.Float,
        nullable=False
    )

    area_km2 = db.Column(
        db.Float,
        nullable=False
    )

    population_density = db.Column(
        db.Float,
        nullable=False
    )

    data_year = db.Column(
        db.Integer,
        nullable=False
    )

    data_source = db.Column(
        db.String(100),
        nullable=False
    )

    def to_dict(self):

        return {
            "id": self.id,
            "site_id": self.site_id,
            "total_population": self.total_population,
            "area_km2": self.area_km2,
            "population_density_per_km2": (
                self.population_density
            ),
            "data_year": self.data_year,
            "data_source": self.data_source
        }



