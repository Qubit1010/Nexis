"""Cross-source lead deduplication utilities."""

import re


def normalize_company(name: str) -> str:
    """Normalize company name for dedup comparison.

    Strips punctuation, lowercases, and removes common suffixes like
    Inc, LLC, Ltd, Corp, etc.
    """
    if not name:
        return ""
    n = name.lower().strip()
    # Remove common legal suffixes
    n = re.sub(r'\b(inc|llc|ltd|corp|co|company|technologies|tech|solutions|group|labs|io|ai|hq)\b', '', n)
    # Remove all non-alphanumeric characters
    n = re.sub(r'[^a-z0-9]', '', n)
    return n


def normalize_name(name: str) -> str:
    """Normalize a person's first name for dedup."""
    if not name:
        return ""
    return name.lower().strip().split()[0] if name.strip() else ""


def dedup_lead_list(leads: list[dict], existing_keys: set = None) -> tuple[list[dict], int]:
    """Deduplicate a list of lead dicts before writing to DB.

    Dedup keys (in priority order):
    1. linkedin_url (most reliable — exact match)
    2. normalize(company) + normalize(first_name)

    Args:
        leads: List of lead dicts
        existing_keys: Set of already-known keys from the DB (optional)

    Returns:
        (unique_leads, skipped_count) tuple
    """
    seen_linkedin = set()
    seen_company_name = set()
    skipped = 0
    unique = []

    if existing_keys:
        # Pre-populate seen sets from existing DB keys
        for key in existing_keys:
            if key.startswith("li:"):
                seen_linkedin.add(key[3:])
            elif key.startswith("cn:"):
                seen_company_name.add(key[3:])

    for lead in leads:
        linkedin = (lead.get("linkedin_url") or "").strip()
        company = normalize_company(lead.get("company", ""))
        first = normalize_name(lead.get("first_name", ""))
        cn_key = f"{company}_{first}"

        # Check LinkedIn URL dedup
        if linkedin and linkedin in seen_linkedin:
            skipped += 1
            continue

        # Check company+name dedup
        if cn_key and cn_key != "_" and cn_key in seen_company_name:
            skipped += 1
            continue

        # Not a duplicate — add to results and update seen sets
        if linkedin:
            seen_linkedin.add(linkedin)
        if cn_key and cn_key != "_":
            seen_company_name.add(cn_key)

        unique.append(lead)

    return unique, skipped


def build_existing_keys_from_db() -> set:
    """Load existing lead keys from the DB for dedup checking.

    Returns a set of strings like:
      "li:https://linkedin.com/in/john-doe"
      "cn:acmecorp_john"
    """
    # Import here to avoid circular imports
    from database import get_connection
    keys = set()
    conn = get_connection()
    try:
        rows = conn.execute(
            "SELECT linkedin_url, company, first_name FROM leads"
        ).fetchall()
        for row in rows:
            if row["linkedin_url"]:
                keys.add(f"li:{row['linkedin_url']}")
            company = normalize_company(row["company"] or "")
            first = normalize_name(row["first_name"] or "")
            if company:
                keys.add(f"cn:{company}_{first}")
    finally:
        conn.close()
    return keys
