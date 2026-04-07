"""Google Sheets exporter — pushes leads to existing outreach CRMs.

Exports to 3 existing CRM sheets with exact column mapping:
  Cold Email CRM  → "Enriched Leads" tab
  LinkedIn CRM    → "Leads" tab
  Instagram CRM   → "Leads" tab

CRM sheet IDs are resolved by name on first run and cached in the DB.
Export flags in the DB prevent double-exporting (idempotent).
"""

import json
import os
import shutil
import subprocess
import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from config import CRM_SHEET_NAMES, CRM_TABS, CRM_COLUMNS, EXPORT_TIERS
from database import (
    get_leads, get_enrichment, get_personalization, get_sequence,
    already_exported, mark_exported, get_config, set_config
)

# ---------------------------------------------------------------------------
# gws CLI helpers (same pattern as cold-outreach gws_utils.py)
# ---------------------------------------------------------------------------

def find_gws():
    npm_dir = Path(os.environ.get("APPDATA", "")) / "npm"
    gws_js = npm_dir / "node_modules" / "@googleworkspace" / "cli" / "run-gws.js"

    if gws_js.exists():
        for candidate in [
            npm_dir / "node.exe",
            Path(os.environ.get("ProgramFiles", "C:\\Program Files")) / "nodejs" / "node.exe",
            Path(os.environ.get("ProgramFiles(x86)", "C:\\Program Files (x86)")) / "nodejs" / "node.exe",
        ]:
            if candidate.exists():
                return ([str(candidate), str(gws_js)], False)
        node = shutil.which("node")
        if node:
            return ([node, str(gws_js)], False)

    gws = shutil.which("gws")
    if gws:
        return ([gws], True)
    gws_cmd = npm_dir / "gws.cmd"
    if gws_cmd.exists():
        return ([str(gws_cmd)], True)
    return (["gws"], True)


GWS_CMD, GWS_USE_SHELL = find_gws()


def run_gws(args, json_body=None):
    cmd = GWS_CMD + args
    if json_body is not None:
        cmd += ["--json", json.dumps(json_body)]
    result = subprocess.run(
        cmd, capture_output=True, text=True, timeout=120,
        shell=GWS_USE_SHELL, encoding="utf-8", errors="replace"
    )
    if result.returncode != 0:
        stderr = result.stderr.strip() if result.stderr else "Unknown error"
        raise RuntimeError(f"gws failed: {' '.join(str(a) for a in args[:3])} | {stderr}")
    stdout = result.stdout.strip()
    if not stdout:
        return {}
    try:
        return json.loads(stdout)
    except json.JSONDecodeError:
        return {"raw": stdout}


def get_sheet_id(platform: str) -> str | None:
    """Get or resolve sheet ID for a CRM platform.

    Cached in DB as 'sheet_id_<platform>'. Resolves by sheet name on first call.
    """
    cache_key = f"sheet_id_{platform}"
    cached = get_config(cache_key)
    if cached:
        return cached

    sheet_name = CRM_SHEET_NAMES.get(platform)
    if not sheet_name:
        return None

    print(f"  Looking up sheet: {sheet_name}...", flush=True)
    try:
        result = run_gws([
            "drive", "files", "list",
            "--params", json.dumps({
                "q": f"name='{sheet_name}' and mimeType='application/vnd.google-apps.spreadsheet' and trashed=false",
                "fields": "files(id,name)"
            })
        ])
        files = result.get("files", [])
        if files:
            sheet_id = files[0]["id"]
            set_config(cache_key, sheet_id)
            print(f"  Found sheet {sheet_name}: {sheet_id}", flush=True)
            return sheet_id
    except RuntimeError as exc:
        print(f"  Could not find sheet '{sheet_name}': {exc}", flush=True)
    return None


def append_rows_to_sheet(sheet_id: str, tab: str, rows: list[list]) -> bool:
    """Append rows to a Google Sheet tab."""
    if not rows:
        return True
    try:
        run_gws(
            ["sheets", "spreadsheets", "values", "append",
             "--params", json.dumps({
                 "spreadsheetId": sheet_id,
                 "range": f"{tab}!A1",
                 "valueInputOption": "RAW",
                 "insertDataOption": "INSERT_ROWS"
             })],
            json_body={"values": rows}
        )
        return True
    except RuntimeError as exc:
        print(f"  Failed to append rows to {tab}: {exc}", flush=True)
        return False


# ---------------------------------------------------------------------------
# Lead → CRM row mapping
# ---------------------------------------------------------------------------

