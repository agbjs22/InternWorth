from aggregator import aggregate
from modules import company_and_conversion, location_fit, pay_extractor, red_flag_detector, role_specificity


def score_posting(posting: dict) -> dict:
    description = posting.get("description", "")
    breakdown = {
        "pay": pay_extractor.score(posting.get("stipend", ""), posting.get("location", "")),
        "role_specificity": role_specificity.score(description),
        "reputation": company_and_conversion.reputation_score(posting.get("company", ""), posting.get("company_info", "")),
        "location_fit": location_fit.score(posting.get("location", ""), description),
        "conversion": company_and_conversion.conversion_score(description),
        "red_flag_absence": red_flag_detector.score(description, posting.get("stipend", "")),
    }
    result = aggregate(breakdown)
    result["posting"] = posting
    result["verdict"] = "Strong opportunity" if result["worth_score"] >= 75 else "Worth considering" if result["worth_score"] >= 55 else "Review carefully"
    return result
