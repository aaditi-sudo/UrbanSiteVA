from analysis.score import calculate_score


class SimulatedClimate:
    def __init__(self, uhi_index):
        self.uhi_index = uhi_index


class SimulatedGreenCover:
    def __init__(self, green_percentage):
        self.green_percentage = green_percentage


class SimulatedCarbon:
    def __init__(self, carbon_intensity):
        self.carbon_intensity = carbon_intensity


def simulate_site(climate, green_cover, carbon, new_green_percentage):

    # Estimate that increasing green cover reduces UHI.
    simulated_uhi = climate.uhi_index

    if new_green_percentage > green_cover.green_percentage:
        improvement = new_green_percentage - green_cover.green_percentage
        simulated_uhi = max(
            0,
            climate.uhi_index - (improvement * 0.1)
        )

    simulated_climate = SimulatedClimate(simulated_uhi)
    simulated_green = SimulatedGreenCover(new_green_percentage)
    simulated_carbon = SimulatedCarbon(carbon.carbon_intensity)

    result = calculate_score(
        simulated_climate,
        simulated_green,
        simulated_carbon
    )

    return {
        "predicted_score": result["score"],
        "predicted_rating": result["rating"],
        "predicted_uhi": round(simulated_uhi, 2)
    }