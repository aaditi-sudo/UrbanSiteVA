def calculate_score(climate, green_cover, carbon):

    score = 100

    # -------------------------
    # UHI Score
    # -------------------------
    if climate.uhi_index > 6:
        score -= 20
    elif climate.uhi_index > 3:
        score -= 10

    # -------------------------
    # Green Cover
    # -------------------------
    if green_cover.green_percentage < 15:
        score -= 20
    elif green_cover.green_percentage < 30:
        score -= 10

    # -------------------------
    # Carbon Intensity
    # -------------------------
    if carbon.carbon_intensity > 80:
        score -= 20
    elif carbon.carbon_intensity > 40:
        score -= 10

    # -------------------------
    # Rating
    # -------------------------
    if score >= 80:
        rating = "Excellent"
    elif score >= 60:
        rating = "Good"
    elif score >= 40:
        rating = "Moderate"
    else:
        rating = "Poor"

    return {
        "score": score,
        "rating": rating
    }