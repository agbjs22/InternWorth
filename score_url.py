from modules.scraper import extract_posting
from scoring import score_posting


def score_live_posting(url: str) -> dict:
    return score_posting({**extract_posting(url), "source_url": url})
