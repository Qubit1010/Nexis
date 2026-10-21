"""Summarise the Islamabad Google Maps scan per category and per sector.

Reads data/maps_raw/*.json, drops government/military/closed rows and anything outside the
twin cities, dedupes by placeId, checks whether listed websites load, scores each business
with the same demand / digital-gap / reachability formula as the Quetta build, and writes:
    data/maps_summary.json   per-category and per-sector stats
    data/prospects.csv       every kept row, scored

Usage (unsandboxed):  python scripts/analyze_maps.py [--no-webcheck]
"""
import csv
import json
import math
import re
import statistics
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import requests

PROJECT = Path(__file__).resolve().parents[1]
RAW = PROJECT / "data" / "maps_raw"
DATA = PROJECT / "data"

SECTOR_OF = {
    "hospitals": "healthcare", "clinics": "healthcare", "dental-clinics": "healthcare",
    "diagnostic-labs": "healthcare", "physio": "healthcare",
    "aesthetic-clinics": "aesthetics",
    "private-schools": "schools", "academies": "schools",
    "study-abroad": "study-abroad", "immigration": "study-abroad",
    "restaurants": "food", "cafes": "food",
    "hotels": "hospitality", "event-venues": "hospitality",
    "real-estate": "real-estate", "builders": "real-estate", "interiors": "interiors",
    "salons": "salons-gyms", "gyms": "salons-gyms",
    "car-dealers": "auto", "law-firms": "law", "travel-agents": "travel",
    "software-houses": "competitor", "marketing-agencies": "competitor",
    "property-dealers": "real-estate", "housing-societies": "real-estate", "medical-centers": "healthcare",
}


def base(slug: str) -> str:
    """Second-pass files are named <area>--<category>; the category decides the sector."""
    return slug.split("--")[-1]


def area(slug: str) -> str:
    return slug.split("--")[0] if "--" in slug else "core"

EXCLUDE_TITLE = re.compile(
    r"\b(pims|polyclinic|federal government|fgpc|cda hospital|nih|cmh|combined military|military|"
    r"govt|government|police|university|board of|directorate|ministry|department|secretariat|"
    r"islamabad model (school|college)|imcb|imcg|imsb|imsg|embassy|high commission)\b", re.I)
EXCLUDE_CATEGORY = re.compile(r"(military|government|university|police|embassy|city hall|consulate)", re.I)
CHAIN = re.compile(
    r"(kfc|mcdonald|pizza hut|subway|optp|hardee|domino|burger king|serena|marriott|pearl continental|"
    r"ramada|movenpick|chughtai|excel lab|essa lab|dr\.? essa|islamabad diagnostic|idc\b|shifa|"
    r"beaconhouse|city school|roots|headstart|froebel|lahore grammar|educators|allied school|"
    r"toni ?& ?guy|nabila|sweet tooth|gloria jeans|tim hortons|starbucks|cheezious|savour)", re.I)
SOCIAL = re.compile(r"(facebook\.com|instagram\.com|fb\.me|linktr\.ee|wa\.me|whatsapp|tiktok\.com)", re.I)
TWIN = re.compile(r"(islamabad|rawalpindi)", re.I)


def load_rows() -> list[dict]:
    rows, seen = [], {}
    for f in sorted(RAW.glob("*.json")):
        for r in json.loads(f.read_text(encoding="utf-8")):
            pid = r.get("placeId") or r.get("url")
            if pid in seen:
                continue
            r["_slug"] = f.stem
            seen[pid] = r
            rows.append(r)
    return rows


def keep(r: dict) -> bool:
    title, cat = r.get("title") or "", r.get("categoryName") or ""
    if not TWIN.search((r.get("city") or "") + " " + (r.get("address") or "")):
        return False
    if r.get("permanentlyClosed") or r.get("temporarilyClosed"):
        return False
    if SECTOR_OF.get(base(r["_slug"])) != "competitor":
        if EXCLUDE_TITLE.search(title) or EXCLUDE_CATEGORY.search(cat):
            return False
    return True


def site_kind(url: str | None) -> str:
    if not url:
        return "none"
    return "social-only" if SOCIAL.search(url) else "own"


