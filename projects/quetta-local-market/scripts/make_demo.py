"""Build a personalised Prospect Demo Kit for one Quetta business.

    python scripts/make_demo.py "<Google Maps URL | placeId | name fragment>" [--sector healthcare|food|education]
                                [--refresh-reviews] [--no-pdf] [--days 14]

1. Find the place in data/maps_raw (the 2026-09-30 scan).
2. Fetch the newest 80 Google reviews (Apify compass/Google-Maps-Reviews-Scraper, no reviewer data)
   -> data/reviews/<placeId>.json (cached; gitignored).
3. Review X-ray: an LLM groups complaints and praise into themes. Counts, star mix, owner-reply
   rate and trend are computed here, not by the model, and every quote is checked verbatim against
   the real reviews; unmatched quotes are dropped.
4. Profile: facts only from Maps fields; sector samples (projects/nexuspoint-demo/data/sectors.json)
   are labelled as samples.
5. Upsert to Supabase demo_businesses (service role, PostgREST) and write data/demos/<slug>.json.
6. Render the Digital Health Check PDF with QR codes to the hub and the assistant.

LLM: Anthropic API (Sonnet 5.5) when the key has credit, else the Claude Code CLI (subscription).
Run unsandboxed on Python312.
"""
import argparse
import hashlib
import json
import re
import secrets
import shutil
import statistics
import subprocess
import sys
import tempfile
import unicodedata
import urllib.error
import urllib.request
from datetime import datetime, timedelta, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
PROJECT = HERE.parent
REPO = PROJECT.parents[1]
DEMO_APP = REPO / "projects" / "nexuspoint-demo"
sys.path.insert(0, str(REPO / ".claude/skills/web-scraper/scripts"))
sys.path.insert(0, str(HERE))

from engines.apify_engine import run_actor  # noqa: E402
from build_prospects import SECTOR_OF  # noqa: E402

REVIEWS_ACTOR = "compass/Google-Maps-Reviews-Scraper"
SONNET = "claude-sonnet-5-5"
SUPPORTED = ("healthcare", "food", "education")
DATA = PROJECT / "data"


def load_env() -> dict:
    env = {}
    for line in (REPO / ".env").read_text(encoding="utf-8").splitlines():
        if "=" in line and not line.strip().startswith("#"):
            k, v = line.strip().split("=", 1)
            env[k] = v.strip().strip('"').strip("'")
    return env


ENV = load_env()


# ---------------------------------------------------------------- 1. place
def find_place(query: str) -> tuple[dict, str]:
    pid = None
    m = re.search(r"query_place_id=([A-Za-z0-9_-]+)", query) or re.fullmatch(r"(ChIJ[A-Za-z0-9_-]{20,})", query.strip())
    if m:
        pid = m.group(1)
    hits = []
    for f in sorted((DATA / "maps_raw").glob("*.json")):
        for r in json.loads(f.read_text(encoding="utf-8")):
            if (pid and r.get("placeId") == pid) or (not pid and query.lower() in (r.get("title") or "").lower()):
                hits.append((r, SECTOR_OF.get(f.stem, "other")))
    if not hits:
        sys.exit(f"No place matches {query!r} in data/maps_raw. Scrape it first or pass the placeId.")
    if not pid and len({h[0]["placeId"] for h in hits}) > 1:
        for r, s in hits[:10]:
            print(f"  {r['title']} | {r.get('reviewsCount')} reviews | {r['placeId']} | {s}")
        sys.exit("Several matches; pass the placeId.")
    return hits[0]


# ---------------------------------------------------------------- 2. reviews
def fetch_reviews(place: dict, refresh: bool) -> list[dict]:
    path = DATA / "reviews" / f"{place['placeId']}.json"
    if path.exists() and not refresh:
        return json.loads(path.read_text(encoding="utf-8"))
    rows = run_actor(REVIEWS_ACTOR, {"placeIds": [place["placeId"]], "maxReviews": 80, "reviewsSort": "newest",
                                     "language": "en", "reviewsOrigin": "google", "personalData": False},
                     max_items=80, timeout_secs=600)
    keep = ("text", "textTranslated", "stars", "publishedAtDate", "responseFromOwnerText", "reviewId")
    rows = [{k: r.get(k) for k in keep} for r in rows]
    path.parent.mkdir(exist_ok=True)
    path.write_text(json.dumps(rows, ensure_ascii=False, indent=1), encoding="utf-8")
    return rows


