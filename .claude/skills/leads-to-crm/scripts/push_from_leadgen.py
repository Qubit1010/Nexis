"""Pushes lead-generator's resolved Main-sheet leads into the same Instagram/LinkedIn/Facebook
Outreach CRMs push.py already maintains -- a second SOURCE feeding the same three CRMs, not a new
channel. Each Main-sheet business row (see .claude/skills/lead-generator/) can carry BOTH a company
social link and the founder's own personal social link per platform; this script pushes both.

Locked with Aleem 2026-07-17:
  - Two stacked rows per business per channel: a Founder row, then a Company row directly below it,
    in Main-sheet row order. One new CRM column, "Contact Type" (Founder/Company); the existing
    Touch 1 Message column holds each row's own message.
  - LinkedIn is FOUNDER ONLY. LinkedIn has no "connection request note" mechanic for a company PAGE
    (you follow a page, you don't connect with it) -- a generated connection note there would
    describe an action Aleem can't take. The company LinkedIn link stays on the Main sheet for
    reference only; Instagram and Facebook still get both a Founder row and a Company row.

Reuses channels.py's Channel classes UNCHANGED for identity()/crm_identity()/crm_record() -- this
script only supplies a different SOURCE of lead dicts (the Main sheet, not a per-channel Instant
Leads sheet) plus a "Contact Type" tag merged onto the record before writing.

Usage:
  python push_from_leadgen.py --channel instagram --dry-run --limit 6
  python push_from_leadgen.py --channel instagram
  python push_from_leadgen.py --channel linkedin
  python push_from_leadgen.py --channel facebook
  python push_from_leadgen.py --channel all --rows 2-165
"""
from __future__ import annotations

import argparse
import re
import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import channels as ch  # noqa: E402
import messages as msg  # noqa: E402
import sheets  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "lead-generator" / "scripts"))
import read_batch_main as RB  # noqa: E402
import facebook_resolve as fr  # noqa: E402


DEFAULT_SHEET_ID = "1QikXgf6WbPfpCdMlxs43nYeZRjqpr0kqdmtqAiiu8mI"
DEFAULT_TAB = "Main"
DEFAULT_ROWS = "2-165"
CONTACT_TYPE_COL = "Contact Type"
PUSH_STATUS_HEADERS = {
    "instagram": "Instagram CRM Push",
    "linkedin": "LinkedIn CRM Push",
    "facebook": "Facebook CRM Push",
}


def parse_row_range(spec):
    a, b = spec.split("-")
    return int(a), int(b)


def _bio_of(biz):
    parts = [p for p in (biz.get("category", ""), biz.get("note", "")) if p]
    return ". ".join(parts).strip()


_NAME_SUFFIXES = {"mba", "phd", "cpa", "esq", "jr", "sr", "ii", "iii", "iv", "cfa", "jd", "md"}


def _is_multi_person(name):
    """True if `name` names 2+ people (comma/&/'and'-joined), not one person with a
    trailing credential ("Toby Fischer, MBA" is one person). Main sheet's Founder field
    is a single string with no per-link attribution, so when it names multiple people
    there's no way to know which one a given social link actually belongs to -- greeting
    by the first-listed name risks addressing the wrong person (caught live: row 8's
    founder_linkedin resolves to Andrew Nasrinpay, not Bobby Steinbach, the first name in
    "Bobby Steinbach, Andrew Nasrinpay")."""
    parts = [p.strip() for p in re.split(r",| & | and ", name, flags=re.I) if p.strip()]
    if len(parts) < 2:
        return False
    return parts[-1].lower().rstrip(".") not in _NAME_SUFFIXES


def _founder_lead(channel_key, biz):
    """Founder-type lead dict, or None if this channel's founder link is blank. Identity keys
    (_handle/_slug/_identity) are set even when extraction fails (empty string) so the normal
    channel.identity()-returns-'' -> needs_review path handles it, same as push.py."""
    url = biz.get(f"founder_{channel_key}", "")
    if not url:
        return None
    name = biz.get("founder", "")
    first_name = "" if _is_multi_person(name) else (ch.first_name_of(name) or (name.split()[0] if name else ""))
    lead = {
        "channel": channel_key,
        "name": name,
        "first_name": first_name,
        "company": biz.get("company", ""),
        "title": "Founder",
        "location": biz.get("location", ""),
        "profile_url": url,
        "followers": "",
        "bio": _bio_of(biz),
    }
    if channel_key == "instagram":
        handle = ch._ig_handle_from_url(url)
        lead["_handle"] = handle
        lead["username"] = ("@" + handle) if handle else ""
        if handle:
            lead["profile_url"] = f"https://www.instagram.com/{handle}/"
    elif channel_key == "linkedin":
        lead["_slug"] = ch._li_slug(url)
        lead["profile_url"] = url.split("?")[0].rstrip("/")
    elif channel_key == "facebook":
        lead["_identity"] = fr.fb_profile_id(url) or fr.fb_slug(url)
    return lead


