"""Phase -1: scrape raw leads from a business directory (or Google Maps) into a scored, sorted, well-
formatted NEW Google Sheet -- the step that PRODUCES the sheet Phase 0-4 already know how to consume.

Two input modes (locked with Aleem 2026-07-17):
  * DIRECTORY URL  --url <clutch/goodfirms/sortlist/designrush listing URL> : the directory sites encode
    location as an opaque internal id (Clutch geona_id) that can't be guessed from a city name, so Aleem
    filters on the site and pastes the URL. Paginated, LLM-extracted (structure-tolerant, one schema
    fits all four), Clutch via crawl4ai (Cloudflare) and the rest via the auto ladder.
  * MAPS KEYWORD   --maps "<keyword>" --location "<city>" : Google Maps via the compass/crawler-google-
    places Apify actor, which takes keyword + location cleanly.

Reuses the web-scraper skill as the extraction engine (same subprocess pattern clutch_resolve.py uses),
merge_leads' dedup primitives, read_batch's phone-clean + South-Asia geo-exclusion, and score.py's
volume-weighted 1-10 score. Output columns match Aleem's "Instant SM Leads" layout + a Score column,
and are deliberately resolve-compatible: run_batch.py (socials/founders) then push_from_leadgen.py (CRM)
can run on the produced sheet next, unchanged.

Usage:
  python scrape_directory.py --url "https://clutch.co/developers/artificial-intelligence?geona_id=25864" --limit 100
  python scrape_directory.py --maps "digital marketing" --location "New York, NY" --limit 100
  python scrape_directory.py --url <url> --limit 15 --dry-run     # scrape+score+md, no sheet
Runs UNSANDBOXED (web-scraper needs DNS + a real browser). Sheet I/O needs a live gws token.
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from datetime import date
from pathlib import Path
from urllib.parse import parse_qs, parse_qsl, urlencode, urlparse, urlunparse

HERE = Path(__file__).resolve().parent
SKILLS = HERE.parents[1]                      # .claude/skills
REPO_ROOT = HERE.parents[3]                   # repo root
WEBSCRAPER = SKILLS / "web-scraper" / "scripts" / "scrape.py"
DIRECTORY_SCHEMA = HERE.parent / "templates" / "directory_schema.json"

sys.path.insert(0, str(HERE))
sys.path.insert(0, str(SKILLS / "leads-to-crm" / "scripts"))
sys.path.insert(0, str(SKILLS / "web-scraper" / "scripts"))
import sheets  # noqa: E402  (leads-to-crm gws wrapper)
import score as scorer  # noqa: E402
import merge_leads  # noqa: E402
import clutch_resolve  # noqa: E402
from channels import _domain  # noqa: E402
from read_batch import _clean_phone, _strip_bullet, _is_south_asia  # noqa: E402

# Per-directory config. LLM extraction absorbs the HTML differences, so this is just: which host, which
# pagination query param, and which engine to start on (Clutch is Cloudflare-protected -> crawl4ai).
DIRECTORY_CONFIG = {
    "clutch.co":      {"page_param": "page", "engine": "crawl4ai"},
    "goodfirms.co":   {"page_param": "page", "engine": "auto"},
    "sortlist.com":   {"page_param": "page", "engine": "auto"},
    "designrush.com": {"page_param": "page", "engine": "auto"},
}

OUTPUT_COLUMNS = [
    "Score", "Link", "Company Name", "Rating", "Reviews", "Budget Range", "Category", "Location",
    "Note", "Website Link", "Social Search Status", "Instagram Link", "LinkedIn Link", "Facebook Link",
]
# canonical-row key -> output column
COL_TO_KEY = {
    "Score": "score", "Link": "link", "Company Name": "company", "Rating": "rating",
    "Reviews": "reviews", "Budget Range": "budget_range", "Category": "category",
    "Location": "location", "Note": "note", "Website Link": "website",
}
MAX_PAGES = 25  # hard stop so a paginating loop can never run away


# ---------------------------------------------------------------------------
# Directory detection + pagination
# ---------------------------------------------------------------------------

def detect_directory(url: str):
    host = urlparse(url).netloc.lower().lstrip("www.")
    for key in DIRECTORY_CONFIG:
        if key in host:
            return key
    return None


def page_url(url: str, page_param: str, value: int) -> str:
    """Return url with page_param set to value, preserving existing query params."""
    parts = urlparse(url)
    q = [(k, v) for k, v in parse_qsl(parts.query) if k != page_param]
    q.append((page_param, str(value)))
    return urlunparse(parts._replace(query=urlencode(q)))


def _norm_link(link: str) -> str:
    """host+path of a profile URL, lowercased, no scheme/query/trailing slash -- the stable per-directory
    identity for a company (each company has ONE profile URL regardless of the office city a page shows)."""
    p = urlparse((link or "").strip().lower())
    return (p.netloc.lstrip("www.") + p.path.rstrip("/")) if p.netloc else ""


def _dir_keys(rec: dict) -> set:
    """Every identity a directory row should dedup on. A row collides if it shares ANY key with a kept
    row, so a linkless duplicate (same company shown on a second page under a different office city)
    still collides on the name key -- the exact miss that let 'Simform' appear twice. Name-only as the
    final key is safe here because a single-category directory scrape won't contain two genuinely
    different companies with the same normalized name (Maps mode keeps merge_leads' name+city key, since
    there local businesses DO legitimately repeat a name across cities).
    ponytail: name-only dedup can, in theory, merge two same-named agencies; within one directory
    category that's rarer than the duplicate it prevents."""
    keys = set()
    link = _norm_link(rec.get("link", ""))
    if link:
        keys.add("link:" + link)
    dom = _domain(rec.get("website", ""))
    if dom:
        keys.add("site:" + dom)
    keys.add("name:" + merge_leads._norm_name(rec.get("company", "")))
    return keys