def review_stats(reviews: list[dict]) -> dict:
    stars = [r["stars"] for r in reviews if r.get("stars")]
    with_text = [r for r in reviews if (r.get("text") or "").strip()]
    replied = sum(1 for r in reviews if (r.get("responseFromOwnerText") or "").strip())
    recent = stars[:20]
    return {
        "analysed": len(reviews), "with_text": len(with_text),
        "avg": round(statistics.mean(stars), 2) if stars else None,
        "recent_avg": round(statistics.mean(recent), 2) if recent else None,
        "mix": {str(s): stars.count(s) for s in range(5, 0, -1)},
        "owner_reply_pct": round(100 * replied / len(reviews)) if reviews else 0,
        "newest": (reviews[0].get("publishedAtDate") or "")[:10] if reviews else None,
        "oldest": (reviews[-1].get("publishedAtDate") or "")[:10] if reviews else None,
    }


# ---------------------------------------------------------------- 3. x-ray
XRAY_SYSTEM = """You analyse Google reviews for a local business in Quetta, Pakistan, for the owner.
Return ONLY a JSON object, no prose, with this shape:
{"summary_en": str, "summary_ur": str,
 "complaints": [{"theme_en": str, "theme_ur": str, "ids": [int], "quotes": [str]}],
 "praise":     [{"theme_en": str, "theme_ur": str, "ids": [int], "quotes": [str]}],
 "fixes": [{"en": str, "ur": str}],
 "faq": [{"en": str, "ur": str}]}
Rules:
- Themes: at most 4 complaints and 4 praise, most frequent first. "ids" lists EVERY review number
  (the [n] prefix) that mentions the theme. A review can appear in several themes.
- quotes: 1 or 2 short fragments copied EXACTLY from those reviews (8 to 20 words, keep the original
  wording and language, no names). Never paraphrase inside a quote.
- summary: one plain sentence addressed to the owner in the second person ("your patients", "your
  restaurant"), never written as the business ("we", "our"). No jargon. Urdu fields in natural Urdu script.
- fixes: exactly 3 concrete actions the owner controls at the front desk or in their systems (replying to
  reviews, follow-up messages, booking, waiting times, communication). Weigh complaints by how many reviews
  raise them and how recent they are (each review starts with its month). Never prescribe clinical, cooking
  or teaching changes from one or two reviews; for rare complaints, fix how they are caught and answered.
- faq: up to 5 questions customers clearly ask or would ask (hours, booking, delivery, fees).
- If there are few complaints, return fewer themes. Never invent a theme without review evidence."""


def _post(url: str, headers: dict, body: dict) -> dict:
    req = urllib.request.Request(url, data=json.dumps(body).encode(), headers={"content-type": "application/json", **headers})
    with urllib.request.urlopen(req, timeout=180) as r:
        return json.loads(r.read())


def call_llm_json(system: str, user: str) -> dict:
    """Provider chain: Anthropic direct -> Claude via OpenRouter -> OpenAI -> Claude Code CLI."""
    msgs = [{"role": "system", "content": system}, {"role": "user", "content": user}]
    attempts = []
    if ENV.get("ANTHROPIC_API_KEY"):
        attempts.append(("anthropic", lambda: "".join(b.get("text", "") for b in _post(
            "https://api.anthropic.com/v1/messages",
            {"x-api-key": ENV["ANTHROPIC_API_KEY"], "anthropic-version": "2023-06-01"},
            {"model": SONNET, "max_tokens": 4000, "system": system, "messages": msgs[1:]})["content"])))
    if ENV.get("OPENROUTER_API_KEY"):
        attempts.append(("openrouter", lambda: _post(
            "https://openrouter.ai/api/v1/chat/completions",
            {"Authorization": f"Bearer {ENV['OPENROUTER_API_KEY']}", "X-Title": "NexusPoint demo"},
            {"model": "anthropic/claude-sonnet-5.5", "max_tokens": 4000, "messages": msgs,
             "response_format": {"type": "json_object"}})["choices"][0]["message"]["content"]))
    if ENV.get("OPENAI_API_KEY"):
        attempts.append(("openai", lambda: _post(
            "https://api.openai.com/v1/chat/completions", {"Authorization": f"Bearer {ENV['OPENAI_API_KEY']}"},
            {"model": "gpt-5.4-mini", "max_completion_tokens": 6000, "reasoning_effort": "low",
             "messages": msgs, "response_format": {"type": "json_object"}})["choices"][0]["message"]["content"]))
    attempts.append(("claude-cli", lambda: claude_cli(system, user)))
    for name, fn in attempts:
        try:
            out = parse_json(fn())
            print(f"[x-ray] via {name}", file=sys.stderr)
            return out
        except urllib.error.HTTPError as e:
            print(f"[x-ray] {name} unavailable ({e.code})", file=sys.stderr)
        except Exception as e:  # noqa: BLE001
            print(f"[x-ray] {name} failed ({str(e)[:120]})", file=sys.stderr)
    raise RuntimeError("every LLM provider failed")


