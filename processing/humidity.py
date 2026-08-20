import ee
import json
from pathlib import Path

from config import EE_PROJECT


# -----------------------------
# Settings
# -----------------------------

START_DATE = "2025-01-01"
END_DATE = "2025-12-31"
SCALE = 10000


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
# Load ERA5-Land climate data
# -----------------------------

print("Loading ERA5-Land climate data...")

era5 = (
    ee.ImageCollection(
        "ECMWF/ERA5_LAND/HOURLY"
    )
    .filterBounds(geometry)
    .filterDate(
        START_DATE,
        END_DATE
    )
)


# -----------------------------
# Calculate mean air temperature
# -----------------------------
# ERA5-Land temperature values are
# in Kelvin, so convert to Celsius

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


# -----------------------------
# Calculate mean dew-point temperature
# -----------------------------

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


# -----------------------------
# Calculate relative humidity
# -----------------------------
#
# RH = 100 × exp(
#   (17.625 × Td) / (243.04 + Td)
#   -
#   (17.625 × T) / (243.04 + T)
# )
#
# T  = air temperature in Celsius
# Td = dew-point temperature in Celsius

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
    .rename("relative_humidity_percent")
)


# -----------------------------
# Calculate study-area mean
# -----------------------------

mean_relative_humidity = (
    relative_humidity
    .reduceRegion(
        reducer=ee.Reducer.mean(),
        geometry=geometry,
        scale=SCALE,
        maxPixels=1e9
    )
    .get("relative_humidity_percent")
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
    "metric": "mean_relative_humidity",
    "mean_relative_humidity_percent": (
        mean_relative_humidity.getInfo()
    )
}


# -----------------------------
# Display results
# -----------------------------

print("\nHUMIDITY RESULTS")
print("-" * 35)

for key, value in results.items():
    print(f"{key}: {value}")


# -----------------------------
# Save summary
# -----------------------------

summary_path = Path(
    "data/processed/humidity_summary.json"
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