# ---------------------------------------------------------------------------
# Scraping
# ---------------------------------------------------------------------------

def scrape_page(url: str, engine: str, timeout: int = 300) -> list[dict]:
    """One listing page -> raw extracted row dicts, via the web-scraper skill (subprocess, same pattern
    as clutch_resolve.py). Returns [] on any failure so one bad page never kills the run."""
    cmd = [sys.executable, str(WEBSCRAPER), "--url", url, "--engine", engine,
           "--extract", "llm", "--schema", str(DIRECTORY_SCHEMA), "--out", "json"]
    try:
        p = subprocess.run(cmd, capture_output=True, text=True,
                           encoding="utf-8", errors="replace", timeout=timeout)
    except subprocess.TimeoutExpired:
        print(f"  page timed out ({timeout}s): {url}", file=sys.stderr)
        return []
    if p.returncode != 0 or not p.stdout.strip():
        print(f"  page failed: {url} :: {(p.stderr or 'no output')[:200]}", file=sys.stderr)
        return []
    try:
        data = json.loads(p.stdout)
    except json.JSONDecodeError:
        return []
    return data if isinstance(data, list) else []


def scrape_directory(url: str, cfg: dict, limit: int) -> list[dict]:
    """Fetch the pasted URL (page 1) then paginate (page_param from 1 upward) until we have `limit`
    unique leads, a page returns nothing, or the hard page cap. Starting pagination at 1 and always
    fetching the original first is robust to either 0- or 1-indexed directories -- at worst one
    redundant page fetch that dedup absorbs."""
    seen, out = set(), []
    origin = f"{urlparse(url).scheme}://{urlparse(url).netloc}"

    def absorb(raw_rows: list[dict]) -> int:
        added = 0
        for raw in raw_rows:
            rec = normalize(raw, origin)
            if not rec:
                continue
            keys = _dir_keys(rec)
            if keys & seen:            # collides on link, domain, OR name -> already have this company
                continue
            seen.update(keys)          # mutate, not `seen |= keys` (that rebinds -> closure UnboundLocalError)
            out.append(rec)
            added += 1
            if len(out) >= limit:
                break
        return added

    print(f"  page 1 (original URL)...", flush=True)
    absorb(scrape_page(url, cfg["engine"]))
    empty_streak = 0
    page = 1
    while len(out) < limit and page <= MAX_PAGES:
        pu = page_url(url, cfg["page_param"], page)
        print(f"  page +{page} ({len(out)}/{limit} so far)...", flush=True)
        added = absorb(scrape_page(pu, cfg["engine"]))
        empty_streak = empty_streak + 1 if added == 0 else 0
        if empty_streak >= 2:   # two consecutive pages with nothing new -> we've reached the end
            break
        page += 1
    return out[:limit]


