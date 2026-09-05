import ee
import json
from pathlib import Path

from config import EE_PROJECT


# -----------------------------
# Settings
# -----------------------------

START_DATE = "2025-01-01"
END_DATE = "2025-12-31"

CLOUD_THRESHOLD = 20
SCALE = 30

REFERENCE_BUFFER_METERS = 5000
REFERENCE_NDVI_THRESHOLD = 0.30


# -----------------------------
# Initialize Earth Engine
# -----------------------------

ee.Initialize(project=EE_PROJECT)


# -----------------------------
# Load Tamil Nadu boundary
# -----------------------------

boundary_path = Path(
    "data/raw/tamil_nadu_boundary.geojson"
)

with open(
    boundary_path,
    "r",
    encoding="utf-8"
) as file:
    boundary_geojson = json.load(file)

geometry = ee.Geometry(
    boundary_geojson["features"][0]["geometry"]
)


# -----------------------------
# Create reference search zone
# -----------------------------

buffered_geometry = geometry.buffer(
    REFERENCE_BUFFER_METERS
)

reference_search_geometry = (
    buffered_geometry.difference(
        geometry,
        1
    )
)


# -----------------------------
# Load Landsat 8 imagery
# -----------------------------

print("Loading Landsat imagery for Tamil Nadu...")

landsat = (
    ee.ImageCollection(
        "LANDSAT/LC08/C02/T1_L2"
    )
    .filterBounds(
        buffered_geometry
    )
    .filterDate(
        START_DATE,
        END_DATE
    )
    .filter(
        ee.Filter.lt(
            "CLOUD_COVER",
            CLOUD_THRESHOLD
        )
    )
)


# -----------------------------
# Create median composite
# -----------------------------

image = landsat.median()


# -----------------------------
# Calculate land-surface temperature
# -----------------------------

lst_kelvin = (
    image
    .select("ST_B10")
    .multiply(0.00341802)
    .add(149.0)
)

lst_celsius = (
    lst_kelvin
    .subtract(273.15)
    .rename("lst_celsius")
)


# -----------------------------
# Calculate NDVI
# -----------------------------

ndvi = (
    image
    .normalizedDifference(
        ["SR_B5", "SR_B4"]
    )
    .rename("ndvi")
)


# -----------------------------
# Create vegetated reference mask
# -----------------------------

vegetated_reference_mask = (
    ndvi.gte(
        REFERENCE_NDVI_THRESHOLD
    )
)


# -----------------------------
# Calculate Tamil Nadu temperature
# -----------------------------

site_mean_temperature = (
    lst_celsius
    .reduceRegion(
        reducer=ee.Reducer.mean(),
        geometry=geometry,
        scale=SCALE,
        maxPixels=1e10
    )
    .get("lst_celsius")
)


# -----------------------------
# Calculate reference temperature
# -----------------------------

reference_mean_temperature = (
    lst_celsius
    .updateMask(
        vegetated_reference_mask
    )
    .reduceRegion(
        reducer=ee.Reducer.mean(),
        geometry=reference_search_geometry,
        scale=SCALE,
        maxPixels=1e10
    )
    .get("lst_celsius")
)


# -----------------------------
# Calculate SUHI intensity
# -----------------------------

suhi_intensity = (
    ee.Number(
        site_mean_temperature
    )
    .subtract(
        ee.Number(
            reference_mean_temperature
        )
    )
)


# -----------------------------
# Get results
# -----------------------------

results = {
    "area_name": "Tamil Nadu",
    "period": {
        "start": START_DATE,
        "end": END_DATE
    },
    "metric": (
        "surface_urban_heat_island_intensity"
    ),
    "site_mean_surface_temperature_celsius": (
        site_mean_temperature.getInfo()
    ),
    "reference_mean_surface_temperature_celsius": (
        reference_mean_temperature.getInfo()
    ),
    "reference_search_buffer_meters": (
        REFERENCE_BUFFER_METERS
    ),
    "reference_ndvi_threshold": (
        REFERENCE_NDVI_THRESHOLD
    ),
    "suhi_intensity_celsius": (
        suhi_intensity.getInfo()
    )
}


# -----------------------------
# Display results
# -----------------------------

print("\nTAMIL NADU SURFACE URBAN HEAT ISLAND RESULTS")
print("-" * 50)

for key, value in results.items():
    print(f"{key}: {value}")


# -----------------------------
# Save summary
# -----------------------------

summary_path = Path(
    "data/processed/uhi_summary.json"
)

with open(
    summary_path,
    "w",
    encoding="utf-8"
) as file:
    json.dump(
        results,
        file,
        indent=4
    )

print(
    f"\nSpatial UHI summary saved to: {summary_path}"
)