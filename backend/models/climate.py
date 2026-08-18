from database import db


class ClimateData(db.Model):

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    site_id = db.Column(
        db.Integer,
        db.ForeignKey("site.id"),
        nullable=False
    )

    temperature = db.Column(
        db.Float,
        nullable=False
    )

    uhi_index = db.Column(
        db.Float,
        nullable=False
    )

    humidity = db.Column(
        db.Float,
        nullable=False
    )


    def to_dict(self):
        return {
            "id": self.id,
            "site_id": self.site_id,
            "temperature": self.temperature,
            "uhi_index": self.uhi_index,
            "humidity": self.humidity
        }