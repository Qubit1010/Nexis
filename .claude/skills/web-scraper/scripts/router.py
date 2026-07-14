"""Router: pick a starting engine for a URL, and know the escalation ladder when one gets blocked.

Two decisions:
1. classify(url) -> a starting tier. Known hard platforms (maps/yelp/zillow/...) start at `apify` with
   a specialized actor; generic targets start cheap (`http`) and climb on BlockedError.
2. LADDER -> the fixed cheapest->most-capable escalation order the orchestrator walks on a block.

Specialized Apify actors per platform (Aleem's policy: Website Content Crawler is the DEFAULT for
generic Apify jobs; a purpose-built actor is used when the target has one).
"""
from __future__ import annotations

from urllib.parse import urlparse

# cheapest -> most capable. scrape.py escalates along this on BlockedError.
LADDER = ["http", "crawl4ai", "firecrawl", "apify", "scrapingant"]

# platform -> specialized Apify actor (used instead of the default website-content-crawler)
PLATFORM_ACTORS = {
    "google_maps": "compass/crawler-google-places",
    "yelp": "yin/yelp-scraper",
    "zillow": "maxcopell/zillow-scraper",
    "instagram": "apify/instagram-scraper",
    "linkedin": "apimaestro/linkedin-profile-scraper",
    "tripadvisor": "maxcopell/tripadvisor",
    "amazon": "junglee/amazon-crawler",
}

_HOST_PLATFORM = {
    "google.com/maps": "google_maps", "maps.google.": "google_maps", "goo.gl/maps": "google_maps",
    "yelp.": "yelp",
    "zillow.": "zillow", "realtor.": "zillow", "redfin.": "zillow", "apartments.": "zillow",
    "instagram.": "instagram",
    "linkedin.": "linkedin",
    "tripadvisor.": "tripadvisor",
    "amazon.": "amazon",
}


def platform_of(url: str) -> str | None:
    u = (url or "").lower()
    host = (urlparse(u).hostname or "") + urlparse(u).path
    for needle, plat in _HOST_PLATFORM.items():
        if needle in u or needle in host:
            return plat
    return None


def classify(url: str) -> dict:
    """Return {engine, actor?, reason}. Known platforms start at apify + a specialized actor."""
    plat = platform_of(url)
    if plat and plat in PLATFORM_ACTORS:
        return {"engine": "apify", "actor": PLATFORM_ACTORS[plat], "platform": plat,
                "reason": f"{plat}: specialized apify actor {PLATFORM_ACTORS[plat]}"}
    return {"engine": "http", "actor": None, "platform": None,
            "reason": "generic target: start cheap (http), escalate on block"}


def next_engine(current: str) -> str | None:
    """The next tier up the ladder after `current`, or None if already at the top."""
    try:
        i = LADDER.index(current)
    except ValueError:
        return None
    return LADDER[i + 1] if i + 1 < len(LADDER) else None


def escalation_from(engine: str) -> list[str]:
    """Every tier from `engine` (inclusive) to the top of the ladder."""
    try:
        return LADDER[LADDER.index(engine):]
    except ValueError:
        return LADDER[:]


if __name__ == "__main__":
    # classify: known platform -> apify + specialized actor
    z = classify("https://www.zillow.com/homes/San-Diego_rb/")
    assert z["engine"] == "apify" and z["actor"] == "maxcopell/zillow-scraper", z
    g = classify("https://www.google.com/maps/search/plumbers+san+diego")
    assert g["actor"] == "compass/crawler-google-places", g
    # classify: generic -> start at http
    assert classify("https://someblog.example.com/post")["engine"] == "http"
    # escalation ladder
    assert next_engine("http") == "crawl4ai", next_engine("http")
    assert next_engine("scrapingant") is None
    assert escalation_from("firecrawl") == ["firecrawl", "apify", "scrapingant"]
    assert platform_of("https://maps.google.com/?q=x") == "google_maps"
    print("router self-check OK")
