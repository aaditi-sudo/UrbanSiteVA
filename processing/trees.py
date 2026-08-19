from pathlib import Path

import geopandas as gpd
import osmnx as ox

# -----------------------------
# Load Velachery boundary
# -----------------------------

boundary_path = Path("data/raw/velachery_boundary.geojson")

boundary = gpd.read_file(boundary_path)

# Extract the Shapely polygon
polygon = boundary.geometry.iloc[0]

# -----------------------------
# Search OpenStreetMap
# -----------------------------

tags = {
    "natural": "tree"
}

print("Searching OpenStreetMap for mapped trees...")

trees = ox.features_from_polygon(
    polygon,
    tags
)

tree_count = len(trees)

print(f"Mapped trees found: {tree_count}")

# -----------------------------
# Save tree locations
# -----------------------------

if tree_count > 0:

    output_path = Path(
        "data/raw/velachery_trees.geojson"
    )

    trees.to_file(
        output_path,
        driver="GeoJSON"
    )

    print(
        f"Tree locations saved to: {output_path}"
    )

else:
    print("No mapped individual trees found.")