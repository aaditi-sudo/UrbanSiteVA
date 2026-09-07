from backend.analysis.score import calculate_score


class SimulatedClimate:
    def __init__(self, uhi_index):
        self.uhi_index = uhi_index


class SimulatedGreenCover:
    def __init__(self, green_percentage):
        self.green_percentage = green_percentage


class SimulatedCarbon:
    def __init__(self, carbon_intensity):
        self.carbon_intensity = carbon_intensity


def simulate_site(
    climate,
    green_cover,
    carbon,
    new_green_percentage
):
    new_green_percentage = float(new_green_percentage)

    # Keep value within valid range
    new_green_percentage = max(
        0,
        min(100, new_green_percentage)
    )

    current_green = float(
        green_cover.green_percentage
    )

    current_uhi = float(
        climate.uhi_index
    )

    # Increasing green cover reduces UHI.
    # Decreasing green cover increases UHI.
    change = new_green_percentage - current_green

    simulated_uhi = current_uhi - (
        change * 0.10
    )

    simulated_uhi = max(
        0,
        simulated_uhi
    )

    simulated_climate = SimulatedClimate(
        simulated_uhi
    )

    simulated_green = SimulatedGreenCover(
        new_green_percentage
    )

    simulated_carbon = SimulatedCarbon(
        carbon.carbon_intensity
    )

    result = calculate_score(
        simulated_climate,
        simulated_green,
        simulated_carbon
    )

    return {
        "predicted_score": result["score"],
        "predicted_rating": result["rating"],
        "predicted_uhi": round(
            simulated_uhi,
            2
        )
    }