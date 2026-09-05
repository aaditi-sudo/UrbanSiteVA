import json
from pathlib import Path

from flask import Blueprint, jsonify, request
from database import db
from models.site import Site
from analysis.score import calculate_score
from models.climate import ClimateData
from models.green_cover import GreenCover
from models.carbon import CarbonData
from recommendations.engine import generate_recommendations
from analysis.simulation import simulate_site
from models.population import PopulationData
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
        ],
        "population": [
            p.to_dict()
            for p in site.population_data
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

@sites_bp.route(
    "/api/sites/<int:site_id>/process-data",
    methods=["POST"]
)
def process_site_data(site_id):

    # Check that the site exists
    site = Site.query.get_or_404(site_id)

    # --------------------------------------------------
    # Current prototype restriction
    # --------------------------------------------------
    # The existing processed JSON files are for the
    # Velachery prototype only.
    #
    # Do NOT attach these values to arbitrary sites.
    # Tamil Nadu-wide/site-specific processing will be
    # supported when the spatial processing pipeline
    # is generalized.
    # --------------------------------------------------

    site_name = site.name.strip().lower()
    site_location = site.location.strip().lower()

    if "velachery" not in site_name and "velachery" not in site_location:
        return jsonify({
            "error": (
                "Processed environmental data is currently "
                "available only for the Velachery prototype site. "
                "Site-specific Tamil Nadu processing is not "
                "available for this location yet."
            )
        }), 400

    # Project root:
    # backend/api/sites.py
    #       ↓
    # backend
    #       ↓
    # project root
    project_root = Path(__file__).resolve().parents[2]

    processed_dir = project_root / "data" / "processed"

    # --------------------------------------------------
    # Load processed JSON files
    # --------------------------------------------------

    try:
        with open(
            processed_dir / "ndvi_summary.json",
            "r",
            encoding="utf-8"
        ) as file:
            ndvi_data = json.load(file)

        with open(
            processed_dir / "heat_summary.json",
            "r",
            encoding="utf-8"
        ) as file:
            heat_data = json.load(file)

        with open(
            processed_dir / "uhi_summary.json",
            "r",
            encoding="utf-8"
        ) as file:
            uhi_data = json.load(file)

        with open(
            processed_dir / "humidity_summary.json",
            "r",
            encoding="utf-8"
        ) as file:
            humidity_data = json.load(file)

        with open(
            processed_dir / "carbon_summary.json",
            "r",
            encoding="utf-8"
        ) as file:
            carbon_data = json.load(file)

    except FileNotFoundError as error:
        return jsonify({
            "error": f"Processed data file not found: {error.filename}"
        }), 404

    # --------------------------------------------------
    # Remove old data for this site
    # --------------------------------------------------

    ClimateData.query.filter_by(
        site_id=site_id
    ).delete()

    GreenCover.query.filter_by(
        site_id=site_id
    ).delete()

    CarbonData.query.filter_by(
        site_id=site_id
    ).delete()

    # --------------------------------------------------
    # Create GreenCover record
    # --------------------------------------------------

    green_cover = GreenCover(
        site_id=site_id,
        green_percentage=ndvi_data["green_percentage"],
        vegetation_area=ndvi_data["vegetation_area_sq_m"],
        mean_ndvi=ndvi_data["mean_ndvi"]
    )

    # --------------------------------------------------
    # Create ClimateData record
    # --------------------------------------------------

    climate = ClimateData(
        site_id=site_id,
        temperature=heat_data[
            "mean_surface_temperature_celsius"
        ],
        uhi_index=uhi_data[
            "suhi_intensity_celsius"
        ],
        humidity=humidity_data[
            "mean_relative_humidity_percent"
        ]
    )

    # --------------------------------------------------
    # Create CarbonData record
    # --------------------------------------------------

    carbon = CarbonData(
        site_id=site_id,
        carbon_intensity=carbon_data["carbon_intensity"],
        emission_source=carbon_data["emission_source"]
    )

    # --------------------------------------------------
    # Save to database
    # --------------------------------------------------

    db.session.add(green_cover)
    db.session.add(climate)
    db.session.add(carbon)

    db.session.commit()

    return jsonify({
        "message": (
            "Processed environmental data successfully "
            "connected to the Velachery site."
        ),
        "site": site.to_dict(),
        "green_cover": green_cover.to_dict(),
        "climate": climate.to_dict(),
        "carbon": carbon.to_dict()
    }), 201