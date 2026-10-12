"""Polite, on-demand extraction for a single user-submitted posting URL."""
from __future__ import annotations

import json
import time
from typing import Any
from urllib.parse import urlparse
from urllib.robotparser import RobotFileParser

import requests
from bs4 import BeautifulSoup

USER_AGENT = "InternWorth/1.0 (+student-project; single-page analysis)"
TIMEOUT_SECONDS = 12
SELECTOR_PROFILES = {
    "internshala.com": {
        "title": ["h1.internship_name", "h1"],
        "company": ["div.company_name a", ".company_name"],
        "location": ["#location_names", ".location_link"],
        "stipend": ["#stipend", ".stipend"],
        "description": ["#about_internship", ".internship_details"],
        "company_info": [".about_company_text_container", ".company_about", "#about_company"],
    }
}


class ScrapeError(Exception):
    pass


def check_robots_allowed(url: str) -> bool:
    """Fail closed if robots.txt is unreachable or declines our user agent."""
    parsed = urlparse(url)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        return False
    parser = RobotFileParser()
    parser.set_url(f"{parsed.scheme}://{parsed.netloc}/robots.txt")
    try:
        parser.read()
        return parser.can_fetch(USER_AGENT, url)
    except Exception:
        return False


def _text(soup: BeautifulSoup, selectors: list[str]) -> str:
    for selector in selectors:
        element = soup.select_one(selector)
        if element:
            return element.get_text(" ", strip=True)
    return ""


def _meta(soup: BeautifulSoup, *keys: str) -> str:
    for key in keys:
        node = soup.find("meta", attrs={"property": key}) or soup.find("meta", attrs={"name": key})
        if node and node.get("content"):
            return node["content"].strip()
    return ""


def _jsonld(soup: BeautifulSoup) -> dict[str, str]:
    for script in soup.select('script[type="application/ld+json"]'):
        try:
            payload: Any = json.loads(script.string or "{}")
            values = payload if isinstance(payload, list) else [payload]
            for item in values:
                item_type = item.get("@type") if isinstance(item, dict) else None
                is_job_posting = item_type == "JobPosting" or (isinstance(item_type, list) and "JobPosting" in item_type)
                if isinstance(item, dict) and is_job_posting:
                    hiring = item.get("hiringOrganization") or {}
                    location = item.get("jobLocation") or item.get("applicantLocationRequirements") or ""
                    return {
                        "title": str(item.get("title", "")),
                        "company": str(hiring.get("name", "") if isinstance(hiring, dict) else hiring),
                        "location": str(location),
                        "description": BeautifulSoup(str(item.get("description", "")), "html.parser").get_text(" ", strip=True),
                    }
        except (json.JSONDecodeError, TypeError):
            continue
    return {}


def _profile_for(host: str) -> dict[str, list[str]]:
    return next((profile for domain, profile in SELECTOR_PROFILES.items() if host.endswith(domain)), {})


def extract_posting(url: str) -> dict[str, str]:
    if not check_robots_allowed(url):
        raise ScrapeError("This site cannot be fetched because its robots.txt does not allow this request. Please use manual entry.")
    last_error: Exception | None = None
    for attempt in range(3):
        try:
            response = requests.get(url, headers={"User-Agent": USER_AGENT, "Accept-Language": "en-IN,en;q=0.9"}, timeout=TIMEOUT_SECONDS)
            response.raise_for_status()
            break
        except requests.RequestException as error:
            last_error = error
            if attempt < 2:
                time.sleep(0.5 * (2 ** attempt))
    else:
        raise ScrapeError(f"The posting could not be fetched after retries: {last_error}")
    soup = BeautifulSoup(response.text, "html.parser")
    profile = _profile_for(urlparse(url).netloc.lower())
    ld = _jsonld(soup)
    data = {
        "title": _text(soup, profile.get("title", ["h1"])) or _meta(soup, "og:title", "twitter:title") or ld.get("title", ""),
        "company": _text(soup, profile.get("company", [])) or ld.get("company", ""),
        "location": _text(soup, profile.get("location", [])) or ld.get("location", ""),
        "stipend": _text(soup, profile.get("stipend", [])),
        "description": _text(soup, profile.get("description", ["main", "article"])) or ld.get("description", "") or _meta(soup, "description", "og:description"),
        "company_info": _text(soup, profile.get("company_info", [])),
    }
    if len(data["description"]) < 40:
        raise ScrapeError("The page loaded, but did not expose enough posting details. Please use manual entry.")
    return data