def lead_to_cold_email_row(lead: dict) -> list:
    """Map lead dict to Cold Email CRM 'Enriched Leads' column order."""
    # CRM_COLUMNS["cold_email"]:
    # First Name, Last Name, Title, Company, Email, Verified,
    # LinkedIn URL, Pain Signal, Enrolled,
    # Email 1 Date, Email 2 Date, Email 3 Date, Email 4 Date,
    # Status, Reply Date, Source
    return [
        lead.get("first_name", ""),
        lead.get("last_name", ""),
        lead.get("title", ""),
        lead.get("company", ""),
        lead.get("email", ""),
        lead.get("email_verified", ""),
        lead.get("linkedin_url", ""),
        lead.get("pain_signal", ""),
        "",   # Enrolled
        "",   # Email 1 Date
        "",   # Email 2 Date
        "",   # Email 3 Date
        "",   # Email 4 Date
        "Unprocessed",  # Status
        "",   # Reply Date
        "lead-gen",  # Source
    ]


def lead_to_linkedin_row(lead: dict) -> list:
    """Map lead dict to LinkedIn CRM 'Leads' column order."""
    # CRM_COLUMNS["linkedin"]:
    # Name, First Name, Company, Role, LinkedIn URL,
    # Location, Recent Post, Connection Message, Status, Date Added
    full_name = lead.get("full_name") or f"{lead.get('first_name', '')} {lead.get('last_name', '')}".strip()

    # Get connection note from outreach sequence if available
    connection_message = ""
    sequence = get_sequence(lead.get("lead_id", ""), "linkedin")
    if sequence and sequence.get("sequence_json"):
        seq_data = sequence["sequence_json"]
        if isinstance(seq_data, dict):
            connection_message = seq_data.get("connection_note", "")

    return [
        full_name,
        lead.get("first_name", ""),
        lead.get("company", ""),
        lead.get("title", ""),
        lead.get("linkedin_url", ""),
        lead.get("location", ""),
        lead.get("recent_activity", "")[:200] if lead.get("recent_activity") else "",
        connection_message,
        "New",
        date.today().isoformat(),
    ]


def lead_to_instagram_row(lead: dict) -> list:
    """Map lead dict to Instagram CRM 'Leads' column order."""
    # CRM_COLUMNS["instagram"]:
    # Name, Username, Company, Role, Instagram URL,
    # Followers, Bio, Touch 1 Message, Status, Date Added
    full_name = lead.get("full_name") or f"{lead.get('first_name', '')} {lead.get('last_name', '')}".strip()

    # Get Touch 1 DM from sequence if available
    touch_1 = ""
    sequence = get_sequence(lead.get("lead_id", ""), "instagram")
    if sequence and sequence.get("sequence_json"):
        seq_data = sequence["sequence_json"]
        if isinstance(seq_data, dict):
            dms = seq_data.get("dms", [])
            if dms:
                touch_1 = dms[0].get("text", "")

    # Get bio from enrichment
    bio = ""
    enrichment = get_enrichment(lead.get("lead_id", ""))
    if enrichment:
        proxycurl = enrichment.get("proxycurl_data", {})
        if isinstance(proxycurl, dict):
            bio = proxycurl.get("summary", "")[:300] or ""

    return [
        full_name,
        lead.get("instagram_handle", ""),
        lead.get("company", ""),
        lead.get("title", ""),
        lead.get("instagram_url", ""),
        "",  # Followers (not stored currently)
        bio,
        touch_1,
        "New",
        date.today().isoformat(),
    ]


# ---------------------------------------------------------------------------
# Main export functions
# ---------------------------------------------------------------------------

def export_to_cold_email(dry_run: bool = False) -> dict:
    """Export HOT/STRONG/WARM leads to Cold Email CRM."""
    sheet_id = get_sheet_id("cold_email")
    if not sheet_id:
        print("  Cold Email CRM not found — skipping.", flush=True)
        return {"exported": 0, "skipped": 0}

    tab = CRM_TABS["cold_email"]
    eligible_tiers = EXPORT_TIERS["cold_email"]

    leads = get_leads(filters={"tier_in": eligible_tiers})
    rows_to_export = []
    exported_ids = []

    for lead in leads:
        lead_id = lead["lead_id"]
        if already_exported(lead_id, "cold_email", "sheets"):
            continue
        if not lead.get("email"):
            if not dry_run:
                mark_exported(lead_id, "cold_email", "sheets", "skipped_no_contact")
            continue

        row = lead_to_cold_email_row(lead)
        rows_to_export.append(row)
        exported_ids.append(lead_id)

    if dry_run:
        print(f"  [DRY RUN] Would export {len(rows_to_export)} leads to Cold Email CRM")
        return {"exported": len(rows_to_export), "skipped": 0}

    if rows_to_export:
        success = append_rows_to_sheet(sheet_id, tab, rows_to_export)
        if success:
            for lead_id in exported_ids:
                mark_exported(lead_id, "cold_email", "sheets", "exported")
            print(f"  Cold Email CRM: exported {len(rows_to_export)} leads.", flush=True)
        else:
            return {"exported": 0, "error": "Sheet write failed"}

    return {"exported": len(rows_to_export), "skipped": 0}


