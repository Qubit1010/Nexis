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
import score  # noqa: E402  reuse its rating+review blend for the post-merge Main sort

MAIN_COLUMNS = [
    "Company Name", "Category", "Rating", "Reviews", "Experience", "Location", "Number", "Note",
    "Website Link", "Link", "Budget Range", "Slogan", "Instagram Link", "LinkedIn Link", "Facebook Link",
    "Founder", "Founder Instagram Link", "Founder LinkedIn Link", "Founder Facebook Link",
    "Social Search Status",
]

# Superset covering the common directory exports. Maps a live header (lowercased) -> normalized key.
HEADER_ALIASES = {
    "company name": "company", "company": "company", "business name": "company", "name": "company",
    "agency": "company", "agency name": "company", "business": "company",
    "category": "category", "industry": "category", "services": "category", "service": "category",
    "specialization": "category", "tagline": "category",
    "rating": "rating", "star rating": "rating",
    "reviews": "reviews", "review count": "reviews", "number of reviews": "reviews",
    "experience": "experience",
    "location": "location", "address": "location", "city": "location", "region": "location",
    "headquarters": "location", "hq": "location", "based in": "location",
    "number": "phone", "phone": "phone", "phone number": "phone", "tel": "phone", "contact number": "phone",
    "note": "note", "notes": "note", "description": "note", "about": "note", "summary": "note", "bio": "note",
    "website link": "website", "website": "website", "url": "website", "site": "website", "web": "website",
    "company website": "website", "visit website": "website",
    "link": "link", "profile link": "link", "profile url": "link",
    "budget range": "budget", "budget": "budget",
    "slogan": "slogan",
    "instagram link": "instagram", "instagram": "instagram",
    "linkedin link": "linkedin", "linkedin": "linkedin",
    "facebook link": "facebook", "facebook": "facebook",
}

