import ee
import json
import requests
from pathlib import Path

from config import EE_PROJECT


# Settings

START_DATE = "2025-01-01"
END_DATE = "2025-12-31"
CLOUD_THRESHOLD = 20
NDVI_VEGETATION_THRESHOLD = 0.30
SCALE = 10


# Initialize Earth Engine

ee.Initialize(project=EE_PROJECT)


# Load Velachery boundary

boundary_path = Path("data/raw/velachery_boundary.geojson")

with open(boundary_path, "r", encoding="utf-8") as file:
    boundary_geojson = json.load(file)

geometry = ee.Geometry(
    boundary_geojson["features"][0]["geometry"]
)

# Load Sentinel-2 imagery

print("Loading Sentinel-2 imagery...")

collection = (
    ee.ImageCollection("COPERNICUS/S2_SR_HARMONIZED")
    .filterBounds(geometry)
    .filterDate(START_DATE, END_DATE)
    .filter(ee.Filter.lt(
        "CLOUDY_PIXEL_PERCENTAGE",
        CLOUD_THRESHOLD
    ))
)

image = collection.median().clip(geometry)


# Calculate NDVI

ndvi = image.normalizedDifference(
    ["B8", "B4"]
).rename("ndvi")

mean_ndvi = ndvi.reduceRegion(
    reducer=ee.Reducer.mean(),
    geometry=geometry,
    scale=SCALE,
    maxPixels=1e9
).get("ndvi")


# Create vegetation mask

vegetation = ndvi.gte(
    NDVI_VEGETATION_THRESHOLD
).rename("vegetation")


# Calculate total area


total_area = ee.Image.pixelArea().reduceRegion(
    reducer=ee.Reducer.sum(),
    geometry=geometry,
    scale=SCALE,
    maxPixels=1e9
).getNumber("area")


# Calculate vegetation area

vegetation_area = (
    ee.Image.pixelArea()
    .updateMask(vegetation)
    .reduceRegion(
        reducer=ee.Reducer.sum(),
        geometry=geometry,
        scale=SCALE,
        maxPixels=1e9
    )
    .getNumber("area")
)


# Calculate green percentage

green_percentage = vegetation_area.divide(
    total_area
).multiply(100)


# Retrieve results

results = {
    "area_name": "Velachery",
    "period": {
        "start": START_DATE,
        "end": END_DATE
    },
    "mean_ndvi": mean_ndvi.getInfo(),
    "ndvi_vegetation_threshold": NDVI_VEGETATION_THRESHOLD,
    "total_area_sq_m": total_area.getInfo(),
    "vegetation_area_sq_m": vegetation_area.getInfo(),
    "green_percentage": green_percentage.getInfo()
}



# Display results

print("\nNDVI AND GREEN COVER RESULTS")
print("-" * 35)

for key, value in results.items():
    print(f"{key}: {value}")


# -----------------------------
# Save summary
# -----------------------------

output_path = Path(
    "data/processed/ndvi_summary.json"
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
    f"\nResults saved to: {output_path}"
)


# Export spatial NDVI as GeoTIFF

print("\nDownloading NDVI GeoTIFF...")

download_url = ndvi.getDownloadURL({
    "name": "velachery_ndvi",
    "region": geometry,
    "scale": SCALE,
    "crs": "EPSG:4326",
    "format": "GEO_TIFF"
})

tif_path = Path("data/processed/ndvi.tif")

response = requests.get(download_url)
response.raise_for_status()

with open(tif_path, "wb") as file:
    file.write(response.content)

print(f"Spatial NDVI saved to: {tif_path}")