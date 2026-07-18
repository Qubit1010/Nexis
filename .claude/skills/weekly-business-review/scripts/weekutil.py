"""Week boundaries + per-source date parsing.

Weeks are ISO Mon-Sun. The Monday's date (YYYY-MM-DD) is the week key / snapshot
filename; the ISO label (2026-W29) is for display.
"""
from datetime import date, datetime, timedelta


def week_bounds(anchor):
    """(monday_date, sunday_date, week_key, label) for the ISO week containing `anchor`."""
    if isinstance(anchor, str):
        anchor = datetime.strptime(anchor, "%Y-%m-%d").date()
    monday = anchor - timedelta(days=anchor.weekday())
    sunday = monday + timedelta(days=6)
    iso_year, iso_week, _ = anchor.isocalendar()
    return monday, sunday, monday.isoformat(), f"{iso_year}-W{iso_week:02d}"


def prev_week_key(week_key):
    monday = datetime.strptime(week_key, "%Y-%m-%d").date()
    return (monday - timedelta(days=7)).isoformat()


def in_week(d, monday, sunday):
    return d is not None and monday <= d <= sunday


def parse_iso(s):
    """CRM 'Date Added' style: 2026-07-14 (tolerates a trailing time)."""
    if not s:
        return None
    s = str(s).strip()[:10]
    try:
        return datetime.strptime(s, "%Y-%m-%d").date()
    except ValueError:
        return None


def parse_ddmmyy(s):
    """Upwork 'Date' col: D/M/YY (e.g. 22/6/26 -> 2026-06-22, 7/7/26 -> 2026-07-07).

    Day-first is unambiguous in the sheet (values like 22/6 rule out month-first).
    """
    if not s:
        return None
    s = str(s).strip()
    for sep in ("/", "-", "."):
        if sep in s:
            parts = s.split(sep)
            break
    else:
        return None
    if len(parts) != 3:
        return None
    try:
        d, m, y = (int(p) for p in parts)
    except ValueError:
        return None
    if y < 100:
        y += 2000
    try:
        return date(y, m, d)
    except ValueError:
        return None


if __name__ == "__main__":
    # ponytail self-check: the two date parsers + week math on known values.
    assert parse_ddmmyy("22/6/26") == date(2026, 6, 22)
    assert parse_ddmmyy("7/7/26") == date(2026, 7, 7)
    assert parse_ddmmyy("garbage") is None
    assert parse_iso("2026-07-14") == date(2026, 7, 14)
    assert parse_iso("2026-07-14 13:05") == date(2026, 7, 14)
    mon, sun, key, label = week_bounds("2026-07-17")  # a Friday
    assert (mon.isoformat(), sun.isoformat(), key) == ("2026-07-13", "2026-07-19", "2026-07-13"), (mon, sun, key)
    assert label == "2026-W29", label
    assert prev_week_key("2026-07-13") == "2026-07-06"
    assert in_week(date(2026, 7, 17), mon, sun) and not in_week(date(2026, 7, 20), mon, sun)
    print("weekutil self-check OK")
