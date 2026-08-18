def generate_recommendations(climate, green_cover, carbon):

    recommendations = []

    # UHI
    if climate.uhi_index > 6:
        recommendations.append(
            "Increase tree plantation to reduce Urban Heat Island effect."
        )

    # Green cover
    if green_cover.green_percentage < 30:
        recommendations.append(
            "Increase green cover to at least 30%."
        )

    # Carbon
    if carbon.carbon_intensity > 80:
        recommendations.append(
            "Reduce transportation-related emissions."
        )

    # If everything is good
    if not recommendations:
        recommendations.append(
            "Current site conditions are environmentally sustainable."
        )

    return recommendations