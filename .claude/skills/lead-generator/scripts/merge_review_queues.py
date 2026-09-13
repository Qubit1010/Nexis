"""Merge per-worker founder review queues back into the single canonical queue.

run_batch.py appends each row's review evidence to `<review-out>.jsonl` and re-renders the
markdown from that store. Running N workers in parallel therefore needs N separate --review-out
paths (concurrent appends to one jsonl interleave partial lines, and the markdown rewrite races).
This merges those worker stores into the canonical one, keyed by sheet row -- last entry wins --
and re-renders the markdown with run_batch's own renderer, so the queue stays one file.

Usage:
  python merge_review_queues.py --canonical ../../../../docs/lead-generator-review-queue.md \
      --workers ../../../../docs/review-queues/w1.md ... [--dry-run]
"""
import argparse
import json
from pathlib import Path

from run_batch import _render_review_md


def load(jsonl: Path):
    """row -> review dict, last line wins. Skips blank/corrupt lines rather than dying:
    a partially-written line from a killed worker must not lose the other 700 entries."""
    out, bad = {}, 0
    if not jsonl.exists():
        return out, bad
    for line in jsonl.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        try:
            rv = json.loads(line)
        except json.JSONDecodeError:
            bad += 1
            continue
        out[rv.get("row")] = rv
    return out, bad


def merge(canonical_md: Path, worker_mds, dry_run=False):
    canonical_jsonl = canonical_md.with_suffix(".jsonl")
    merged, bad_total = load(canonical_jsonl)
    before = len(merged)
    added_by_worker = {}
    for w in worker_mds:
        rows, bad = load(Path(w).with_suffix(".jsonl"))
        bad_total += bad
        new = len(set(rows) - set(merged))
        added_by_worker[Path(w).stem] = {"entries": len(rows), "new": new}
        merged.update(rows)
    entries = [merged[k] for k in sorted(merged, key=lambda r: (r is None, r))]
    if not dry_run:
        canonical_jsonl.write_text(
            "\n".join(json.dumps(e, ensure_ascii=False) for e in entries) + "\n", encoding="utf-8")
        canonical_md.write_text(_render_review_md(entries), encoding="utf-8")
    return {"before": before, "after": len(merged), "corrupt_lines_skipped": bad_total,
            "by_worker": added_by_worker, "dry_run": dry_run}


def demo():
    import tempfile
    with tempfile.TemporaryDirectory() as d:
        d = Path(d)
        def e(row, company):
            # the shape run_batch actually appends -- row/company/website/founder_guess are
            # load-bearing for _render_review_md, everything else it reads via .get().
            return json.dumps({"row": row, "company": company, "website": "https://x.co",
                               "founder_guess": "Jane Doe"}, ensure_ascii=False)
        (d / "canon.jsonl").write_text(e(2, "A") + "\n" + e(3, "B") + "\n", encoding="utf-8")
        # w1 adds a new row; w2 re-states row 3 (last wins) and carries one corrupt line
        (d / "w1.jsonl").write_text(e(10, "C") + "\n", encoding="utf-8")
        (d / "w2.jsonl").write_text(e(3, "B2") + "\n{oops\n\n", encoding="utf-8")
        r = merge(d / "canon.md", [d / "w1.md", d / "w2.md"])
        assert r["before"] == 2 and r["after"] == 3, r
        assert r["corrupt_lines_skipped"] == 1, r
        assert r["by_worker"]["w1"]["new"] == 1 and r["by_worker"]["w2"]["new"] == 0, r
        back, _ = load(d / "canon.jsonl")
        assert back[3]["company"] == "B2", back  # later worker entry overwrote the canonical one
        assert sorted(back) == [2, 3, 10], sorted(back)
        assert (d / "canon.md").read_text(encoding="utf-8").strip(), "markdown must not be empty"
        # dry-run leaves both files untouched
        r2 = merge(d / "canon.md", [d / "w1.md"], dry_run=True)
        assert r2["dry_run"] and load(d / "canon.jsonl")[0].keys() == back.keys()
    print("merge_review_queues self-check OK")


if __name__ == "__main__":
    p = argparse.ArgumentParser(description="Merge per-worker review queues into the canonical one.")
    p.add_argument("--canonical", type=Path)
    p.add_argument("--workers", type=Path, nargs="*", default=[])
    p.add_argument("--dry-run", action="store_true")
    p.add_argument("--selftest", action="store_true")
    a = p.parse_args()
    if a.selftest:
        demo()
    else:
        if not a.canonical:
            raise SystemExit("--canonical is required (or pass --selftest)")
        print(json.dumps(merge(a.canonical, a.workers, a.dry_run), indent=2))
