"""Scrape Quetta businesses from Google Maps via the Apify compass/crawler-google-places actor.

Calls the web-scraper engine directly, bypassing lead-generator's SOUTH_ASIA filter and
phone-blanking (both drop Quetta rows). One actor run per category; raw rows saved per category
to data/maps_raw/<slug>.json so a failed category can be re-run alone.

Usage (unsandboxed, Python312):
    python scripts/scrape_maps.py                 # all categories
    python scripts/scrape_maps.py dental-clinics  # one or more slugs
"""
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
PROJECT = HERE.parent
REPO = PROJECT.parents[1]
sys.path.insert(0, str(REPO / ".claude/skills/web-scraper/scripts"))

from engines.apify_engine import run_actor  # noqa: E402

ACTOR = "compass/crawler-google-places"
LOCATION = "Quetta, Pakistan"
OUT = PROJECT / "data" / "maps_raw"

# slug -> (search string, max places)
CATEGORIES = {
    "hospitals": ("private hospital", 80),
    "clinics": ("medical clinic", 80),
    "dental-clinics": ("dental clinic", 60),
    "diagnostic-labs": ("diagnostic laboratory", 60),
    "private-schools": ("private school", 100),
    "colleges-academies": ("college academy coaching", 80),
    "restaurants": ("restaurant", 100),
    "cafes-fastfood": ("cafe fast food", 80),
    "hotels": ("hotel", 60),
    "real-estate": ("real estate agency", 80),
    "builders-developers": ("builders and developers housing scheme", 60),
    "distributors": ("distributor wholesale", 80),
    "dry-fruits": ("dry fruit shop", 60),
    "car-showrooms": ("car showroom", 60),
    "pharmacies": ("pharmacy", 60),
    "jewellers": ("jewellers", 60),
    "gyms-salons": ("gym fitness salon", 60),
    "marble-minerals": ("marble mining minerals company", 40),
    "carpets": ("carpet shop", 40),
    "logistics": ("goods transport logistics courier", 60),
    "software-houses": ("software house", 60),
    "marketing-agencies": ("digital marketing agency", 40),
    # second pass: simpler queries where the compound ones under-returned
    "academies": ("academy", 80),
    "colleges": ("private college", 60),
    "property-dealers": ("property dealer", 80),
    "marriage-halls": ("marriage hall", 40),
}


def scrape(slug: str) -> int:
    query, limit = CATEGORIES[slug]
    run_input = {
        "searchStringsArray": [query],
        "locationQuery": LOCATION,
        "maxCrawledPlacesPerSearch": limit,
        "language": "en",
        "skipClosedPlaces": True,
    }
    rows = run_actor(ACTOR, run_input, max_items=limit, timeout_secs=900)
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / f"{slug}.json").write_text(json.dumps(rows, ensure_ascii=False, indent=1), encoding="utf-8")
    return len(rows)


def main() -> None:
    slugs = sys.argv[1:] or list(CATEGORIES)
    for slug in slugs:
        try:
            n = scrape(slug)
            print(f"[ok] {slug}: {n} rows", flush=True)
        except Exception as exc:  # keep going; report at the end
            print(f"[FAIL] {slug}: {type(exc).__name__}: {exc}", flush=True)


if __name__ == "__main__":
    main()
