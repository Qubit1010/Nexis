"""Cold Email Sheet Push — Firecrawl email extraction + CRM export.

Reads manually scraped leads from a source Google Sheet (website URL, no email),
crawls each website with Firecrawl to find the email address and social links,
generates a personalized Touch 1 cold email, and pushes qualifying leads to the
Cold Email Outreach CRM.

Filters applied:
  - Skip if Rating < 3
  - Skip if already in CRM (by company name or email)
  - Skip CRM push if no email found (social links still written back)

Usage:
  python cold_email_push.py           # live run
  python cold_email_push.py --dry-run # preview without writing
"""

import argparse
import csv
import json
import os
import re
import shutil
import subprocess
import sys
import time
from datetime import date
from pathlib import Path
from urllib.parse import urlparse

import requests

sys.path.insert(0, str(Path(__file__).resolve().parent))
from transformers.email_transformer import generate_cold_email_touch1

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

SOURCE_SHEET_ID = "18ButtEgVFZ7IRu6ywotyTfmPdys-oxiB_gU4fZXhA8I"
SOURCE_TAB      = "Sheet1"

CRM_SHEET_ID    = "1F5QYhh0pVjMds7XOBPfCIWyZX_9L8wFZNIwZYxH9Kx4"
CRM_TAB         = "Enriched Leads"

MIN_RATING      = 3.0

FIRECRAWL_URL   = "https://api.firecrawl.dev/v1/scrape"
FIRECRAWL_TIMEOUT = 20   # seconds per request
FIRECRAWL_SLEEP   = 1.0  # seconds between calls

# Business words that indicate a name is a company, not a person
_BUSINESS_WORDS = {
    "agency", "marketing", "digital", "studio", "media", "group",
    "llc", "inc", "ltd", "co", "services", "solutions", "consulting",
    "design", "creative", "brand", "brands", "ventures", "labs",
    "tech", "technologies", "management", "productions", "collective",
    "associates", "partners", "enterprises", "systems", "global",
}

GENERIC_EMAIL_PREFIXES = {
    "info", "contact", "hello", "admin", "support", "sales",
    "team", "general", "enquiries", "enquiry", "noreply", "no-reply",
    "mail", "office", "help", "billing", "careers", "press", "hr",
    "jobs", "accounts", "accounting",
}

BLOCKED_EMAIL_DOMAINS = {"google.com", "bing.com", "yahoo.com", "domain.com", "example.com"}
BLOCKED_EMAILS = {"example@domain.com", "noreply@example.com", "test@test.com", "press@google.com"}

EMAIL_RE = re.compile(r'(?<![a-zA-Z0-9])([a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,})(?![a-zA-Z])')

# ---------------------------------------------------------------------------
# gws helpers
# ---------------------------------------------------------------------------

def _find_gws():
    import os as _os
    npm_dir = Path(_os.environ.get("APPDATA", "")) / "npm"
    gws_js = npm_dir / "node_modules" / "@googleworkspace" / "cli" / "run-gws.js"
    if gws_js.exists():
        for candidate in [
            npm_dir / "node.exe",
            Path(_os.environ.get("ProgramFiles", "C:\\Program Files")) / "nodejs" / "node.exe",
            Path(_os.environ.get("ProgramFiles(x86)", "C:\\Program Files (x86)")) / "nodejs" / "node.exe",
        ]:
            if candidate.exists():
                return ([str(candidate), str(gws_js)], False)
        node = shutil.which("node")
        if node:
            return ([node, str(gws_js)], False)
    gws = shutil.which("gws")
    if gws:
        return ([gws], True)
    gws_cmd = npm_dir / "gws.cmd"
    if gws_cmd.exists():
        return ([str(gws_cmd)], True)
    return (["gws"], True)


_GWS_CMD, _GWS_SHELL = _find_gws()


def _run_gws(args: list, json_body: dict = None) -> dict:
    cmd = _GWS_CMD + args
    if json_body is not None:
        cmd += ["--json", json.dumps(json_body)]
    result = subprocess.run(
        cmd, capture_output=True, text=True, timeout=120,
        shell=_GWS_SHELL, encoding="utf-8", errors="replace"
    )
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or "gws error")
    stdout = result.stdout.strip()
    if not stdout:
        return {}
    try:
        return json.loads(stdout)
    except json.JSONDecodeError:
        return {"raw": stdout}