def scrape_maps(keyword: str, location: str, limit: int) -> list[dict]:
    """Google Maps via the compass/crawler-google-places actor (keyword + location, structured out)."""
    from engines import apify_engine  # web-scraper engine, imported lazily (needs apify-client)
    res = apify_engine.actor(
        "compass/crawler-google-places",
        {"searchStringsArray": [keyword], "locationQuery": location,
         "maxCrawledPlacesPerSearch": limit},
        max_items=limit,
    )
    seen, out = set(), []
    for place in res.get("rows", []):
        rec = normalize_maps(place)
        if not rec:
            continue
        key = merge_leads.dedup_key(rec)
        if key in seen:
            continue
        seen.add(key)
        out.append(rec)
    return out[:limit]


# ---------------------------------------------------------------------------
# Normalization (both sources -> the one canonical row shape)
# ---------------------------------------------------------------------------

def _digits(val) -> str:
    return re.sub(r"\D", "", str(val or ""))


# Directory redirect/tracking params whose value carries the real destination website. `provider_website`
# + `u` are Clutch's (handled by clutch_resolve too); the rest cover generic redirect shapes.
_REDIRECT_PARAMS = ("provider_website", "u", "url", "website", "redirect", "target", "link", "out", "r")
_DOMAINISH = re.compile(r"^(https?://)?[a-z0-9-]+(\.[a-z0-9-]+)+", re.I)


def _clean_site(url: str) -> str:
    """A website reduced to its canonical homepage: scheme + host only. Directory 'Visit Website' links
    carry a campaign landing path in the tracking `u` param (e.g. .../clutch/ai-business-automation) --
    the root domain is the more useful Website Link and the better seed for resolve.py's footer/about
    scrape. Drops path, query, and fragment; https-prefixes a bare domain."""
    url = (url or "").strip()
    if not url:
        return ""
    if "://" not in url:
        url = "https://" + url
    p = urlparse(url)
    if not p.netloc:
        return ""
    return urlunparse((p.scheme, p.netloc, "", "", "", ""))


def _is_directory_domain(url: str) -> bool:
    """True if this decoded URL's host is one of the directories themselves (e.g. ppc.clutch.co) -- a
    sponsored/PPC 'Visit Website' that never actually leaves the directory, not a real company site."""
    host = urlparse(url).netloc.lower()
    return any(d in host for d in DIRECTORY_CONFIG)


def decode_website(raw: str, directory: str | None) -> str:
    """Turn a 'Visit Website' href into the company's real website. Handles three shapes: a Clutch
    redirect (reuse clutch_resolve's decoder), any directory-domain redirect carrying the target in a
    query param, and an already-external link (just strip utm/tracking). Returns '' if it can't be
    decoded OR resolves back to a directory's own domain (a sponsored/PPC link) -- resolve.py can still
    recover a real site from the profile page later, so a miss is never fatal, but a directory URL in
    the Website column would be actively wrong."""
    raw = (raw or "").strip()
    if not raw:
        return ""
    host = urlparse(raw if "://" in raw else "https://" + raw).netloc.lower()
    dir_token = (directory or "").split(".")[0].lower()
    cand = ""

    clutch_hit = clutch_resolve.website_from_markdown(raw)  # r.clutch.co/redirect?...&provider_website=...
    if clutch_hit:
        cand = _clean_site(clutch_hit)
    elif dir_token and dir_token in host:
        # a redirect ON the directory's own domain -> pull the target out of a query param
        qs = parse_qs(urlparse(raw).query)
        for key in _REDIRECT_PARAMS:
            if qs.get(key) and _DOMAINISH.match(qs[key][0].strip()):
                cand = _clean_site(qs[key][0])
                break
        else:
            for vals in qs.values():   # any param value that looks like a full URL
                for v in vals:
                    if v.strip().lower().startswith(("http://", "https://")):
                        cand = _clean_site(v)
                        break
                if cand:
                    break
    else:
        cand = _clean_site(raw)  # already an external website link -> just drop tracking params

    return "" if (cand and _is_directory_domain(cand)) else cand


