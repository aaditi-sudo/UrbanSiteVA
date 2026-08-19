import osmnx as ox

place = "Velachery, Chennai, Tamil Nadu, India"

print(f"Searching OpenStreetMap for: {place}")

boundary = ox.geocode_to_gdf(place)

boundary.to_file(
    "data/raw/velachery_boundary.geojson",
    driver="GeoJSON"
)

print("Boundary saved successfully.")
print(boundary)