def _read_sheet(sheet_id: str, tab: str) -> list[list]:
    try:
        data = _run_gws([
            "sheets", "spreadsheets", "values", "get",
            "--params", json.dumps({"spreadsheetId": sheet_id, "range": tab})
        ])
        return data.get("values", [])
    except RuntimeError as e:
        print(f"  ERROR reading sheet {sheet_id} tab {tab}: {e}", flush=True)
        return []


def _update_column(sheet_id: str, tab: str, col_letter: str, start_row: int, values: list) -> bool:
    if not values:
        return True
    end_row = start_row + len(values) - 1
    range_str = f"{tab}!{col_letter}{start_row}:{col_letter}{end_row}"
    try:
        _run_gws(
            ["sheets", "spreadsheets", "values", "update",
             "--params", json.dumps({
                 "spreadsheetId": sheet_id,
                 "range": range_str,
                 "valueInputOption": "RAW",
             })],
            json_body={"values": [[v] for v in values]}
        )
        return True
    except RuntimeError as e:
        print(f"  ERROR updating column {col_letter}: {e}", flush=True)
        return False


def _append_rows(sheet_id: str, tab: str, rows: list[list], batch_size: int = 10) -> bool:
    if not rows:
        return True
    for i in range(0, len(rows), batch_size):
        batch = rows[i:i + batch_size]
        try:
            _run_gws(
                ["sheets", "spreadsheets", "values", "append",
                 "--params", json.dumps({
                     "spreadsheetId": sheet_id,
                     "range": f"{tab}!A1",
                     "valueInputOption": "RAW",
                     "insertDataOption": "INSERT_ROWS"
                 })],
                json_body={"values": batch}
            )
        except RuntimeError as e:
            print(f"  ERROR appending batch {i//batch_size + 1}: {e}", flush=True)
            return False
    return True

# ---------------------------------------------------------------------------
# Firecrawl helpers
# ---------------------------------------------------------------------------

def _load_env():
    """Load .env from the project directory."""
    env_path = Path(__file__).resolve().parent / ".env"
    if env_path.exists():
        for line in env_path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, _, val = line.partition("=")
                os.environ.setdefault(key.strip(), val.strip())


def _firecrawl_scrape(url: str, api_key: str) -> dict:
    """Scrape a single URL with Firecrawl. Returns {markdown, links} or {}."""
    try:
        resp = requests.post(
            FIRECRAWL_URL,
            headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
            json={"url": url, "formats": ["markdown", "links"]},
            timeout=FIRECRAWL_TIMEOUT,
        )
        if resp.status_code != 200:
            return {}
        data = resp.json()
        if not data.get("success"):
            return {}
        return data.get("data", {})
    except Exception:
        return {}


def _base_url(url: str) -> str:
    """Return scheme + netloc, e.g. https://example.com"""
    parsed = urlparse(url)
    return f"{parsed.scheme}://{parsed.netloc}"


def _clean_email(email: str) -> str:
    """Strip fused label prefixes and fix TLD garbage (e.g. comhi -> com)."""
    if "@" not in email:
        return email
    local, domain = email.split("@", 1)
    # Strip known label words fused to start of local part (e.g. "Emailinfo" -> "info")
    for prefix in ("email", "e-mail", "mailto"):
        lc = local.lower()
        if lc.startswith(prefix) and len(local) > len(prefix):
            local = local[len(prefix):]
            break
    # Fix TLD garbage: "comhi" -> "com", "netXX" -> "net"
    parts = domain.split(".")
    if parts:
        tld = parts[-1]
        for known in ("com", "net", "org", "edu", "gov", "mil"):
            if tld.lower().startswith(known) and len(tld) > len(known):
                parts[-1] = tld[:len(known)]
                domain = ".".join(parts)
                break
    return f"{local}@{domain}"


def extract_best_email(text: str) -> str:
    """Return best email from text — prefer non-generic, else first generic."""
    found = []
    for e in EMAIL_RE.findall(text or ""):
        if any(e.lower().endswith(ext) for ext in
               [".png", ".jpg", ".gif", ".svg", ".webp", ".jpeg", ".ico"]):
            continue
        e = _clean_email(e)
        domain = e.split("@")[-1].lower() if "@" in e else ""
        if domain in BLOCKED_EMAIL_DOMAINS:
            continue
        if e.lower() in BLOCKED_EMAILS:
            continue
        found.append(e)
    if not found:
        return ""
    non_generic = [e for e in found if e.split("@")[0].lower() not in GENERIC_EMAIL_PREFIXES]
    return (non_generic or found)[0]


