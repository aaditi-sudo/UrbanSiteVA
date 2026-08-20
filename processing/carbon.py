import json
from pathlib import Path

from carbon_config import (
    TRANSPORT_FACTORS,
    GRID_EMISSION_FACTOR,
    DIESEL_EMISSION_FACTOR,
    LPG_EMISSION_FACTOR,
    HIGH_IMPACT_CARBON_DENSITY
)


# -----------------------------------
# Sample user input
# -----------------------------------
# Temporary test values.
# Later these will come from the
# frontend/backend API.


site_area_sq_m = 10000


transport_inputs = {
    "two_wheeler": {
        "trips_per_day": 500,
        "distance_km_per_trip": 5
    },

    "petrol_car": {
        "trips_per_day": 200,
        "distance_km_per_trip": 8
    },

    "diesel_bus": {
        "trips_per_day": 20,
        "distance_km_per_trip": 10
    }
}

operating_days_per_year = 300


building_inputs = {
    "annual_electricity_kwh": 250000
}


other_inputs = {
    "diesel_litres_per_year": 5000,
    "lpg_kg_per_year": 1000
}


# -----------------------------------
# Transport emissions
# -----------------------------------

transport_emissions = 0

for vehicle_type, values in transport_inputs.items():

    trips = values["trips_per_day"]
    distance = values["distance_km_per_trip"]

    factor = TRANSPORT_FACTORS[vehicle_type]

    emissions = (
        trips
        * distance
        * operating_days_per_year
        * factor
    )

    transport_emissions += emissions


# -----------------------------------
# Building emissions
# -----------------------------------

annual_electricity = (
    building_inputs["annual_electricity_kwh"]
)

building_emissions = (
    annual_electricity
    * GRID_EMISSION_FACTOR
)


# -----------------------------------
# Other emissions
# -----------------------------------

diesel_emissions = (
    other_inputs["diesel_litres_per_year"]
    * DIESEL_EMISSION_FACTOR
)

lpg_emissions = (
    other_inputs["lpg_kg_per_year"]
    * LPG_EMISSION_FACTOR
)

other_emissions = (
    diesel_emissions
    + lpg_emissions
)


# -----------------------------------
# Total emissions
# -----------------------------------

total_emissions = (
    transport_emissions
    + building_emissions
    + other_emissions
)


# -----------------------------------
# Carbon density
# -----------------------------------

carbon_density = (
    total_emissions
    / site_area_sq_m
)


# -----------------------------------
# Normalize to 0-100
# -----------------------------------

carbon_intensity = min(
    100,
    (
        carbon_density
        / HIGH_IMPACT_CARBON_DENSITY
    )
    * 100
)


# -----------------------------------
# Find largest emission source
# -----------------------------------

emission_components = {
    "Transportation": transport_emissions,
    "Building Energy": building_emissions,
    "Other Sources": other_emissions
}

emission_source = max(
    emission_components,
    key=emission_components.get
)


# -----------------------------------
# Results
# -----------------------------------

results = {
    "carbon_intensity": round(
        carbon_intensity,
        2
    ),

    "emission_source": emission_source,

    "total_annual_emissions_kg_co2e": round(
        total_emissions,
        2
    ),

    "carbon_density_kg_co2e_per_m2_per_year": round(
        carbon_density,
        2
    ),

    "emission_breakdown_kg_co2e_per_year": {
        "transportation": round(
            transport_emissions,
            2
        ),

        "building_energy": round(
            building_emissions,
            2
        ),

        "other_sources": round(
            other_emissions,
            2
        )
    }
}


# -----------------------------------
# Display results
# -----------------------------------

print("\nCARBON RESULTS")
print("-" * 35)

for key, value in results.items():
    print(f"{key}: {value}")


# -----------------------------------
# Save summary
# -----------------------------------

output_path = Path(
    "data/processed/carbon_summary.json"
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