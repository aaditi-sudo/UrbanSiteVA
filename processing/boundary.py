import osmnx as ox
from pathlib import Path

PLACE = "Tamil Nadu, India"

print(f"Searching OpenStreetMap for: {PLACE}")

boundary = ox.geocode_to_gdf(PLACE)

output_path = Path("data/raw/tamil_nadu_boundary.geojson")
output_path.parent.mkdir(parents=True, exist_ok=True)

boundary.to_file(
    output_path,
    driver="GeoJSON"
)

print(f"Tamil Nadu boundary saved to: {output_path}")
print(boundary)