def extract_socials(content: str) -> dict:
    """Find Instagram, Facebook, LinkedIn URLs in scraped content."""
    patterns = {
        "instagram": r'https?://(?:www\.)?instagram\.com/[^\s"\'<>)\]]+',
        "facebook":  r'https?://(?:www\.)?(?:facebook|fb)\.com/[^\s"\'<>)\]]+',
        "linkedin":  r'https?://(?:www\.)?linkedin\.com/(?:in|company)/[^\s"\'<>)\]]+',
    }
    result = {}
    for platform, pattern in patterns.items():
        match = re.search(pattern, content)
        if match:
            result[platform] = match.group(0).rstrip("/.,)")
    return result


def crawl_for_email_and_socials(website: str, api_key: str) -> tuple[str, dict]:
    """Try up to 3 pages to find an email. Return (email, socials_dict)."""
    if not website or not api_key:
        return "", {}

    base = _base_url(website)
    pages_to_try = [
        website,
        f"{base}/contact",
        f"{base}/about",
    ]

    all_content = ""
    email = ""

    for i, url in enumerate(pages_to_try):
        if i > 0:
            time.sleep(FIRECRAWL_SLEEP)

        data = _firecrawl_scrape(url, api_key)
        if not data:
            continue

        markdown = data.get("markdown", "") or ""
        links = data.get("links", []) or []
        links_text = " ".join(links)
        page_content = markdown + " " + links_text
        all_content += " " + page_content

        email = extract_best_email(page_content)
        if email:
            break  # found one — stop crawling

    socials = extract_socials(all_content)
    return email, socials

# ---------------------------------------------------------------------------
# Name helpers
# ---------------------------------------------------------------------------

def _extract_first_name(company_name: str) -> str:
    """Return a person first name, or '' if it looks like a business name."""
    if not company_name:
        return ""
    base = re.split(r'\s*[|\-–]\s*', company_name)[0].strip()
    words = base.split()
    if not words:
        return ""
    lower_words = {w.lower().rstrip(".,") for w in words}
    if lower_words & _BUSINESS_WORDS:
        return ""
    if len(words) > 3:
        return ""
    return words[0]


def _normalize_company(name: str) -> str:
    """Normalize company name for dedup: lowercase, strip legal suffixes."""
    n = name.lower().strip()
    for suffix in [" llc", " inc", " ltd", " co.", " corp", ",", "."]:
        n = n.replace(suffix, "")
    return n.strip()

# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="Cold Email Sheet Push")
    parser.add_argument("--dry-run", action="store_true", help="Preview without writing to CRM")
    args = parser.parse_args()

    dry_run = args.dry_run

    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")

    if dry_run:
        print("[DRY RUN] No changes will be written.\n")

    _load_env()
    api_key = os.environ.get("FIRECRAWL_API_KEY", "").strip()
    if not api_key:
        print("ERROR: FIRECRAWL_API_KEY not set in .env. Exiting.")
        sys.exit(1)

    # 1. Read source sheet
    print(f"Reading source sheet: {SOURCE_SHEET_ID} | Tab: {SOURCE_TAB}", flush=True)
    source_rows = _read_sheet(SOURCE_SHEET_ID, SOURCE_TAB)
    if not source_rows:
        print("No data found in source sheet. Exiting.")
        sys.exit(1)

    header = source_rows[0]
    data_rows = source_rows[1:]
    print(f"  Source rows: {len(data_rows)}", flush=True)
    print(f"  Headers: {header}", flush=True)

    # Map header indices
    def col_idx(name_variants):
        for name in name_variants:
            for i, h in enumerate(header):
                if h.strip().lower() == name.lower():
                    return i
        return None

    idx_name      = col_idx(["Name", "Company Name"])
    idx_link      = col_idx(["Link", "Website", "Company Website", "URL"])
    idx_rating    = col_idx(["Rating"])
    idx_loc_years = col_idx(["Location/Years", "Location", "Years"])
    idx_reviews   = col_idx(["Reviews", "Review"])
    idx_include   = col_idx(["Include to CRM", "Include", "Include in CRM"])
    idx_instagram = col_idx(["Instagram"])
    idx_facebook  = col_idx(["Facebook"])
    idx_linkedin  = col_idx(["LinkedIn", "LinkedIn URL"])

    def get(row, idx, default=""):
        if idx is None or idx >= len(row):
            return default
        return row[idx].strip()

    # Build include col letter for writeback
    include_col_letter = chr(ord("A") + idx_include) if idx_include is not None else None
    existing_include_values = {}
    if idx_include is not None:
        for i, row in enumerate(data_rows):
            existing_include_values[i] = get(row, idx_include)

    # Read existing social col values for writeback (preserve non-empty)
    existing_ig   = {i: get(row, idx_instagram) for i, row in enumerate(data_rows)} if idx_instagram is not None else {}
    existing_fb   = {i: get(row, idx_facebook)  for i, row in enumerate(data_rows)} if idx_facebook  is not None else {}
    existing_li   = {i: get(row, idx_linkedin)   for i, row in enumerate(data_rows)} if idx_linkedin  is not None else {}

    # 2. Read existing CRM for dedup
    print(f"Reading CRM sheet for dedup: {CRM_SHEET_ID} | Tab: {CRM_TAB}", flush=True)
    crm_rows = _read_sheet(CRM_SHEET_ID, CRM_TAB)
    existing_companies: set[str] = set()
    existing_emails: set[str] = set()

    if crm_rows and len(crm_rows) > 1:
        crm_header = crm_rows[0]
        company_idx = next((i for i, h in enumerate(crm_header) if h.strip().lower() == "company"), 3)
        email_idx   = next((i for i, h in enumerate(crm_header) if h.strip().lower() == "email"), 4)
        for row in crm_rows[1:]:
            c = get(row, company_idx)
            e = get(row, email_idx)
            if c:
                existing_companies.add(_normalize_company(c))
            if e:
                existing_emails.add(e.lower())

    print(f"  Existing CRM companies: {len(existing_companies)} | emails: {len(existing_emails)}", flush=True)

    # 3. Process rows
    kept_rows   = []
    touch1_rows = []  # for CSV export
    writeback   = {}  # {row_idx: status}
    social_writeback = {}  # {row_idx: {instagram, facebook, linkedin}}
    stats = {"kept": 0, "rating_low": 0, "no_email": 0, "crawl_fail": 0, "dup": 0, "blank": 0}

    for row_idx, row in enumerate(data_rows):
        if not any(cell.strip() for cell in row):
            stats["blank"] += 1
            writeback[row_idx] = ""
            continue

        company   = get(row, idx_name)
        website   = get(row, idx_link)
        rating_s  = get(row, idx_rating)
        loc_years = get(row, idx_loc_years)
        reviews   = get(row, idx_reviews)
        li_url    = get(row, idx_linkedin)

        if not company and not website:
            stats["blank"] += 1
            writeback[row_idx] = ""
            continue

        # Filter: rating
        try:
            rating = float(rating_s) if rating_s else 0.0
        except ValueError:
            rating = 0.0
        if rating < MIN_RATING:
            stats["rating_low"] += 1
            writeback[row_idx] = "Rating Too Low"
            continue

        # Filter: duplicate
        if _normalize_company(company) in existing_companies:
            stats["dup"] += 1
            writeback[row_idx] = "Dropped - Duplicate"
            continue

        # Crawl website
        print(f"  [{row_idx + 2}] Crawling: {website or '(no url)'} — {company}", flush=True)
        if not website:
            stats["no_email"] += 1
            writeback[row_idx] = "No Email Found"
            continue

        email, socials = crawl_for_email_and_socials(website, api_key)
        time.sleep(FIRECRAWL_SLEEP)

        # Store found socials for writeback regardless of email result
        if socials:
            social_writeback[row_idx] = socials

        if not email:
            print(f"    -> No email found", flush=True)
            stats["no_email"] += 1
            writeback[row_idx] = "No Email Found"
            continue

        print(f"    -> {email}", flush=True)

        # Check email duplicate
        if email.lower() in existing_emails:
            stats["dup"] += 1
            writeback[row_idx] = "Dropped - Duplicate"
            continue

        # Source is Google Maps company names — no contact person, always blank
        first_name = ""
        lead = {
            "first_name": first_name,
            "company":    company,
            "reviews":    reviews,
            "loc_years":  loc_years,
        }
        touch1 = generate_cold_email_touch1(lead)

        # Use LinkedIn from source sheet or found on website
        linkedin_url = li_url or socials.get("linkedin", "")

        crm_row = [
            first_name,                         # A: First Name
            "",                                 # B: Last Name
            "",                                 # C: Title
            company,                            # D: Company
            email,                              # E: Email
            "Unverified",                       # F: Verified
            linkedin_url,                       # G: LinkedIn URL
            reviews[:200] if reviews else "",   # H: Pain Signal/Reviews
            "",                                 # I: Enrolled
            touch1["body"],                     # J: Touch 1 Message
            "",                                 # K: Touch 2 Message
            "",                                 # L: Touch 3 Message
            "",                                 # M: Touch 4 Message
            "",                                 # N: Email 1 Date
            "",                                 # O: Email 2 Date
            "",                                 # P: Email 3 Date
            "",                                 # Q: Email 4 Date
            "New",                              # R: Status
            "",                                 # S: Reply Date
        ]

        kept_rows.append(crm_row)
        touch1_rows.append({
            "Company": company,
            "Email":   email,
            "Subject": touch1["subject"],
            "Body":    touch1["body"],
        })
        writeback[row_idx] = "Added"
        stats["kept"] += 1

        # Add to dedup sets for same-run duplicates
        existing_companies.add(_normalize_company(company))
        existing_emails.add(email.lower())

    # 4. Summary
    print(f"\n--- Filter Results ---")
    print(f"  Kept (email found + qualified): {stats['kept']}")
    print(f"  Rating too low (<{MIN_RATING}):       {stats['rating_low']}")
    print(f"  No email found:                {stats['no_email']}")
    print(f"  Duplicate:                     {stats['dup']}")
    print(f"  Blank/skipped:                 {stats['blank']}")

    if not kept_rows:
        print("\nNothing to push.")

    if dry_run:
        if touch1_rows:
            print(f"\n[DRY RUN] Would push {len(touch1_rows)} leads. Sample Touch 1 emails:")
            for t in touch1_rows[:3]:
                print(f"\n  Company: {t['Company']} | Email: {t['Email']}")
                print(f"  Subject: {t['Subject']}")
                body_preview = t["Body"].replace("\n", " ")[:200]
                print(f"  Body: {body_preview}...")
        return

    # 5. Append to CRM
    if kept_rows:
        print(f"\nAppending {len(kept_rows)} rows to Cold Email CRM...", flush=True)
        success = _append_rows(CRM_SHEET_ID, CRM_TAB, kept_rows)
        if success:
            print(f"Done. {len(kept_rows)} leads added to CRM.")
        else:
            print("Failed to write to CRM sheet.")
            sys.exit(1)

    # 6. Save Touch 1 emails to CSV
    if touch1_rows:
        data_dir = Path(__file__).resolve().parent / "data"
        data_dir.mkdir(exist_ok=True)
        csv_path = data_dir / f"cold_email_touch1_{date.today().isoformat()}.csv"
        with open(csv_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=["Company", "Email", "Subject", "Body"])
            writer.writeheader()
            writer.writerows(touch1_rows)
        print(f"\nTouch 1 emails saved to: {csv_path}", flush=True)

    # 7. Write back to source sheet
    if include_col_letter:
        print(f"\nWriting status back to source sheet column {include_col_letter}...", flush=True)
        col_values = []
        for i in range(len(data_rows)):
            existing = existing_include_values.get(i, "")
            new_val  = writeback.get(i, "")
            if new_val == "Added":
                col_values.append(new_val)
            elif existing:
                col_values.append(existing)
            else:
                col_values.append(new_val)
        _update_column(SOURCE_SHEET_ID, SOURCE_TAB, include_col_letter, 2, col_values)
        print("  Done.", flush=True)
    else:
        print("\n  WARNING: 'Include to CRM' column not found — skipping writeback.", flush=True)

    # 8. Write back discovered social links to source sheet (preserve existing)
    social_col_map = []
    if idx_instagram is not None:
        social_col_map.append((chr(ord("A") + idx_instagram), "instagram", existing_ig))
    if idx_facebook is not None:
        social_col_map.append((chr(ord("A") + idx_facebook), "facebook", existing_fb))
    if idx_linkedin is not None:
        social_col_map.append((chr(ord("A") + idx_linkedin), "linkedin", existing_li))

    if social_col_map and social_writeback:
        print("\nWriting discovered social links back to source sheet...", flush=True)
        for col_letter, platform, existing_vals in social_col_map:
            col_values = []
            for i in range(len(data_rows)):
                existing = existing_vals.get(i, "")
                found    = social_writeback.get(i, {}).get(platform, "")
                col_values.append(existing if existing else found)
            _update_column(SOURCE_SHEET_ID, SOURCE_TAB, col_letter, 2, col_values)
        print("  Done.", flush=True)


if __name__ == "__main__":
    main()
