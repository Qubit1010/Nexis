"""CSV exporter — generates platform-ready CSV files for Instantly/Lemlist/Waalaxy.

Output files go to projects/lead-gen/exports/ directory.
"""

import csv
import json
import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from database import get_leads, get_personalization, get_sequence, get_enrichment
from config import EXPORT_TIERS

EXPORTS_DIR = Path(__file__).resolve().parent.parent / "exports"


def ensure_exports_dir():
    EXPORTS_DIR.mkdir(exist_ok=True)


def export_cold_email_csv(dry_run: bool = False) -> Path | None:
    """Export cold email leads as CSV for Instantly/Lemlist/Smartlead."""
    ensure_exports_dir()
    leads = get_leads(filters={"tier_in": EXPORT_TIERS["cold_email"]})
    leads = [l for l in leads if l.get("email")]

    if not leads:
        print("  No email leads to export.", flush=True)
        return None

    today = date.today().strftime("%Y%m%d")
    output_path = EXPORTS_DIR / f"cold_email_{today}.csv"

    if dry_run:
        print(f"  [DRY RUN] Would export {len(leads)} leads to {output_path}")
        return output_path

    fieldnames = [
        "first_name", "last_name", "email", "company", "website",
        "title", "industry", "linkedin_url", "pain_signal",
        "hook_1", "hook_2", "value_prop",
        "email_1_subject", "email_1_body",
        "email_2_body", "email_3_body", "email_4_body",
        "score", "tier", "source"
    ]

    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()

        for lead in leads:
            lead_id = lead["lead_id"]
            personalization = get_personalization(lead_id) or {}
            sequence = get_sequence(lead_id, "cold_email")
            seq_data = {}
            if sequence and sequence.get("sequence_json"):
                seq_data = sequence["sequence_json"]
                if isinstance(seq_data, str):
                    try:
                        seq_data = json.loads(seq_data)
                    except (json.JSONDecodeError, TypeError):
                        seq_data = {}

            emails = seq_data.get("emails", [])
            e1 = emails[0] if len(emails) > 0 else {}
            e2 = emails[1] if len(emails) > 1 else {}
            e3 = emails[2] if len(emails) > 2 else {}
            e4 = emails[3] if len(emails) > 3 else {}

            writer.writerow({
                "first_name": lead.get("first_name", ""),
                "last_name": lead.get("last_name", ""),
                "email": lead.get("email", ""),
                "company": lead.get("company", ""),
                "website": lead.get("company_website", ""),
                "title": lead.get("title", ""),
                "industry": lead.get("industry", ""),
                "linkedin_url": lead.get("linkedin_url", ""),
                "pain_signal": lead.get("pain_signal", ""),
                "hook_1": personalization.get("hook_1", ""),
                "hook_2": personalization.get("hook_2", ""),
                "value_prop": personalization.get("value_prop", ""),
                "email_1_subject": e1.get("subject_options", [""])[0] if e1 else "",
                "email_1_body": e1.get("body", "") if e1 else "",
                "email_2_body": e2.get("body", "") if e2 else "",
                "email_3_body": e3.get("body", "") if e3 else "",
                "email_4_body": e4.get("body", "") if e4 else "",
                "score": lead.get("total_score", ""),
                "tier": lead.get("tier", ""),
                "source": lead.get("source", ""),
            })

    print(f"  Cold email CSV: {output_path} ({len(leads)} leads)", flush=True)
    return output_path