def claude_cli(system: str, user: str) -> str:
    """Claude Code CLI as a bare completion (pattern: web-scraper/scripts/extract.py). The review text
    goes through stdin, not argv, because Windows caps command lines at ~32K characters."""
    exe = shutil.which("claude")
    if not exe:
        raise RuntimeError("claude CLI not found and the Anthropic key has no credit")
    cmd = [exe, "-p", "Analyse the reviews provided on stdin as instructed. Return only the JSON object.",
           "--model", "sonnet", "--output-format", "json", "--system-prompt", system,
           "--disallowedTools", "*", "--disable-slash-commands", "--effort", "low"]
    p = subprocess.run(cmd, input=user, capture_output=True, text=True, encoding="utf-8", errors="replace",
                       timeout=300, cwd=tempfile.gettempdir())
    if p.returncode != 0:
        raise RuntimeError(f"claude CLI exited {p.returncode}: {(p.stderr or p.stdout)[:300]}")
    data = json.loads(p.stdout)
    if data.get("is_error"):
        raise RuntimeError(f"claude CLI error: {str(data.get('result'))[:300]}")
    return data.get("result", "")


def parse_json(text: str) -> dict:
    m = re.search(r"\{.*\}", text, re.S)
    if not m:
        raise ValueError(f"no JSON in model output: {text[:200]}")
    return json.loads(m.group(0))


def norm(s: str) -> str:
    s = unicodedata.normalize("NFKC", s or "").lower()
    return re.sub(r"[^\w]+", " ", s).strip()


def xray(place: dict, reviews: list[dict]) -> dict:
    stats = review_stats(reviews)
    texts = [(i + 1, r) for i, r in enumerate(reviews) if (r.get("text") or "").strip()]
    if len(texts) < 5:
        return {"stats": stats, "complaints": [], "praise": [], "fixes": [], "faq": [],
                "summary_en": "Not enough written reviews to analyse yet.",
                "summary_ur": "تجزیے کے لیے ابھی کافی تحریری ریویوز نہیں ہیں۔", "source": "none"}
    lines = [f"[{n}] {(r.get('publishedAtDate') or '')[:7]} {r.get('stars')}★ {r['text'].strip()[:600]}" for n, r in texts]
    user = f"Business: {place['title']} ({place.get('categoryName')}), Quetta.\nReviews:\n" + "\n".join(lines)
    out = call_llm_json(XRAY_SYSTEM, user)
    corpus = {n: norm(r["text"]) for n, r in texts}
    for group in ("complaints", "praise"):
        cleaned = []
        for t in out.get(group, []):
            ids = sorted({i for i in t.get("ids", []) if i in corpus})
            quotes = [q.strip() for q in t.get("quotes", []) if len(norm(q).split()) >= 5
                      and any(re.search(r"(^| )" + re.escape(norm(q)) + r"( |$)", corpus[i]) for i in ids or corpus)]
            if ids:
                cleaned.append({"theme_en": t.get("theme_en"), "theme_ur": t.get("theme_ur"),
                                "count": len(ids), "quotes": quotes[:2]})
        out[group] = sorted(cleaned, key=lambda x: -x["count"])[:4]
    out["stats"] = stats
    out["source"] = "claude"
    return out


# ---------------------------------------------------------------- 4. profile + health
def fmt_hours(place: dict) -> list[dict]:
    fix = lambda v: (v or "").replace(" ", " ").replace(" ", " ")  # noqa: E731
    return [{"day": h.get("day"), "hours": fix(h.get("hours"))} for h in place.get("openingHours") or []]


def extras(place: dict) -> list[str]:
    out = []
    for group in place.get("additionalInfo") or {}:
        if group in ("Service options", "Offerings", "Payments", "Amenities", "Accessibility", "Planning"):
            for item in place["additionalInfo"][group]:
                for k, v in item.items():
                    if v:
                        out.append(k)
    return out[:10]


