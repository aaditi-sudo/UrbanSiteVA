import ee
import geopandas as gpd
from pathlib import Path


# ============================================================
# SETTINGS
# ============================================================

GRID_PATH = Path(
    "data/raw/tamil_nadu_grid.geojson"
)

OUTPUT_PATH = Path(
    "data/processed/ndvi_grid.geojson"
)

START_DATE = "2025-01-01"
END_DATE = "2025-12-31"

CLOUD_THRESHOLD = 20

# NDVI >= 0.30 is considered vegetation
NDVI_VEGETATION_THRESHOLD = 0.30

SCALE = 100

# Stay below GEE's 5,000 element getInfo limit
BATCH_SIZE = 500


# ============================================================
# INITIALIZE GOOGLE EARTH ENGINE
# ============================================================

print("Initializing Google Earth Engine...")

ee.Initialize(project="urbansiteva")


# ============================================================
# LOAD GRID
# ============================================================

print("Loading Tamil Nadu grid...")

if not GRID_PATH.exists():
    raise FileNotFoundError(
        f"Grid not found: {GRID_PATH}"
    )

grid = gpd.read_file(GRID_PATH)

print(
    f"Grid cells found: {len(grid)}"
)


# ============================================================
# CONVERT GRID TO GEE FEATURES
# ============================================================

print(
    "Converting grid to Earth Engine features..."
)

features = []

for _, row in grid.iterrows():

    geometry = ee.Geometry(
        row.geometry.__geo_interface__
    )

    features.append(
        ee.Feature(
            geometry,
            {
                "grid_id": row["grid_id"]
            }
        )
    )

grid_fc = ee.FeatureCollection(features)


# ============================================================
# LOAD SENTINEL-2
# ============================================================

print(
    "Loading Sentinel-2 imagery..."
)

boundary = grid_fc.geometry()

collection = (
    ee.ImageCollection(
        "COPERNICUS/S2_SR_HARMONIZED"
    )
    .filterBounds(boundary)
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
    f"Sentinel-2 images available: "
    f"{image_count}"
)

if image_count == 0:
    raise RuntimeError(
        "No Sentinel-2 imagery found."
    )


# ============================================================
# NDVI
# ============================================================

print(
    "Calculating NDVI composite..."
)

image = (
    collection
    .median()
    .clip(boundary)
)

ndvi = (
    image
    .normalizedDifference(
        ["B8", "B4"]
    )
    .rename("ndvi")
)


# ============================================================
# VEGETATION MASK
# ============================================================

vegetation = (
    ndvi
    .gte(
        NDVI_VEGETATION_THRESHOLD
    )
    .rename("vegetation")
)


# ============================================================
# COMBINE NDVI + VEGETATION
# ============================================================

combined_image = (
    ndvi
    .addBands(vegetation)
)


# ============================================================
# PROCESS GRID IN BATCHES
# ============================================================

print(
    "Retrieving grid results from GEE..."
)

results = []

total_cells = len(features)

for start in range(
    0,
    total_cells,
    BATCH_SIZE
):

    end = min(
        start + BATCH_SIZE,
        total_cells
    )

    print(
        f"Processing cells "
        f"{start + 1}-{end} "
        f"of {total_cells}..."
    )

    batch_fc = ee.FeatureCollection(
        features[start:end]
    )

    batch_results = combined_image.reduceRegions(
        collection=batch_fc,
        reducer=ee.Reducer.mean(),
        scale=SCALE
    )

    batch_info = batch_results.getInfo()

    results.extend(
        batch_info["features"]
    )


# ============================================================
# EXTRACT RESULTS
# ============================================================

print(
    "Combining grid results..."
)

result_lookup = {}

for feature in results:

    properties = feature["properties"]

    grid_id = properties["grid_id"]

    result_lookup[grid_id] = {
        "mean_ndvi":
            properties.get("ndvi"),

        "vegetation_fraction":
            properties.get("vegetation")
    }


# ============================================================
# ATTACH RESULTS TO GRID
# ============================================================

grid["mean_ndvi"] = [
    result_lookup.get(
        grid_id,
        {}
    ).get("mean_ndvi")
    for grid_id in grid["grid_id"]
]


grid["green_percentage"] = [
    (
        result_lookup.get(
            grid_id,
            {}
        ).get("vegetation_fraction")
        * 100
        if result_lookup.get(
            grid_id,
            {}
        ).get("vegetation_fraction") is not None
        else None
    )
    for grid_id in grid["grid_id"]
]


# ============================================================
# SAVE
# ============================================================

OUTPUT_PATH.parent.mkdir(
    parents=True,
    exist_ok=True
)

grid.to_file(
    OUTPUT_PATH,
    driver="GeoJSON"
)


# ============================================================
# DISPLAY RESULTS
# ============================================================

print("\n")
print("=" * 50)
print(
    "TAMIL NADU SPATIAL NDVI RESULTS"
)
print("=" * 50)

print(
    f"Grid cells processed: "
    f"{len(grid)}"
)

print(
    f"Mean NDVI across grid: "
    f"{grid['mean_ndvi'].mean():.4f}"
)

print(
    f"Mean green cover: "
    f"{grid['green_percentage'].mean():.2f}%"
)

print(
    f"\nSpatial NDVI results saved to:"
    f"\n{OUTPUT_PATH}"
)

print("=" * 50)

print(
    "\nTamil Nadu spatial NDVI "
    "processing completed successfully."
)