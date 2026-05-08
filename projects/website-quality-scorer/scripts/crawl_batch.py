"""Batch crawler — builds data/labeled/dataset.csv for ML training.

Pulls URLs from 3 sources:
  1. projects/lead-gen/data/leads.db  (company_website column)
  2. projects/lead-gen/data/cold_email_touch1_2026-04-09.csv  (domain from email)
  3. Curated hardcoded list  (SaaS, e-commerce, portfolios, dev-infra)

Usage:
    cd projects/website-quality-scorer
    python scripts/crawl_batch.py              # full run (~200 sites)
    python scripts/crawl_batch.py --limit 5   # quick test
    python scripts/crawl_batch.py --workers 3  # slower, fewer concurrent requests
"""

from __future__ import annotations

import argparse
import csv
import os
import random
import sqlite3
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from urllib.parse import urlparse

from tqdm import tqdm

# Allow imports from backend/
_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_ROOT / "backend"))

from crawler.firecrawl_client import CrawlError, crawl
from crawler.pagespeed import fetch_pagespeed_metrics
from features.extractor import FEATURE_NAMES, extract_all
from ml.heuristic_label import heuristic_score_detailed

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
LEADS_DB = _ROOT.parent / "lead-gen" / "data" / "leads.db"
LEADS_CSV = _ROOT.parent / "lead-gen" / "data" / "cold_email_touch1_2026-04-09.csv"
OUT_CSV = _ROOT / "data" / "labeled" / "dataset.csv"
FAILED_LOG = _ROOT / "data" / "raw" / "failed_urls.txt"

# ---------------------------------------------------------------------------
# Curated URL list — diverse industries to balance the B2B-heavy lead data
# ---------------------------------------------------------------------------
CURATED_URLS: list[str] = [
    # SaaS / B2B (30)
    "https://stripe.com",
    "https://notion.so",
    "https://linear.app",
    "https://vercel.com",
    "https://netlify.com",
    "https://supabase.com",
    "https://hubspot.com",
    "https://intercom.com",
    "https://figma.com",
    "https://webflow.com",
    "https://zapier.com",
    "https://calendly.com",
    "https://typeform.com",
    "https://loom.com",
    "https://airtable.com",
    "https://monday.com",
    "https://clickup.com",
    "https://freshdesk.com",
    "https://mailchimp.com",
    "https://convertkit.com",
    "https://jotform.com",
    "https://tawk.to",
    "https://acuityscheduling.com",
    "https://teachable.com",
    "https://podia.com",
    "https://kartra.com",
    "https://kajabi.com",
    "https://systeme.io",
    "https://gohighlevel.com",
    "https://thrivecart.com",
    # E-commerce (30)
    "https://allbirds.com",
    "https://warbyparker.com",
    "https://mvmt.com",
    "https://beardbrand.com",
    "https://bombas.com",
    "https://chubbies.com",
    "https://ridgewallet.com",
    "https://bellroy.com",
    "https://gymshark.com",
    "https://tentree.com",
    "https://ugmonk.com",
    "https://hardgraft.com",
    "https://nomadgoods.com",
    "https://tuftandneedle.com",
    "https://brooklinen.com",
    "https://parachutehome.com",
    "https://glossier.com",
    "https://curology.com",
    "https://ritual.com",
    "https://hims.com",
    "https://drinkag1.com",
    "https://koala.com",
    "https://leesa.com",
    "https://patagonia.com",
    "https://rei.com",
    "https://everlane.com",
    "https://frankandoak.com",
    "https://outerknown.com",
    "https://casper.com",
    "https://saatva.com",
    # Professional services / marketing (30)
    "https://wpengine.com",
    "https://kinsta.com",
    "https://webfx.com",
    "https://ignitevisibility.com",
    "https://victorious.com",
    "https://neilpatel.com",
    "https://backlinko.com",
    "https://moz.com",
    "https://semrush.com",
    "https://ahrefs.com",
    "https://optimizely.com",
    "https://unbounce.com",
    "https://leadpages.com",
    "https://instapage.com",
    "https://clickfunnels.com",
    "https://memberpress.com",
    "https://wishpond.com",
    "https://sproutsocial.com",
    "https://buffer.com",
    "https://hootsuite.com",
    "https://later.com",
    "https://meetedgar.com",
    "https://socialbee.io",
    "https://sendgrid.com",
    "https://campaignmonitor.com",
    "https://activecampaign.com",
    "https://klaviyo.com",
    "https://drip.com",
    "https://omnisend.com",
    "https://getresponse.com",
    # Portfolios / personal brands (15)
    "https://levels.io",
    "https://bradfrost.com",
    "https://alistapart.com",
    "https://smashingmagazine.com",
    "https://taniarascia.com",
    "https://waitbutwhy.com",
    "https://paulgraham.com",
    "https://ghost.org",
    "https://bearblog.dev",
    "https://overreacted.io",
    "https://css-tricks.com",
    "https://dev.to",
    "https://hashnode.com",
    "https://medium.com",
    "https://substack.com",
    # Dev infra / hosting (15)
    "https://cloudflare.com",
    "https://digitalocean.com",
    "https://vultr.com",
    "https://render.com",
    "https://railway.app",
    "https://fly.io",
    "https://bun.sh",
    "https://deno.com",
    "https://turso.tech",
    "https://neon.tech",
    "https://upstash.com",
    "https://sanity.io",
    "https://contentful.com",
    "https://storyblok.com",
    "https://directus.io",
]


# ---------------------------------------------------------------------------
# URL loading helpers
# ---------------------------------------------------------------------------