def health(place: dict, stats: dict) -> dict:
    site = place.get("website") or ""
    social = bool(re.search(r"facebook\.com|instagram\.com", site))
    items = [
        {"key": "website", "ok": bool(site) and not social, "weight": 25,
         "en": "Own website" if site and not social else ("Only a Facebook page" if social else "No website"),
         "ur": "اپنی ویب سائٹ" if site and not social else ("صرف فیس بک پیج" if social else "کوئی ویب سائٹ نہیں")},
        {"key": "claimed", "ok": not place.get("claimThisBusiness"), "weight": 20,
         "en": "Google listing claimed" if not place.get("claimThisBusiness") else "Google listing unclaimed",
         "ur": "گوگل لسٹنگ آپ کے نام" if not place.get("claimThisBusiness") else "گوگل لسٹنگ آپ کے نام نہیں"},
        {"key": "hours", "ok": bool(place.get("openingHours")), "weight": 10,
         "en": "Opening hours listed" if place.get("openingHours") else "No opening hours",
         "ur": "اوقات درج ہیں" if place.get("openingHours") else "اوقات درج نہیں"},
        {"key": "photos", "ok": (place.get("imagesCount") or 0) >= 20, "weight": 10,
         "en": f"{place.get('imagesCount') or 0:,} photos", "ur": f"{place.get('imagesCount') or 0:,} تصاویر"},
        {"key": "rating", "ok": (place.get("totalScore") or 0) >= 4.2, "weight": 15,
         "en": f"Rated {place.get('totalScore')} on {place.get('reviewsCount') or 0:,} reviews",
         "ur": f"{place.get('reviewsCount') or 0:,} ریویوز پر {place.get('totalScore')} ریٹنگ"},
        {"key": "replies", "ok": stats.get("owner_reply_pct", 0) >= 50, "weight": 20,
         "en": f"Owner replied to {stats.get('owner_reply_pct', 0)}% of recent reviews",
         "ur": f"مالک نے حالیہ {stats.get('owner_reply_pct', 0)}% ریویوز کا جواب دیا"},
    ]
    return {"score": sum(i["weight"] for i in items if i["ok"]), "items": items}


def slugify(name: str) -> str:
    s = unicodedata.normalize("NFKD", name).encode("ascii", "ignore").decode().lower()
    return re.sub(r"[^a-z0-9]+", "-", s).strip("-")[:32] or "business"


def build_demo(place: dict, sector: str, days: int) -> dict:
    sectors = json.loads((DEMO_APP / "data" / "sectors.json").read_text(encoding="utf-8"))
    S = sectors[sector]
    index_path = DATA / "demos" / "index.json"
    index = json.loads(index_path.read_text(encoding="utf-8")) if index_path.exists() else {}
    prev = index.get(place["placeId"])
    slug = prev["slug"] if prev else f"{slugify(place['title'])}-{secrets.token_hex(2)}"
    token = prev["token"] if prev else secrets.token_urlsafe(12)
    code = prev["code"] if prev else "".join(secrets.choice("ABCDEFGHJKMNPQRSTUVWXYZ23456789") for _ in range(5))
    hours = fmt_hours(place)
    facts = {
        "name": place["title"], "category": place.get("categoryName"), "address": place.get("address"),
        "neighborhood": place.get("neighborhood"), "city": place.get("city"), "hours": hours, "extras": extras(place),
        "rating": place.get("totalScore"), "reviews": place.get("reviewsCount"),
        "maps_url": f"https://www.google.com/maps/search/?api=1&query_place_id={place['placeId']}&query={urllib.request.quote(place['title'])}",
        "location": place.get("location"),
    }
    hours_line = "; ".join(f"{h['day']}: {h['hours']}" for h in hours) or "Not listed on Google"
    about = (f"{place['title']} is a {place.get('categoryName') or S['noun']['en']} at {place.get('address')}. "
             f"Opening hours: {hours_line}. " + (f"Also listed on Google: {', '.join(facts['extras'])}. " if facts["extras"] else "")
             + S["about_default"])
    # a dentist or a lab must not see a generic clinic menu on their draft site
    cat = f"{place.get('categoryName') or ''} {place['title']}".lower()
    services = next((c["services"] for c in S.get("services_by_category", []) if re.search(c["match"], cat)),
                    S["services_sample"])
    profile = {"facts": facts, "about": about, "sector": sector, "services_sample": services,
               "questions": S["questions"], "warm_when": S["warm_when"], "unqualified_when": S["unqualified_when"],
               "action": S["action"], "demo_hint": S["demo_hint"],
               "fallback_reply": {"en": f"Thanks for messaging {place['title']}! A team member will reply shortly.",
                                  "ur": f"{place['title']} کو میسج کرنے کا شکریہ! ہمارا عملہ جلد جواب دے گا۔"}}
    index[place["placeId"]] = {"slug": slug, "token": token, "code": code}
    index_path.parent.mkdir(exist_ok=True)
    index_path.write_text(json.dumps(index, indent=1), encoding="utf-8")
    return {"slug": slug, "token": token, "code": code, "sector": sector, "name": place["title"], "profile": profile,
            "site": {"posts": {k: [p.replace("{name}", place["title"]) for p in v] for k, v in S["posts"].items()}},
            "roi": S["roi"],
            "expires_at": (datetime.now(timezone.utc) + timedelta(days=days)).isoformat()}


