import ee
import json
import requests
from pathlib import Path

from config import EE_PROJECT


# ============================================================
# SETTINGS
# ============================================================

START_DATE = "2025-01-01"
END_DATE = "2025-12-31"

CLOUD_THRESHOLD = 20

# 100 m is used because the study area is now Tamil Nadu
SCALE = 100


# ============================================================
# INITIALIZE EARTH ENGINE
# ============================================================

print("Initializing Google Earth Engine...")

ee.Initialize(project=EE_PROJECT)


# ============================================================
# LOAD TAMIL NADU BOUNDARY
# ============================================================

print("Loading Tamil Nadu boundary...")

boundary_path = Path(
    "data/raw/tamil_nadu_boundary.geojson"
)

if not boundary_path.exists():
    raise FileNotFoundError(
        f"Tamil Nadu boundary not found: {boundary_path}"
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


# ============================================================
# LOAD LANDSAT 8 THERMAL IMAGERY
# ============================================================

print("Loading Landsat thermal imagery...")

landsat = (
    ee.ImageCollection(
        "LANDSAT/LC08/C02/T1_L2"
    )
    .filterBounds(geometry)
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

image_count = landsat.size().getInfo()

print(
    f"Landsat images available: {image_count}"
)

if image_count == 0:
    raise RuntimeError(
        "No Landsat thermal imagery found for Tamil Nadu "
        "with the current filters."
    )


# ============================================================
# CREATE MEDIAN COMPOSITE
# ============================================================

print("Creating median thermal composite...")

image = (
    landsat
    .median()
    .clip(geometry)
)


# ============================================================
# CONVERT THERMAL BAND TO CELSIUS
# ============================================================

# Landsat Collection 2 Level 2:
#
# Surface temperature (Kelvin)
# = ST_B10 * 0.00341802 + 149.0
#
# Then convert Kelvin → Celsius.

print("Converting surface temperature to Celsius...")

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


# ============================================================
# CALCULATE MEAN SURFACE TEMPERATURE
# ============================================================

print("Calculating Tamil Nadu mean surface temperature...")

mean_temperature = (
    lst_celsius
    .reduceRegion(
        reducer=ee.Reducer.mean(),
        geometry=geometry,
        scale=SCALE,
        maxPixels=1e10
    )
    .get("lst_celsius")
)


# ============================================================
# GET RESULTS
# ============================================================

temperature_value = mean_temperature.getInfo()

results = {
    "area_name": "Tamil Nadu",

    "period": {
        "start": START_DATE,
        "end": END_DATE
    },

    "mean_surface_temperature_celsius":
        temperature_value
}


# ============================================================
# DISPLAY RESULTS
# ============================================================

print("\n")
print("=" * 50)
print("TAMIL NADU SURFACE TEMPERATURE RESULTS")
print("=" * 50)

for key, value in results.items():
    print(f"{key}: {value}")

print("=" * 50)


# ============================================================
# SAVE SUMMARY
# ============================================================

processed_dir = Path(
    "data/processed"
)

processed_dir.mkdir(
    parents=True,
    exist_ok=True
)

summary_path = (
    processed_dir /
    "heat_summary.json"
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
    f"\nHeat summary saved to: {summary_path}"
)


# ============================================================
# EXPORT SPATIAL HEAT LAYER
# ============================================================

print("\nPreparing spatial temperature GeoTIFF...")

download_url = (
    lst_celsius.getDownloadURL({
        "name": "tamil_nadu_heat",
        "region": geometry,
        "scale": SCALE,
        "crs": "EPSG:4326",
        "format": "GEO_TIFF"
    })
)

tif_path = (
    processed_dir /
    "heat.tif"
)

print("Downloading heat GeoTIFF...")

response = requests.get(
    download_url,
    timeout=300
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

print(
    "\nTamil Nadu heat processing completed successfully."
)