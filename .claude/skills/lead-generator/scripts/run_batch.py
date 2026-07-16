"""Permanent batch orchestrator for Phase 2-4 (resolve + write). Replaces the disposable C:\\tmp driver
scripts that were re-derived -- and re-buggy -- on every real run: a founder-confidence fix built mid-run
once lived only in a throwaway driver and never made it back into the shipped `resolve.py`, so the next
run repeated the same mistake. This script is the one place that loop lives now.

Write policy (locked with Aleem 2026-07-16):
  * Company website + company socials (each already passed its gate -- website footer links, or search
    results token-verified against the company name) are AUTO-WRITTEN.
  * FOUNDERS ARE NEVER AUTO-WRITTEN. Even a website team-page extraction can surface a prominent
    non-founder exec (one live case returned its current Chief Business Officer, not the co-founder), so
    every founder -- website- or search-sourced -- goes to a REVIEW QUEUE with its evidence for a human
    confirm. Any stale founder value already on a reprocessed row is CLEARED, so the sheet never shows an
    unverified founder; the review queue markdown is the source of truth until Aleem fills it in.

Two modes:
  incremental (default): next unresolved batch via read_batch_main.next_batch (new leads).
  reprocess (--rows A-B): re-run an explicit row range that already carries data, bypassing the
    'already resolved' skip. Resume-safe -- finished rows get a 'v3:' status marker and are skipped on
    a re-run, so a batch that dies partway continues where it left off.

Usage:
  python run_batch.py --sheet-id <id> --tab Main --limit 12                 # incremental
  python run_batch.py --sheet-id <id> --tab Main --rows 2-165               # reprocess a range
  python run_batch.py --sheet-id <id> --tab Main --rows 2-165 --dry-run     # resolve+print, no writes
Runs UNSANDBOXED (resolve.py needs research/web-scraper network access). Sheet I/O needs a live gws token.
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import read_batch_main  # noqa: E402
import resolve as R  # noqa: E402
import write_result_main as W  # noqa: E402

SOCIAL_FIELDS = ("instagram", "linkedin", "facebook")
FOUNDER_KEYS = ("founder", "founder_instagram", "founder_linkedin", "founder_facebook")
MARKER = "v3:"  # status prefix that marks a row as v3-processed (resume skip + audit trail)
DEFAULT_REVIEW_OUT = (Path(__file__).resolve().parents[4] / "docs" / "lead-generator-review-queue.md")


def process_one(biz: dict, *, dry_run: bool, rederive: bool = False) -> dict:
    # Capture what the row currently carries BEFORE any blanking -- needed to know what to CLEAR.
    original = {k: biz.get(k, "") for k in SOCIAL_FIELDS + FOUNDER_KEYS}
    # Reprocess: forget existing socials + founders so resolve re-derives everything FRESH. Without this,
    # resolve's gap-fill-only logic (it only fills an empty platform) preserves a wrong existing value --
    # the exact bug that re-wrote a target company's Instagram with an unrelated business's handle on a
    # reprocess. Website is kept (a
    # wrong website is far rarer, and re-running Clutch per row is expensive). Incremental keeps existing
    # socials (they're trusted there) and gap-fills.
    if rederive:
        for k in SOCIAL_FIELDS + FOUNDER_KEYS:
            biz[k] = ""

    report = R.resolve(biz, do_founder=True)

    # Auto-write company website + all company socials (each passed its gate). Founders never auto-write.
    to_write: dict[str, str] = {}
    for p in SOCIAL_FIELDS:
        if report["company_socials"].get(p):
            to_write[p] = report["company_socials"][p]
    if report["website_freshly_found"] and report.get("website"):
        to_write["website"] = report["website"]

    founder_guess = report["founder"].get("name", "")
    has_founder_review = bool(founder_guess) or bool(report.get("founder_search", {}).get("all_candidates"))

    status_bits = [p for p in SOCIAL_FIELDS if to_write.get(p)]
    status = MARKER + (f" Resolved - {', '.join(status_bits)}" if status_bits else " no company socials")
    if has_founder_review:
        status += " | Founder: REVIEW"

    # Clear: founders always (never auto-written) + on a reprocess, any company social that WAS on the row
    # but the fresh pass didn't re-find (else write_row's skip-if-empty leaves the old wrong value in place).
    to_clear = [k for k in FOUNDER_KEYS if original.get(k)]
    if rederive:
        to_clear += [p for p in SOCIAL_FIELDS if original.get(p) and not to_write.get(p)]

    written: list[str] = []
    if not dry_run:
        if to_clear:
            W.clear_fields(biz["sheet_id"], biz["tab"], biz["row"], to_clear)
        written = W.write_row(biz["sheet_id"], biz["tab"], biz["row"], status,
                              website=to_write.get("website"), instagram=to_write.get("instagram"),
                              linkedin=to_write.get("linkedin"), facebook=to_write.get("facebook"))

    result = {"row": biz["row"], "company": biz["company"], "status": status,
             "wrote": written or list(to_write.keys()), "cleared": to_clear, "notes": report.get("notes", [])}
    if has_founder_review:
        result["review"] = {
            "row": biz["row"], "company": biz["company"], "website": report.get("website", ""),
            "founder_guess": founder_guess,
            "founder_provenance": report["provenance"].get("founder", ""),
            "founder_socials": {p: report["founder"].get(p, "") for p in SOCIAL_FIELDS},
            "candidates": (report.get("founder_search") or {}).get("all_candidates", []),
            "answer_hit": (report.get("founder_search") or {}).get("answer_hit", {}),
            "confidence": (report.get("founder_search") or {}).get("confidence", ""),
        }
    return result


def _flat(s: str) -> str:
    """Collapse whitespace/newlines to a single space -- LinkedIn snippets and some name captures carry
    embedded newlines that would otherwise break the markdown list formatting."""
    return " ".join((s or "").split())


def _render_review_md(reviews: list[dict]) -> str:
    lines = [f"# Lead Generator — Founder Review Queue",
             f"", f"*Generated {datetime.now():%Y-%m-%d %H:%M} — {len(reviews)} rows need a founder confirm.*",
             f"",
             "Company website + socials are already written to the sheet. Founders are NOT — confirm each",
             "against the website/candidates below, then fill the Founder + Founder-social columns by hand",
             "(or tell me the confirmed name and I'll write it).", ""]
    for rv in reviews:
        lines.append(f"## Row {rv['row']} — {_flat(rv['company'])}")
        lines.append(f"- **Website:** {rv['website'] or '(none)'}")
        gp = rv.get("founder_provenance", "")
        lines.append(f"- **Best guess:** {_flat(rv['founder_guess']) or '(none)'}"
                     + (f"  _(from {gp})_" if gp else "") + f"  — confidence: {rv.get('confidence','n/a')}")
        fs = rv.get("founder_socials", {})
        if any(fs.values()):
            lines.append(f"- **Guess's socials (unverified):** "
                         + ", ".join(f"{p}: {u}" for p, u in fs.items() if u))
        if rv.get("answer_hit", {}).get("name"):
            lines.append(f"- **Search answer said:** {_flat(rv['answer_hit']['name'])} — "
                         f"\"{_flat(rv['answer_hit'].get('source_text',''))[:200]}\"")
        cands = rv.get("candidates", [])
        if cands:
            lines.append(f"- **LinkedIn candidates:**")
            for c in cands[:6]:
                lines.append(f"  - [{_flat(c.get('name','?'))}]({c.get('linkedin','')}) — "
                             f"{_flat(c.get('snippet',''))[:120]}")
        lines.append("")
    return "\n".join(lines)


def run(sheet_id: str, tab: str, *, limit: int, rows: tuple[int, int] | None,
        dry_run: bool, review_out: Path, no_resume: bool = False) -> dict:
    if rows:
        # resume-skip the v3: marker unless dry-run (regenerating the queue) or --no-resume (redo the range)
        skip = None if (dry_run or no_resume) else MARKER
        batch = read_batch_main.rows_in_range(sheet_id, tab, rows[0], rows[1], skip_status_substr=skip)
    else:
        batch = read_batch_main.next_batch(sheet_id, tab, limit)

    jsonl = review_out.with_suffix(".jsonl")  # durable per-row review store (survives a mid-run crash)
    if not dry_run:
        review_out.parent.mkdir(parents=True, exist_ok=True)

    processed, errors = [], []
    for biz in batch["businesses"]:
        biz["sheet_id"], biz["tab"] = sheet_id, tab
        try:
            r = process_one(biz, dry_run=dry_run, rederive=bool(rows))
            processed.append(r)
            print(f"row {r['row']} ({r['company']}): {r['status']}", file=sys.stderr)
            if r.get("review") and not dry_run:
                # append immediately so a crash 4 hrs in doesn't lose the earlier rows' review data
                with jsonl.open("a", encoding="utf-8") as fh:
                    fh.write(json.dumps(r["review"], ensure_ascii=False) + "\n")
        except Exception as e:  # noqa: BLE001 - one bad business must not kill the batch
            errors.append({"row": biz["row"], "company": biz["company"], "error": str(e)})
            print(f"row {biz['row']} ({biz['company']}): ERROR {e}", file=sys.stderr)

    reviews = [r["review"] for r in processed if r.get("review")]
    review_total = len(reviews)
    if not dry_run and jsonl.exists():
        # render the markdown from the FULL durable store (last entry wins per row), so the queue
        # accumulates across resumes/re-runs instead of only holding this run's rows.
        merged: dict[int, dict] = {}
        for line in jsonl.read_text(encoding="utf-8").splitlines():
            if line.strip():
                rv = json.loads(line)
                merged[rv.get("row")] = rv
        all_reviews = [merged[k] for k in sorted(merged)]
        review_total = len(all_reviews)
        review_out.write_text(_render_review_md(all_reviews), encoding="utf-8")
    elif reviews and not dry_run:
        review_out.write_text(_render_review_md(reviews), encoding="utf-8")

    return {
        "mode": "reprocess" if rows else "incremental",
        "processed": len(processed), "errors": errors,
        "skipped_geo_this_run": batch.get("skipped_geo_this_run", 0),
        "skipped_already_done": batch.get("already_done_this_run", 0),
        "review_count": review_total,
        "review_file": str(review_out) if review_total and not dry_run else None,
        "results": processed,
    }


def _tier(rv: dict) -> str:
    p = rv.get("founder_provenance", "")
    if p == "website":
        return "website"
    if p == "search_fallback":
        return "search_" + (rv.get("confidence", "") or "na")
    return "none"


def write_founders_from_queue(sheet_id: str, tab: str, jsonl_path: Path, tiers: set[str],
                              *, dry_run: bool = False) -> dict:
    """Write the founder guesses from the durable review queue onto the sheet -- the human-confirm step,
    now that Aleem has reviewed. `tiers` selects which confidence tiers to write (website / search_low /
    search_ambiguous). Founder name + any found founder socials go to their columns; the row's status is
    updated from 'Founder: REVIEW' to the written name + tier so the sheet self-documents its provenance.
    Company socials are untouched. Idempotent-ish: re-running rewrites the same values."""
    import sheets  # noqa: E402  (leads-to-crm sheets module, on path via write_result_main)
    merged: dict[int, dict] = {}
    for line in Path(jsonl_path).read_text(encoding="utf-8").splitlines():
        if line.strip():
            rv = json.loads(line)
            merged[rv.get("row")] = rv

    header = sheets.read_values(sheet_id, f"{tab}!1:1")[0]
    header = W.ensure_columns(sheet_id, tab, header)
    # one batch read of the status column (rows 2..max) so we don't read per row
    status_col = W.col_letter_for(header, W.STATUS_HEADER)
    col_vals = sheets.read_values(sheet_id, f"{tab}!{status_col}2:{status_col}{max(merged)}")
    statuses = {idx: (cell[0] if cell else "") for idx, cell in enumerate(col_vals, start=2)}

    written, skipped = [], []
    for row in sorted(merged):
        rv = merged[row]
        name = _flat(rv.get("founder_guess", ""))
        if not name or _tier(rv) not in tiers:
            skipped.append(row)
            continue
        fs = rv.get("founder_socials", {}) or {}
        old = statuses.get(row, "")
        new_status = old.replace("Founder: REVIEW", f"Founder: {name} ({_tier(rv)})") \
            if "Founder: REVIEW" in old else (old + f" | Founder: {name} ({_tier(rv)})")
        if dry_run:
            written.append((row, name))
            continue
        W.write_row(sheet_id, tab, row, new_status, founder=name,
                    founder_instagram=fs.get("instagram") or None,
                    founder_linkedin=fs.get("linkedin") or None,
                    founder_facebook=fs.get("facebook") or None)
        written.append((row, name))
        print(f"row {row}: wrote founder '{name}' ({_tier(rv)})", file=sys.stderr)
    return {"written": len(written), "skipped": len(skipped), "tiers": sorted(tiers)}


def backfill_founder_socials(sheet_id: str, tab: str, start_row: int, end_row: int,
                             *, dry_run: bool = False) -> dict:
    """For rows that already carry a confirmed Founder name, search for whichever of their instagram/
    linkedin/facebook are still missing -- Aleem's method of typing 'company + founder name + platform'
    once the identity is known. Does NOT touch company data or re-derive the founder name; only fills
    social-column gaps on rows that already have one. Appends to the existing status rather than
    overwriting it (write_row would otherwise clobber the 'Resolved...' / 'Founder: X (tier)' text
    already there)."""
    import sheets  # noqa: E402
    batch = read_batch_main.rows_in_range(sheet_id, tab, start_row, end_row)
    candidates = [b for b in batch["businesses"] if (b.get("founder") or "").strip()
                 and any(not b.get(f"founder_{p}") for p in R.PLATFORMS)]
    if not candidates:
        return {"updated": 0, "skipped": len(batch["businesses"]), "errors": [], "results": []}

    header = sheets.read_values(sheet_id, f"{tab}!1:1")[0]
    header = W.ensure_columns(sheet_id, tab, header)
    status_col = W.col_letter_for(header, W.STATUS_HEADER)
    lo = min(b["row"] for b in candidates)
    hi = max(b["row"] for b in candidates)
    col_vals = sheets.read_values(sheet_id, f"{tab}!{status_col}{lo}:{status_col}{hi}")
    statuses = {lo + i: (c[0] if c else "") for i, c in enumerate(col_vals)}

    updated, errors = [], []
    for biz in candidates:
        missing = [p for p in R.PLATFORMS if not biz.get(f"founder_{p}")]
        try:
            found = R.founder_social_search(biz["founder"], biz["company"], missing)
        except Exception as e:  # noqa: BLE001 - one bad lookup must not kill the batch
            errors.append({"row": biz["row"], "company": biz["company"], "error": str(e)})
            print(f"row {biz['row']} ({biz['company']}): ERROR {e}", file=sys.stderr)
            continue
        if not found:
            print(f"row {biz['row']} ({biz['company']}): no backfill found", file=sys.stderr)
            continue
        old = statuses.get(biz["row"], "")
        new_status = old + f" | Founder socials backfilled: {', '.join(found)}"
        if not dry_run:
            W.write_row(sheet_id, tab, biz["row"], new_status,
                        founder_instagram=found.get("instagram"),
                        founder_linkedin=found.get("linkedin"),
                        founder_facebook=found.get("facebook"))
        updated.append({"row": biz["row"], "company": biz["company"], "found": found})
        print(f"row {biz['row']} ({biz['company']}): backfilled {list(found)}", file=sys.stderr)

    return {"updated": len(updated), "skipped": len(batch["businesses"]) - len(candidates),
            "errors": errors, "results": updated}


def reverify_founder_socials(sheet_id: str, tab: str, start_row: int, end_row: int,
                             *, dry_run: bool = False) -> dict:
    """Re-check EVERY currently-set founder-social value under the tightened person-name-match gate
    (added 2026-07-17 after a company-token-only check let "Cathryn Bird" -- an unrelated stranger whose
    surname happened to match the company "Bird Marketing" -- get written as a founder's LinkedIn). For
    each platform with an existing value, re-search fresh: keep if reconfirmed (same URL), overwrite if a
    corrected URL is found, clear if nothing passes the new gate. More expensive than backfill (which only
    searches gaps) since every populated platform gets a fresh round-trip, but this is the only way to
    close the window the earlier, weaker gate left open across every founder-social value written before
    it existed."""
    import sheets  # noqa: E402
    batch = read_batch_main.rows_in_range(sheet_id, tab, start_row, end_row)
    candidates = [b for b in batch["businesses"] if (b.get("founder") or "").strip()
                 and any(b.get(f"founder_{p}") for p in R.PLATFORMS)]
    if not candidates:
        return {"checked": 0, "kept": 0, "changed": 0, "cleared": 0, "errors": [], "results": []}

    header = sheets.read_values(sheet_id, f"{tab}!1:1")[0]
    header = W.ensure_columns(sheet_id, tab, header)
    status_col = W.col_letter_for(header, W.STATUS_HEADER)
    lo, hi = min(b["row"] for b in candidates), max(b["row"] for b in candidates)
    col_vals = sheets.read_values(sheet_id, f"{tab}!{status_col}{lo}:{status_col}{hi}")
    statuses = {lo + i: (c[0] if c else "") for i, c in enumerate(col_vals)}

    kept_n, changed_n, cleared_n, errors, results = 0, 0, 0, [], []
    for biz in candidates:
        set_platforms = [p for p in R.PLATFORMS if biz.get(f"founder_{p}")]
        try:
            fresh = R.founder_social_search(biz["founder"], biz["company"], set_platforms)
        except Exception as e:  # noqa: BLE001 - one bad lookup must not kill the batch
            errors.append({"row": biz["row"], "company": biz["company"], "error": str(e)})
            print(f"row {biz['row']} ({biz['company']}): ERROR {e}", file=sys.stderr)
            continue

        row_kept, row_changed, row_cleared, write_kwargs, clear_keys = [], [], [], {}, []
        for p in set_platforms:
            old, new = biz.get(f"founder_{p}", ""), fresh.get(p, "")
            if new == old:
                row_kept.append(p)
            elif new:
                write_kwargs[f"founder_{p}"] = new
                row_changed.append(p)
            else:
                clear_keys.append(f"founder_{p}")
                row_cleared.append(p)

        if not dry_run and (write_kwargs or clear_keys):
            if clear_keys:
                W.clear_fields(sheet_id, tab, biz["row"], clear_keys)
            old_status = statuses.get(biz["row"], "")
            new_status = old_status + f" | Re-verified: changed {row_changed or 'none'}, cleared {row_cleared or 'none'}"
            W.write_row(sheet_id, tab, biz["row"], new_status, **write_kwargs)

        kept_n += len(row_kept)
        changed_n += len(row_changed)
        cleared_n += len(row_cleared)
        results.append({"row": biz["row"], "company": biz["company"], "kept": row_kept,
                        "changed": row_changed, "cleared": row_cleared})
        print(f"row {biz['row']} ({biz['company']}): kept={row_kept} changed={row_changed} cleared={row_cleared}",
              file=sys.stderr)

    return {"checked": len(candidates), "kept": kept_n, "changed": changed_n, "cleared": cleared_n,
            "errors": errors, "results": results}


def _parse_rows(s: str) -> tuple[int, int]:
    a, _, b = s.partition("-")
    return (int(a), int(b or a))


def main():
    p = argparse.ArgumentParser(description="Batch-resolve + write Main-sheet rows (website-first, founders reviewed).")
    p.add_argument("--sheet-id", required=True)
    p.add_argument("--tab", required=True)
    p.add_argument("--limit", type=int, default=12, help="incremental mode: max new rows to process")
    p.add_argument("--rows", type=_parse_rows, default=None, help="reprocess an explicit range, e.g. 2-165")
    p.add_argument("--review-out", type=Path, default=DEFAULT_REVIEW_OUT, help="markdown review-queue path")
    p.add_argument("--dry-run", action="store_true", help="resolve + print, never write to the sheet")
    p.add_argument("--no-resume", action="store_true",
                   help="reprocess mode: redo rows already marked v3: (don't skip them)")
    p.add_argument("--write-founders", default=None,
                   help="write reviewed founders from the queue to the sheet; value = comma list of tiers "
                        "(website,search_low,search_ambiguous) or 'all'. Does no resolving.")
    p.add_argument("--backfill-founder-socials", action="store_true",
                   help="for rows with a Founder name already set, search for any missing founder "
                        "instagram/linkedin/facebook (use with --rows A-B). Does not touch company data.")
    p.add_argument("--reverify-founder-socials", action="store_true",
                   help="re-check EVERY currently-set founder-social value under the person-name-match "
                        "gate (use with --rows A-B); keeps reconfirmed values, replaces or clears the rest.")
    args = p.parse_args()

    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")

    if args.write_founders is not None:
        all_tiers = {"website", "search_low", "search_ambiguous"}
        tiers = all_tiers if args.write_founders.strip().lower() == "all" else \
            {t.strip() for t in args.write_founders.split(",") if t.strip()}
        out = write_founders_from_queue(args.sheet_id, args.tab,
                                        args.review_out.with_suffix(".jsonl"), tiers, dry_run=args.dry_run)
        print(json.dumps(out, indent=2, ensure_ascii=False))
        return

    if args.backfill_founder_socials:
        if not args.rows:
            raise SystemExit("--backfill-founder-socials requires --rows A-B")
        out = backfill_founder_socials(args.sheet_id, args.tab, args.rows[0], args.rows[1],
                                       dry_run=args.dry_run)
        out["results"] = f"[{len(out['results'])} rows]"
        print(json.dumps(out, indent=2, ensure_ascii=False))
        return

    if args.reverify_founder_socials:
        if not args.rows:
            raise SystemExit("--reverify-founder-socials requires --rows A-B")
        out = reverify_founder_socials(args.sheet_id, args.tab, args.rows[0], args.rows[1],
                                       dry_run=args.dry_run)
        out["results"] = f"[{len(out['results'])} rows]"
        print(json.dumps(out, indent=2, ensure_ascii=False))
        return

    out = run(args.sheet_id, args.tab, limit=args.limit, rows=args.rows,
              dry_run=args.dry_run, review_out=args.review_out, no_resume=args.no_resume)
    out["results"] = f"[{len(out['results'])} rows]"  # keep stdout summary compact; details went to stderr
    print(json.dumps(out, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
