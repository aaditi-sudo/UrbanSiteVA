import ee
import geopandas as gpd
from pathlib import Path


from config import EE_PROJECT


# ============================================================
# SETTINGS
# ============================================================

GRID_PATH = Path(
    "data/raw/tamil_nadu_grid.geojson"
)

OUTPUT_PATH = Path(
    "data/processed/humidity_grid.geojson"
)

START_DATE = "2025-01-01"
END_DATE = "2025-12-31"

# ERA5-Land spatial resolution is approximately 9 km
SCALE = 10000

# Number of grid cells processed per GEE request
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

grid = gpd.read_file(GRID_PATH)

print(
    f"Grid cells found: {len(grid)}"
)


# ============================================================
# CREATE SEARCH GEOMETRY
# ============================================================

grid_bounds = grid.total_bounds

search_geometry = ee.Geometry.Rectangle([
    float(grid_bounds[0]),
    float(grid_bounds[1]),
    float(grid_bounds[2]),
    float(grid_bounds[3])
])


# ============================================================
# LOAD ERA5-LAND
# ============================================================

print(
    "Loading ERA5-Land climate data..."
)

era5 = (
    ee.ImageCollection(
        "ECMWF/ERA5_LAND/HOURLY"
    )
    .filterBounds(search_geometry)
    .filterDate(
        START_DATE,
        END_DATE
    )
)

image_count = era5.size().getInfo()

print(
    f"ERA5-Land images available: {image_count}"
)

if image_count == 0:
    raise RuntimeError(
        "No ERA5-Land data found for Tamil Nadu."
    )


# ============================================================
# CALCULATE MEAN AIR TEMPERATURE
# ============================================================

print(
    "Calculating mean air temperature..."
)

mean_temperature_kelvin = (
    era5
    .select("temperature_2m")
    .mean()
)

mean_temperature_celsius = (
    mean_temperature_kelvin
    .subtract(273.15)
    .rename("temperature_celsius")
)


# ============================================================
# CALCULATE MEAN DEW POINT
# ============================================================

print(
    "Calculating mean dew point..."
)

mean_dewpoint_kelvin = (
    era5
    .select("dewpoint_temperature_2m")
    .mean()
)

mean_dewpoint_celsius = (
    mean_dewpoint_kelvin
    .subtract(273.15)
    .rename("dewpoint_celsius")
)


# ============================================================
# CALCULATE RELATIVE HUMIDITY
# ============================================================

print(
    "Calculating relative humidity..."
)

temperature_term = (
    mean_temperature_celsius
    .multiply(17.625)
    .divide(
        mean_temperature_celsius
        .add(243.04)
    )
)

dewpoint_term = (
    mean_dewpoint_celsius
    .multiply(17.625)
    .divide(
        mean_dewpoint_celsius
        .add(243.04)
    )
)

relative_humidity = (
    dewpoint_term
    .subtract(temperature_term)
    .exp()
    .multiply(100)
    .rename(
        "relative_humidity_percent"
    )
)


# ============================================================
# CONVERT GRID TO EARTH ENGINE FEATURES
# ============================================================

print(
    "Converting grid to Earth Engine features..."
)

features = []

for index, row in grid.iterrows():

    geometry = ee.Geometry(
        row.geometry.__geo_interface__
    )

    feature = ee.Feature(
        geometry,
        {
            "grid_id": row["grid_id"]
        }
    )

    features.append(feature)

grid_fc = ee.FeatureCollection(features)


# ============================================================
# PROCESS GRID IN BATCHES
# ============================================================

print(
    "Retrieving grid humidity results from GEE..."
)

all_results = []

total_cells = len(grid)

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

    batch_results = (
        relative_humidity
        .reduceRegions(
            collection=batch,
            reducer=ee.Reducer.mean(),
            scale=SCALE
        )
    )

    batch_info = batch_results.getInfo()

    all_results.extend(
        batch_info["features"]
    )


# ============================================================
# EXTRACT HUMIDITY VALUES
# ============================================================

print(
    "Combining grid results..."
)

humidity_lookup = {}

for feature in all_results:

    properties = feature.get(
        "properties",
        {}
    )

    grid_id = properties.get(
        "grid_id"
    )

    humidity = properties.get(
        "mean"
    )

    humidity_lookup[
        grid_id
    ] = humidity


humidity_values = []

for grid_id in grid["grid_id"]:

    humidity_values.append(
        humidity_lookup.get(
            grid_id
        )
    )


# ============================================================
# ATTACH RESULTS
# ============================================================

grid[
    "relative_humidity_percent"
] = humidity_values


# ============================================================
# CHECK RESULTS
# ============================================================

valid = (
    grid[
        "relative_humidity_percent"
    ].notna()
)

valid_count = int(
    valid.sum()
)

missing_count = (
    len(grid) - valid_count
)

print(
    f"\nValid humidity cells: "
    f"{valid_count}"
)

print(
    f"Missing humidity cells: "
    f"{missing_count}"
)


# ============================================================
# SAVE SPATIAL HUMIDITY
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
    "TAMIL NADU SPATIAL HUMIDITY RESULTS"
)
print("=" * 50)

print(
    f"Grid cells processed: "
    f"{len(grid)}"
)

if valid_count > 0:

    values = (
        grid[
            "relative_humidity_percent"
        ]
        .dropna()
    )

    print(
        f"Mean relative humidity: "
        f"{values.mean():.2f}%"
    )

    print(
        "\nHumidity range:"
    )

    print(
        f"Minimum: "
        f"{values.min():.2f}%"
    )

    print(
        f"Maximum: "
        f"{values.max():.2f}%"
    )

else:

    print(
        "ERROR: No valid humidity "
        "values were returned."
    )

print(
    "\nSpatial humidity results saved to:"
    f"\n{OUTPUT_PATH}"
)

print("=" * 50)

print(
    "\nTamil Nadu spatial humidity "
    "processing completed successfully."
)