def normalize(raw: dict, origin: str) -> dict | None:
    """One LLM-extracted directory row -> canonical rec, or None if unusable/geo-excluded."""
    company = (raw.get("company") or "").strip()
    if not company:
        return None
    location = (raw.get("location") or "").strip()
    if _is_south_asia(location) or _is_south_asia(company):
        return None
    link = (raw.get("profile_link") or "").strip()
    if link.startswith("/"):
        link = origin.rstrip("/") + link
    return {
        "company": company,
        "link": link,
        "rating": (str(raw.get("rating")).strip() if raw.get("rating") not in (None, "") else ""),
        "reviews": _digits(raw.get("reviews")),
        "budget_range": (raw.get("budget_range") or "").strip(),
        "category": _strip_bullet((raw.get("category") or "").strip()),
        "location": location,
        "note": (raw.get("note") or "").strip(),
        # decode the 'Visit Website' href off the listing (Clutch redirect / directory redirect / utm
        # link) so Website Link is filled at scrape time instead of waiting for resolve.py
        "website": decode_website(raw.get("website", ""), detect_directory(origin)),
        "phone": "",  # not on directory index pages; kept for dedup-key shape parity with Maps
    }


def normalize_maps(place: dict) -> dict | None:
    """One Google Places actor item -> canonical rec (the actor's field names differ from the schema)."""
    company = (place.get("title") or "").strip()
    if not company:
        return None
    location = (place.get("city") or place.get("address") or "").strip()
    if _is_south_asia(location) or _is_south_asia(company):
        return None
    return {
        "company": company,
        "link": (place.get("url") or "").strip(),                 # the Google Maps place URL
        "rating": (str(place.get("totalScore")).strip() if place.get("totalScore") else ""),
        "reviews": _digits(place.get("reviewsCount")),
        "budget_range": "",
        "category": (place.get("categoryName") or "").strip(),
        "location": location,
        "note": (place.get("description") or "").strip(),
        "website": (place.get("website") or "").strip(),
        "phone": _clean_phone(place.get("phone") or ""),
    }


# ---------------------------------------------------------------------------
# Profile enrichment (the reliable pass -- listing pages hide rating/reviews/website in widgets that
# don't survive HTML->markdown, and rotate results; each company's PROFILE page carries all of it cleanly)
# ---------------------------------------------------------------------------

# many:false -- one company per profile page. Pulled from the profile HEADER (first ~8k chars), where the
# overall rating, review count, and min-project-size budget live, so the LLM can't grab a stray in-review
# star number from lower down.
PROFILE_SCHEMA = {
    "many": False,
    "fields": [
        {"name": "rating", "description": "the company's OVERALL review star rating shown near the top, e.g. 4.8 (a 0-5 number). Not an individual review's score."},
        {"name": "reviews", "description": "the TOTAL number of reviews for the company, digits only, e.g. 86"},
        {"name": "budget_range", "description": "the minimum project size / budget, e.g. '$25,000+' or '$1,000+'"},
        {"name": "category", "description": "the company's primary service line / what they do"},
        {"name": "location", "description": "the company's headquarters city and state/country"},
        {"name": "note", "description": "a one-sentence description of what the company does"},
        {"name": "website", "description": "the destination of the company's 'Visit Website' button (often an r.clutch.co/redirect link) -- the full href"},
    ],
}


def fetch_markdown(url: str, engine: str, timeout: int = 180) -> str:
    """One page -> raw markdown via the web-scraper skill (subprocess, same pattern as clutch_resolve)."""
    cmd = [sys.executable, str(WEBSCRAPER), "--url", url, "--engine", engine, "--extract", "raw", "--out", "json"]
    try:
        p = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=timeout)
    except subprocess.TimeoutExpired:
        return ""
    if p.returncode != 0 or not p.stdout.strip():
        return ""
    try:
        data = json.loads(p.stdout)
    except json.JSONDecodeError:
        return ""
    row = data[0] if isinstance(data, list) and data else (data if isinstance(data, dict) else {})
    return row.get("markdown", "")


def _merge_profile(disc: dict, detail: dict, website: str) -> dict:
    """Merge profile-page detail onto a discovered lead. Profile WINS for rating/reviews/budget/website
    (the whole reason for the pass); discovery keeps company/link/location/category unless profile fills
    a gap. A failed profile fetch (empty detail + website) leaves the discovery values untouched."""
    out = dict(disc)
    r = str(detail.get("rating") or "").strip()
    if r:
        out["rating"] = r
    rev = _digits(detail.get("reviews"))
    if rev:
        out["reviews"] = rev
    bud = (detail.get("budget_range") or "").strip()
    if bud:
        out["budget_range"] = bud
    if website:
        out["website"] = website
    for k in ("category", "location", "note"):
        if not out.get(k) and (detail.get(k) or "").strip():
            out[k] = str(detail.get(k)).strip()
    return out


