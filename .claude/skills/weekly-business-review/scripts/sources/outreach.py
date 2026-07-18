"""LinkedIn / Instagram / Facebook outreach volume from the per-channel CRM sheets.

Sent-volume only: the CRMs track Status = New / Sent (accepted/replied/closed are not
recorded anywhere), so per week we report leads added + outreach sent, keyed on
'Date Added'. Founder/Company split where a clean 'Contact Type' column exists.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config
import sheets
import weekutil

CHANNELS = ["linkedin", "instagram", "facebook"]


def _one(channel, monday, sunday):
    cfg = config.SHEETS[channel]
    rows = sheets.read_values(cfg["id"], cfg["tab"])
    if not rows:
        return {"available": False, "reason": f"could not read {channel} CRM"}
    header, data = rows[0], rows[1:]
    di = sheets.header_index(header, ["Date Added"])
    si = sheets.header_index(header, ["Status"])
    ti = sheets.header_index(header, ["Contact Type"])
    ni = sheets.header_index(header, ["Name"])
    ci = sheets.header_index(header, ["Company"])
    ri = sheets.header_index(header, ["Role"])
    ui = sheets.header_index(header, ["LinkedIn URL", "Instagram URL", "Profile URL", "URL"])
    hi = sheets.header_index(header, ["Username"])
    if di is None or si is None:
        return {"available": False, "reason": f"{channel} CRM missing Date Added/Status columns"}

    def get(row, idx):
        return row[idx].strip() if idx is not None and idx < len(row) and row[idx] else ""

    added = sent = 0
    types = {"Founder": 0, "Company": 0}
    leads = []
    for row in data:
        d = weekutil.parse_iso(row[di]) if di < len(row) else None
        if not weekutil.in_week(d, monday, sunday):
            continue
        added += 1
        status = (row[si].strip().lower() if si < len(row) else "")
        if status == "sent":
            sent += 1
        ctype = ""
        if ti is not None and ti < len(row):
            t = row[ti].strip().lower()
            if t == "founder":
                types["Founder"] += 1
                ctype = "Founder"
            elif t == "company":
                types["Company"] += 1
                ctype = "Company"
        leads.append({
            "name": get(row, ni),
            "company": get(row, ci),
            "role": get(row, ri),
            "url": get(row, ui),
            "handle": get(row, hi),
            "type": ctype,
            "status": row[si].strip() if si < len(row) else "",
            "date": d.isoformat() if d else None,
        })

    leads.sort(key=lambda x: x["date"] or "", reverse=True)
    out = {"available": True, "added": added, "sent": sent, "leads": leads}
    if ti is not None and (types["Founder"] or types["Company"]):
        out["by_type"] = types
    return out


def collect(monday, sunday):
    channels = {c: _one(c, monday, sunday) for c in CHANNELS}
    totals = {
        "added": sum(v.get("added", 0) for v in channels.values() if v.get("available")),
        "sent": sum(v.get("sent", 0) for v in channels.values() if v.get("available")),
    }
    return {"available": True, "channels": channels, "totals": totals}
