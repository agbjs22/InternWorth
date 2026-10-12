def reputation_score(company: str, company_info: str = "") -> dict:
    """Score only signals supplied live with the posting; never invent a company rating."""
    info = (company_info or "").lower()
    company = (company or "").strip()
    transparent = [word for word in ("founded", "employees", "headquartered", "website", "clients", "funded", "about") if word in info]
    if not company:
        return {"sub_score": 35, "note": "No company name was provided, so reputation cannot be verified."}
    if len(info) < 40:
        return {"sub_score": 50, "note": f"{company} is named, but the posting provides little verifiable company context."}
    points = min(85, 52 + len(transparent) * 6)
    return {"sub_score": points, "note": f"Live posting context for {company} includes: {', '.join(transparent) or 'basic company information'}."}


def conversion_score(description: str) -> dict:
    text = (description or "").lower()
    phrases = ("pre-placement offer", "ppo", "full-time offer", "full time offer", "conversion", "convert to full time")
    found = [phrase for phrase in phrases if phrase in text]
    if found:
        return {"sub_score": 95, "note": f"A possible conversion path is stated ({found[0]})."}
    return {"sub_score": 45, "note": "No internship-to-full-time conversion path is stated."}