def _normalize(url: str) -> str:
    url = url.strip()
    if not url:
        return ""
    if not url.startswith("http"):
        url = "https://" + url
    # Strip path — we score homepages only
    parsed = urlparse(url)
    return f"{parsed.scheme}://{parsed.netloc}".rstrip("/")


def _load_from_leads_db() -> list[str]:
    if not LEADS_DB.exists():
        return []
    try:
        con = sqlite3.connect(str(LEADS_DB))
        rows = con.execute("SELECT company_website FROM leads WHERE company_website IS NOT NULL").fetchall()
        con.close()
        return [_normalize(r[0]) for r in rows if r[0]]
    except Exception as exc:
        print(f"[warn] leads.db load failed: {exc}")
        return []


def _load_from_email_csv() -> list[str]:
    if not LEADS_CSV.exists():
        return []
    urls = []
    try:
        with open(LEADS_CSV, encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                email = (row.get("Email") or "").strip()
                if "@" in email:
                    domain = email.split("@", 1)[1].strip()
                    if domain:
                        urls.append(_normalize(domain))
    except Exception as exc:
        print(f"[warn] email CSV load failed: {exc}")
    return urls


def _load_all_urls(limit: int | None = None) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []

    for url in _load_from_leads_db() + _load_from_email_csv() + [_normalize(u) for u in CURATED_URLS]:
        if url and url not in seen:
            seen.add(url)
            result.append(url)

    random.shuffle(result)
    return result if limit is None else result[:limit]


# ---------------------------------------------------------------------------
# Per-URL processing
# ---------------------------------------------------------------------------

CSV_HEADERS = (
    ["url"]
    + [f"feature_{n}" for n in FEATURE_NAMES]
    + ["score_ux", "score_content", "score_technical", "score_trust", "score_total"]
    + ["annotator_1", "annotator_2", "kappa_agreement"]
)


def _process_url(url: str) -> dict | None:
    """Crawl + extract features + label one URL. Returns row dict or None on failure."""
    try:
        crawl_data = crawl(url)
    except CrawlError as exc:
        return {"_error": str(exc), "_url": url}
    except Exception as exc:
        return {"_error": str(exc), "_url": url}

    try:
        pagespeed_data = fetch_pagespeed_metrics(url)
        time.sleep(0.5)  # gentle rate-limit on PageSpeed API
    except Exception:
        pagespeed_data = {"mobile": {}, "desktop": {}}

    try:
        features = extract_all(crawl_data, pagespeed_data)
    except Exception as exc:
        return {"_error": f"feature extraction: {exc}", "_url": url}

    scores = heuristic_score_detailed(features)

    row: dict = {"url": crawl_data["url"]}
    for name in FEATURE_NAMES:
        row[f"feature_{name}"] = features.get(name)
    row["score_ux"] = scores["ux"]
    row["score_content"] = scores["content"]
    row["score_technical"] = scores["technical"]
    row["score_trust"] = scores["trust"]
    row["score_total"] = scores["total"]
    row["annotator_1"] = "heuristic"
    row["annotator_2"] = "heuristic"
    row["kappa_agreement"] = True
    return row


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(description="Batch website crawler for ML training data")
    parser.add_argument("--limit", type=int, default=None, help="Max URLs to process (default: all)")
    parser.add_argument("--workers", type=int, default=5, help="Concurrent workers (default: 5)")
    args = parser.parse_args()

    OUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    FAILED_LOG.parent.mkdir(parents=True, exist_ok=True)

    # Resume: load already-processed URLs
    done_urls: set[str] = set()
    write_header = not OUT_CSV.exists()
    if OUT_CSV.exists():
        with open(OUT_CSV, encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row.get("url"):
                    done_urls.add(row["url"].rstrip("/"))
        print(f"Resuming — {len(done_urls)} URLs already in dataset")

    all_urls = _load_all_urls(limit=args.limit)
    pending = [u for u in all_urls if u.rstrip("/") not in done_urls]
    print(f"URLs loaded: {len(all_urls)} total, {len(pending)} pending")

    if not pending:
        print("Nothing to do.")
        return

    success = 0
    failures = 0

    out_file = open(OUT_CSV, "a", newline="", encoding="utf-8")
    writer = csv.DictWriter(out_file, fieldnames=CSV_HEADERS, extrasaction="ignore")
    if write_header:
        writer.writeheader()
    failed_log = open(FAILED_LOG, "a", encoding="utf-8")

    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        futures = {pool.submit(_process_url, url): url for url in pending}
        with tqdm(total=len(pending), unit="site") as bar:
            for future in as_completed(futures):
                url = futures[future]
                try:
                    result = future.result()
                except Exception as exc:
                    result = {"_error": str(exc), "_url": url}

                if result is None or "_error" in result:
                    err = (result or {}).get("_error", "unknown error")
                    tqdm.write(f"  FAIL  {url}  — {err}")
                    failed_log.write(f"{url}\t{err}\n")
                    failures += 1
                else:
                    score = result.get("score_total", "?")
                    tqdm.write(f"  OK    {result['url']}  → {score}")
                    writer.writerow(result)
                    out_file.flush()
                    success += 1

                bar.update(1)
                bar.set_postfix(ok=success, fail=failures)

    out_file.close()
    failed_log.close()

    print(f"\n=== Done ===")
    print(f"  Success : {success}")
    print(f"  Failed  : {failures}")
    print(f"  Dataset : {OUT_CSV}")
    if failures:
        print(f"  Failures: {FAILED_LOG}")

    # Score distribution
    if success > 0:
        import pandas as pd
        df = pd.read_csv(OUT_CSV)
        print(f"\nScore distribution (n={len(df)}):")
        print(df["score_total"].describe().round(1).to_string())


if __name__ == "__main__":
    main()