def export_to_linkedin(dry_run: bool = False) -> dict:
    """Export HOT/STRONG leads to LinkedIn CRM."""
    sheet_id = get_sheet_id("linkedin")
    if not sheet_id:
        print("  LinkedIn CRM not found — skipping.", flush=True)
        return {"exported": 0, "skipped": 0}

    tab = CRM_TABS["linkedin"]
    eligible_tiers = EXPORT_TIERS["linkedin"]

    leads = get_leads(filters={"tier_in": eligible_tiers})
    rows_to_export = []
    exported_ids = []

    for lead in leads:
        lead_id = lead["lead_id"]
        if already_exported(lead_id, "linkedin", "sheets"):
            continue
        if not lead.get("linkedin_url"):
            if not dry_run:
                mark_exported(lead_id, "linkedin", "sheets", "skipped_no_contact")
            continue

        row = lead_to_linkedin_row(lead)
        rows_to_export.append(row)
        exported_ids.append(lead_id)

    if dry_run:
        print(f"  [DRY RUN] Would export {len(rows_to_export)} leads to LinkedIn CRM")
        return {"exported": len(rows_to_export), "skipped": 0}

    if rows_to_export:
        success = append_rows_to_sheet(sheet_id, tab, rows_to_export)
        if success:
            for lead_id in exported_ids:
                mark_exported(lead_id, "linkedin", "sheets", "exported")
            print(f"  LinkedIn CRM: exported {len(rows_to_export)} leads.", flush=True)

    return {"exported": len(rows_to_export), "skipped": 0}


def export_to_instagram(dry_run: bool = False) -> dict:
    """Export HOT leads (with instagram_url) to Instagram CRM."""
    sheet_id = get_sheet_id("instagram")
    if not sheet_id:
        print("  Instagram CRM not found — skipping.", flush=True)
        return {"exported": 0, "skipped": 0}

    tab = CRM_TABS["instagram"]
    eligible_tiers = EXPORT_TIERS["instagram"]

    leads = get_leads(filters={"tier_in": eligible_tiers})
    rows_to_export = []
    exported_ids = []
    skipped_no_url = 0

    for lead in leads:
        lead_id = lead["lead_id"]
        if already_exported(lead_id, "instagram", "sheets"):
            continue
        if not lead.get("instagram_url"):
            skipped_no_url += 1
            if not dry_run:
                mark_exported(lead_id, "instagram", "sheets", "skipped_no_contact")
            continue

        row = lead_to_instagram_row(lead)
        rows_to_export.append(row)
        exported_ids.append(lead_id)

    if dry_run:
        print(f"  [DRY RUN] Would export {len(rows_to_export)} leads to Instagram CRM (skipped {skipped_no_url} without Instagram URL)")
        return {"exported": len(rows_to_export), "skipped": skipped_no_url}

    if rows_to_export:
        success = append_rows_to_sheet(sheet_id, tab, rows_to_export)
        if success:
            for lead_id in exported_ids:
                mark_exported(lead_id, "instagram", "sheets", "exported")
            print(f"  Instagram CRM: exported {len(rows_to_export)} leads.", flush=True)

    return {"exported": len(rows_to_export), "skipped": skipped_no_url}


def run_export(platform: str = "all", dry_run: bool = False) -> dict:
    """Export leads to specified platform CRM(s).

    Args:
        platform: "cold_email" | "linkedin" | "instagram" | "all"
        dry_run: If True, print what would be exported without writing

    Returns:
        Summary dict
    """
    results = {}

    if platform in ("cold_email", "cold-email", "cold", "all"):
        results["cold_email"] = export_to_cold_email(dry_run=dry_run)

    if platform in ("linkedin", "all"):
        results["linkedin"] = export_to_linkedin(dry_run=dry_run)

    if platform in ("instagram", "all"):
        results["instagram"] = export_to_instagram(dry_run=dry_run)

    return results
