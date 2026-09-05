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

# NDVI >= 0.30 is considered vegetation
NDVI_VEGETATION_THRESHOLD = 0.30

# Larger study area = larger scale for faster processing
SCALE = 100


# ============================================================
# INITIALIZE GOOGLE EARTH ENGINE
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
# LOAD SENTINEL-2 IMAGERY
# ============================================================

print("Loading Sentinel-2 imagery...")

collection = (
    ee.ImageCollection(
        "COPERNICUS/S2_SR_HARMONIZED"
    )
    .filterBounds(geometry)
    .filterDate(
        START_DATE,
        END_DATE
    )
    .filter(
        ee.Filter.lt(
            "CLOUDY_PIXEL_PERCENTAGE",
            CLOUD_THRESHOLD
        )
    )
)

image_count = collection.size().getInfo()

print(
    f"Sentinel-2 images available: {image_count}"
)

if image_count == 0:
    raise RuntimeError(
        "No Sentinel-2 imagery found for Tamil Nadu "
        "with the current date and cloud filters."
    )


# Use median composite to reduce cloud/noise effects
image = (
    collection
    .median()
    .clip(geometry)
)


# ============================================================
# CALCULATE NDVI
# ============================================================

print("Calculating NDVI...")

ndvi = (
    image
    .normalizedDifference(
        ["B8", "B4"]
    )
    .rename("ndvi")
)


# ============================================================
# MEAN NDVI
# ============================================================

mean_ndvi = ndvi.reduceRegion(
    reducer=ee.Reducer.mean(),
    geometry=geometry,
    scale=SCALE,
    maxPixels=1e10
).get("ndvi")


# ============================================================
# CREATE VEGETATION MASK
# ============================================================

vegetation = (
    ndvi
    .gte(NDVI_VEGETATION_THRESHOLD)
    .rename("vegetation")
)


# ============================================================
# TOTAL STUDY AREA
# ============================================================

print("Calculating Tamil Nadu area...")

total_area = (
    ee.Image.pixelArea()
    .reduceRegion(
        reducer=ee.Reducer.sum(),
        geometry=geometry,
        scale=SCALE,
        maxPixels=1e10
    )
    .getNumber("area")
)


# ============================================================
# VEGETATION AREA
# ============================================================

print("Calculating vegetation area...")

vegetation_area = (
    ee.Image.pixelArea()
    .updateMask(vegetation)
    .reduceRegion(
        reducer=ee.Reducer.sum(),
        geometry=geometry,
        scale=SCALE,
        maxPixels=1e10
    )
    .getNumber("area")
)


# ============================================================
# GREEN COVER PERCENTAGE
# ============================================================

green_percentage = (
    vegetation_area
    .divide(total_area)
    .multiply(100)
)


# ============================================================
# RETRIEVE RESULTS
# ============================================================

print("Retrieving NDVI results...")

results = {
    "area_name": "Tamil Nadu",

    "period": {
        "start": START_DATE,
        "end": END_DATE
    },

    "mean_ndvi": mean_ndvi.getInfo(),

    "ndvi_vegetation_threshold":
        NDVI_VEGETATION_THRESHOLD,

    "total_area_sq_m":
        total_area.getInfo(),

    "vegetation_area_sq_m":
        vegetation_area.getInfo(),

    "green_percentage":
        green_percentage.getInfo()
}


# ============================================================
# DISPLAY RESULTS
# ============================================================

print("\n")
print("=" * 50)
print("TAMIL NADU NDVI AND GREEN COVER RESULTS")
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

output_path = (
    processed_dir /
    "ndvi_summary.json"
)

with open(
    output_path,
    "w",
    encoding="utf-8"
) as file:

    json.dump(
        results,
        file,
        indent=4
    )

print(
    f"\nNDVI summary saved to: {output_path}"
)


# ============================================================
# EXPORT SPATIAL NDVI AS GEOTIFF
# ============================================================

print("\nPreparing spatial NDVI GeoTIFF...")

download_url = ndvi.getDownloadURL({
    "name": "tamil_nadu_ndvi",
    "region": geometry,
    "scale": SCALE,
    "crs": "EPSG:4326",
    "format": "GEO_TIFF"
})

tif_path = (
    processed_dir /
    "ndvi.tif"
)

print("Downloading NDVI GeoTIFF...")

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
    f"Spatial NDVI saved to: {tif_path}"
)

print("\nTamil Nadu NDVI processing completed successfully.")