def export_linkedin_csv(dry_run: bool = False) -> Path | None:
    """Export LinkedIn leads as CSV for Dripify/Waalaxy."""
    ensure_exports_dir()
    leads = get_leads(filters={"tier_in": EXPORT_TIERS["linkedin"]})
    leads = [l for l in leads if l.get("linkedin_url")]

    if not leads:
        print("  No LinkedIn leads to export.", flush=True)
        return None

    today = date.today().strftime("%Y%m%d")
    output_path = EXPORTS_DIR / f"linkedin_{today}.csv"

    if dry_run:
        print(f"  [DRY RUN] Would export {len(leads)} leads to {output_path}")
        return output_path

    fieldnames = [
        "first_name", "last_name", "full_name", "title", "company",
        "linkedin_url", "location", "connection_note",
        "dm_1", "dm_2", "dm_3", "dm_4",
        "score", "tier"
    ]

    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()

        for lead in leads:
            lead_id = lead["lead_id"]
            sequence = get_sequence(lead_id, "linkedin")
            seq_data = {}
            if sequence and sequence.get("sequence_json"):
                seq_data = sequence["sequence_json"]
                if isinstance(seq_data, str):
                    try:
                        seq_data = json.loads(seq_data)
                    except (json.JSONDecodeError, TypeError):
                        seq_data = {}

            dms = seq_data.get("dms", [])

            writer.writerow({
                "first_name": lead.get("first_name", ""),
                "last_name": lead.get("last_name", ""),
                "full_name": lead.get("full_name", ""),
                "title": lead.get("title", ""),
                "company": lead.get("company", ""),
                "linkedin_url": lead.get("linkedin_url", ""),
                "location": lead.get("location", ""),
                "connection_note": seq_data.get("connection_note", ""),
                "dm_1": dms[0]["text"] if len(dms) > 0 else "",
                "dm_2": dms[1]["text"] if len(dms) > 1 else "",
                "dm_3": dms[2]["text"] if len(dms) > 2 else "",
                "dm_4": dms[3]["text"] if len(dms) > 3 else "",
                "score": lead.get("total_score", ""),
                "tier": lead.get("tier", ""),
            })

    print(f"  LinkedIn CSV: {output_path} ({len(leads)} leads)", flush=True)
    return output_path


def export_instagram_csv(dry_run: bool = False) -> Path | None:
    """Export Instagram leads as CSV."""
    ensure_exports_dir()
    leads = get_leads(filters={"tier_in": EXPORT_TIERS["instagram"]})
    leads = [l for l in leads if l.get("instagram_url")]

    if not leads:
        print("  No Instagram leads to export.", flush=True)
        return None

    today = date.today().strftime("%Y%m%d")
    output_path = EXPORTS_DIR / f"instagram_{today}.csv"

    if dry_run:
        print(f"  [DRY RUN] Would export {len(leads)} leads to {output_path}")
        return output_path

    fieldnames = [
        "full_name", "instagram_handle", "instagram_url",
        "company", "title", "dm_1", "dm_2", "dm_3", "dm_4",
        "pre_engagement_plan", "score", "tier"
    ]

    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()

        for lead in leads:
            lead_id = lead["lead_id"]
            sequence = get_sequence(lead_id, "instagram")
            seq_data = {}
            if sequence and sequence.get("sequence_json"):
                seq_data = sequence["sequence_json"]
                if isinstance(seq_data, str):
                    try:
                        seq_data = json.loads(seq_data)
                    except (json.JSONDecodeError, TypeError):
                        seq_data = {}

            dms = seq_data.get("dms", [])
            plan = seq_data.get("pre_dm_engagement", [])
            plan_text = " | ".join(
                f"Day {p['day']}: {p['action']}" for p in plan
            ) if plan else ""

            writer.writerow({
                "full_name": lead.get("full_name", ""),
                "instagram_handle": lead.get("instagram_handle", ""),
                "instagram_url": lead.get("instagram_url", ""),
                "company": lead.get("company", ""),
                "title": lead.get("title", ""),
                "dm_1": dms[0]["text"] if len(dms) > 0 else "",
                "dm_2": dms[1]["text"] if len(dms) > 1 else "",
                "dm_3": dms[2]["text"] if len(dms) > 2 else "",
                "dm_4": dms[3]["text"] if len(dms) > 3 else "",
                "pre_engagement_plan": plan_text,
                "score": lead.get("total_score", ""),
                "tier": lead.get("tier", ""),
            })

    print(f"  Instagram CSV: {output_path} ({len(leads)} leads)", flush=True)
    return output_path


def run_csv_export(platform: str = "all", dry_run: bool = False) -> list[Path]:
    """Export leads to CSV files for the specified platform.

    Args:
        platform: "cold_email" | "cold" | "linkedin" | "instagram" | "all"
        dry_run: Print what would be exported without writing files

    Returns:
        List of output file paths
    """
    outputs = []

    if platform in ("cold_email", "cold", "all"):
        path = export_cold_email_csv(dry_run=dry_run)
        if path:
            outputs.append(path)

    if platform in ("linkedin", "all"):
        path = export_linkedin_csv(dry_run=dry_run)
        if path:
            outputs.append(path)

    if platform in ("instagram", "all"):
        path = export_instagram_csv(dry_run=dry_run)
        if path:
            outputs.append(path)

    return outputs
