import json
import time
from pathlib import Path

import requests


# -----------------------------
# Settings
# -----------------------------

WORLDPOP_API = "https://api.worldpop.org/v2"
POPULATION_YEAR = 2025
RESOLUTION = "100m"


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

geometry = boundary_geojson["features"][0]["geometry"]


# -----------------------------
# Request population analysis
# -----------------------------

payload = {
    "geojson": geometry,
    "year": POPULATION_YEAR,
    "resolution": RESOLUTION
}

print("Submitting population request to WorldPop...")

response = requests.post(
    f"{WORLDPOP_API}/population",
    json=payload
)

response.raise_for_status()

task_id = response.json()["task_id"]

print(f"Task ID: {task_id}")
print("Calculating population...")


# -----------------------------
# Wait for result
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
        raise RuntimeError(
            result_data.get(
                "error",
                "WorldPop population analysis failed."
            )
        )

    time.sleep(2)


# -----------------------------
# Extract results
# -----------------------------

population_result = result_data["result"]

results = {
    "area_name": "Velachery",
    "data_source": population_result.get("data_source"),
    "data_year": population_result.get("data_year"),
    "resolution": RESOLUTION,
    "total_population": population_result.get(
        "total_population"
    ),
    "area_km2": population_result.get(
        "area_km2"
    ),
    "population_density_per_km2": population_result.get(
        "population_density"
    )
}


# -----------------------------
# Display results
# -----------------------------

print("\nPOPULATION RESULTS")
print("-" * 35)

for key, value in results.items():
    print(f"{key}: {value}")


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