"""leads-to-crm — push manually-scraped leads into the right CRM, with messages.

One engine, any channel. Reads the per-channel "Instant ... Leads" source sheet,
decides what is genuinely new, generates a Touch 1 message (Claude Haiku), and
appends to the matching "NexusPoint ... Outreach CRM".

The decision logic is the whole fix for the two old bugs. Per source row:

  - status already "Added"        -> skip (already pushed)
  - identity already in the CRM    -> RECONCILE: stamp source "Added", do NOT
                                       re-append. This makes the run idempotent
                                       even if a previous writeback failed, which
                                       is what kills the duplicates.
  - identity resolves, not in CRM  -> PUSH: generate message, append, stamp "Added"
  - identity unresolvable          -> "Needs Review" (visible, never silently dropped)

No follower / geo / post-URL auto-drops: Aleem curates the source sheet by hand,
so the skill trusts the rows he marked. (Optional --filter-followers / --exclude-geo
exist for when he wants them, off by default.)

Usage:
  python push.py --channel instagram
  python push.py --channel instagram --dry-run     # decision table, no writes
  python push.py --channel linkedin
  python push.py --channel instagram --no-messages  # push blank Touch 1, fill later
  python push.py --channel instagram --dedup        # remove existing CRM dupes by identity
"""

import argparse
import sys
from datetime import date

sys.path.insert(0, str(__import__("pathlib").Path(__file__).resolve().parent))

import channels as ch
import messages as msg
import sheets


SOUTH_ASIA = [
    "pakistan", "india", "bangladesh", "sri lanka", "nepal", "karachi", "lahore",
    "islamabad", "mumbai", "delhi", "bangalore", "bengaluru", "chennai", "hyderabad",
    "pune", "kolkata", "dhaka", "colombo",
]
# LinkedIn country subdomains catch South-Asian profiles whose location field is
# blank (the text match alone misses those), matching the old pipeline's behavior.
SOUTH_ASIA_URL = ("//pk.linkedin", "//in.linkedin", "//bd.linkedin",
                  "//lk.linkedin", "//np.linkedin")


def _is_south_asia(lead):
    text = (lead.get("location", "") + " " + lead.get("title", "")).lower()
    if any(k in text for k in SOUTH_ASIA):
        return True
    url = lead.get("profile_url", "").lower()
    return any(p in url for p in SOUTH_ASIA_URL)


def _parse_followers(raw):
    if not raw:
        return None
    s = raw.strip().lower()
    if s.startswith("http"):
        return None
    import re
    m = re.search(r"(\d+(?:[.,]\d+)?)\s*([km])?", s)
    if not m:
        return None
    num = float(m.group(1).replace(",", ""))
    unit = m.group(2) or ""
    return int(num * (1000 if unit == "k" else 1_000_000 if unit == "m" else 1))


