"""Sort the Instant Facebook Leads source sheet: actual profiles on top, group
links at the bottom.

Facebook leads are a mix of real profile/page links (directly messageable) and
group-post links (the author isn't in the URL, needs manual lookup). Working the
sheet top-down is easier if the messageable ones come first. This is a pure
re-order of the existing rows — no data is changed or dropped — ranked only by the
URL type (no LLM needed):

  0  actual profile        facebook.com/<slug>/  |  profile.php?id=<n>
  1  page/profile post     facebook.com/<slug>/posts|videos|photos/...
  2  group post, resolved  group post whose author we DID resolve to a profile URL
  3  group post            facebook.com/groups/<g>/posts/<id>/   (bottom)
  4  unknown / unrecognized
  9  blank rows            (very bottom)

The sort is stable, so original order is preserved within each tier.

Run:  python facebook_sort_source.py --dry-run    # preview the new order
      python facebook_sort_source.py              # apply (writes the sheet)
"""

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import channels as ch
import facebook_resolve as fr
import sheets

SOURCE_SHEET_ID = fr.SOURCE_SHEET_ID
SOURCE_TAB = fr.SOURCE_TAB

RANK_LABEL = {
    0: "profile", 1: "page/post", 2: "group (resolved)",
    3: "group", 4: "unknown", 9: "blank",
}


def rank_row(row, col_map, cache):
    if not any((c or "").strip() for c in row):
        return 9
    url, _ = ch.split_url_and_name(row, col_map)
    if not url:
        return 4
    kind = fr.fb_classify(url)
    if kind in ("profile", "profile_id"):
        return 0
    if kind == "page_post":
        return 1
    if kind == "group_post":
        rec = cache.get(url)
        if rec and rec.get("profile_url") and rec.get("status") == "New":
            return 2
        return 3
    return 4


def main():
    p = argparse.ArgumentParser(description="Sort Instant Facebook Leads: profiles top, groups bottom.")
    p.add_argument("--dry-run", action="store_true", help="Preview the new order, write nothing")
    args = p.parse_args()
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")

    print("=== facebook_sort_source ===")
    vals = sheets.read_values(SOURCE_SHEET_ID, SOURCE_TAB)
    if not vals:
        print("No source data.")
        return
    header, data = vals[0], vals[1:]
    ncols = len(header)
    col_map = ch.build_col_map(header, ch.CHANNELS["facebook"].source_aliases)
    cache = fr.load_cache()

    ranked = []
    counts = {}
    for i, row in enumerate(data):
        r = rank_row(row, col_map, cache)
        counts[r] = counts.get(r, 0) + 1
        ranked.append((r, i, row))

    # Stable sort: by rank, then original position.
    ranked.sort(key=lambda t: (t[0], t[1]))

    print("Tiers (top -> bottom):")
    for r in sorted(counts):
        print(f"  {r} {RANK_LABEL.get(r, '?'):<16} {counts[r]} rows")

    print("\nNew top 8:")
    for r, _, row in ranked[:8]:
        url = ch.split_url_and_name(row, col_map)[0]
        print(f"  [{RANK_LABEL.get(r,'?'):<16}] {url[:70]}")
    print("New bottom 5:")
    for r, _, row in ranked[-5:]:
        url = ch.split_url_and_name(row, col_map)[0]
        print(f"  [{RANK_LABEL.get(r,'?'):<16}] {url[:70]}")

    # Build the rectangular output (pad/truncate each row to header width).
    out = []
    for _, _, row in ranked:
        padded = (list(row) + [""] * ncols)[:ncols]
        out.append(padded)

    if args.dry_run:
        print("\n[DRY RUN] sheet not written.")
        return

    print(f"\nWriting {len(out)} sorted rows (from row 2) in batches ...")
    if sheets.update_rows(SOURCE_SHEET_ID, SOURCE_TAB, 2, out, ncols):
        print("  done.")
    else:
        print("  write failed.")


if __name__ == "__main__":
    main()
