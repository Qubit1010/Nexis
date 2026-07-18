"""Upwork weekly funnel from the 'Proposals Timeline' sheet (one row = one proposal)."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config
import sheets
import weekutil


def _col(header, *names):
    """Index of the first header cell containing any of `names` (case-insensitive)."""
    low = [h.strip().lower() for h in header]
    for name in names:
        for i, h in enumerate(low):
            if name in h:
                return i
    return None


def _yes(v):
    return str(v).strip().lower().startswith("yes")


def _int(v):
    try:
        return int(float(str(v).strip()))
    except (ValueError, TypeError):
        return 0


def _rate(part, whole):
    return round(100 * part / whole, 1) if whole else 0.0


def collect(monday, sunday):
    rows = sheets.read_values(config.SHEETS["upwork"]["id"], config.SHEETS["upwork"]["tab"])
    if not rows:
        return {"available": False, "reason": "could not read Proposals Timeline sheet"}
    header, data = rows[0], rows[1:]
    ci = {
        "date": _col(header, "date"),
        "title": _col(header, "job title", "title"),
        "boosted": _col(header, "boosted"),
        "connects": _col(header, "connect"),
        "viewed": _col(header, "viewed"),
        "interview": _col(header, "interview"),
        "hired": _col(header, "hired"),
        "sender": _col(header, "sender"),
    }

    def cell(row, key):
        i = ci[key]
        return row[i] if i is not None and i < len(row) else ""

    proposals = connects = boosted = viewed = interviews = hired = 0
    by_sender = {}
    items = []
    for row in data:
        d = weekutil.parse_ddmmyy(cell(row, "date"))
        if not weekutil.in_week(d, monday, sunday):
            continue
        proposals += 1
        c = _int(cell(row, "connects"))
        connects += c
        b = _yes(cell(row, "boosted"))
        v = _yes(cell(row, "viewed"))
        iv = _yes(cell(row, "interview"))
        hr = _yes(cell(row, "hired"))
        boosted += b
        viewed += v
        interviews += iv
        hired += hr
        s = (str(cell(row, "sender")).strip() or "Unknown")
        agg = by_sender.setdefault(s, {"proposals": 0, "viewed": 0, "interviews": 0, "hired": 0})
        agg["proposals"] += 1
        agg["viewed"] += v
        agg["interviews"] += iv
        agg["hired"] += hr
        # one row per proposal, most-advanced stage as the outcome
        outcome = "hired" if hr else "interview" if iv else "viewed" if v else "sent"
        items.append({
            "date": d.isoformat() if d else None,
            "title": str(cell(row, "title")).strip(),
            "connects": c,
            "boosted": b,
            "sender": s,
            "outcome": outcome,
        })

    items.sort(key=lambda p: p["date"] or "", reverse=True)
    return {
        "available": True,
        "proposals": proposals,
        "connects": connects,
        "dollars": round(connects * config.UPWORK_CONNECT_USD, 2),
        "boosted": boosted,
        "viewed": viewed,
        "view_rate": _rate(viewed, proposals),
        "interviews": interviews,
        "interview_rate": _rate(interviews, proposals),
        "hired": hired,
        "hire_rate": _rate(hired, proposals),
        "by_sender": by_sender,
        "items": items,
    }