def check_site(url: str) -> str:
    try:
        resp = requests.get(url, timeout=10, allow_redirects=True,
                            headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"})
        if resp.status_code >= 400:
            return f"broken ({resp.status_code})"
        return "live (https)" if resp.url.startswith("https") else "live (no https)"
    except requests.RequestException:
        return "down"


def is_mobile(phone: str | None) -> bool:
    digits = re.sub(r"\D", "", phone or "")
    return digits.startswith("923") or digits.startswith("03")


def score(r: dict) -> int:
    reviews = r.get("reviewsCount") or 0
    rating = r.get("totalScore")
    demand = min(40.0, 40 * math.log10(reviews + 1) / math.log10(1001))
    gap = 0.0
    kind, status = r["_site_kind"], r.get("_site_status", "")
    if kind == "none":
        gap += 18
    elif kind == "social-only":
        gap += 12
    elif status.startswith(("broken", "down")):
        gap += 15
    elif status == "live (no https)":
        gap += 5
    if r.get("claimThisBusiness"):
        gap += 8
    if rating is not None and reviews >= 20 and rating < 4.0:
        gap += 6
    if not r.get("openingHours"):
        gap += 4
    if (r.get("imagesCount") or 0) < 10:
        gap += 4
    reach = (12 if r.get("phone") else 0) + (8 if is_mobile(r.get("phone")) else 0)
    total = demand + min(40.0, gap) + reach
    return round(total * (0.5 if CHAIN.search(r.get("title") or "") else 1))


def stats(group: list[dict]) -> dict:
    n = len(group)
    if not n:
        return {"businesses": 0}
    pct = lambda k: round(100 * sum(1 for r in group if k(r)) / n)  # noqa: E731
    reviews = [r.get("reviewsCount") or 0 for r in group]
    ratings = [r["totalScore"] for r in group if r.get("totalScore")]
    return {
        "businesses": n,
        "no_website_pct": pct(lambda r: r["_site_kind"] == "none"),
        "social_only_pct": pct(lambda r: r["_site_kind"] == "social-only"),
        "site_broken_pct": pct(lambda r: r.get("_site_status", "").startswith(("broken", "down"))),
        "no_working_site_pct": pct(lambda r: r["_site_kind"] != "own"
                                   or r.get("_site_status", "").startswith(("broken", "down"))),
        "unclaimed_pct": pct(lambda r: r.get("claimThisBusiness")),
        "mobile_phone_pct": pct(lambda r: is_mobile(r.get("phone"))),
        "median_reviews": statistics.median(reviews),
        "with_100plus_reviews": sum(1 for x in reviews if x >= 100),
        "with_500plus_reviews": sum(1 for x in reviews if x >= 500),
        "median_rating": round(statistics.median(ratings), 1) if ratings else None,
        "rated_below_4_with_20plus": sum(1 for r in group if (r.get("reviewsCount") or 0) >= 20
                                         and r.get("totalScore") and r["totalScore"] < 4.0),
        "chains": sum(1 for r in group if CHAIN.search(r.get("title") or "")),
        "median_score": statistics.median(r["_score"] for r in group),
        "score_70plus": sum(1 for r in group if r["_score"] >= 70),
    }


def main() -> None:
    rows = [r for r in load_rows() if keep(r)]
    for r in rows:
        r["_site_kind"] = site_kind(r.get("website"))
    if "--no-webcheck" not in sys.argv:
        own = [r for r in rows if r["_site_kind"] == "own"]
        with ThreadPoolExecutor(max_workers=16) as pool:
            for r, st in zip(own, pool.map(lambda x: check_site(x["website"]), own)):
                r["_site_status"] = st
    for r in rows:
        r["_score"] = score(r)

    by_cat, by_sector, by_area = {}, {}, {}
    for r in rows:
        by_cat.setdefault(base(r["_slug"]), []).append(r)
        by_sector.setdefault(SECTOR_OF[base(r["_slug"])], []).append(r)
        by_area.setdefault(area(r["_slug"]), []).append(r)
    summary = {
        "categories": {k: stats(v) for k, v in sorted(by_cat.items())},
        "sectors": {k: stats(v) for k, v in sorted(by_sector.items())},
        "areas": {k: stats(v) for k, v in sorted(by_area.items())},
        "total_kept": len(rows),
    }
    (DATA / "maps_summary.json").write_text(json.dumps(summary, indent=1), encoding="utf-8")

    fields = ["sector", "category", "area", "score", "name", "gmaps_category", "rating", "reviews", "phone",
              "website", "website_status", "listing_claimed", "neighborhood", "address", "maps_url"]
    out = DATA / "prospects.csv"
    try:
        out.open("a").close()
    except PermissionError:  # open in Excel/WPS on Windows
        out = DATA / "prospects_latest.csv"
        print(f"prospects.csv is locked (open in a spreadsheet app); writing {out.name} instead")
    with open(out, "w", newline="", encoding="utf-8-sig") as fh:
        w = csv.writer(fh)
        w.writerow(fields)
        for r in sorted(rows, key=lambda x: (SECTOR_OF[base(x["_slug"])], -x["_score"])):
            w.writerow([SECTOR_OF[base(r["_slug"])], base(r["_slug"]), area(r["_slug"]), r["_score"], r.get("title"),
                        r.get("categoryName"), r.get("totalScore"), r.get("reviewsCount"),
                        r.get("phone"), r.get("website"),
                        r.get("_site_status") or r["_site_kind"],
                        "no" if r.get("claimThisBusiness") else "yes", r.get("neighborhood"),
                        r.get("address"), r.get("url")])

    print(f"kept {len(rows)} rows")
    hdr = ("n", "noSite%", "social%", "noWork%", "unclm%", "mob%", "medRev", "100+", "500+",
           "medRat", "<4", "chain", "medScr", "70+")
    keys = ("businesses", "no_website_pct", "social_only_pct", "no_working_site_pct", "unclaimed_pct",
            "mobile_phone_pct", "median_reviews", "with_100plus_reviews", "with_500plus_reviews",
            "median_rating", "rated_below_4_with_20plus", "chains", "median_score", "score_70plus")
    for title, block in (("CATEGORY", summary["categories"]), ("SECTOR", summary["sectors"]), ("AREA", summary["areas"])):
        print(f"\n{title:<20}" + "".join(f"{h:>8}" for h in hdr))
        for k, s in block.items():
            print(f"{k:<20}" + "".join(f"{str(s.get(x)):>8}" for x in keys))


if __name__ == "__main__":
    main()
