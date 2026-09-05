import json
import time
from pathlib import Path

import requests
from shapely.geometry import shape, mapping, box


# -----------------------------
# Settings
# -----------------------------

WORLDPOP_API = "https://api.worldpop.org/v2"
POPULATION_YEAR = 2025
RESOLUTION = "1km"

# Each grid cell is deliberately kept well below
# WorldPop's 50,000 km² polygon limit.
GRID_SIZE_DEGREES = 2.0


# -----------------------------
# Load Tamil Nadu boundary
# -----------------------------

boundary_path = Path("data/raw/tamil_nadu_boundary.geojson")

with open(boundary_path, "r", encoding="utf-8") as file:
    boundary_geojson = json.load(file)

geometry = shape(boundary_geojson["features"][0]["geometry"])

print("Loaded Tamil Nadu boundary.")


# -----------------------------
# Create smaller grid cells
# -----------------------------

min_x, min_y, max_x, max_y = geometry.bounds

cells = []

x = min_x

while x < max_x:
    y = min_y

    while y < max_y:
        grid_cell = box(
            x,
            y,
            min(x + GRID_SIZE_DEGREES, max_x),
            min(y + GRID_SIZE_DEGREES, max_y)
        )

        clipped_cell = geometry.intersection(grid_cell)

        if not clipped_cell.is_empty:
            cells.append(clipped_cell)

        y += GRID_SIZE_DEGREES

    x += GRID_SIZE_DEGREES

print(f"Created {len(cells)} population regions.")


# -----------------------------
# Submit each region
# -----------------------------

total_population = 0.0
total_area_km2 = 0.0
successful_regions = 0

for index, cell in enumerate(cells, start=1):

    print(
        f"\nProcessing region {index}/{len(cells)}..."
    )

    payload = {
        "geojson": mapping(cell),
        "year": POPULATION_YEAR,
        "resolution": RESOLUTION
    }

    response = requests.post(
        f"{WORLDPOP_API}/population",
        json=payload
    )

    if response.status_code != 200:
        print(
            f"Region {index} failed: "
            f"{response.text}"
        )
        continue

    task_id = response.json()["task_id"]

    print(f"Task ID: {task_id}")

    # -----------------------------
    # Wait for WorldPop result
    # -----------------------------

    while True:

        result_response = requests.get(
            f"{WORLDPOP_API}/tasks/{task_id}"
        )

        result_response.raise_for_status()

        result_data = result_response.json()

        status = result_data["status"]

        print(f"Status: {status}")

        if status == "success":
            break

        if status == "failure":
            print(
                f"Region {index} failed: "
                f"{result_data.get('error', 'Unknown error')}"
            )
            break

        time.sleep(2)

    if status != "success":
        continue

    # -----------------------------
    # Extract region result
    # -----------------------------

    population_result = result_data["result"]

    population = population_result.get(
        "total_population"
    )

    area = population_result.get(
        "area_km2"
    )

    if population is not None:
        total_population += float(population)

    if area is not None:
        total_area_km2 += float(area)

    successful_regions += 1

    print(
        f"Region population: {population}"
    )


# -----------------------------
# Final results
# -----------------------------

population_density = (
    total_population / total_area_km2
    if total_area_km2 > 0
    else None
)

results = {
    "area_name": "Tamil Nadu",
    "data_source": "WorldPop",
    "data_year": POPULATION_YEAR,
    "resolution": RESOLUTION,
    "regions_processed": successful_regions,
    "total_regions": len(cells),
    "total_population": total_population,
    "area_km2": total_area_km2,
    "population_density_per_km2": population_density
}


# -----------------------------
# Display results
# -----------------------------

print("\n" + "=" * 50)
print("TAMIL NADU POPULATION RESULTS")
print("=" * 50)

for key, value in results.items():
    print(f"{key}: {value}")

print("=" * 50)


# -----------------------------
# Save summary
# -----------------------------

output_path = Path(
    "data/processed/population_summary.json"
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