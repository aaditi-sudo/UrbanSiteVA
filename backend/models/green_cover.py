from database import db


class GreenCover(db.Model):

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    site_id = db.Column(
        db.Integer,
        db.ForeignKey("site.id"),
        nullable=False
    )

    green_percentage = db.Column(
        db.Float,
        nullable=False
    )

    vegetation_area = db.Column(
        db.Float,
        nullable=False
    )

    mean_ndvi = db.Column(
        db.Float,
        nullable=True
    )

    def to_dict(self):
        return {
            "id": self.id,
            "site_id": self.site_id,
            "green_percentage": self.green_percentage,
            "vegetation_area": self.vegetation_area,
            "mean_ndvi": self.mean_ndvi
        }