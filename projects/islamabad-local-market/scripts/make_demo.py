"""Build a personalised Prospect Demo Kit for one Islamabad or Rawalpindi business.

    python scripts/make_demo.py "<Google Maps URL | placeId | name fragment>"
                                [--sector healthcare|food|education|real-estate]
                                [--refresh-reviews] [--no-pdf] [--days 14] [--reset]

Same pipeline as projects/quetta-local-market/scripts/make_demo.py, whose helpers it imports
(review stats, LLM chain, health score, Supabase upsert), with three differences:
1. Places come from this project's data/maps_raw (core files plus "<area>--<category>" files).
2. The demo carries its city (Islamabad or Rawalpindi, from the place) and market "islamabad", so the
   app shows Islamabad prices, city copy and the city in the assistant prompt.
3. Property businesses map to the real-estate sector (agencies, developers, builders, property
   managers), which gets the buyer portal, agent pipeline and manager view.
Demo records are written to data/demos/ here (gitignored with the rest of data/).
Run unsandboxed (Apify + Supabase + LLM keys from the repo .env).
"""
import argparse
import importlib.util
import json
import re
import secrets
import subprocess
import sys
import urllib.request
from datetime import datetime, timedelta, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
PROJECT = HERE.parent
REPO = PROJECT.parents[1]
DEMO_APP = REPO / "projects" / "nexuspoint-demo"
DATA = PROJECT / "data"

# Reuse the Quetta script's helpers. It is loaded by path because this file has the same name.
_spec = importlib.util.spec_from_file_location("quetta_make_demo", REPO / "projects/quetta-local-market/scripts/make_demo.py")
Q = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(Q)
Q.DATA = DATA  # reviews cache under this project's data/reviews
sys.path.insert(0, str(HERE))  # this folder first, so `import render` is the Islamabad renderer

SUPPORTED = ("healthcare", "food", "education", "real-estate")
# Scan file (category part of the stem) -> app sector.
SECTOR_OF_FILE = {
    "hospitals": "healthcare", "clinics": "healthcare", "dental-clinics": "healthcare", "diagnostic-labs": "healthcare",
    "physio": "healthcare", "aesthetic-clinics": "healthcare", "medical-centers": "healthcare",
    "restaurants": "food", "cafes": "food",
    "private-schools": "education", "academies": "education",
    "real-estate": "real-estate", "builders": "real-estate", "property-dealers": "real-estate", "housing-societies": "real-estate",
}
# Google categories that are property businesses wherever they were scanned.
REAL_ESTATE_CATEGORY = re.compile(r"real estate|property (management|investment|dealer)|builder|developer|housing (society|development)|construction company", re.I)


def sector_for(place: dict, file_stem: str) -> str:
    if REAL_ESTATE_CATEGORY.search(place.get("categoryName") or ""):
        return "real-estate"
    return SECTOR_OF_FILE.get(file_stem.split("--")[-1], "other")


def city_for(place: dict) -> str:
    """Islamabad or Rawalpindi from the place itself; Maps city values in this scan are often noisy."""
    for value in (place.get("city") or "", place.get("address") or ""):
        if re.search(r"rawalpindi", value, re.I):
            return "Rawalpindi"
        if re.search(r"islamabad", value, re.I):
            return "Islamabad"
    return "Islamabad"


def find_place(query: str) -> tuple[dict, str]:
    m = re.search(r"query_place_id=([A-Za-z0-9_-]+)", query) or re.fullmatch(r"(ChIJ[A-Za-z0-9_-]{20,})", query.strip())
    pid = m.group(1) if m else None
    hits, seen = [], set()
    for f in sorted((DATA / "maps_raw").glob("*.json")):
        for r in json.loads(f.read_text(encoding="utf-8")):
            if r.get("placeId") in seen:
                continue
            if (pid and r.get("placeId") == pid) or (not pid and query.lower() in (r.get("title") or "").lower()):
                seen.add(r.get("placeId"))
                hits.append((r, sector_for(r, f.stem)))
    if not hits:
        sys.exit(f"No place matches {query!r} in data/maps_raw. Scrape it first or pass the placeId.")
    if not pid and len(hits) > 1:
        for r, s in hits[:10]:
            print(f"  {r['title']} | {r.get('categoryName')} | {r.get('reviewsCount')} reviews | {r['placeId']} | {s}")
        sys.exit("Several matches; pass the placeId.")
    return hits[0]


