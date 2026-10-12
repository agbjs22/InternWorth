def score(location: str, description: str = "") -> dict:
    combined = f"{location} {description}".lower()
    is_remote = "remote" in combined or "work from home" in combined or "wfh" in combined
    contradictions = ("remote" in (location or "").lower() and any(word in (description or "").lower() for word in ("mandatory office", "must relocate", "daily office")))
    if contradictions:
        return {"sub_score": 35, "note": "The location information conflicts with an in-office requirement."}
    if is_remote:
        return {"sub_score": 90, "note": "Remote or work-from-home availability is clearly stated."}
    if location and location.strip():
        return {"sub_score": 70, "note": f"A specific work location is stated: {location.strip()}."}
    return {"sub_score": 40, "note": "No clear work location or remote policy was found."}