def _company_lead(channel_key, biz):
    """Company/brand-type lead dict, or None if this channel's company link is blank -- or the
    channel is LinkedIn, which never gets a company row (see module docstring)."""
    if channel_key == "linkedin":
        return None
    url = biz.get(channel_key, "")
    if not url:
        return None
    name = biz.get("company", "")
    lead = {
        "channel": channel_key,
        "name": name,
        "first_name": "",  # deliberately blank -- signals "not a person" to the *_company styles
        "company": name,
        "title": biz.get("category", ""),
        "location": biz.get("location", ""),
        "profile_url": url,
        "followers": "",
        "bio": _bio_of(biz),
    }
    if channel_key == "instagram":
        handle = ch._ig_handle_from_url(url)
        lead["_handle"] = handle
        lead["username"] = ("@" + handle) if handle else ""
        if handle:
            lead["profile_url"] = f"https://www.instagram.com/{handle}/"
    elif channel_key == "facebook":
        lead["_identity"] = fr.fb_profile_id(url) or fr.fb_slug(url)
    return lead


def build_pairs(channel_key, businesses):
    """Founder-then-Company per business, in Main-sheet row order -- the stacking Aleem asked for."""
    out = []  # (row_num, "Founder"/"Company", lead)
    for biz in businesses:
        f = _founder_lead(channel_key, biz)
        if f:
            out.append((biz["row"], "Founder", f))
        c = _company_lead(channel_key, biz)
        if c:
            out.append((biz["row"], "Company", c))
    return out


