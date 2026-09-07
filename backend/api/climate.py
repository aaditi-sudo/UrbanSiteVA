from flask import Blueprint, jsonify, request
from backend.database import db
from backend.models.climate import ClimateData


climate_bp = Blueprint("climate", __name__)


@climate_bp.route("/api/climate", methods=["GET"])
def get_climate():

    data = ClimateData.query.all()

    return jsonify([
        item.to_dict()
        for item in data
    ])



@climate_bp.route("/api/climate", methods=["POST"])
def add_climate():

    data = request.get_json()

    climate = ClimateData(
        site_id=data["site_id"],
        temperature=data["temperature"],
        uhi_index=data["uhi_index"],
        humidity=data["humidity"]
    )

    db.session.add(climate)
    db.session.commit()

    return jsonify({
        "message": "Climate data added successfully",
        "climate": climate.to_dict()
    }), 201


