"""Phase 0: merge raw directory leads from multiple tabs of ONE Google Sheet into the Main tab,
dropping duplicates across tabs AND against rows already in Main. Idempotent -- re-running appends
nothing new.

Aleem hands leads from several directories (Google Maps, Clutch, DesignRush, ...) as one tab each in
the same sheet. Each directory exports different headers, so HEADER_ALIASES is a superset that
normalizes them all to the Main schema. Dedup reuses leads-to-crm's own identity primitives
(_domain, _digits): website domain first, then phone, then normalized company-name + city.

Usage:
  python merge_leads.py --sheet-id <id> --main-tab Main [--source-tabs "Google Maps,Clutch,DesignRush"]
  # default source tabs = every tab except the Main tab
"""

import argparse
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "leads-to-crm" / "scripts"))
import sheets  # noqa: E402
from channels import _digits, _domain  # noqa: E402  reuse the exact dedup primitives
from read_batch import _clean_phone, _strip_bullet  # noqa: E402

MAIN_COLUMNS = [
    "Company Name", "Category", "Rating", "Experience", "Location", "Number", "Note",
    "Website Link", "Instagram Link", "LinkedIn Link", "Facebook Link",
    "Founder", "Founder Instagram Link", "Founder LinkedIn Link", "Founder Facebook Link",
    "Social Search Status",
]

# Superset covering the common directory exports. Maps a live header (lowercased) -> normalized key.
HEADER_ALIASES = {
    "company name": "company", "company": "company", "business name": "company", "name": "company",
    "agency": "company", "agency name": "company", "business": "company",
    "category": "category", "industry": "category", "services": "category", "service": "category",
    "specialization": "category", "tagline": "category",
    "rating": "rating", "star rating": "rating", "reviews": "rating",
    "experience": "experience",
    "location": "location", "address": "location", "city": "location", "region": "location",
    "headquarters": "location", "hq": "location", "based in": "location",
    "number": "phone", "phone": "phone", "phone number": "phone", "tel": "phone", "contact number": "phone",
    "note": "note", "notes": "note", "description": "note", "about": "note", "summary": "note", "bio": "note",
    "website link": "website", "website": "website", "url": "website", "site": "website", "web": "website",
    "company website": "website", "visit website": "website",
    "instagram link": "instagram", "instagram": "instagram",
    "linkedin link": "linkedin", "linkedin": "linkedin",
    "facebook link": "facebook", "facebook": "facebook",
}

# Main header name -> normalized rec key (columns not listed are left blank: founder*, status).
COL_TO_KEY = {
    "Company Name": "company", "Category": "category", "Rating": "rating", "Experience": "experience",
    "Location": "location", "Number": "phone", "Note": "note", "Website Link": "website",
    "Instagram Link": "instagram", "LinkedIn Link": "linkedin", "Facebook Link": "facebook",
}

_LEGAL = re.compile(r"\b(llc|inc|ltd|co|corp|llp|plc|gmbh|pvt|private limited|limited)\b\.?", re.I)


def _norm_name(name):
    n = re.sub(r"&", " and ", (name or "").lower())
    n = _LEGAL.sub(" ", n)
    n = re.sub(r"[^a-z0-9]+", " ", n)
    return re.sub(r"\s+", " ", n).strip()


def _norm_city(loc):
    first = (loc or "").split(",")[0]
    return re.sub(r"[^a-z0-9]+", " ", first.lower()).strip()


def dedup_key(rec):
    """Website domain > phone > normalized company+city. Same tiered identity leads-to-crm uses.
    Phone uses the last 10 digits so a US number with/without the +1 country code still matches
    (leads are US-focused, South-Asia already excluded upstream)."""
    dom = _domain(rec.get("website", ""))
    if dom:
        return "site:" + dom
    ph = _digits(rec.get("phone", ""))
    if len(ph) >= 10:
        return "phone:" + ph[-10:]
    if len(ph) >= 7:
        return "phone:" + ph
    return "name:" + _norm_name(rec.get("company", "")) + "|" + _norm_city(rec.get("location", "") or rec.get("experience", ""))


def build_col_map(header):
    col_map = {}
    for i, h in enumerate(header):
        key = HEADER_ALIASES.get(h.strip().lower())
        if key and key not in col_map:  # first header wins if a tab has duplicate-meaning columns
            col_map[key] = i
    return col_map


def _cell(row, col_map, key):
    idx = col_map.get(key)
    return row[idx].strip() if idx is not None and idx < len(row) else ""


def normalize_row(row, col_map):
    company = _cell(row, col_map, "company")
    if not company:
        return None
    return {
        "company": company,
        "category": _strip_bullet(_cell(row, col_map, "category")),
        "rating": _cell(row, col_map, "rating"),
        "experience": _cell(row, col_map, "experience"),
        "location": _cell(row, col_map, "location"),
        "phone": _clean_phone(_cell(row, col_map, "phone")),
        "note": _cell(row, col_map, "note"),
        "website": _cell(row, col_map, "website"),
        "instagram": _cell(row, col_map, "instagram"),
        "linkedin": _cell(row, col_map, "linkedin"),
        "facebook": _cell(row, col_map, "facebook"),
    }


