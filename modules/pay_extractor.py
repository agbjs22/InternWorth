import re


# Monthly student living-cost proxy in INR. Easy to update as better local data arrives.
COST_OF_LIVING = {
    "bangalore": 26000, "bengaluru": 26000, "mumbai": 30000, "delhi": 25000,
    "new delhi": 25000, "gurgaon": 25000, "gurugram": 25000, "noida": 22000,
    "hyderabad": 21000, "pune": 21000, "chennai": 21000, "kolkata": 18000,
    "ahmedabad": 17000, "jaipur": 16000, "kochi": 17000, "indore": 15000,
    "lucknow": 15000, "bhopal": 14000, "chandigarh": 19000, "remote": 18000,
}


def extract_amount(value: str) -> int | None:
    """Return a best-effort monthly INR stipend from common Indian posting formats."""
    if not value:
        return None
    text = value.lower().replace(",", "")
    if any(token in text for token in ("unpaid", "no stipend", "without pay")):
        return 0
    match = re.search(r"(?:₹|rs\.?|inr)\s*(\d+(?:\.\d+)?)\s*([kl])?", text)
    if not match:
        match = re.search(r"\b(\d+(?:\.\d+)?)\s*([kl])\b", text)
    if not match:
        return None
    amount = float(match.group(1))
    suffix = match.group(2)
    if suffix == "k":
        amount *= 1000
    elif suffix == "l":
        amount *= 100000
    # Daily/weekly ranges need converting to a monthly equivalent.
    if "per day" in text or "/day" in text:
        amount *= 22
    elif "per week" in text or "/week" in text:
        amount *= 4.33
    return round(amount)


def score(stipend: str, location: str) -> dict:
    amount = extract_amount(stipend)
    if amount is None:
        return {"sub_score": 35, "note": "No clear stipend was found; compensation transparency is limited.", "amount": None}
    if amount == 0:
        return {"sub_score": 0, "note": "The posting appears unpaid.", "amount": 0}
    location_text = (location or "").lower()
    city, baseline = next(((city, cost) for city, cost in COST_OF_LIVING.items() if city in location_text), ("India", 18000))
    ratio = amount / baseline
    points = min(100, max(5, round(ratio * 70)))
    return {
        "sub_score": points,
        "note": f"₹{amount:,}/month is {ratio:.1f}× the {city.title()} student-cost benchmark (₹{baseline:,}).",
        "amount": amount,
    }
