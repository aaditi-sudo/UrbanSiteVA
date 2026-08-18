from database import db


class CarbonData(db.Model):

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    site_id = db.Column(
        db.Integer,
        db.ForeignKey("site.id"),
        nullable=False
    )

    carbon_intensity = db.Column(
        db.Float,
        nullable=False
    )

    emission_source = db.Column(
        db.String(100),
        nullable=False
    )


    def to_dict(self):
        return {
            "id": self.id,
            "site_id": self.site_id,
            "carbon_intensity": self.carbon_intensity,
            "emission_source": self.emission_source
        }