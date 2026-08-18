from flask import Blueprint, jsonify, request
from database import db
from models.carbon import CarbonData


carbon_bp = Blueprint("carbon", __name__)


@carbon_bp.route("/api/carbon", methods=["GET"])
def get_carbon():

    data = CarbonData.query.all()

    return jsonify([
        item.to_dict()
        for item in data
    ])



@carbon_bp.route("/api/carbon", methods=["POST"])
def add_carbon():

    data = request.get_json()

    carbon = CarbonData(
        site_id=data["site_id"],
        carbon_intensity=data["carbon_intensity"],
        emission_source=data["emission_source"]
    )

    db.session.add(carbon)
    db.session.commit()

    return jsonify({
        "message": "Carbon data added successfully",
        "carbon": carbon.to_dict()
    }), 201