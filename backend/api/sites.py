from flask import Blueprint, jsonify, request
from database import db
from models.site import Site
from analysis.score import calculate_score
from models.climate import ClimateData
from models.green_cover import GreenCover
from models.carbon import CarbonData
from recommendations.engine import generate_recommendations
from analysis.simulation import simulate_site

sites_bp = Blueprint("sites", __name__)


@sites_bp.route("/api/sites", methods=["GET"])
def get_sites():

    sites = Site.query.all()

    return jsonify([
        site.to_dict()
        for site in sites
    ])



@sites_bp.route("/api/sites", methods=["POST"])
def add_site():

    data = request.get_json()

    required_fields = [
        "name",
        "location",
        "latitude",
        "longitude",
        "area"
    ]


    for field in required_fields:
        if field not in data:
            return jsonify({
                "error": f"Missing field: {field}"
            }), 400


    site = Site(
        name=data["name"],
        location=data["location"],
        latitude=data["latitude"],
        longitude=data["longitude"],
        area=data["area"]
    )


    db.session.add(site)
    db.session.commit()


    return jsonify({
        "message": "Site added successfully",
        "site": site.to_dict()
    }), 201
@sites_bp.route("/api/sites/<int:site_id>/summary", methods=["GET"])
def get_site_summary(site_id):

    site = Site.query.get_or_404(site_id)

    return jsonify({
        "site": site.to_dict(),
        "climate": [
            c.to_dict()
            for c in site.climate_data
        ],
        "green_cover": [
            g.to_dict()
            for g in site.green_cover
        ],
        "carbon": [
            c.to_dict()
            for c in site.carbon_data
        ]
    })
@sites_bp.route("/api/sites/<int:site_id>/score", methods=["GET"])
def get_site_score(site_id):

    site = Site.query.get_or_404(site_id)

    climate = ClimateData.query.filter_by(site_id=site_id).first()
    green_cover = GreenCover.query.filter_by(site_id=site_id).first()
    carbon = CarbonData.query.filter_by(site_id=site_id).first()

    if not climate or not green_cover or not carbon:
        return jsonify({
            "error": "Incomplete environmental data for this site."
        }), 400

    result = calculate_score(
        climate,
        green_cover,
        carbon
    )

    recommendations = generate_recommendations(
        climate,
        green_cover,
        carbon
    )

    return jsonify({
        "site": site.name,
        "score": result["score"],
        "rating": result["rating"],
        "recommendations": recommendations
    })
@sites_bp.route("/api/sites/<int:site_id>/simulate", methods=["POST"])
def simulate(site_id):

    site = Site.query.get_or_404(site_id)

    climate = ClimateData.query.filter_by(site_id=site_id).first()
    green_cover = GreenCover.query.filter_by(site_id=site_id).first()
    carbon = CarbonData.query.filter_by(site_id=site_id).first()

    if not climate or not green_cover or not carbon:
        return jsonify({
            "error": "Incomplete environmental data."
        }), 400

    data = request.get_json()

    new_green = data.get("green_percentage")

    if new_green is None:
        return jsonify({
            "error": "green_percentage is required."
        }), 400

    result = simulate_site(
        climate,
        green_cover,
        carbon,
        new_green
    )

    return jsonify({
        "site": site.name,
        "current_score": calculate_score(
            climate,
            green_cover,
            carbon
        )["score"],
        "current_green_cover": green_cover.green_percentage,
        "proposed_green_cover": new_green,
        "predicted_score": result["predicted_score"],
        "predicted_rating": result["predicted_rating"],
        "predicted_uhi": result["predicted_uhi"]
    })