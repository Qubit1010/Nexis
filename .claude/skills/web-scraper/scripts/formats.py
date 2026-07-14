"""Output shaping: dedup rows, then render json | csv | md. Also jsonl for ML corpora.

Dedup keeps first occurrence (Q3/Q5 finding: dedup AFTER cleaning, keep the earliest/best row).
csv unions all keys across rows so ragged rows don't lose columns.
"""
from __future__ import annotations

import csv
import io
import json


def dedup(rows: list[dict], *, key: str | list[str] | None = None) -> list[dict]:
    """Drop duplicate rows, keeping first seen. key = field(s) to dedup on; None = whole-row."""
    keys = [key] if isinstance(key, str) else key
    seen, out = set(), []
    for r in rows:
        if keys:
            sig = tuple((r.get(k) or "").strip().lower() if isinstance(r.get(k), str) else r.get(k) for k in keys)
        else:
            sig = json.dumps(r, sort_keys=True, default=str)
        if sig in seen:
            continue
        seen.add(sig)
        out.append(r)
    return out


def to_csv(rows: list[dict]) -> str:
    if not rows:
        return ""
    cols: list[str] = []
    for r in rows:  # union of keys, first-seen order
        for k in r:
            if k not in cols:
                cols.append(k)
    buf = io.StringIO()
    w = csv.DictWriter(buf, fieldnames=cols, extrasaction="ignore")
    w.writeheader()
    for r in rows:
        w.writerow({k: r.get(k, "") for k in cols})
    return buf.getvalue()


def to_jsonl(rows: list[dict]) -> str:
    return "\n".join(json.dumps(r, ensure_ascii=False, default=str) for r in rows)


def to_md(rows: list[dict]) -> str:
    if not rows:
        return ""
    cols: list[str] = []
    for r in rows:
        for k in r:
            if k not in cols:
                cols.append(k)
    lines = ["| " + " | ".join(cols) + " |", "| " + " | ".join("---" for _ in cols) + " |"]
    for r in rows:
        lines.append("| " + " | ".join(str(r.get(c, "")).replace("\n", " ").replace("|", "\\|") for c in cols) + " |")
    return "\n".join(lines)


def render(rows: list[dict], fmt: str) -> str:
    if fmt == "json":
        return json.dumps(rows, ensure_ascii=False, indent=2, default=str)
    if fmt == "jsonl":
        return to_jsonl(rows)
    if fmt == "csv":
        return to_csv(rows)
    if fmt == "md":
        return to_md(rows)
    raise ValueError(f"unknown format: {fmt}")


if __name__ == "__main__":
    rows = [{"name": "A", "url": "u1"}, {"name": "A", "url": "u1"}, {"name": "B", "city": "SD"}]
    assert len(dedup(rows)) == 2, dedup(rows)
    assert len(dedup(rows, key="name")) == 2, "name-key dedup"
    csv_out = to_csv(dedup(rows))
    assert "name,url,city" in csv_out, csv_out          # ragged union
    assert render(rows, "jsonl").count("\n") == 2, "jsonl lines"
    assert render(dedup(rows), "md").startswith("| name | url | city |"), render(dedup(rows), "md")
    print("formats self-check OK")
