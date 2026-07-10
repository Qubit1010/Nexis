"""Appends qualified leads into an existing "Instant ... Leads" sheet, reusing
leads-to-crm's own sheets.py for the actual gws I/O (same auth, same batching,
same retry-on-transient-error behavior — one code path, not a second one that
could drift). This is the one place all 4 source_*.py scripts share, since
"read the live header, place each field by header name" is identical work
regardless of platform.

Deliberately does NOT touch the "Include to CRM" status column — leaving it
blank is what makes push.py pick these rows up on its next run, same as every
other row that lands in these sheets today.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "leads-to-crm" / "scripts"))
import sheets  # noqa: E402


def append_qualified(sheet_id, tab, leads, field_map):
    """field_map: {exact live header string: lead dict key to read for that column}.
    A header with no entry in field_map is left blank (e.g. "Include to CRM").
    Returns the number of rows appended, or raises on a hard sheets failure."""
    header_rows = sheets.read_values(sheet_id, f"{tab}!1:1")
    header = header_rows[0] if header_rows else []
    if not header:
        raise RuntimeError(f"Could not read header row for {sheet_id} [{tab}] — check the tab name.")

    rows = []
    for lead in leads:
        row = [str(lead.get(field_map[h], "") or "") if h in field_map else "" for h in header]
        rows.append(row)

    if not sheets.append_rows(sheet_id, tab, rows):
        raise RuntimeError(f"Append failed for {sheet_id} [{tab}].")
    return len(rows)