# Main header name -> normalized rec key (columns not listed are left blank: founder*, status).
COL_TO_KEY = {
    "Company Name": "company", "Category": "category", "Rating": "rating", "Reviews": "reviews",
    "Experience": "experience", "Location": "location", "Number": "phone", "Note": "note",
    "Website Link": "website", "Link": "link", "Budget Range": "budget", "Slogan": "slogan",
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


def _clean_reviews(val):
    """'98\\n   reviews' / '(10 reviews)' / '19 Reviews' -> a clean 'N reviews' string,
    matching the format already on Main. Blank stays blank (never invented)."""
    n = score._num(val)
    return f"{int(n)} reviews" if n is not None else ""


def _clean_location(val):
    """A location with no letters isn't one. DesignRush's scrape leaks a numeric artifact
    ('-92', '-6') into the Location column on 479/536 rows; blank it rather than write junk
    onto Main, where it would poison the name+city dedup key and any later geo filter."""
    v = (val or "").strip()
    return v if re.search(r"[A-Za-z]", v) else ""


def normalize_row(row, col_map):
    company = _cell(row, col_map, "company")
    if not company:
        return None
    return {
        "company": company,
        "category": _strip_bullet(_cell(row, col_map, "category")),
        "rating": _cell(row, col_map, "rating"),
        "reviews": _clean_reviews(_cell(row, col_map, "reviews")),
        "experience": _cell(row, col_map, "experience"),
        "location": _clean_location(_cell(row, col_map, "location")),
        "phone": _clean_phone(_cell(row, col_map, "phone")),
        "note": _cell(row, col_map, "note"),
        "website": _cell(row, col_map, "website"),
        "link": _cell(row, col_map, "link"),
        "budget": _cell(row, col_map, "budget"),
        "slogan": _cell(row, col_map, "slogan"),
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
    """(tiered identity keys, normalized company names) for everything already on Main."""
    rows = sheets.read_values(sheet_id, main_tab)
    if not rows:
        return set(), set()
    col_map = build_col_map(rows[0])
    keys, names = set(), set()
    for row in rows[1:]:
        rec = normalize_row(row, col_map)
        if rec:
            keys.add(dedup_key(rec))
            names.add(_norm_name(rec["company"]))
    return keys, names


def merge(sheet_id, main_tab, requested_tabs, per_tab_limit=None):
    """Append new uniques from each source tab to Main, best-scoring first.

    Duplicates are caught on the tiered identity key OR the normalized company name. The name
    tier is load-bearing for directory tabs: Clutch and Sortlist export no website and no usable
    city (Clutch stamps every row 'World Wide'), so their key collapses to name+city and matches
    nothing on Main. Measured on this batch, key-only caught 110 duplicates and missed 266 that
    are the same agency listed under a different directory's city string.
    """
    header = ensure_main_header(sheet_id, main_tab)
    seen, seen_names = existing_keys(sheet_id, main_tab)
    tabs = source_tab_titles(sheet_id, main_tab, requested_tabs)

    per_tab, dropped, uniques = {}, [], []
    for tab in tabs:
        rows = sheets.read_values(sheet_id, tab)
        if not rows:
            per_tab[tab] = 0
            continue
        col_map = build_col_map(rows[0])
        recs = [r for r in (normalize_row(row, col_map) for row in rows[1:]) if r]
        # Best-first, so a per-tab quota keeps the strongest leads, not the top of the scrape.
        # Ranking is only meaningful WITHIN a directory -- DesignRush exports no review counts at
        # all, so its rows would lose every cross-directory comparison on volume alone.
        recs.sort(key=lambda r: score.score_one(r["rating"], r["reviews"]), reverse=True)
        kept = 0
        for rec in recs:
            if per_tab_limit is not None and kept >= per_tab_limit:
                break
            key, name = dedup_key(rec), _norm_name(rec["company"])
            matched = "website/phone/city" if key in seen else ("company name" if name in seen_names else "")
            if matched:
                dropped.append((tab, rec, matched))
                continue
            seen.add(key)
            seen_names.add(name)
            rec["_source"] = tab
            uniques.append(rec)
            kept += 1
        per_tab[tab] = len(recs)

    if uniques:
        out_rows = [[str(rec.get(COL_TO_KEY.get(h, ""), "") or "") for h in header] for rec in uniques]
        # batch_size=5 for the same measured reason sort_main_by_score uses it: Note runs to ~3.9K
        # chars/row and a bigger batch blows past Windows' ~32K CreateProcess limit.
        if not sheets.append_rows(sheet_id, main_tab, out_rows, batch_size=5):
            raise RuntimeError(f"Append failed for {sheet_id} [{main_tab}].")
    return {"tabs": per_tab, "dropped": len(dropped), "dropped_rows": dropped,
            "appended": len(uniques), "appended_by_tab": _count_by(uniques)}


def log_duplicates(sheet_id, dup_tab, dropped):
    """Append each dropped duplicate to the Duplicates tab with what it matched on. Dropping
    leads on a name heuristic is lossy, so it stays auditable -- the tab and this schema
    (Source Tab / Matched Existing Lead / Matched On / ...) already existed in the sheet."""
    if not dropped:
        return 0
    rows = sheets.read_values(sheet_id, f"{dup_tab}!1:1")
    header = rows[0] if rows and rows[0] else ["Source Tab", "Matched Existing Lead", "Matched On"] + MAIN_COLUMNS
    out = []
    for tab, rec, matched in dropped:
        lead = {"Source Tab": tab, "Matched Existing Lead": rec["company"], "Matched On": matched}
        out.append([str(lead.get(h) or rec.get(COL_TO_KEY.get(h, ""), "") or "") for h in header])
    if not sheets.append_rows(sheet_id, dup_tab, out, batch_size=5):
        raise RuntimeError(f"Duplicate-log append failed for {sheet_id} [{dup_tab}].")
    return len(out)


def _count_by(uniques):
    out = {}
    for rec in uniques:
        out[rec["_source"]] = out.get(rec["_source"], 0) + 1
    return out


def rank_rows(header, data_rows):
    """Sort Main's data rows by score.py's rating+review blend, best first.
    Pads short rows (Sheets API drops trailing blank cells)."""
    ri = sheets.header_index(header, ["rating"])
    vi = sheets.header_index(header, ["reviews"])
    ncols = len(header)
    padded = [r + [""] * (ncols - len(r)) for r in data_rows]
    scored = [(score.score_one(r[ri] if ri is not None else "", r[vi] if vi is not None else ""), r)
              for r in padded]
    scored.sort(key=lambda t: t[0], reverse=True)
    return [r for _, r in scored]


def sort_main_by_score(sheet_id, main_tab):
    rows = sheets.read_values(sheet_id, main_tab)
    if len(rows) < 3:
        return 0
    header, data = rows[0], rows[1:]
    sorted_rows = rank_rows(header, data)
    # batch_size=5: Main's Note column runs up to ~3.9K chars/row, and update_rows' default
    # 25-row batch blew past Windows' ~32K CreateProcess command-line limit (measured live).
    if not sheets.update_rows(sheet_id, main_tab, 2, sorted_rows, len(header), batch_size=5):
        raise RuntimeError(f"Sort write failed for {sheet_id} [{main_tab}].")
    return len(sorted_rows)


def _richness(row, header):
    """How resolved a Main row is, richest first: Founder > Social Search Status >
    any company social > website > most filled cells overall (generic tiebreak)."""
    idx = {name.lower(): i for i, name in enumerate(header)}

    def has(col):
        i = idx.get(col.lower())
        return bool(i is not None and i < len(row) and row[i].strip())

    return (
        has("Founder"), has("Social Search Status"),
        has("Instagram Link") or has("LinkedIn Link") or has("Facebook Link"),
        has("Website Link"), sum(1 for c in row if c.strip()),
    )


def find_link_duplicates(header, indexed_rows):
    """Group (row_num, row) pairs by exact Link match -- the same directory profile
    URL merged into Main more than once across sessions is definitionally the same
    company. For each group of 2+, keep the richest row and return the rest's row
    numbers to delete."""
    li = sheets.header_index(header, ["link"])
    if li is None:
        return []
    groups = {}
    for row_num, row in indexed_rows:
        link = row[li].strip().rstrip("/") if li < len(row) else ""
        if link:
            groups.setdefault(link, []).append((row_num, row))
    to_delete = []
    for occurrences in groups.values():
        if len(occurrences) < 2:
            continue
        occurrences.sort(key=lambda t: _richness(t[1], header), reverse=True)
        to_delete.extend(n for n, _ in occurrences[1:])
    return sorted(to_delete)


def dedupe_main_by_link(sheet_id, main_tab):
    rows = sheets.read_values(sheet_id, main_tab)
    if len(rows) < 3:
        return 0
    header, data = rows[0], rows[1:]
    indexed = [(i, r + [""] * (len(header) - len(r))) for i, r in enumerate(data, start=2)]
    to_delete = find_link_duplicates(header, indexed)
    if to_delete:
        gid = sheets.get_gid(sheet_id, main_tab)
        sheets.delete_rows(sheet_id, gid, to_delete)
    return len(to_delete)


_SLUG_RE = re.compile(r"/(?:company|profile|agency(?:/profile)?)/([^/?#]+)")


def slug_to_name(url):
    """Best-effort company name from a directory profile URL slug, for source rows
    whose own Company Name cell is blank. Never invents one with no URL to derive from."""
    m = _SLUG_RE.search(url or "")
    if not m:
        return ""
    return " ".join(w.capitalize() for w in m.group(1).split("-") if w)


def backfill_company_names(sheet_id, tab):
    """Fill blank Company Name cells from their row's Link slug, in place. Rows where
    Link is also blank are left alone -- nothing to derive a name from."""
    rows = sheets.read_values(sheet_id, tab)
    if not rows:
        return {"filled": 0, "unrecoverable": 0}
    header, data = rows[0], rows[1:]
    ci = sheets.header_index(header, ["company name", "company"])
    li = sheets.header_index(header, ["link"])
    if ci is None or li is None:
        return {"filled": 0, "unrecoverable": 0}
    col = sheets.col_letter(ci)
    filled = unrecoverable = 0
    for i, row in enumerate(data, start=2):
        company = row[ci].strip() if ci < len(row) else ""
        if company:
            continue
        name = slug_to_name(row[li].strip() if li < len(row) else "")
        if name:
            sheets.update_range(sheet_id, f"{tab}!{col}{i}", [[name]])
            filled += 1
        else:
            unrecoverable += 1
    return {"filled": filled, "unrecoverable": unrecoverable}


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
    # reviews cleaning: messy directory formats -> a clean 'N reviews' string
    assert _clean_reviews("98\n                        \n                            reviews") == "98 reviews"
    assert _clean_reviews("(10 reviews)") == "10 reviews"
    assert _clean_reviews("19 Reviews") == "19 reviews"
    assert _clean_reviews("") == ""
    # rating and reviews no longer collide on the same alias key (the bug this fixes)
    header = ["Link", "Company Name", "Rating", "Reviews", "Website Link"]
    col_map = build_col_map(header)
    rec = normalize_row(["https://x.co/p", "Acme", "4.8", "52 Reviews", "https://acme.com"], col_map)
    assert rec["rating"] == "4.8" and rec["reviews"] == "52 reviews" and rec["link"] == "https://x.co/p", rec
    # rank_rows: a proven 4.8/92 outranks an untested 5.0/2 and a lower-volume 4.9/40 (score.py's own rule)
    ranked = rank_rows(
        ["Company Name", "Rating", "Reviews"],
        [["Thin", "5.0", "2"], ["Established", "4.8", "92"], ["Solid", "4.9", "40"]],
    )
    assert [r[0] for r in ranked] == ["Established", "Solid", "Thin"], ranked
    # find_link_duplicates: same Link twice -> delete the blank one, keep the resolved one
    dup_header = ["Link", "Company Name", "Website Link", "Founder", "Social Search Status"]
    dupes = find_link_duplicates(dup_header, [
        (2, ["https://x.co/a", "Acme", "", "", ""]),
        (5, ["https://x.co/a", "Acme", "https://acme.com", "Jane Doe", "Resolved"]),
        (7, ["https://x.co/b", "Solo", "", "", ""]),
    ])
    assert dupes == [2], dupes
    # slug_to_name: derive from a directory profile URL, never invent with no URL
    assert slug_to_name("https://www.goodfirms.co/company/app-makers-la") == "App Makers La"
    assert slug_to_name("https://clutch.co/profile/bop-design") == "Bop Design"
    assert slug_to_name("https://example.com/not-a-directory-link") == ""
    assert slug_to_name("") == ""
    # location junk: a value with no letters is not a location (DesignRush's '-92'), blank it
    assert _clean_location("-92") == "" and _clean_location("New Jersey") == "New Jersey"
    assert _clean_location("") == ""
    # name-tier dedup catches what the key tier structurally cannot: Clutch stamps every row
    # 'World Wide' and exports no website, so the same agency under two directories keeps two
    # different keys but ONE normalized name.
    clutch = {"company": "League Design Agency", "website": "", "phone": "", "location": "World Wide"}
    other = {"company": "League Design Agency", "website": "", "phone": "", "location": "Warsaw, Poland"}
    assert dedup_key(clutch) != dedup_key(other), "city differs, so the key tier misses it"
    assert _norm_name(clutch["company"]) == _norm_name(other["company"]), "name tier catches it"
    # per-tab quota keeps the BEST rows, not the first ones scraped
    recs = [{"company": f"C{i}", "rating": r, "reviews": v}
            for i, (r, v) in enumerate([("4.0", "5"), ("5.0", "120"), ("4.9", "80")])]
    recs.sort(key=lambda r: score.score_one(r["rating"], r["reviews"]), reverse=True)
    assert [r["company"] for r in recs[:2]] == ["C1", "C2"], recs
    print("merge_leads self-check OK")


def main():
    p = argparse.ArgumentParser(description="Merge + dedup directory-lead tabs into the Main tab.")
    p.add_argument("--sheet-id")
    p.add_argument("--main-tab", default="Main")
    p.add_argument("--source-tabs", default="", help="Comma list; default = all tabs except Main.")
    p.add_argument("--per-tab-limit", type=int, default=None,
                   help="Keep at most N new uniques per source tab, best-scoring first (e.g. 50 x 4 tabs = 200).")
    p.add_argument("--dup-tab", default="", help="Tab name: log every dropped duplicate there with what it matched on.")
    p.add_argument("--sort", action="store_true", help="After merging, sort all of Main by the rating+review score (best first).")
    p.add_argument("--dedupe-existing", action="store_true",
                    help="Collapse rows already in Main that share the same Link (accumulated across past sessions), keeping the most-resolved row per group.")
    p.add_argument("--backfill-names", default="", help="Tab name: fill blank Company Name cells from their Link slug, in place.")
    p.add_argument("--selftest", action="store_true")
    args = p.parse_args()

    if args.selftest:
        demo()
        return
    if not args.sheet_id:
        raise SystemExit("--sheet-id is required (or pass --selftest)")

    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")

    if args.backfill_names:
        r = backfill_company_names(args.sheet_id, args.backfill_names)
        print(f"Backfilled {r['filled']} company names on [{args.backfill_names}] ({r['unrecoverable']} unrecoverable, no Link to derive from).")

    requested = [t for t in args.source_tabs.split(",")] if args.source_tabs else None
    result = merge(args.sheet_id, args.main_tab, requested, per_tab_limit=args.per_tab_limit)
    print(f"Read per tab: {result['tabs']}")
    print(f"Duplicates dropped: {result['dropped']}")
    print(f"Uniques appended: {result['appended']}  {result['appended_by_tab']}")

    if args.dup_tab:
        n = log_duplicates(args.sheet_id, args.dup_tab, result["dropped_rows"])
        print(f"Logged {n} dropped duplicates to [{args.dup_tab}].")

    if args.dedupe_existing:
        n = dedupe_main_by_link(args.sheet_id, args.main_tab)
        print(f"Deduped {n} legacy rows from Main (same Link, kept the most-resolved copy).")

    if args.sort:
        n = sort_main_by_score(args.sheet_id, args.main_tab)
        print(f"Sorted {n} Main rows by rating+review score (best first).")


if __name__ == "__main__":
    main()
