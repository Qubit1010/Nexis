"""Fill Touch 1 DMs ONLY for 'New' leads whose Touch 1 is currently blank.

Unlike instagram_push.py --refresh-touch1 (which regenerates every 'New' lead),
this is surgical: it never overwrites a DM that already exists. Use it after a
blank-DM push + dedup to generate real GPT DMs for just the survivors that need one.

Usage:
  python fill_blank_dms.py            # live
  python fill_blank_dms.py --dry-run  # preview count + samples
"""
import sys
import instagram_push as ip
from transformers.instagram_transformer import generate_touch1_dm

CRM, TAB = ip.CRM_SHEET_ID, ip.CRM_TAB

def main():
    dry = "--dry-run" in sys.argv
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")

    rows = ip._read_sheet(CRM, TAB)
    header, data = rows[0], rows[1:]

    def col(names, default):
        for i, h in enumerate(header):
            if h.strip().lower() in names:
                return i
        return default
    t1 = col(["touch 1 message", "touch1 message", "touch 1"], 7)
    st = col(["status"], 11)
    t1_letter = chr(ord("A") + t1)

    # Build the full Touch 1 column; only change blank + New cells.
    new_col, fill_idx = [], []
    for r in data:
        status = r[st].strip() if st < len(r) else ""
        cur = r[t1].strip() if t1 < len(r) else ""
        new_col.append(cur)
        if status == "New" and not cur:
            fill_idx.append(len(new_col) - 1)

    print(f"'New' leads with blank Touch 1 to fill: {len(fill_idx)}")
    if not fill_idx:
        print("Nothing to fill.")
        return

    for n, i in enumerate(fill_idx, 1):
        r = data[i]
        lead = {
            "first_name": ip._extract_first_name(r[0].strip() if len(r) > 0 else ""),
            "title":      r[3].strip() if len(r) > 3 else "",
            "company":    r[2].strip() if len(r) > 2 else "",
            "bio":        r[6].strip() if len(r) > 6 else "",
            "followers":  r[5].strip() if len(r) > 5 else "",
            "username":   r[1].strip() if len(r) > 1 else "",
        }
        dm = generate_touch1_dm(lead)
        new_col[i] = dm
        tag = (lead["first_name"] or lead["username"] or r[0][:20])
        if dry:
            print(f"  [{n}/{len(fill_idx)}] {tag}: {dm[:90]}")
        elif n % 20 == 0:
            print(f"  generated {n}/{len(fill_idx)}", flush=True)

    if dry:
        return

    # Write back the whole Touch 1 column in batches (row 2 onward).
    print(f"Writing Touch 1 column {t1_letter}...", flush=True)
    B = 50
    for i in range(0, len(new_col), B):
        ip._update_column(CRM, TAB, t1_letter, 2 + i, new_col[i:i + B])
        print(f"  wrote rows {2+i}-{2+i+len(new_col[i:i+B])-1}", flush=True)
    print(f"Done. Filled {len(fill_idx)} blank DMs.")

if __name__ == "__main__":
    main()