# ---------------------------------------------------------------- 5. store
def upsert(demo: dict) -> None:
    url = ENV["SUPABASE_URL"].rstrip("/") + "/rest/v1/demo_businesses?on_conflict=slug"
    key = ENV["SUPABASE_SERVICE_ROLE_KEY"]
    req = urllib.request.Request(url, data=json.dumps(demo, ensure_ascii=False).encode(), method="POST", headers={
        "apikey": key, "Authorization": f"Bearer {key}", "Content-Type": "application/json",
        "Prefer": "resolution=merge-duplicates,return=minimal"})
    try:
        urllib.request.urlopen(req, timeout=30).read()
    except urllib.error.HTTPError as e:
        sys.exit(f"Supabase upsert failed {e.code}: {e.read().decode()[:300]}")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("query")
    ap.add_argument("--sector", choices=SUPPORTED)
    ap.add_argument("--refresh-reviews", action="store_true")
    ap.add_argument("--no-pdf", action="store_true")
    ap.add_argument("--days", type=int, default=14)
    ap.add_argument("--reset", action="store_true", help="clear earlier conversations for this demo")
    a = ap.parse_args()

    place, sector = find_place(a.query)
    sector = a.sector or sector
    if sector not in SUPPORTED:
        sys.exit(f"{place['title']} is in sector '{sector}'. Pass --sector healthcare|food|education.")
    print(f"place: {place['title']} ({sector}) {place['placeId']}")
    reviews = fetch_reviews(place, a.refresh_reviews)
    print(f"reviews: {len(reviews)} fetched")
    demo = build_demo(place, sector, a.days)
    demo["xray"] = xray(place, reviews)
    demo["health"] = health(place, demo["xray"]["stats"])
    x = demo["xray"]
    print(f"x-ray: {len(x['complaints'])} complaint themes, {len(x['praise'])} praise themes, "
          f"owner replies {x['stats']['owner_reply_pct']}%, health {demo['health']['score']}/100")
    upsert(demo)
    if a.reset:
        subprocess.run([sys.executable, str(DEMO_APP / "scripts" / "reset_demo.py"), demo["slug"]], check=False)
    (DATA / "demos" / f"{demo['slug']}.json").write_text(json.dumps(demo, ensure_ascii=False, indent=1), encoding="utf-8")
    base = ENV.get("DEMO_BASE_URL", "https://nexuspoint-demo.vercel.app")
    hub = f"{base}/d/{demo['slug']}?t={demo['token']}"
    wa = ENV.get("DEMO_WHATSAPP_NUMBER")
    chat = f"https://wa.me/{wa}?text={urllib.request.quote('DEMO-' + demo['code'] + ' Assalam o alaikum')}" if wa else f"{hub}&chat=1"
    print(f"hub:  {hub}\nchat: {chat}\ncode: {demo['code']}")
    if not a.no_pdf:
        render_pdf(demo, hub, chat)


def render_pdf(demo: dict, hub: str, chat: str) -> None:
    import asyncio
    import render
    ctx = render.load_context()
    ctx.update({"demo": demo, "qr_hub": render.qr_svg(hub), "qr_chat": render.qr_svg(chat), "hub_url": hub,
                "prepared": datetime.now(timezone.utc).strftime("%Y-%m-%d")})
    jobs = [("healthcheck.html.j2", f"Health-Check-{demo['slug']}-{lang}", render.A4, {"lang": lang}) for lang in ("en", "ur")]
    asyncio.run(render.render(jobs, ctx))


if __name__ == "__main__":
    main()
