import re

VAGUE_PHRASES = ("dynamic environment", "go getter", "go-getter", "rockstar", "wear many hats", "other duties", "fast paced", "self starter")
CONCRETE_SIGNALS = ("python", "java", "javascript", "react", "sql", "figma", "excel", "research", "analysis", "testing", "mentor", "mentorship", "deliverable", "project", "training", "api", "git", "dashboard", "customer")


def score(description: str) -> dict:
    text = (description or "").lower()
    concrete = sorted({term for term in CONCRETE_SIGNALS if re.search(r"\b" + re.escape(term) + r"\b", text)})
    vague = sorted({term for term in VAGUE_PHRASES if term in text})
    if len(text.strip()) < 80:
        return {"sub_score": 25, "note": "The role description is too short to explain work, skills, or outcomes."}
    points = max(10, min(100, 40 + len(concrete) * 8 - len(vague) * 8))
    detail = f"Concrete signals: {', '.join(concrete[:5]) or 'few'}"
    if vague:
        detail += f". Vague language: {', '.join(vague[:3])}"
    return {"sub_score": points, "note": detail + "."}
