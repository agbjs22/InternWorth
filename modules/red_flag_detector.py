import re

RED_FLAGS = {
    "unpaid": (r"\bunpaid\b", r"\bwithout pay\b", r"\bno stipend\b"),
    "pay-to-work": (r"registration fee", r"security deposit", r"pay.*training", r"training.*fee"),
    "excessive-hours": (r"\b(?:10|11|12)\s*(?:hours|hrs)\b", r"seven days", r"no (?:weekly )?off"),
    "guaranteed-income": (r"guaranteed income", r"earn unlimited", r"commission only"),
    "unclear-work": (r"any task assigned", r"whatever.*required"),
}


def score(description: str, stipend: str = "") -> dict:
    text = f"{description or ''} {stipend or ''}".lower()
    matches = [label for label, patterns in RED_FLAGS.items() if any(re.search(pattern, text) for pattern in patterns)]
    points = max(0, 100 - len(matches) * 24)
    note = "No common exploitation signals were detected." if not matches else "Potential concerns: " + ", ".join(matches) + "."
    return {"sub_score": points, "note": note, "flags": matches}