def run_push(channel, dry_run=False, no_messages=False, limit=None,
             filter_followers=0, exclude_geo=False):
    today = date.today().isoformat()
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")

    print(f"=== leads-to-crm: {channel.label} ===")
    if dry_run:
        print("[DRY RUN] no writes\n")

    # 1. Source
    src = sheets.read_values(channel.source_sheet_id, channel.source_tab)
    if not src:
        # tab name may have changed — fall back to the first tab
        tab = sheets.first_tab_title(channel.source_sheet_id)
        if tab != channel.source_tab:
            print(f"  source tab '{channel.source_tab}' empty; trying first tab '{tab}'")
            src = sheets.read_values(channel.source_sheet_id, tab)
            channel.source_tab = tab
    if not src:
        print("No source data. Exiting.")
        return
    header, data_rows = src[0], src[1:]
    col_map = ch.build_col_map(header, channel.source_aliases)
    print(f"Source: {len(data_rows)} rows | tab '{channel.source_tab}' | columns {list(col_map.keys())}")

    # Status column ("Include to CRM" in both sheets today)
    status_idx = sheets.header_index(header, channel.status_header_names)
    if status_idx is None:
        print(f"  WARNING: no status column {channel.status_header_names} found — "
              "cannot skip already-Added rows or write back.")
    status_letter = sheets.col_letter(status_idx) if status_idx is not None else None
    existing_status = {
        i: (row[status_idx].strip() if status_idx is not None and status_idx < len(row) else "")
        for i, row in enumerate(data_rows)
    }

    # 2. Existing CRM identities
    crm = sheets.read_values(channel.crm_sheet_id, channel.crm_tab)
    crm_header = crm[0] if crm else []
    crm_cols = {h.strip().lower(): i for i, h in enumerate(crm_header)}
    existing = set()
    for row in crm[1:] if len(crm) > 1 else []:
        ident = channel.crm_identity(row, crm_cols)
        if ident:
            existing.add(ident)
    print(f"CRM: {max(len(crm) - 1, 0)} rows | {len(existing)} known identities\n")

    # 3. Classify
    decisions = {}   # row_idx -> writeback string ("Added"/"Needs Review"/"")
    kept = []        # list of (row_idx, lead)
    stats = {"pushed": 0, "reconciled": 0, "skipped_added": 0,
             "needs_review": 0, "blank": 0, "filtered": 0}
    seen_this_run = set()

    for i, row in enumerate(data_rows):
        if limit and stats["pushed"] >= limit:
            break

        if existing_status.get(i, "").lower() == "added":
            stats["skipped_added"] += 1
            continue

        lead = channel.parse_row(row, col_map)
        if lead is None:
            stats["blank"] += 1
            decisions[i] = ""
            continue

        ident = channel.identity(lead)
        if not ident:
            stats["needs_review"] += 1
            decisions[i] = "Needs Review"
            continue

        if ident in existing or ident in seen_this_run:
            # already in CRM (or a same-run dup) — reconcile, never re-append
            stats["reconciled"] += 1
            decisions[i] = "Added"
            continue

        # Optional, off-by-default ICP guards
        if exclude_geo and _is_south_asia(lead):
            stats["filtered"] += 1
            decisions[i] = "Skipped - geo"
            continue
        if filter_followers:
            n = _parse_followers(lead.get("followers", ""))
            if n is not None and n < filter_followers:
                stats["filtered"] += 1
                decisions[i] = "Skipped - followers"
                continue

        seen_this_run.add(ident)
        kept.append((i, lead))
        decisions[i] = "Added"
        stats["pushed"] += 1

    # 4. Messages. On a dry run we only sample a few so a preview doesn't burn the
    # whole batch of API calls; the live run generates one per kept lead.
    messages_out = ["" for _ in kept]
    if kept and not no_messages:
        sample = kept if not dry_run else kept[:min(3, len(kept))]
        print(f"Generating {len(sample)} message(s) via {msg.MODEL}"
              f"{' (dry-run sample)' if dry_run else ''}...")
        client = msg.get_client()
        gen = msg.generate_batch(client, channel.message_style, [l for _, l in sample])
        for k in range(len(gen)):
            messages_out[k] = gen[k]

    # 5. Summary
    print(f"\n--- Decisions ---")
    print(f"  Pushed (new):        {stats['pushed']}")
    print(f"  Reconciled (in CRM): {stats['reconciled']}")
    print(f"  Skipped (Added):     {stats['skipped_added']}")
    print(f"  Needs review:        {stats['needs_review']}")
    print(f"  Blank:               {stats['blank']}")
    if stats["filtered"]:
        print(f"  Filtered (opt-in):   {stats['filtered']}")

    if dry_run:
        if kept:
            print("\n[DRY RUN] sample of rows that WOULD be pushed:")
            for (idx, lead), m in list(zip(kept, messages_out))[:8]:
                tag = lead.get("name") or lead.get("username") or "?"
                print(f"  + {str(tag)[:40]:<40} id={channel.identity(lead)}")
                if m:
                    print(f"      msg ({len(m)}): {m[:110]}")
        return

    if not kept:
        print("\nNothing new to push.")
    else:
        records = [channel.crm_record(lead, m, today) for (_, lead), m in zip(kept, messages_out)]
        rows_out = [[rec.get(h, "") for h in crm_header] for rec in records]
        print(f"\nAppending {len(rows_out)} rows to {channel.label} CRM...")
        if not sheets.append_rows(channel.crm_sheet_id, channel.crm_tab, rows_out):
            print("Append failed — aborting before writeback so nothing is double-counted.")
            return
        print("  appended.")

    # 6. Write status back to source (idempotency: 'Added' is what stops re-pushes)
    if status_letter:
        col_values = []
        for i in range(len(data_rows)):
            new_val = decisions.get(i)
            prior = existing_status.get(i, "")
            if new_val == "Added":
                col_values.append("Added")
            elif new_val and new_val != "":
                col_values.append(new_val)          # Needs Review / Skipped-*
            elif prior:
                col_values.append(prior)            # preserve existing
            else:
                col_values.append("")
        print(f"Writing status back to source column {status_letter}...")
        sheets.update_column(channel.source_sheet_id, channel.source_tab, status_letter, 2, col_values)
        print("  done.")