def enrich_one(rec: dict, directory: str | None, engine: str) -> dict:
    """Fetch one company's profile page and merge accurate rating/reviews/budget/website onto its
    discovered record. Website is decoded deterministically from the profile markdown (Clutch redirect)
    first, LLM-extracted field second. On any failure the discovered record passes through unchanged."""
    url = rec.get("link", "")
    if not url.lower().startswith("http"):
        return rec
    md = fetch_markdown(url, engine)
    if not md:
        return rec
    website = _clean_site(clutch_resolve.website_from_markdown(md))  # first r.clutch.co/redirect on the profile
    detail = {}
    try:
        import extract as wextract  # web-scraper's extractor (already on sys.path)
        rows = wextract.extract_llm(md[:8000], PROFILE_SCHEMA)  # header only: overall rating/reviews/budget
        detail = rows[0] if rows else {}
    except Exception as e:  # noqa: BLE001 - one bad profile never kills the batch
        print(f"    profile extract failed for {url}: {str(e)[:120]}", file=sys.stderr)
    if not website:  # fall back to the LLM's website field, decoded
        website = decode_website(detail.get("website", ""), directory)
    if website and _is_directory_domain(website):
        website = ""
    return _merge_profile(rec, detail, website)


def enrich_profiles(recs: list[dict], directory: str | None, engine: str, *, workers: int = 4) -> list[dict]:
    """Enrich every discovered lead from its profile page, in parallel (fetches are I/O-bound). Order
    preserved so the later score-sort is deterministic."""
    from concurrent.futures import ThreadPoolExecutor, as_completed
    out: list[dict] = [None] * len(recs)  # type: ignore[list-item]
    done = 0
    with ThreadPoolExecutor(max_workers=workers) as ex:
        futs = {ex.submit(enrich_one, r, directory, engine): i for i, r in enumerate(recs)}
        for fut in as_completed(futs):
            i = futs[fut]
            out[i] = fut.result()
            done += 1
            if done % 5 == 0 or done == len(recs):
                print(f"  enriched {done}/{len(recs)} profiles...", flush=True)
    return out


# ---------------------------------------------------------------------------
# Output
# ---------------------------------------------------------------------------

def write_md(rows: list[dict], out_md: Path, meta: dict):
    out_md.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        f"# Directory scrape: {meta['query']}",
        "",
        f"- Source: {meta['source']}",
        f"- Date: {meta['date']}",
        f"- Leads: {len(rows)} (sorted by Score, best first)",
        "",
        "| Score | Company | Rating | Reviews | Budget | Category | Location | Link |",
        "|---|---|---|---|---|---|---|---|",
    ]
    for r in rows:
        note = (r.get("company") or "").replace("|", "/")
        lines.append(
            f"| {r['score']} | {note} | {r.get('rating','')} | {r.get('reviews','')} | "
            f"{r.get('budget_range','')} | {(r.get('category','') or '').replace('|','/')} | "
            f"{(r.get('location','') or '').replace('|','/')} | {r.get('link','')} |"
        )
    out_md.write_text("\n".join(lines) + "\n", encoding="utf-8")


def push_to_sheet(rows: list[dict], title: str) -> str:
    """Create a new sheet, write the sorted rows with a Score column, bold+freeze the header. Returns URL."""
    sid, tab, gid = sheets.create_spreadsheet(title)
    values = [OUTPUT_COLUMNS]
    for r in rows:
        values.append([str(r.get(COL_TO_KEY.get(h, ""), "") or "") for h in OUTPUT_COLUMNS])
    sheets.update_range(sid, f"{tab}!A1", values)
    sheets.batch_update(sid, [
        {"repeatCell": {
            "range": {"sheetId": gid, "startRowIndex": 0, "endRowIndex": 1},
            "cell": {"userEnteredFormat": {"textFormat": {"bold": True},
                                           "backgroundColor": {"red": 0.9, "green": 0.9, "blue": 0.9}}},
            "fields": "userEnteredFormat(textFormat,backgroundColor)"}},
        {"updateSheetProperties": {
            "properties": {"sheetId": gid,
                           "gridProperties": {"frozenRowCount": 1, "frozenColumnCount": 1}},
            "fields": "gridProperties(frozenRowCount,frozenColumnCount)"}},
    ])
    return f"https://docs.google.com/spreadsheets/d/{sid}/edit"


