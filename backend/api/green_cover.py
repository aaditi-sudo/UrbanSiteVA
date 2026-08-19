from flask import Blueprint, jsonify, request
from database import db
from models.green_cover import GreenCover


green_cover_bp = Blueprint("green_cover", __name__)


@green_cover_bp.route("/api/green-cover", methods=["GET"])
def get_green_cover():

    data = GreenCover.query.all()

    return jsonify([
        item.to_dict()
        for item in data
    ])


@green_cover_bp.route("/api/green-cover", methods=["POST"])
def add_green_cover():

    data = request.get_json()

    green_cover = GreenCover(
        site_id=data["site_id"],
        green_percentage=data["green_percentage"],
        vegetation_area=data["vegetation_area"],
        mean_ndvi=data.get("mean_ndvi")
    )

    db.session.add(green_cover)
    db.session.commit()

    return jsonify({
        "message": "Green cover data added successfully",
        "green_cover": green_cover.to_dict()
    }), 201