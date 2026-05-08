import json, subprocess, os

CRM_SHEET_ID = "1xql6icDspoJxzP1_vIQpjqBWK1RYQBN1C8N28OzkGs8"
npm_dir = os.path.join(os.environ.get("APPDATA", ""), "npm")
gws_cmd = os.path.join(npm_dir, "gws.cmd")

result = subprocess.run(
    [gws_cmd, "sheets", "spreadsheets", "values", "get",
     "--params", json.dumps({"spreadsheetId": CRM_SHEET_ID, "range": "Leads"})],
    capture_output=True, text=True, timeout=60, shell=True, encoding="utf-8", errors="replace"
)
data = json.loads(result.stdout)
rows = data.get("values", [])

print("HEADERS:", rows[0])
print(f"\nTotal rows: {len(rows) - 1}")
print("\nSAMPLE ROWS (2-12):")
for i, row in enumerate(rows[1:12], 2):
    name = row[0][:50] if len(row) > 0 else ""
    uname = row[1] if len(row) > 1 else ""
    url = row[4][:60] if len(row) > 4 else ""
    date = row[-1] if row else ""
    print(f"  Row {i:>4} | Name: {name:<52} | Username: {uname:<25} | Date: {date}")

# Count rows with empty username
empty_uname = sum(1 for r in rows[1:] if len(r) < 2 or not r[1].strip())
print(f"\nRows with empty Username: {empty_uname}")

# Show duplicates by extracting username from URL
import re
def extract_handle(url):
    m = re.match(r"https?://[^/]*instagram\.com/([^/?#]+)", url.strip().lower())
    return m.group(1).rstrip("/") if m else ""

seen = {}
dups = []
for i, row in enumerate(rows[1:], 2):
    uname = row[1].strip().lower().lstrip("@") if len(row) > 1 else ""
    url = row[4].strip() if len(row) > 4 else ""
    name = row[0].strip() if len(row) > 0 else ""

    handle = uname or extract_handle(url) or extract_handle(name)
    if not handle:
        continue
    if handle in seen:
        dups.append((i, handle, seen[handle]))
    else:
        seen[handle] = i

print(f"\nDuplicates by extracted handle: {len(dups)}")
for row_idx, handle, first_row in dups[:20]:
    print(f"  Row {row_idx:>4}: @{handle:<40} (first at row {first_row})")
if len(dups) > 20:
    print(f"  ... and {len(dups) - 20} more")