# ---------------------------------------------------------------------------
# Orchestration
# ---------------------------------------------------------------------------

def _slug(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", (text or "").lower()).strip("-")[:50] or "leads"


def run(args) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    today = date.today().isoformat()

    if args.maps:
        query = f"{args.maps} in {args.location}"
        source = f"Google Maps ({query})"
        print(f"Scraping Google Maps: {query} (limit {args.limit})...")
        rows = scrape_maps(args.maps, args.location, args.limit)
        slug = _slug(f"maps-{args.maps}-{args.location}")
        default_title = f"Google Maps Leads - {args.maps} {args.location} - {today}"
    else:
        directory = detect_directory(args.url)
        if not directory:
            print(f"Unrecognized directory host in {args.url}. Supported: {', '.join(DIRECTORY_CONFIG)}",
                  file=sys.stderr)
            return 2
        cfg = DIRECTORY_CONFIG[directory]
        query = args.url
        source = f"{directory} ({args.url})"
        print(f"Scraping {directory} (engine {cfg['engine']}, limit {args.limit})...")
        discovered = scrape_directory(args.url, cfg, args.limit)
        if args.no_enrich:
            print(f"  discovered {len(discovered)} (--no-enrich: skipping profile pass, listing data only)")
            rows = discovered
        else:
            print(f"  discovered {len(discovered)}; enriching from profile pages (rating/reviews/budget/website)...")
            rows = enrich_profiles(discovered, directory, cfg["engine"])
        slug = _slug(f"{directory}-{urlparse(args.url).path}")
        default_title = f"{directory} Leads - {slug} - {today}"

    if not rows:
        print("No leads scraped. Nothing to write.", file=sys.stderr)
        return 1

    scorer.score_batch(rows)
    rows.sort(key=lambda r: r.get("score", 0), reverse=True)

    out_md = Path(args.out_md) if args.out_md else (REPO_ROOT / "docs" / "directory-scrapes" / f"{slug}-{today}.md")
    write_md(rows, out_md, {"query": query, "source": source, "date": today})
    print(f"\n{len(rows)} leads scraped + scored. Top 5:")
    for r in rows[:5]:
        print(f"  {r['score']:>4}  {r['company'][:40]:<40} r={r.get('rating','')} n={r.get('reviews','')}")
    print(f"Markdown: {out_md}")

    if args.dry_run:
        print("\n[DRY RUN] sheet not created.")
        return 0

    url = push_to_sheet(rows, args.sheet_title or default_title)
    print(f"\nSheet created ({len(rows)} rows, sorted best-first): {url}")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description="Scrape a directory (or Maps) into a scored, sorted Google Sheet.")
    src = ap.add_mutually_exclusive_group()
    src.add_argument("--url", help="directory listing URL (clutch/goodfirms/sortlist/designrush)")
    src.add_argument("--maps", help="Google Maps keyword (needs --location)")
    ap.add_argument("--location", default="", help="location for --maps mode, e.g. 'New York, NY'")
    ap.add_argument("--limit", type=int, default=100)
    ap.add_argument("--out-md", help="markdown artifact path (default docs/directory-scrapes/...)")
    ap.add_argument("--sheet-title", help="new-sheet title (default derived from the query + date)")
    ap.add_argument("--dry-run", action="store_true", help="scrape+score+md, don't create the sheet")
    ap.add_argument("--no-enrich", action="store_true",
                    help="directory mode: skip the per-profile enrichment pass (fast, but listing-only "
                         "rating/reviews/website -- many rows will be incomplete)")
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args()

    if args.selftest:
        demo()
        return 0
    if args.maps and not args.location:
        ap.error("--maps requires --location")
    if not args.maps and not args.url:
        ap.error("pass --url <directory-url> or --maps <keyword> --location <city>")
    return run(args)


