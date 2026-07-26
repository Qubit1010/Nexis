"""Rewrite the Touch 1 copy on CRM rows that were already pushed, without touching anything else.

Why this exists as a real script rather than a throwaway: copy quality has now needed rework twice
(2026-07-25 burned phrases, 2026-07-26 scraped rating/review figures), and each time the leads were
already in the CRM. The same lesson `run_batch.py` records for lead-generator applies here -- a
disposable driver gets re-derived and re-broken every time, so the loop lives in one place instead.

Only the Touch 1 Message column is written. Identity, status, dates, and every other column are left
exactly as they are, so a regeneration is never a re-push and never creates a duplicate row.

Usage:
  python regenerate_messages.py --channel linkedin --date 2026-07-25 --dry-run
  python regenerate_messages.py --channel all --date 2026-07-25
  python regenerate_messages.py --channel instagram --date 2026-07-25 --only-flagged
Runs UNSANDBOXED (LLM calls). Sheet I/O needs a live gws token.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "lead-generator" / "scripts"))
import channels as ch  # noqa: E402
import messages as msg  # noqa: E402
import push_from_leadgen as P  # noqa: E402
import read_batch_main as RB  # noqa: E402
import sheets  # noqa: E402

MESSAGE_HEADER = "Touch 1 Message"
DATE_HEADER = "Date Added"


def _needs_fix(text):
    """A message worth spending a regeneration on: cites a scraped figure, or uses banned phrasing.
    (Repeat detection is not used here -- it is relative to batch order, so it is applied during
    regeneration itself, not as a selection filter.)"""
    return bool(msg.number_hits(text) or msg.banned_hits(text))


def leads_by_identity(channel_key, sheet_id, tab, start_row, end_row):
    """identity -> lead, rebuilt from Main exactly the way the original push built it."""
    rows = sheets.read_values(sheet_id, tab)
    header, data = rows[0], rows[1:]
    col_map = RB.build_col_map(header)
    biz = [RB.row_to_biz(i, r, col_map) for i, r in enumerate(data, start=2)
           if start_row <= i <= end_row and any(c.strip() for c in r)]
    channel = ch.CHANNELS[channel_key]
    out = {}
    for _row, _ctype, lead in P.build_pairs(channel_key, biz):
        ident = channel.identity(lead)
        if ident:
            out.setdefault(ident, lead)
    return out


def regenerate(channel_key, date_str, *, sheet_id, tab, start_row, end_row,
               dry_run=False, only_flagged=False, limit=None):
    channel = ch.CHANNELS[channel_key]
    rows = sheets.read_values(channel.crm_sheet_id, channel.crm_tab)
    if not rows:
        print(f"  {channel.label}: CRM unreadable, skipping.")
        return {"updated": 0, "unmatched": 0}
    header, data = rows[0], rows[1:]
    cols = {h.strip().lower(): i for i, h in enumerate(header)}
    mi, di = cols.get(MESSAGE_HEADER.lower()), cols.get(DATE_HEADER.lower())
    if mi is None or di is None:
        print(f"  {channel.label}: no '{MESSAGE_HEADER}'/'{DATE_HEADER}' column, skipping.")
        return {"updated": 0, "unmatched": 0}

    targets = []  # (sheet_row_1based, identity, current_message)
    for i, row in enumerate(data, start=2):
        if (row[di].strip() if di < len(row) else "") != date_str:
            continue
        current = row[mi] if mi < len(row) else ""
        if only_flagged and not _needs_fix(current):
            continue
        targets.append((i, channel.crm_identity(row, cols), current))
    if limit:
        targets = targets[:limit]
    if not targets:
        print(f"  {channel.label}: nothing to regenerate for {date_str}.")
        return {"updated": 0, "unmatched": 0}

    lead_map = leads_by_identity(channel_key, sheet_id, tab, start_row, end_row)
    matched = [(r, lead_map[ident], cur) for r, ident, cur in targets if ident in lead_map]
    unmatched = len(targets) - len(matched)
    print(f"  {channel.label}: {len(targets)} row(s) dated {date_str}, "
          f"{len(matched)} matched to a Main lead, {unmatched} unmatched (left untouched).")
    if not matched:
        return {"updated": 0, "unmatched": unmatched}

    fresh = msg.generate_batch(msg.get_client(), channel.message_style, [l for _, l, _ in matched])

    updates = [(r, new) for (r, _l, _c), new in zip(matched, fresh) if new.strip()]
    if dry_run:
        print(f"\n  [DRY RUN] {len(updates)} row(s) would be rewritten:")
        for r, new in updates[:8]:
            was = next(c for rr, _l, c in matched if rr == r)
            print(f"    row {r}\n      was: {was[:110]}\n      now: {new[:110]}")
        return {"updated": 0, "unmatched": unmatched}

    col = sheets.col_letter(mi)
    wrote = 0
    # Written per contiguous run so a scattered selection stays correct; appended batches are
    # contiguous in practice, so this is normally a single write.
    updates.sort()
    i = 0
    while i < len(updates):
        j = i
        while j + 1 < len(updates) and updates[j + 1][0] == updates[j][0] + 1:
            j += 1
        block = [v for _, v in updates[i:j + 1]]
        if sheets.update_column(channel.crm_sheet_id, channel.crm_tab, col, updates[i][0], block):
            wrote += len(block)
        i = j + 1
    print(f"  {channel.label}: rewrote {wrote} Touch 1 message(s).")
    return {"updated": wrote, "unmatched": unmatched}


def main():
    p = argparse.ArgumentParser(description="Regenerate Touch 1 copy on already-pushed CRM rows.")
    p.add_argument("--channel", required=True, choices=["instagram", "linkedin", "facebook", "all"])
    p.add_argument("--date", required=True, help="Date Added value to target, e.g. 2026-07-25")
    p.add_argument("--sheet-id", default=P.DEFAULT_SHEET_ID)
    p.add_argument("--tab", default=P.DEFAULT_TAB)
    p.add_argument("--rows", default=P.DEFAULT_ROWS)
    p.add_argument("--dry-run", action="store_true")
    p.add_argument("--only-flagged", action="store_true",
                   help="only rows whose current copy cites a scraped figure or uses banned phrasing")
    p.add_argument("--limit", type=int, default=None)
    args = p.parse_args()

    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    start_row, end_row = P.parse_row_range(args.rows)
    keys = ["instagram", "linkedin", "facebook"] if args.channel == "all" else [args.channel]

    total = 0
    for key in keys:
        print(f"\n=== regenerate: {key} ({args.date}) ===")
        total += regenerate(key, args.date, sheet_id=args.sheet_id, tab=args.tab,
                            start_row=start_row, end_row=end_row, dry_run=args.dry_run,
                            only_flagged=args.only_flagged, limit=args.limit)["updated"]
    print(f"\nTotal rewritten: {total}")


if __name__ == "__main__":
    main()
