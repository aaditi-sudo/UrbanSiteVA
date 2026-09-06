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
    "data/processed/heat_grid.geojson"
)

START_DATE = "2025-01-01"
END_DATE = "2025-12-31"

CLOUD_THRESHOLD = 20

SCALE = 100


# ============================================================
# INITIALIZE GOOGLE EARTH ENGINE
# ============================================================

print("Initializing Google Earth Engine...")

ee.Initialize(project=EE_PROJECT)


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
# LOAD LANDSAT 8 + LANDSAT 9
# ============================================================

print("Loading Landsat thermal imagery...")

# Use the total grid bounding box to search for imagery
grid_bounds = grid.total_bounds

search_geometry = ee.Geometry.Rectangle([
    float(grid_bounds[0]),
    float(grid_bounds[1]),
    float(grid_bounds[2]),
    float(grid_bounds[3])
])

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

landsat = landsat8.merge(landsat9)

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
    .select("ST_B10")
    .median()
)


# ============================================================
# CONVERT ST_B10 TO CELSIUS
# ============================================================

print(
    "Converting surface temperature to Celsius..."
)

lst_celsius = (
    image
    .multiply(0.00341802)
    .add(149.0)
    .subtract(273.15)
    .rename(
        "surface_temperature_celsius"
    )
)


# ============================================================
# PROCESS EACH GRID CELL
# ============================================================

print(
    "Calculating temperature for grid cells..."
)

temperatures = []

total_cells = len(grid)

for index, row in grid.iterrows():

    if index % 100 == 0:
        print(
            f"Processing cell "
            f"{index + 1}-{min(index + 100, total_cells)} "
            f"of {total_cells}..."
        )

    geometry = ee.Geometry(
        row.geometry.__geo_interface__
    )

    value = (
        lst_celsius
        .reduceRegion(
            reducer=ee.Reducer.mean(),
            geometry=geometry,
            scale=SCALE,
            maxPixels=1e10
        )
        .get(
            "surface_temperature_celsius"
        )
    )

    try:
        temperature = value.getInfo()
    except Exception:
        temperature = None

    temperatures.append(
        temperature
    )


# ============================================================
# ATTACH RESULTS
# ============================================================

print(
    "Combining grid results..."
)

grid[
    "surface_temperature_celsius"
] = temperatures


# ============================================================
# CHECK RESULTS
# ============================================================

valid = (
    grid[
        "surface_temperature_celsius"
    ].notna()
)

valid_count = valid.sum()

missing_count = (
    len(grid) - valid_count
)

print(
    f"\nValid temperature cells: "
    f"{valid_count}"
)

print(
    f"Missing temperature cells: "
    f"{missing_count}"
)


# ============================================================
# SAVE GEOJSON
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
    "TAMIL NADU SPATIAL HEAT RESULTS"
)
print("=" * 50)

print(
    f"Grid cells processed: "
    f"{len(grid)}"
)

if valid_count > 0:

    values = (
        grid[
            "surface_temperature_celsius"
        ]
        .dropna()
    )

    print(
        "Mean surface temperature: "
        f"{values.mean():.2f} °C"
    )

    print(
        "\nTemperature range:"
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
        "ERROR: No valid temperature "
        "values were returned."
    )

print(
    "\nSpatial heat results saved to:"
    f"\n{OUTPUT_PATH}"
)

print("=" * 50)

print(
    "\nTamil Nadu spatial heat "
    "processing completed successfully."
)