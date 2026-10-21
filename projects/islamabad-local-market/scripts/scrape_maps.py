"""Scrape Islamabad businesses from Google Maps via the Apify compass/crawler-google-places actor.

Same approach as projects/quetta-local-market/scripts/scrape_maps.py: calls the web-scraper
engine directly (lead-generator's SOUTH_ASIA filter and phone-blanking would drop every row).
One actor run per category; raw rows saved to data/maps_raw/<slug>.json so a failed category
can be re-run alone.

Usage (unsandboxed):
    python scripts/scrape_maps.py                 # all categories
    python scripts/scrape_maps.py dental-clinics  # one or more slugs
    python scripts/scrape_maps.py --second-pass   # outer societies + deeper core, 3 sectors
"""
import json
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

HERE = Path(__file__).resolve().parent
PROJECT = HERE.parent
REPO = PROJECT.parents[1]
sys.path.insert(0, str(REPO / ".claude/skills/web-scraper/scripts"))

from engines.apify_engine import run_actor  # noqa: E402

ACTOR = "compass/crawler-google-places"
LOCATION = "Islamabad, Pakistan"
OUT = PROJECT / "data" / "maps_raw"

# slug -> (search string, max places)
CATEGORIES = {
    # healthcare
    "hospitals": ("private hospital", 60),
    "clinics": ("medical clinic", 60),
    "dental-clinics": ("dental clinic", 60),
    "aesthetic-clinics": ("skin aesthetic clinic", 60),
    "diagnostic-labs": ("diagnostic laboratory", 40),
    "physio": ("physiotherapy clinic", 40),
    # education
    "private-schools": ("private school", 60),
    "academies": ("academy coaching", 60),
    "study-abroad": ("study abroad consultant", 60),
    "immigration": ("immigration consultant", 40),
    # food and hospitality
    "restaurants": ("restaurant", 80),
    "cafes": ("cafe", 60),
    "hotels": ("hotel", 40),
    "event-venues": ("marquee wedding venue", 40),
    # property
    "real-estate": ("real estate agency", 60),
    "builders": ("builders and developers", 40),
    "interiors": ("interior design company", 40),
    # lifestyle and other services
    "salons": ("beauty salon", 60),
    "gyms": ("gym", 40),
    "car-dealers": ("car showroom", 40),
    "law-firms": ("law firm", 40),
    "travel-agents": ("travel agency", 40),
    # competitors
    "software-houses": ("software house", 40),
    "marketing-agencies": ("digital marketing agency", 40),
}


# Second pass (2026-10-21): the "Islamabad, Pakistan" polygon is only the 78 km2 core, so it
# missed the societies. Healthcare, food and real estate only, run per outer area.
OUTER_AREAS = {
    "dha": "DHA Phase 2, Islamabad, Pakistan",
    "bahria": "Bahria Town, Rawalpindi, Pakistan",
    "gulberg": "Gulberg Greens, Islamabad, Pakistan",
    "b17": "B-17, Islamabad, Pakistan",
}
OUTER_QUERIES = {
    "real-estate": ("real estate agency", 50),
    "property-dealers": ("property dealer", 50),
    "builders": ("builders and developers", 30),
    "hospitals": ("hospital", 30),
    "clinics": ("medical clinic", 30),
    "dental-clinics": ("dental clinic", 25),
    "aesthetic-clinics": ("skin aesthetic clinic", 25),
    "restaurants": ("restaurant", 40),
    "cafes": ("cafe", 25),
}
for _area, _loc in OUTER_AREAS.items():
    for _cat, (_q, _n) in OUTER_QUERIES.items():
        CATEGORIES[f"{_area}--{_cat}"] = (_q, _n, _loc)
# deeper core pass for the chosen sectors
CATEGORIES["core--property-dealers"] = ("property dealer", 80)
CATEGORIES["core--housing-societies"] = ("housing society sales office", 40)
CATEGORIES["core--medical-centers"] = ("medical centre specialist", 60)
FIRST_PASS = [s for s in CATEGORIES if "--" not in s]


def scrape(slug: str) -> int:
    query, limit, *loc = CATEGORIES[slug]
    run_input = {
        "searchStringsArray": [query],
        "locationQuery": loc[0] if loc else LOCATION,
        "maxCrawledPlacesPerSearch": limit,
        "language": "en",
        "skipClosedPlaces": True,
    }
    rows = run_actor(ACTOR, run_input, max_items=limit, timeout_secs=900)
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / f"{slug}.json").write_text(json.dumps(rows, ensure_ascii=False, indent=1), encoding="utf-8")
    return len(rows)


def _run(slug: str) -> str:
    try:
        return f"[ok] {slug}: {scrape(slug)} rows"
    except Exception as exc:  # keep going; report at the end
        return f"[FAIL] {slug}: {type(exc).__name__}: {exc}"


def main() -> None:
    args = sys.argv[1:]
    if args == ["--second-pass"]:
        slugs = [s for s in CATEGORIES if "--" in s]
    else:
        slugs = args or FIRST_PASS
    with ThreadPoolExecutor(max_workers=4) as pool:
        for line in pool.map(_run, slugs):
            print(line, flush=True)


if __name__ == "__main__":
    main()
