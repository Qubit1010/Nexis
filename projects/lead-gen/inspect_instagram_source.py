"""Inspect the Instagram source sheet — show header, sample rows from
different positions, and a breakdown of what's being rejected so we can
diagnose whether filters are too aggressive."""

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

SOURCE_SHEET_ID = "1kOEaNhwD3fsbpAJM6l6-dR0z6n06xgJyyWr3EHKmzyg"
SOURCE_TAB      = "Raw"
CRM_SHEET_ID    = "1xql6icDspoJxzP1_vIQpjqBWK1RYQBN1C8N28OzkGs8"
CRM_TAB         = "Leads"

# Re-use the same gws-finder pattern as instagram_push.py
def _find_gws():
    npm_dir = Path(os.environ.get("APPDATA", "")) / "npm"
    for js_name in ("run.js", "run-gws.js"):
        gws_js = npm_dir / "node_modules" / "@googleworkspace" / "cli" / js_name
        if gws_js.exists():
            for candidate in [
                npm_dir / "node.exe",
                Path(os.environ.get("ProgramFiles", "C:\\Program Files")) / "nodejs" / "node.exe",
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


def _run_gws(args):
    cmd = _GWS_CMD + args
    result = subprocess.run(
        cmd, capture_output=True, text=True, timeout=120,
        shell=_GWS_SHELL, encoding="utf-8", errors="replace"
    )
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or "gws error")
    return json.loads(result.stdout) if result.stdout.strip() else {}


def read_sheet(sheet_id, tab):
    return _run_gws([
        "sheets", "spreadsheets", "values", "get",
        "--params", json.dumps({"spreadsheetId": sheet_id, "range": tab})
    ]).get("values", [])


if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

# 1. Inspect source sheet
print("=" * 80)
print("SOURCE SHEET")
print("=" * 80)
rows = read_sheet(SOURCE_SHEET_ID, SOURCE_TAB)
print(f"Total rows (incl header): {len(rows)}")
print(f"Header columns: {rows[0]}")
print(f"Number of columns: {len(rows[0])}")
print()

print("--- 10 rows from MIDDLE of sheet (rows 400-409) ---")
for i, row in enumerate(rows[400:410], 400):
    print(f"\nRow {i}: ({len(row)} cells)")
    for j, cell in enumerate(row):
        header = rows[0][j] if j < len(rows[0]) else f"col{j}"
        print(f"  [{j}] {header}: {cell[:120]!r}")

print("\n--- 10 rows from END (last 10) ---")
for i, row in enumerate(rows[-10:], len(rows) - 10):
    print(f"\nRow {i}: ({len(row)} cells)")
    for j, cell in enumerate(row):
        header = rows[0][j] if j < len(rows[0]) else f"col{j}"
        print(f"  [{j}] {header}: {cell[:120]!r}")

# 2. Read CRM and build dedup set
print("\n" + "=" * 80)
print("CRM SHEET")
print("=" * 80)
crm_rows = read_sheet(CRM_SHEET_ID, CRM_TAB)
print(f"Total CRM rows (incl header): {len(crm_rows)}")
print(f"CRM header: {crm_rows[0]}")

# Build dedup sets (URL idx 4, username idx 1)
existing_urls = set()
existing_usernames = set()
for row in crm_rows[1:]:
    if len(row) > 4 and row[4].strip():
        existing_urls.add(row[4].strip().lower().rstrip("/").split("?")[0])
    if len(row) > 1 and row[1].strip():
        existing_usernames.add(row[1].strip().lower().lstrip("@"))

print(f"CRM URLs: {len(existing_urls)} | Usernames: {len(existing_usernames)}")

# 3. Walk through source rows that are NOT duplicates, classify them
print("\n" + "=" * 80)
print("CLASSIFICATION OF NON-DUPLICATE SOURCE ROWS")
print("=" * 80)

INVALID_URL_PATTERNS = ["/popular/", "/explore/", "/topics/", "/tags/",
                         "/search/", "/reels/", "/p/"]

def parse_followers(raw):
    if not raw:
        return None
    cleaned = raw.strip().lower().replace(",", "").replace("+", "").replace(" ", "")
    if cleaned.endswith("k"):
        try:
            return int(float(cleaned[:-1]) * 1000)
        except ValueError:
            return None
    if cleaned.endswith("m"):
        try:
            return int(float(cleaned[:-1]) * 1_000_000)
        except ValueError:
            return None
    try:
        return int(float(cleaned))
    except ValueError:
        return None


# Assume header order: Name, Link/URL, Followers, Bio, Title — based on prior output
def get_col_idx(header_row, candidates):
    for i, h in enumerate(header_row):
        if h.strip().lower() in candidates:
            return i
    return None

header = rows[0]
url_idx       = get_col_idx(header, ("link", "instagram url", "instagram", "url", "profile url"))
followers_idx = get_col_idx(header, ("followers", "follower count"))
name_idx      = get_col_idx(header, ("name", "full name"))
bio_idx       = get_col_idx(header, ("note", "bio", "notes"))
title_idx     = get_col_idx(header, ("location/designation", "designation", "title", "role", "position"))

print(f"Resolved column indices:")
print(f"  name={name_idx}  url={url_idx}  followers={followers_idx}  bio={bio_idx}  title={title_idx}")
print()

new_rows = []
buckets = {"invalid_url": [], "bad_followers_url": [], "bad_followers_text": [],
           "low_followers": [], "would_keep": []}

for i, row in enumerate(rows[1:], 1):
    if not any(c.strip() for c in row):
        continue
    url = row[url_idx].strip() if url_idx is not None and url_idx < len(row) else ""
    followers_raw = row[followers_idx].strip() if followers_idx is not None and followers_idx < len(row) else ""
    name = row[name_idx].strip() if name_idx is not None and name_idx < len(row) else ""

    # Dedup
    url_norm = url.lower().rstrip("/").split("?")[0]
    if url_norm and url_norm in existing_urls:
        continue
    # Also dedup by username extracted from URL
    handle = ""
    if url_norm.startswith("https://www.instagram.com/") or url_norm.startswith("https://instagram.com/"):
        handle = url_norm.split("instagram.com/")[-1].split("/")[0]
    if handle and handle in existing_usernames:
        continue

    # Classify
    url_lower = url.lower()
    if any(p in url_lower for p in INVALID_URL_PATTERNS):
        buckets["invalid_url"].append((i, name, url, followers_raw))
        continue

    count = parse_followers(followers_raw)
    if count is None:
        if followers_raw.startswith("http"):
            buckets["bad_followers_url"].append((i, name, url, followers_raw))
        else:
            buckets["bad_followers_text"].append((i, name, url, followers_raw))
        continue
    if count < 100:
        buckets["low_followers"].append((i, name, url, followers_raw))
        continue
    buckets["would_keep"].append((i, name, url, followers_raw))


for bucket, items in buckets.items():
    print(f"\n--- {bucket}: {len(items)} rows ---")
    for row_num, name, url, foll in items[:8]:
        print(f"  R{row_num}: {name[:50]!r} | url={url[:80]!r} | followers={foll[:40]!r}")
    if len(items) > 8:
        print(f"  ... and {len(items) - 8} more")