def xray(place: dict, reviews: list[dict], city: str) -> dict:
    """The Quetta review X-ray with the city swapped into the prompt."""
    stats = Q.review_stats(reviews)
    texts = [(i + 1, r) for i, r in enumerate(reviews) if (r.get("text") or "").strip()]
    if len(texts) < 5:
        return {"stats": stats, "complaints": [], "praise": [], "fixes": [], "faq": [],
                "summary_en": "Not enough written reviews to analyse yet.",
                "summary_ur": "تجزیے کے لیے ابھی کافی تحریری ریویوز نہیں ہیں۔", "source": "none"}
    system = Q.XRAY_SYSTEM.replace("Quetta, Pakistan", f"{city}, Pakistan").replace(
        "teaching changes", "teaching or construction changes")
    lines = [f"[{n}] {(r.get('publishedAtDate') or '')[:7]} {r.get('stars')}★ {r['text'].strip()[:600]}" for n, r in texts]
    out = Q.call_llm_json(system, f"Business: {place['title']} ({place.get('categoryName')}), {city}.\nReviews:\n" + "\n".join(lines))
    corpus = {n: Q.norm(r["text"]) for n, r in texts}
    for group in ("complaints", "praise"):
        cleaned = []
        for t in out.get(group, []):
            ids = sorted({i for i in t.get("ids", []) if i in corpus})
            quotes = [q.strip() for q in t.get("quotes", []) if len(Q.norm(q).split()) >= 5
                      and any(re.search(r"(^| )" + re.escape(Q.norm(q)) + r"( |$)", corpus[i]) for i in ids or corpus)]
            if ids:
                cleaned.append({"theme_en": t.get("theme_en"), "theme_ur": t.get("theme_ur"), "count": len(ids), "quotes": quotes[:2]})
        out[group] = sorted(cleaned, key=lambda x: -x["count"])[:4]
    out["stats"], out["source"] = stats, "claude"
    return out


def build_demo(place: dict, sector: str, days: int, city: str) -> dict:
    sectors = json.loads((DEMO_APP / "src" / "data" / "sectors.json").read_text(encoding="utf-8"))
    S = sectors[sector]
    index_path = DATA / "demos" / "index.json"
    index = json.loads(index_path.read_text(encoding="utf-8")) if index_path.exists() else {}
    prev = index.get(place["placeId"])
    slug = prev["slug"] if prev else f"{Q.slugify(place['title'])}-{secrets.token_hex(2)}"
    token = prev["token"] if prev else secrets.token_urlsafe(12)
    code = prev["code"] if prev else "".join(secrets.choice("ABCDEFGHJKMNPQRSTUVWXYZ23456789") for _ in range(5))
    hours = Q.fmt_hours(place)
    facts = {
        "name": place["title"], "category": place.get("categoryName"), "address": place.get("address"),
        "neighborhood": place.get("neighborhood"), "city": city, "hours": hours, "extras": Q.extras(place),
        "rating": place.get("totalScore"), "reviews": place.get("reviewsCount"),
        "maps_url": f"https://www.google.com/maps/search/?api=1&query_place_id={place['placeId']}&query={urllib.request.quote(place['title'])}",
        "location": place.get("location"),
    }
    hours_line = "; ".join(f"{h['day']}: {h['hours']}" for h in hours) or "Not listed on Google"
    about = (f"{place['title']} is a {place.get('categoryName') or S['noun']['en']} at {place.get('address')}. "
             f"Opening hours: {hours_line}. " + (f"Also listed on Google: {', '.join(facts['extras'])}. " if facts["extras"] else "")
             + S["about_default"].replace("{city}", city))
    cat = f"{place.get('categoryName') or ''} {place['title']}".lower()
    services = next((c["services"] for c in S.get("services_by_category", []) if re.search(c["match"], cat)), S["services_sample"])
    profile = {"city": city, "market": "islamabad", "facts": facts, "about": about, "sector": sector, "services_sample": services,
               "questions": S["questions"], "warm_when": S["warm_when"], "unqualified_when": S["unqualified_when"],
               "action": S["action"], "demo_hint": S["demo_hint"],
               "fallback_reply": {"en": f"Thanks for messaging {place['title']}! A team member will reply shortly.",
                                  "ur": f"{place['title']} کو میسج کرنے کا شکریہ! ہمارا عملہ جلد جواب دے گا۔"}}
    index[place["placeId"]] = {"slug": slug, "token": token, "code": code}
    index_path.parent.mkdir(exist_ok=True)
    index_path.write_text(json.dumps(index, indent=1), encoding="utf-8")
    return {"slug": slug, "token": token, "code": code, "sector": sector, "name": place["title"], "profile": profile,
            "site": {"posts": {k: [p.replace("{name}", place["title"]) for p in v] for k, v in S["posts"].items()}},
            "roi": S["roi"], "expires_at": (datetime.now(timezone.utc) + timedelta(days=days)).isoformat()}


