"""Turn raw Google Maps rows into a scored, sector-organised Quetta prospect database.

Reads data/maps_raw/*.json, filters public/military/chain noise, dedupes by placeId, checks
whether listed websites actually load, scores every business on visible demand, digital gap and
reachability, writes a plain-language "top opportunity" line, and saves:
    data/prospects.csv             every kept row
    deliverables/Quetta-Prospects.xlsx   one sheet per sector, ranked, plus a summary
    data/prospects_summary.json    per-sector stats used by the report

Usage (unsandboxed, Python312):  python scripts/build_prospects.py [--no-webcheck]
"""
import csv
import json
import math
import re
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import requests
from openpyxl import Workbook
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.utils import get_column_letter

PROJECT = Path(__file__).resolve().parents[1]
RAW = PROJECT / "data" / "maps_raw"
DATA = PROJECT / "data"
OUT = PROJECT / "deliverables"

# category slug -> sector key
SECTOR_OF = {
    "hospitals": "healthcare", "clinics": "healthcare", "dental-clinics": "healthcare",
    "diagnostic-labs": "healthcare",
    "restaurants": "food", "cafes-fastfood": "food",
    "real-estate": "real-estate", "builders-developers": "real-estate", "property-dealers": "real-estate",
    "marriage-halls": "hospitality",
    "private-schools": "education", "colleges-academies": "education", "academies": "education",
    "colleges": "education",
    "hotels": "hospitality",
    "distributors": "trade", "dry-fruits": "trade", "marble-minerals": "trade", "carpets": "trade",
    "logistics": "logistics",
    "car-showrooms": "auto",
    "pharmacies": "retail", "jewellers": "retail",
    "gyms-salons": "lifestyle",
    "software-houses": "competitor", "marketing-agencies": "competitor",
}

SECTORS = {  # display order = beachheads first
    "healthcare": ("Healthcare", "WhatsApp booking + reminder agent, review engine, billing/POS compliance"),
    "food": ("Restaurants & cafes", "BRA-linked POS setup, WhatsApp ordering agent, menu site + Google profile"),
    "education": ("Schools & academies", "Fee reminders, parent WhatsApp updates, admissions funnel"),
    "real-estate": ("Real estate", "Lead-capture site, 60-second WhatsApp responder, follow-up CRM"),
    "hospitality": ("Hotels & event venues", "Direct-booking site, WhatsApp enquiry agent, review engine"),
    "trade": ("Distributors & traders", "Orders on WhatsApp, receivables reminders, e-invoicing"),
    "logistics": ("Transport & logistics", "Dispatch board, WhatsApp status updates, invoicing"),
    "auto": ("Car showrooms", "Inventory website, lead responder, follow-up"),
    "lifestyle": ("Gyms & salons", "Bookings, membership reminders, BRA POS"),
    "retail": ("Retail, pharmacies, jewellers", "POS + inventory, WhatsApp catalogue"),
    "competitor": ("Competitors (software houses, agencies)", "Not a prospect: competitor map"),
}

EXCLUDE_TITLE = re.compile(
    r"\b(civil hospital|cmh|combined military|fc hospital|military|govt|government|police|"
    r"university|board of|directorate|department|secretariat|cantonment board|pphi|"
    r"bolan medical complex|sandeman|provincial)\b", re.I)
EXCLUDE_CATEGORY = re.compile(r"(military|government|university|police|embassy|city hall)", re.I)
CHAIN = re.compile(
    r"(kfc|mcdonald|pizza hut|subway|optp|hardee|domino|serena|pc hotel|pearl continental|"
    r"hbl|ubl|meezan|jazz|telenor|zong|ufone|chughtai|excel lab|essa lab|dr\.? essa|shaheen chemist|"
    r"beaconhouse|city school|allied school|dar-e-arqam|educators|roots)", re.I)
SOCIAL = re.compile(r"(facebook\.com|instagram\.com|fb\.me|linktr\.ee|wa\.me|whatsapp|tiktok\.com)", re.I)


def load_rows() -> list[dict]:
    rows, seen = [], {}
    for f in sorted(RAW.glob("*.json")):
        slug = f.stem
        for r in json.loads(f.read_text(encoding="utf-8")):
            pid = r.get("placeId") or r.get("url")
            if pid in seen:
                seen[pid]["also_in"].add(slug)
                continue
            r["_slug"], r["also_in"] = slug, set()
            seen[pid] = r
            rows.append(r)
    return rows


def keep(r: dict) -> bool:
    title, cat = r.get("title") or "", r.get("categoryName") or ""
    addr = ((r.get("city") or "") + " " + (r.get("address") or "")).lower()
    if "quetta" not in addr:
        return False
    if r.get("permanentlyClosed") or r.get("temporarilyClosed"):
        return False
    if SECTOR_OF.get(r["_slug"]) != "competitor":
        if EXCLUDE_TITLE.search(title) or EXCLUDE_CATEGORY.search(cat):
            return False
    return True


