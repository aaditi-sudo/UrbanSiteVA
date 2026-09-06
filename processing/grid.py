#grid.py

import geopandas as gpd
import numpy as np
from pathlib import Path
from shapely.geometry import box


BOUNDARY_PATH = Path("data/raw/tamil_nadu_boundary.geojson")
OUTPUT_PATH = Path("data/raw/tamil_nadu_grid.geojson")

GRID_SIZE_KM = 5


def create_grid():

    # Load Tamil Nadu boundary
    boundary = gpd.read_file(BOUNDARY_PATH)

    # Convert to a projected CRS so distances are measured in metres
    boundary = boundary.to_crs("EPSG:32644")

    min_x, min_y, max_x, max_y = boundary.total_bounds

    grid_size = GRID_SIZE_KM * 1000

    x_values = np.arange(min_x, max_x, grid_size)
    y_values = np.arange(min_y, max_y, grid_size)

    cells = []

    for x in x_values:
        for y in y_values:

            cell = box(
                x,
                y,
                x + grid_size,
                y + grid_size
            )

            cells.append(cell)

    grid = gpd.GeoDataFrame(
        {
            "grid_id": [
                f"TN_{i:05d}"
                for i in range(1, len(cells) + 1)
            ]
        },
        geometry=cells,
        crs=boundary.crs
    )

    # Keep only grid cells that intersect Tamil Nadu
    grid = gpd.overlay(
        grid,
        boundary[["geometry"]],
        how="intersection"
    )

    # Give every resulting cell a unique ID again
    grid["grid_id"] = [
        f"TN_{i:05d}"
        for i in range(1, len(grid) + 1)
    ]

    # Save spatial grid
    OUTPUT_PATH.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    grid.to_crs("EPSG:4326").to_file(
        OUTPUT_PATH,
        driver="GeoJSON"
    )

    print("\nTAMIL NADU GRID")
    print("-" * 35)
    print(f"Grid size: {GRID_SIZE_KM} km x {GRID_SIZE_KM} km")
    print(f"Number of cells: {len(grid)}")
    print(f"Saved to: {OUTPUT_PATH}")


if __name__ == "__main__":
    create_grid()