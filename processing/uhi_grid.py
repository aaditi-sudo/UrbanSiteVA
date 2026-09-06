import ee
import geopandas as gpd
import json
from pathlib import Path


from config import EE_PROJECT


# ============================================================
# SETTINGS
# ============================================================

GRID_PATH = Path(
    "data/raw/tamil_nadu_grid.geojson"
)

OUTPUT_PATH = Path(
    "data/processed/uhi_grid.geojson"
)

START_DATE = "2025-01-01"
END_DATE = "2025-12-31"

CLOUD_THRESHOLD = 20

# Landsat spatial resolution
SCALE = 30

REFERENCE_NDVI_THRESHOLD = 0.30

# Number of grid cells per GEE request
BATCH_SIZE = 500


# ============================================================
# INITIALIZE EARTH ENGINE
# ============================================================

print("Initializing Google Earth Engine...")

ee.Initialize(project=EE_PROJECT)


# ============================================================
# LOAD TAMIL NADU GRID
# ============================================================

print("Loading Tamil Nadu grid...")

if not GRID_PATH.exists():
    raise FileNotFoundError(
        f"Grid not found: {GRID_PATH}"
    )

grid = gpd.read_file(
    GRID_PATH
)

print(
    f"Grid cells found: {len(grid)}"
)


# ============================================================
# CREATE TAMIL NADU SEARCH GEOMETRY
# ============================================================

print(
    "Creating Tamil Nadu search geometry..."
)

bounds = grid.total_bounds

search_geometry = ee.Geometry.Rectangle([
    float(bounds[0]),
    float(bounds[1]),
    float(bounds[2]),
    float(bounds[3])
])


# ============================================================
# LOAD LANDSAT 8
# ============================================================

print(
    "Loading Landsat 8 thermal imagery..."
)

landsat8 = (
    ee.ImageCollection(
        "LANDSAT/LC08/C02/T1_L2"
    )
    .filterBounds(search_geometry)
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
    .filter(
        ee.Filter.eq(
            "PROCESSING_LEVEL",
            "L2SP"
        )
    )
)


# ============================================================
# LOAD LANDSAT 9
# ============================================================

print(
    "Loading Landsat 9 thermal imagery..."
)

landsat9 = (
    ee.ImageCollection(
        "LANDSAT/LC09/C02/T1_L2"
    )
    .filterBounds(search_geometry)
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
    .filter(
        ee.Filter.eq(
            "PROCESSING_LEVEL",
            "L2SP"
        )
    )
)


# ============================================================
# COMBINE COLLECTIONS
# ============================================================

landsat = landsat8.merge(
    landsat9
)

image_count = landsat.size().getInfo()

print(
    f"Landsat images available: {image_count}"
)

if image_count == 0:
    raise RuntimeError(
        "No Landsat thermal imagery found."
    )


# ============================================================
# CREATE MEDIAN COMPOSITE
# ============================================================

print(
    "Creating median thermal composite..."
)

image = (
    landsat
    .median()
    .clip(search_geometry)
)


# ============================================================
# CALCULATE LAND SURFACE TEMPERATURE
# ============================================================

print(
    "Converting surface temperature to Celsius..."
)

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
# CALCULATE NDVI
# ============================================================

print(
    "Calculating NDVI reference mask..."
)

ndvi = (
    image
    .normalizedDifference(
        ["SR_B5", "SR_B4"]
    )
    .rename("ndvi")
)


# ============================================================
# VEGETATED REFERENCE MASK
# ============================================================

vegetated_reference = (
    ndvi
    .gte(
        REFERENCE_NDVI_THRESHOLD
    )
)


# ============================================================
# CALCULATE TAMIL NADU REFERENCE TEMPERATURE
# ============================================================

print(
    "Calculating Tamil Nadu vegetated reference temperature..."
)

reference_temperature = (
    lst_celsius
    .updateMask(
        vegetated_reference
    )
    .reduceRegion(
        reducer=ee.Reducer.mean(),
        geometry=search_geometry,
        scale=SCALE,
        maxPixels=1e10
    )
    .get("lst_celsius")
)