def run_channel(channel_key, sheet_id, tab, start_row, end_row, *, dry_run=False,
                no_messages=False, limit=None):
    channel = ch.CHANNELS[channel_key]
    today = date.today().isoformat()
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")

    print(f"=== push_from_leadgen: {channel.label} (rows {start_row}-{end_row}) ===")
    if dry_run:
        print("[DRY RUN] no writes\n")

    rows = sheets.read_values(sheet_id, tab)
    if not rows:
        print("No Main sheet data. Exiting.")
        return
    header, data_rows = rows[0], rows[1:]
    col_map = RB.build_col_map(header)
    push_status_header = PUSH_STATUS_HEADERS[channel_key]
    push_idx = sheets.header_index(header, [push_status_header])

    businesses = []
    for row_num, row in enumerate(data_rows, start=2):
        if row_num < start_row or row_num > end_row:
            continue
        if not any(c.strip() for c in row):
            continue
        already = row[push_idx].strip() if push_idx is not None and push_idx < len(row) else ""
        if already:
            continue
        biz = RB.row_to_biz(row_num, row, col_map)
        if not biz.get("company"):
            continue
        businesses.append(biz)

    print(f"Main sheet: {len(businesses)} unpushed business row(s) in range | columns {list(col_map.keys())}")

    pairs = build_pairs(channel_key, businesses)
    if limit:
        pairs = pairs[:limit]

    # Existing CRM identities -- same safety net push.py relies on, so even if the Main-sheet
    # push-status flag were ever wrong, a real duplicate still can't land in the CRM twice.
    crm = sheets.read_values(channel.crm_sheet_id, channel.crm_tab)
    if len(crm) <= 1:
        # A live CRM read that comes back with zero data rows is never legitimate for these
        # three sheets (each already has hundreds of rows) -- it means the read failed (a gws
        # transient error was swallowed into an empty list by sheets.read_values) and pushing
        # now would treat every lead as "not in the CRM", duplicating whatever's already there.
        # Caught live 2026-07-17: an "unavailable" gws error wasn't in _TRANSIENT_MARKERS, so it
        # wasn't retried, and this exact silent-empty-CRM state resulted.
        raise SystemExit(
            f"ABORT: {channel.label} CRM read returned {len(crm)} row(s) (expected hundreds). "
            "Refusing to push against what looks like a failed read, not a genuinely empty CRM. "
            "Re-run once the read succeeds."
        )
    crm_header = crm[0] if crm else []
    crm_cols = {h.strip().lower(): i for i, h in enumerate(crm_header)}
    existing = set()
    for row in crm[1:] if len(crm) > 1 else []:
        ident = channel.crm_identity(row, crm_cols)
        if ident:
            existing.add(ident)
    print(f"CRM: {max(len(crm) - 1, 0)} rows | {len(existing)} known identities\n")

    kept = []          # (row_num, contact_type, lead)
    row_result = {}    # row_num -> set of contact types resolved (pushed or reconciled) this run
    seen_this_run = set()
    stats = {"pushed": 0, "reconciled": 0, "needs_review": 0}

    for row_num, contact_type, lead in pairs:
        ident = channel.identity(lead)
        if not ident:
            stats["needs_review"] += 1
            row_result.setdefault(row_num, set())
            continue
        if ident in existing or ident in seen_this_run:
            stats["reconciled"] += 1
            row_result.setdefault(row_num, set()).add(contact_type)
            continue
        seen_this_run.add(ident)
        kept.append((row_num, contact_type, lead))
        row_result.setdefault(row_num, set()).add(contact_type)
        stats["pushed"] += 1

    # Messages: Founder rows use the channel's own style; Company rows use "<style>_company".
    messages_out = ["" for _ in kept]
    if kept and not no_messages:
        sample = kept if not dry_run else kept[:min(6, len(kept))]
        print(f"Generating {len(sample)} message(s) via {msg.MODEL}"
              f"{' (dry-run sample)' if dry_run else ''}...")
        client = msg.get_client()
        for k, (row_num, contact_type, lead) in enumerate(sample):
            style = channel.message_style if contact_type == "Founder" else f"{channel.message_style}_company"
            text, arch, provider = client.generate(style, lead) if client else ("", "", "")
            tag = lead.get("first_name") or lead.get("name") or "?"
            status = f"{len(text)} chars [{arch} via {provider}]" if text else f"BLANK [{arch}]"
            print(f"    [{k + 1}/{len(sample)}] {contact_type:<8} {str(tag)[:28]:<28} {status}", flush=True)
            messages_out[k] = text

    print("\n--- Decisions ---")
    print(f"  Pushed (new):        {stats['pushed']}")
    print(f"  Reconciled (in CRM): {stats['reconciled']}")
    print(f"  Needs review:        {stats['needs_review']}")

    if dry_run:
        if kept:
            print("\n[DRY RUN] sample of rows that WOULD be pushed:")
            for (row_num, contact_type, lead), m in list(zip(kept, messages_out))[:10]:
                tag = lead.get("name") or "?"
                print(f"  row {row_num} + {contact_type:<8} {str(tag)[:35]:<35} id={channel.identity(lead)}")
                if m:
                    print(f"      msg ({len(m)}): {m[:110]}")
        return

    if not kept:
        print("\nNothing new to push.")
    else:
        crm_header = sheets.ensure_columns(channel.crm_sheet_id, channel.crm_tab, crm_header,
                                           [CONTACT_TYPE_COL])
        records = []
        for (row_num, contact_type, lead), m in zip(kept, messages_out):
            rec = channel.crm_record(lead, m, today)
            rec[CONTACT_TYPE_COL] = contact_type
            records.append(rec)
        rows_out = [[rec.get(h, "") for h in crm_header] for rec in records]
        print(f"\nAppending {len(rows_out)} rows to {channel.label} CRM...")
        if not sheets.append_rows(channel.crm_sheet_id, channel.crm_tab, rows_out):
            print("Append failed -- aborting before writeback so nothing is double-counted.")
            return
        print("  appended.")

    # Stamp push-status back onto the Main sheet rows this run touched (pushed, reconciled, or
    # needs_review all count as "resolved" -- only rows with no link at all for this channel stay
    # blank, so they're cheaply re-examined rather than permanently skipped).
    header = sheets.ensure_columns(sheet_id, tab, header, [push_status_header])
    push_idx = sheets.header_index(header, [push_status_header])
    push_letter = sheets.col_letter(push_idx)
    col_values = []
    for row_num, row in enumerate(data_rows, start=2):
        if row_num not in row_result:
            prior = row[push_idx].strip() if push_idx is not None and push_idx < len(row) else ""
            col_values.append(prior)
            continue
        types = row_result[row_num]
        col_values.append(", ".join(sorted(types)) if types else "No identity")
    sheets.update_column(sheet_id, tab, push_letter, 2, col_values)
    print(f"Stamped '{push_status_header}' on {len(row_result)} row(s).")


def main():
    p = argparse.ArgumentParser(description="Push lead-generator's Main-sheet leads into the outreach CRMs.")
    p.add_argument("--channel", required=True, choices=["instagram", "linkedin", "facebook", "all"])
    p.add_argument("--sheet-id", default=DEFAULT_SHEET_ID)
    p.add_argument("--tab", default=DEFAULT_TAB)
    p.add_argument("--rows", default=DEFAULT_ROWS)
    p.add_argument("--dry-run", action="store_true")
    p.add_argument("--no-messages", action="store_true")
    p.add_argument("--limit", type=int, default=0, help="Cap CRM rows pushed for this channel")
    args = p.parse_args()

    start_row, end_row = parse_row_range(args.rows)
    channels_to_run = ["instagram", "linkedin", "facebook"] if args.channel == "all" else [args.channel]
    for key in channels_to_run:
        run_channel(key, args.sheet_id, args.tab, start_row, end_row,
                    dry_run=args.dry_run, no_messages=args.no_messages,
                    limit=args.limit or None)
        print()


if __name__ == "__main__":
    main()
