from flask import Flask, jsonify
from database import db
from models.site import Site
from api.sites import sites_bp
from models.climate import ClimateData
from api.climate import climate_bp
from models.green_cover import GreenCover
from api.green_cover import green_cover_bp
from models.carbon import CarbonData
from api.carbon import carbon_bp

app = Flask(__name__)

# Database configuration
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///urban.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Connect database
db.init_app(app)

# Create tables
with app.app_context():
    db.create_all()

# Register APIs
app.register_blueprint(sites_bp)
app.register_blueprint(climate_bp)
app.register_blueprint(green_cover_bp)
app.register_blueprint(carbon_bp)

@app.route("/")
def home():
    return "UrbanSiteVA Backend is Running!"


@app.route("/api/status")
def status():
    return jsonify({
        "status": "running",
        "project": "UrbanSiteVA"
    })


if __name__ == "__main__":
    app.run(debug=True)