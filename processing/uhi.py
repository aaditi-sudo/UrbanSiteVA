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

# Distance around the study area in which
# we search for a reference area
REFERENCE_BUFFER_METERS = 5000

# Pixels with NDVI >= 0.30 are considered
# vegetated reference pixels
REFERENCE_NDVI_THRESHOLD = 0.30


# -----------------------------
# Initialize Earth Engine
# -----------------------------

ee.Initialize(project=EE_PROJECT)


# -----------------------------
# Load study-area boundary
# -----------------------------

boundary_path = Path(
    "data/raw/velachery_boundary.geojson"
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

# Create a 5 km surrounding area
buffered_geometry = geometry.buffer(
    REFERENCE_BUFFER_METERS
)

# Remove the study area itself
reference_search_geometry = (
    buffered_geometry.difference(
        geometry,
        1
    )
)


# -----------------------------
# Load Landsat 8 imagery
# -----------------------------

print("Loading Landsat imagery...")

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
# Landsat Collection 2 Level 2:
# Surface temperature =
# ST_B10 * 0.00341802 + 149.0 Kelvin

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
# Landsat 8:
# SR_B5 = Near Infrared
# SR_B4 = Red

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
# Calculate study-area temperature
# -----------------------------

site_mean_temperature = (
    lst_celsius
    .reduceRegion(
        reducer=ee.Reducer.mean(),
        geometry=geometry,
        scale=SCALE,
        maxPixels=1e9
    )
    .get("lst_celsius")
)


# -----------------------------
# Calculate reference temperature
# -----------------------------
# Only vegetated pixels in the surrounding
# reference search zone are used

reference_mean_temperature = (
    lst_celsius
    .updateMask(
        vegetated_reference_mask
    )
    .reduceRegion(
        reducer=ee.Reducer.mean(),
        geometry=reference_search_geometry,
        scale=SCALE,
        maxPixels=1e9
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
    "area_name": "Velachery",
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

print("\nSURFACE URBAN HEAT ISLAND RESULTS")
print("-" * 40)

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
    f"\nResults saved to: {summary_path}"
)