def site_kind(url: str | None) -> str:
    if not url:
        return "none"
    if SOCIAL.search(url):
        return "social-only"
    return "own"


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


def score(r: dict) -> tuple[int, list[str]]:
    reviews = r.get("reviewsCount") or 0
    rating = r.get("totalScore")
    demand = min(40.0, 40 * math.log10(reviews + 1) / math.log10(1001))

    gap, notes = 0.0, []
    kind = r["_site_kind"]
    status = r.get("_site_status", "")
    if kind == "none":
        gap += 18
        if reviews >= 50:
            notes.append(f"{reviews:,} Google reviews but no website: demand is visible, capture is missing")
        else:
            notes.append("No website")
    elif kind == "social-only":
        gap += 12
        notes.append("Only a Facebook/Instagram page, no site of its own")
    elif status.startswith(("broken", "down")):
        gap += 15
        notes.append(f"Website listed but {status}")
    elif status == "live (no https)":
        gap += 5
        notes.append("Website has no HTTPS (browsers flag it 'Not secure')")
    if r.get("claimThisBusiness"):
        gap += 8
        notes.append("Google listing unclaimed: anyone can suggest edits")
    if rating is not None and reviews >= 20 and rating < 4.0:
        gap += 6
        notes.append(f"Rated {rating} on {reviews:,} reviews: reputation is costing walk-ins")
    if not r.get("openingHours"):
        gap += 4
    if (r.get("imagesCount") or 0) < 10:
        gap += 4
    gap = min(40.0, gap)

    reach = (12 if r.get("phone") else 0) + (8 if is_mobile(r.get("phone")) else 0)
    total = demand + gap + reach
    if CHAIN.search(r.get("title") or ""):
        total *= 0.5
        notes.insert(0, "National chain branch: decisions sit at head office")
    return round(total), notes


def gap_tags(r: dict) -> str:
    tags = []
    kind, status = r["_site_kind"], r.get("_site_status", "")
    if kind == "none":
        tags.append("no website")
    elif kind == "social-only":
        tags.append("Facebook only")
    elif status.startswith(("broken", "down")):
        tags.append("site down")
    elif status == "live (no https)":
        tags.append("site not secure")
    if r.get("claimThisBusiness"):
        tags.append("listing unclaimed")
    rating, reviews = r.get("totalScore"), r.get("reviewsCount") or 0
    if rating is not None and reviews >= 20 and rating < 4.0:
        tags.append(f"{rating}★ rating")
    if not r.get("openingHours"):
        tags.append("no hours")
    return " · ".join(tags) or "listing in good shape"