def source_tab_titles(sheet_id, main_tab, requested):
    if requested:
        return [t.strip() for t in requested if t.strip() and t.strip().lower() != main_tab.lower()]
    meta = sheets.get_metadata(sheet_id)
    titles = [sh.get("properties", {}).get("title", "") for sh in meta.get("sheets", [])]
    return [t for t in titles if t and t.strip().lower() != main_tab.lower()]


def ensure_main_header(sheet_id, main_tab):
    """Read Main's header; if empty, write the full MAIN_COLUMNS; if partial, append any missing.
    Returns the live header list."""
    rows = sheets.read_values(sheet_id, f"{main_tab}!1:1")
    header = rows[0] if rows else []
    if not header:
        sheets.update_range(sheet_id, f"{main_tab}!A1", [MAIN_COLUMNS])
        return list(MAIN_COLUMNS)
    for name in MAIN_COLUMNS:
        if not any(h.strip().lower() == name.lower() for h in header):
            col = sheets.col_letter(len(header))
            sheets.update_range(sheet_id, f"{main_tab}!{col}1", [[name]])
            header.append(name)
    return header


def existing_keys(sheet_id, main_tab):
    rows = sheets.read_values(sheet_id, main_tab)
    if not rows:
        return set()
    col_map = build_col_map(rows[0])
    keys = set()
    for row in rows[1:]:
        rec = normalize_row(row, col_map)
        if rec:
            keys.add(dedup_key(rec))
    return keys


def merge(sheet_id, main_tab, requested_tabs):
    header = ensure_main_header(sheet_id, main_tab)
    seen = existing_keys(sheet_id, main_tab)
    tabs = source_tab_titles(sheet_id, main_tab, requested_tabs)

    per_tab, dropped, uniques = {}, 0, []
    for tab in tabs:
        rows = sheets.read_values(sheet_id, tab)
        if not rows:
            per_tab[tab] = 0
            continue
        col_map = build_col_map(rows[0])
        count = 0
        for row in rows[1:]:
            rec = normalize_row(row, col_map)
            if not rec:
                continue
            count += 1
            key = dedup_key(rec)
            if key in seen:
                dropped += 1
                continue
            seen.add(key)
            rec["_source"] = tab
            uniques.append(rec)
        per_tab[tab] = count

    if uniques:
        out_rows = [[str(rec.get(COL_TO_KEY.get(h, ""), "") or "") for h in header] for rec in uniques]
        if not sheets.append_rows(sheet_id, main_tab, out_rows):
            raise RuntimeError(f"Append failed for {sheet_id} [{main_tab}].")
    return {"tabs": per_tab, "dropped": dropped, "appended": len(uniques),
            "appended_by_tab": _count_by(uniques)}


def _count_by(uniques):
    out = {}
    for rec in uniques:
        out[rec["_source"]] = out.get(rec["_source"], 0) + 1
    return out


def demo():
    """Self-check: dedup keying + across-tab dedup, no sheets I/O."""
    a = {"company": "Acme, LLC", "website": "https://www.acme.com/home", "phone": "+1 619 555 1000", "location": "San Diego, CA"}
    b = {"company": "Acme LLC", "website": "http://acme.com", "phone": "", "location": "San Diego, CA, USA"}  # same domain
    c = {"company": "Bob HVAC", "website": "", "phone": "+1 (415) 555-2000", "location": "SF"}
    d = {"company": "Bob HVAC", "website": "", "phone": "415.555.2000", "location": "SF"}  # same phone
    e = {"company": "Zeta Studio", "website": "", "phone": "", "location": "Austin, TX"}
    assert dedup_key(a) == dedup_key(b) == "site:acme.com", (dedup_key(a), dedup_key(b))
    assert dedup_key(c) == dedup_key(d) == "phone:4155552000", (dedup_key(c), dedup_key(d))  # +1 tolerated
    assert dedup_key(e) == "name:zeta studio|austin", dedup_key(e)
    # across-tab dedup: 5 records, 2 collisions -> 3 uniques
    seen, uniq = set(), []
    for rec in (a, b, c, d, e):
        k = dedup_key(rec)
        if k not in seen:
            seen.add(k)
            uniq.append(rec)
    assert len(uniq) == 3, len(uniq)
    # header row-building leaves founder/status blank
    row = [str({"Company Name": "Acme"}.get(h, "")) for h in MAIN_COLUMNS]
    assert row[MAIN_COLUMNS.index("Founder")] == "" and row[MAIN_COLUMNS.index("Social Search Status")] == ""
    print("merge_leads self-check OK")


def main():
    p = argparse.ArgumentParser(description="Merge + dedup directory-lead tabs into the Main tab.")
    p.add_argument("--sheet-id")
    p.add_argument("--main-tab", default="Main")
    p.add_argument("--source-tabs", default="", help="Comma list; default = all tabs except Main.")
    p.add_argument("--selftest", action="store_true")
    args = p.parse_args()

    if args.selftest:
        demo()
        return
    if not args.sheet_id:
        raise SystemExit("--sheet-id is required (or pass --selftest)")

    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")

    requested = [t for t in args.source_tabs.split(",")] if args.source_tabs else None
    result = merge(args.sheet_id, args.main_tab, requested)
    print(f"Read per tab: {result['tabs']}")
    print(f"Duplicates dropped: {result['dropped']}")
    print(f"Uniques appended: {result['appended']}  {result['appended_by_tab']}")


if __name__ == "__main__":
    main()
