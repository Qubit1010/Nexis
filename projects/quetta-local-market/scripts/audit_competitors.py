"""Audit every Quetta software house / agency website found on Google Maps.

For each site: fetch the homepage plus up to 3 linked service/portfolio/case pages, then count
AI claims against proof signals. Output data/competitors.json (used by the report) and a table.
Heuristic, not a verdict: the report pairs it with manual reads of the leading sites.
"""
import json
import re
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from urllib.parse import urljoin, urlparse

import requests

PROJECT = Path(__file__).resolve().parents[1]
RAW = PROJECT / "data" / "maps_raw"
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/126 Safari/537.36"}

AI = re.compile(r"\b(ai|artificial intelligence|machine learning|chat ?bots?|automation|gpt|llm|ai[- ]powered)\b", re.I)
WHATSAPP = re.compile(r"whats ?app (bot|chatbot|automation|api|agent)", re.I)
PROOF = {
    "case_study": re.compile(r"case stud(y|ies)", re.I),
    "portfolio": re.compile(r"\bportfolio\b|our work|projects", re.I),
    "testimonial": re.compile(r"testimonial|what our clients say|client reviews?", re.I),
    "demo": re.compile(r"\b(live demo|book a demo|request a demo|try (it|the) demo|watch demo)\b", re.I),
    "pricing": re.compile(r"(pkr|rs\.?)\s?[\d,]{3,}|pricing|packages?", re.I),
    "resilience": re.compile(r"(internet shut ?down|internet outage|works offline|offline mode|offline[- ]first|without internet|sms fallback|when the internet)", re.I),
}
SUBPAGE = re.compile(r"(portfolio|case|work|project|service|ai|automation|pricing|package)", re.I)


def fetch(url: str) -> str:
    try:
        r = requests.get(url, headers=UA, timeout=12)
        if r.status_code >= 400:
            return ""
        return r.text
    except requests.RequestException:
        return ""


def text_of(html: str) -> str:
    html = re.sub(r"(?is)<(script|style|noscript).*?</\1>", " ", html)
    return re.sub(r"\s+", " ", re.sub(r"(?s)<[^>]+>", " ", html))


def audit(row: dict) -> dict:
    url = row["website"].split("?")[0]
    home = fetch(url)
    pages, host = [home], urlparse(url).netloc
    links = re.findall(r'href=["\']([^"\'#]+)', home)
    subs = []
    for href in links:
        full = urljoin(url, href)
        if urlparse(full).netloc == host and SUBPAGE.search(full) and full not in subs:
            subs.append(full)
    for sub in subs[:3]:
        pages.append(fetch(sub))
    txt = " ".join(text_of(p) for p in pages)
    out = {"name": row["title"], "reviews": row.get("reviewsCount") or 0, "rating": row.get("totalScore"),
           "website": url, "reachable": bool(home), "pages_read": sum(1 for p in pages if p),
           "ai_mentions": len(AI.findall(txt)), "whatsapp_bot": bool(WHATSAPP.search(txt))}
    for k, rx in PROOF.items():
        out[k] = len(rx.findall(txt))
    return out


def main() -> None:
    rows = []
    for slug in ("software-houses", "marketing-agencies"):
        for r in json.loads((RAW / f"{slug}.json").read_text(encoding="utf-8")):
            addr = ((r.get("city") or "") + (r.get("address") or "")).lower()
            if r.get("website") and "quetta" in addr and "facebook.com" not in r["website"]:
                r["_kind"] = slug
                rows.append(r)
    seen, uniq = set(), []
    for r in rows:
        host = urlparse(r["website"]).netloc.replace("www.", "")
        if host not in seen:
            seen.add(host)
            uniq.append(r)
    with ThreadPoolExecutor(max_workers=12) as pool:
        results = list(pool.map(audit, uniq))
    for res, r in zip(results, uniq):
        res["kind"] = r["_kind"]
        res["address"] = r.get("address")
    results.sort(key=lambda x: -x["reviews"])
    (PROJECT / "data" / "competitors_audit.json").write_text(json.dumps(results, indent=1), encoding="utf-8")
    print(f"{'name':42} {'rev':>4} {'ok':>3} {'AI':>4} {'WAbot':>5} {'case':>4} {'port':>4} {'test':>4} {'demo':>4} {'resil':>5}")
    for x in results:
        print(f"{x['name'][:42]:42} {x['reviews']:>4} {str(x['reachable'])[0]:>3} {x['ai_mentions']:>4} "
              f"{str(x['whatsapp_bot'])[0]:>5} {x['case_study']:>4} {x['portfolio']:>4} {x['testimonial']:>4} {x['demo']:>4} {x['resilience']:>5}")


if __name__ == "__main__":
    main()