def render_pdf(demo: dict, hub: str, chat: str) -> None:
    """Health Check PDFs through this project's render.py (same API as the Quetta renderer)."""
    import asyncio
    sys.modules.pop("render", None)
    try:
        import render
    except ImportError as e:
        print(f"PDF skipped: Islamabad render.py not importable ({e}). Re-run with --no-pdf to silence.", file=sys.stderr)
        return
    ctx = render.load_context()
    ctx.update({"demo": demo, "qr_hub": render.qr_svg(hub), "qr_chat": render.qr_svg(chat), "hub_url": hub,
                "prepared": datetime.now(timezone.utc).strftime("%Y-%m-%d")})
    jobs = [("healthcheck.html.j2", f"Health-Check-{demo['slug']}-{lang}", render.A4, {"lang": lang}) for lang in ("en", "ur")]
    asyncio.run(render.render(jobs, ctx))


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("query")
    ap.add_argument("--sector", choices=SUPPORTED)
    ap.add_argument("--refresh-reviews", action="store_true")
    ap.add_argument("--no-pdf", action="store_true")
    ap.add_argument("--days", type=int, default=14)
    ap.add_argument("--reset", action="store_true", help="clear earlier conversations and workspace activity for this demo")
    a = ap.parse_args()

    place, sector = find_place(a.query)
    sector = a.sector or sector
    if sector not in SUPPORTED:
        sys.exit(f"{place['title']} is in sector '{sector}'. Pass --sector {'|'.join(SUPPORTED)}.")
    city = city_for(place)
    print(f"place: {place['title']} ({sector}, {city}) {place['placeId']}")
    reviews = Q.fetch_reviews(place, a.refresh_reviews)
    print(f"reviews: {len(reviews)} fetched")
    demo = build_demo(place, sector, a.days, city)
    demo["xray"] = xray(place, reviews, city)
    demo["health"] = Q.health(place, demo["xray"]["stats"])
    x = demo["xray"]
    print(f"x-ray: {len(x['complaints'])} complaint themes, {len(x['praise'])} praise themes, "
          f"owner replies {x['stats']['owner_reply_pct']}%, health {demo['health']['score']}/100")
    Q.upsert(demo)
    if a.reset:
        subprocess.run([sys.executable, str(DEMO_APP / "scripts" / "reset_demo.py"), demo["slug"]], check=False)
    (DATA / "demos" / f"{demo['slug']}.json").write_text(json.dumps(demo, ensure_ascii=False, indent=1), encoding="utf-8")
    base = Q.ENV.get("DEMO_BASE_URL", "https://nexuspoint-demo.vercel.app")
    hub = f"{base}/d/{demo['slug']}?t={demo['token']}"
    wa = Q.ENV.get("DEMO_WHATSAPP_NUMBER")
    chat = f"https://wa.me/{wa}?text={urllib.request.quote('DEMO-' + demo['code'] + ' Assalam o alaikum')}" if wa else f"{hub}&chat=1"
    print(f"hub:  {hub}\nchat: {chat}\ncode: {demo['code']}")
    if not a.no_pdf:
        render_pdf(demo, hub, chat)


if __name__ == "__main__":
    main()