def demo():
    """Self-check: pagination URL building, directory detection, normalization + geo-exclude (no network)."""
    assert detect_directory("https://clutch.co/agencies/digital-marketing?geona_id=25864") == "clutch.co"
    assert detect_directory("https://www.goodfirms.co/directory/x") == "goodfirms.co"
    assert detect_directory("https://example.com/x") is None
    # pagination preserves existing query params and replaces the page param
    pu = page_url("https://clutch.co/x?geona_id=25864", "page", 2)
    assert "geona_id=25864" in pu and "page=2" in pu, pu
    pu2 = page_url("https://clutch.co/x?geona_id=25864&page=1", "page", 3)
    assert pu2.count("page=") == 1 and "page=3" in pu2, pu2
    # normalize: keeps a good row, geo-excludes South Asia, drops blank company, absolutizes a relative link
    good = normalize({"company": "Acme", "profile_link": "/profile/acme", "rating": "4.9",
                      "reviews": "52 reviews", "location": "New York, NY"}, "https://clutch.co")
    assert good and good["link"] == "https://clutch.co/profile/acme" and good["reviews"] == "52", good
    assert normalize({"company": "X", "location": "Karachi, Pakistan"}, "https://clutch.co") is None
    assert normalize({"company": "", "location": "NY"}, "https://clutch.co") is None
    # maps normalization maps the actor's field names
    m = normalize_maps({"title": "Bob SEO", "url": "https://maps.google/x", "totalScore": 4.7,
                        "reviewsCount": 88, "categoryName": "Marketing agency", "city": "Austin, TX",
                        "website": "https://bobseo.com", "phone": "+1 512-555-1000"})
    assert m and m["rating"] == "4.7" and m["reviews"] == "88" and m["website"] == "https://bobseo.com", m
    # website decode: Clutch redirect, generic directory redirect param, external utm link, bad -> blank
    clutch_redir = ("https://r.clutch.co/redirect?content_group=profile&provider_website=appmakers.us"
                    "&u=https%3A%2F%2Fwww.appmakers.us%2F")
    assert decode_website(clutch_redir, "clutch.co") == "https://appmakers.us", decode_website(clutch_redir, "clutch.co")
    ext = decode_website("https://www.simform.com/?utm_source=clutch&utm_medium=referral", "clutch.co")
    assert ext == "https://www.simform.com", ext
    generic = decode_website("https://www.designrush.com/redirect?url=https://gojilabs.com/", "designrush.com")
    assert generic == "https://gojilabs.com", generic
    assert decode_website("", "clutch.co") == "" and decode_website("https://r.clutch.co/redirect?x=1", "clutch.co") == ""
    # a sponsored/PPC link that decodes back to the directory's own domain must be rejected (Azumo bug)
    assert decode_website("https://r.clutch.co/redirect?u=https%3A%2F%2Fppc.clutch.co%2Fx", "clutch.co") == "", \
        decode_website("https://r.clutch.co/redirect?u=https%3A%2F%2Fppc.clutch.co%2Fx", "clutch.co")
    # profile enrichment merge: profile wins for rating/reviews/budget/website; discovery kept elsewhere
    disc = {"company": "Acme", "link": "https://clutch.co/profile/acme", "rating": "", "reviews": "",
            "budget_range": "", "category": "AI Development", "location": "New York, NY", "note": ""}
    merged = _merge_profile(disc, {"rating": "4.8", "reviews": "86 reviews", "budget_range": "$25,000+",
                                   "category": "X", "location": "", "note": "Builds AI apps"},
                            "https://acme.com")
    assert merged["rating"] == "4.8" and merged["reviews"] == "86" and merged["budget_range"] == "$25,000+", merged
    assert merged["website"] == "https://acme.com" and merged["company"] == "Acme", merged
    assert merged["category"] == "AI Development" and merged["note"] == "Builds AI apps", merged  # keep disc, fill gap
    # a failed profile (empty detail + website) leaves discovery values untouched
    assert _merge_profile(disc, {}, "") == disc
    # dedup: a linked company and its linkless twin (different office city) must collide on the name key
    linked = {"company": "Simform", "link": "https://clutch.co/profile/simform", "location": "New York, NY"}
    twin = {"company": "Simform", "link": "", "location": "Orlando, FL"}
    seen = set()
    seen |= _dir_keys(linked)
    assert _dir_keys(twin) & seen, "linkless same-name twin should be deduped"
    # but two genuinely different companies do NOT collide
    other = {"company": "Computools", "link": "https://clutch.co/profile/computools", "location": "NY"}
    assert not (_dir_keys(other) & seen), "different company should not collide"
    print("scrape_directory self-check OK")


if __name__ == "__main__":
    raise SystemExit(main())
