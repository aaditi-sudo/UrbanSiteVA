import ee
import json
import requests
from pathlib import Path

from config import EE_PROJECT


# -----------------------------
# Settings
# -----------------------------

START_DATE = "2025-01-01"
END_DATE = "2025-12-31"
CLOUD_THRESHOLD = 20
SCALE = 30


# -----------------------------
# Initialize Earth Engine
# -----------------------------

ee.Initialize(project=EE_PROJECT)


# -----------------------------
# Load Velachery boundary
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
# Load Landsat 8 imagery
# -----------------------------

print("Loading Landsat thermal imagery...")

landsat = (
    ee.ImageCollection("LANDSAT/LC08/C02/T1_L2")
    .filterBounds(geometry)
    .filterDate(START_DATE, END_DATE)
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

image = landsat.median().clip(geometry)


# -----------------------------
# Convert thermal band to Celsius
# -----------------------------
# Landsat Collection 2 Level 2:
# Surface temperature = ST_B10 * 0.00341802 + 149.0 Kelvin

lst_kelvin = image.select(
    "ST_B10"
).multiply(
    0.00341802
).add(
    149.0
)

lst_celsius = lst_kelvin.subtract(
    273.15
).rename(
    "lst_celsius"
)


# -----------------------------
# Calculate mean temperature
# -----------------------------

mean_temperature = lst_celsius.reduceRegion(
    reducer=ee.Reducer.mean(),
    geometry=geometry,
    scale=SCALE,
    maxPixels=1e9
).get(
    "lst_celsius"
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
    "mean_surface_temperature_celsius": (
        mean_temperature.getInfo()
    )
}


# -----------------------------
# Display results
# -----------------------------

print("\nHEAT RESULTS")
print("-" * 35)

for key, value in results.items():
    print(f"{key}: {value}")


# -----------------------------
# Save summary
# -----------------------------

summary_path = Path(
    "data/processed/heat_summary.json"
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


# -----------------------------
# Export spatial heat layer
# -----------------------------

print("\nDownloading heat GeoTIFF...")

download_url = lst_celsius.getDownloadURL({
    "name": "velachery_heat",
    "region": geometry,
    "scale": SCALE,
    "crs": "EPSG:4326",
    "format": "GEO_TIFF"
})

tif_path = Path(
    "data/processed/heat.tif"
)

response = requests.get(
    download_url
)

response.raise_for_status()

with open(
    tif_path,
    "wb"
) as file:
    file.write(
        response.content
    )

print(
    f"Spatial heat layer saved to: {tif_path}"
)