def main() -> None:
    webcheck = "--no-webcheck" not in sys.argv
    rows = [r for r in load_rows() if keep(r)]
    for r in rows:
        r["_site_kind"] = site_kind(r.get("website"))
    if webcheck:
        own = [r for r in rows if r["_site_kind"] == "own"]
        with ThreadPoolExecutor(max_workers=16) as pool:
            for r, st in zip(own, pool.map(lambda x: check_site(x["website"]), own)):
                r["_site_status"] = st

    out = []
    for r in rows:
        s, notes = score(r)
        sector = SECTOR_OF.get(r["_slug"], "other")
        out.append({
            "sector": sector,
            "sector_name": SECTORS.get(sector, (sector,))[0],
            "score": s,
            "name": r.get("title"),
            "category": r.get("categoryName"),
            "rating": r.get("totalScore"),
            "reviews": r.get("reviewsCount") or 0,
            "phone": r.get("phone") or "",
            "whatsapp_reachable": "yes" if is_mobile(r.get("phone")) else "",
            "website": r.get("website") or "",
            "website_status": r.get("_site_status", "") if r["_site_kind"] == "own" else r["_site_kind"],
            "listing_claimed": "no" if r.get("claimThisBusiness") else "yes",
            "address": r.get("address") or "",
            "maps_url": r.get("url") or "",
            "top_opportunity": "; ".join(notes[:2]),
            "gap_short": gap_tags(r),
            "suggested_bundle": SECTORS.get(sector, ("", ""))[1],
            "source_query": r["_slug"],
        })
    out.sort(key=lambda x: (list(SECTORS).index(x["sector"]) if x["sector"] in SECTORS else 99, -x["score"]))

    DATA.mkdir(exist_ok=True)
    OUT.mkdir(exist_ok=True)
    with open(DATA / "prospects.csv", "w", newline="", encoding="utf-8-sig") as fh:
        w = csv.DictWriter(fh, fieldnames=list(out[0]))
        w.writeheader()
        w.writerows(out)

    summary = {}
    for key, (name, _) in SECTORS.items():
        grp = [x for x in out if x["sector"] == key]
        if not grp:
            continue
        n = len(grp)
        summary[key] = {
            "name": name, "businesses": n,
            "no_own_website_pct": round(100 * sum(1 for x in grp if x["website_status"] in ("none", "social-only")) / n),
            "unclaimed_pct": round(100 * sum(1 for x in grp if x["listing_claimed"] == "no") / n),
            "mobile_phone_pct": round(100 * sum(1 for x in grp if x["whatsapp_reachable"]) / n),
            "median_reviews": sorted(x["reviews"] for x in grp)[n // 2],
            "with_100plus_reviews": sum(1 for x in grp if x["reviews"] >= 100),
            "rated_below_4_with_20plus": sum(1 for x in grp if x["rating"] and x["reviews"] >= 20 and x["rating"] < 4),
        }
    (DATA / "prospects_summary.json").write_text(json.dumps(summary, indent=1), encoding="utf-8")
    write_xlsx(out, summary)
    for k, v in summary.items():
        print(k, v)


HEADERS = {"whatsapp_reachable": "WhatsApp reachable", "gap_short": "Digital gap", "maps_url": "Google Maps link",
           "listing_claimed": "Listing claimed", "top_opportunity": "Top opportunity", "suggested_bundle": "Suggested bundle"}


def write_xlsx(out: list[dict], summary: dict) -> None:
    ink, brand, tint = "02040A", "0369A1", "EAF6FD"
    head_font = Font(name="Urbanist", bold=True, color="FFFFFF", size=10)
    head_fill = PatternFill("solid", fgColor=ink)
    wb = Workbook()
    ws = wb.active
    ws.title = "Summary"
    ws["A1"] = "Quetta prospect database"
    ws["A1"].font = Font(name="Urbanist", bold=True, size=16, color=ink)
    ws["A2"] = ("Google Maps, scraped 2026-09-30. Score = visible demand (reviews, 40) + digital gap (40) "
                "+ reachability (20). National chains halved. Govt and military excluded.")
    ws["A2"].font = Font(name="Urbanist", size=9, color="475569")
    cols = ["Sector", "Businesses", "No own website %", "Unclaimed listing %", "Mobile number %",
            "Median reviews", "100+ reviews", "Rated <4 (20+ reviews)"]
    for c, h in enumerate(cols, 1):
        cell = ws.cell(row=4, column=c, value=h)
        cell.font, cell.fill = head_font, head_fill
    for i, v in enumerate(summary.values(), 5):
        vals = [v["name"], v["businesses"], v["no_own_website_pct"], v["unclaimed_pct"], v["mobile_phone_pct"],
                v["median_reviews"], v["with_100plus_reviews"], v["rated_below_4_with_20plus"]]
        for c, val in enumerate(vals, 1):
            ws.cell(row=i, column=c, value=val).font = Font(name="Urbanist", size=10)
    for c, wdt in enumerate([34, 12, 16, 18, 16, 15, 13, 20], 1):
        ws.column_dimensions[get_column_letter(c)].width = wdt

    fields = ["score", "name", "category", "rating", "reviews", "phone", "whatsapp_reachable", "gap_short",
              "website", "website_status", "listing_claimed", "top_opportunity", "suggested_bundle", "address", "maps_url"]
    widths = [7, 34, 20, 7, 8, 16, 10, 30, 28, 14, 9, 60, 44, 40, 30]
    for key, (name, _) in SECTORS.items():
        grp = [x for x in out if x["sector"] == key]
        if not grp:
            continue
        sh = wb.create_sheet(name[:31].replace("/", "-").replace("&", "and"))
        for c, h in enumerate(fields, 1):
            cell = sh.cell(row=1, column=c, value=HEADERS.get(h, h.replace("_", " ").capitalize()))
            cell.font, cell.fill = head_font, head_fill
            cell.alignment = Alignment(vertical="center", wrap_text=True)
        for i, x in enumerate(grp, 2):
            for c, f in enumerate(fields, 1):
                cell = sh.cell(row=i, column=c, value=x[f])
                cell.font = Font(name="Urbanist", size=10, bold=(f == "name"))
                cell.alignment = Alignment(vertical="top", wrap_text=f in ("top_opportunity", "suggested_bundle"))
                if i <= 16 and key != "competitor":
                    cell.fill = PatternFill("solid", fgColor=tint)
        for c, wdt in enumerate(widths, 1):
            sh.column_dimensions[get_column_letter(c)].width = wdt
        sh.freeze_panes = "C2"
        sh.auto_filter.ref = f"A1:{get_column_letter(len(fields))}{len(grp) + 1}"
    wb.save(OUT / "Quetta-Prospects.xlsx")


if __name__ == "__main__":
    main()