reference_temperature_value = (
    ee.Number(
        reference_temperature
    ).getInfo()
)


print(
    "Reference temperature: "
    f"{reference_temperature_value:.2f} °C"
)


# ============================================================
# CONVERT GRID TO EARTH ENGINE FEATURES
# ============================================================

print(
    "Converting grid to Earth Engine features..."
)

features = []

for _, row in grid.iterrows():

    geometry = ee.Geometry(
        row.geometry.__geo_interface__
    )

    feature = ee.Feature(
        geometry,
        {
            "grid_id": row["grid_id"]
        }
    )

    features.append(
        feature
    )


# ============================================================
# PROCESS GRID IN BATCHES
# ============================================================

print(
    "Calculating UHI for grid cells..."
)

all_results = []

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

    batch = ee.FeatureCollection(
        features[start:end]
    )

    # Calculate mean LST for every grid cell
    batch_results = (
        lst_celsius
        .reduceRegions(
            collection=batch,
            reducer=ee.Reducer.mean(),
            scale=SCALE
        )
    )

    batch_info = (
        batch_results
        .getInfo()
    )

    all_results.extend(
        batch_info["features"]
    )


# ============================================================
# EXTRACT TEMPERATURES
# ============================================================

print(
    "Combining grid results..."
)

temperature_lookup = {}

for feature in all_results:

    properties = feature.get(
        "properties",
        {}
    )

    grid_id = properties.get(
        "grid_id"
    )

    temperature = properties.get(
        "mean"
    )

    temperature_lookup[
        grid_id
    ] = temperature


# ============================================================
# ATTACH TEMPERATURE AND UHI
# ============================================================

cell_temperatures = []
uhi_values = []

for grid_id in grid["grid_id"]:

    temperature = (
        temperature_lookup.get(
            grid_id
        )
    )

    cell_temperatures.append(
        temperature
    )

    if temperature is None:
        uhi_values.append(
            None
        )
    else:
        uhi_values.append(
            temperature
            - reference_temperature_value
        )


grid[
    "surface_temperature_celsius"
] = cell_temperatures

grid[
    "uhi_intensity_celsius"
] = uhi_values


# ============================================================
# CHECK RESULTS
# ============================================================

valid = (
    grid[
        "uhi_intensity_celsius"
    ].notna()
)

valid_count = int(
    valid.sum()
)

missing_count = (
    len(grid)
    - valid_count
)

print(
    f"\nValid UHI cells: "
    f"{valid_count}"
)

print(
    f"Missing UHI cells: "
    f"{missing_count}"
)


# ============================================================
# SAVE SPATIAL UHI
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
    "TAMIL NADU SPATIAL UHI RESULTS"
)
print("=" * 50)

print(
    f"Grid cells processed: "
    f"{len(grid)}"
)

print(
    f"Reference temperature: "
    f"{reference_temperature_value:.2f} °C"
)

if valid_count > 0:

    values = (
        grid[
            "uhi_intensity_celsius"
        ]
        .dropna()
    )

    temperatures = (
        grid[
            "surface_temperature_celsius"
        ]
        .dropna()
    )

    print(
        f"Mean surface temperature: "
        f"{temperatures.mean():.2f} °C"
    )

    print(
        f"Mean UHI intensity: "
        f"{values.mean():.2f} °C"
    )

    print(
        "\nUHI range:"
    )

    print(
        f"Minimum: "
        f"{values.min():.2f} °C"
    )

    print(
        f"Maximum: "
        f"{values.max():.2f} °C"
    )

else:

    print(
        "ERROR: No valid UHI values "
        "were returned."
    )


print(
    "\nSpatial UHI results saved to:"
    f"\n{OUTPUT_PATH}"
)

print("=" * 50)

print(
    "\nTamil Nadu spatial UHI processing "
    "completed successfully."
)