def run_dedup(channel, dry_run=False):
    """Remove existing CRM duplicates by identity (keeps first occurrence)."""
    print(f"=== dedup {channel.label} CRM ===")
    rows = sheets.read_values(channel.crm_sheet_id, channel.crm_tab)
    if len(rows) < 2:
        print("CRM empty.")
        return
    header, data = rows[0], rows[1:]
    crm_cols = {h.strip().lower(): i for i, h in enumerate(header)}
    seen, to_remove = {}, []
    for i, row in enumerate(data):
        ident = channel.crm_identity(row, crm_cols)
        if not ident:
            continue
        if ident in seen:
            to_remove.append((i + 2, ident, seen[ident]))
        else:
            seen[ident] = i + 2
    print(f"  {len(data)} rows | {len(to_remove)} duplicates")
    for r, ident, first in to_remove[:40]:
        print(f"    row {r}: {ident} (dup of row {first})")
    if not to_remove:
        print("  clean.")
        return
    if dry_run:
        print(f"\n[DRY RUN] would delete {len(to_remove)} rows.")
        return
    gid = sheets.get_gid(channel.crm_sheet_id, channel.crm_tab)
    if gid is None:
        print("  ERROR: could not resolve CRM tab gid.")
        return
    sheets.delete_rows(channel.crm_sheet_id, gid, [r[0] for r in to_remove])
    print(f"  removed {len(to_remove)} duplicates.")


def main():
    p = argparse.ArgumentParser(description="Push Instant-Leads rows into the channel CRM.")
    p.add_argument("--channel", required=True, choices=sorted(ch.CHANNELS.keys()))
    p.add_argument("--dry-run", action="store_true", help="Preview decisions, write nothing")
    p.add_argument("--no-messages", action="store_true", help="Push with blank Touch 1 (fill later)")
    p.add_argument("--dedup", action="store_true", help="Remove existing CRM duplicates and exit")
    p.add_argument("--limit", type=int, default=0, help="Cap new pushes (handy for a test run)")
    p.add_argument("--filter-followers", type=int, default=0, help="Opt-in min follower count")
    p.add_argument("--exclude-geo", action="store_true", help="Opt-in: skip South Asia rows")
    args = p.parse_args()

    channel = ch.CHANNELS[args.channel]
    if args.dedup:
        run_dedup(channel, dry_run=args.dry_run)
        return
    run_push(channel, dry_run=args.dry_run, no_messages=args.no_messages,
             limit=args.limit, filter_followers=args.filter_followers,
             exclude_geo=args.exclude_geo)


if __name__ == "__main__":
    main()
