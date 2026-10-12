WEIGHTS = {
    "pay": 0.25,
    "role_specificity": 0.20,
    "reputation": 0.15,
    "location_fit": 0.10,
    "conversion": 0.05,
    "red_flag_absence": 0.25,
}


def aggregate(breakdown: dict) -> dict:
    score = round(sum(breakdown[key]["sub_score"] * weight for key, weight in WEIGHTS.items()))
    return {"worth_score": max(0, min(100, score)), "weights": WEIGHTS, "breakdown": breakdown}
