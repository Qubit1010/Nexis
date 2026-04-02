#!/usr/bin/env python3
"""Find and verify email addresses for leads in the CRM.

For each lead in Raw Leads with Status = "Unprocessed":
1. Extracts company domain from LinkedIn URL or company website
2. Guesses email patterns (first@domain, first.last@domain, etc.)
3. Verifies via SMTP handshake (no email sent)
4. Writes verified email + Status="Ready" to Enriched Leads tab

Usage:
    python find_emails.py              # process up to 50 unprocessed leads
    python find_emails.py --limit 20   # process fewer
    python find_emails.py --test       # dry run, print emails without saving
"""

import argparse
import json
import re
import smtplib
import socket
import sys
import time
from datetime import date
from pathlib import Path

# dnspython for MX record lookup
try:
    import dns.resolver
    HAS_DNS = True
except ImportError:
    HAS_DNS = False
    print("Warning: dnspython not installed. Install with: pip install dnspython", file=sys.stderr)
    print("Falling back to direct SMTP connections (less accurate).", file=sys.stderr)

sys.path.insert(0, str(Path(__file__).resolve().parent))
from gws_utils import (
    get_or_create_sheet, append_rows, read_all_rows, update_cell,
    TAB_RAW, TAB_ENRICHED, RAW_HEADERS, ENRICHED_HEADERS,
    col_index, col_letter
)

# SMTP verification constants
SMTP_TIMEOUT = 10
SMTP_FROM = "verify@nexuspoint.io"  # fake sender for RCPT check
MAX_RETRIES = 2


# ---------------------------------------------------------------------------
# Domain extraction
# ---------------------------------------------------------------------------

def extract_domain(linkedin_url):
    """Try to get a company's email domain from their LinkedIn company URL.

    LinkedIn company URLs look like: linkedin.com/company/company-name
    We attempt to guess the domain from the slug. This is imperfect but works
    for most companies that use their company name as their domain.
    """
    if not linkedin_url:
        return None

    # Extract company slug from LinkedIn URL
    match = re.search(r'linkedin\.com/company/([^/?&\s]+)', linkedin_url, re.IGNORECASE)
    if not match:
        return None

    slug = match.group(1).rstrip("/").lower()
    # Normalize: remove common suffixes like -inc, -llc, -ltd, -co
    slug = re.sub(r'[-_](inc|llc|ltd|corp|co|company|technologies|tech|solutions|group|labs|io)$', '', slug)
    # Convert hyphens to nothing (most domains don't have hyphens from the slug)
    domain_guess = slug.replace("-", "") + ".com"
    return domain_guess


def get_mx_server(domain):
    """Get primary MX server for a domain."""
    if not HAS_DNS:
        return domain  # fallback: try domain directly

    try:
        records = dns.resolver.resolve(domain, "MX")
        # Sort by preference (lowest = most preferred)
        sorted_records = sorted(records, key=lambda r: r.preference)
        return str(sorted_records[0].exchange).rstrip(".")
    except Exception:
        return None


# ---------------------------------------------------------------------------
# Email pattern generation
# ---------------------------------------------------------------------------

def generate_patterns(first_name, last_name, domain):
    """Generate candidate email addresses in priority order."""
    first = first_name.lower().strip() if first_name else ""
    last = last_name.lower().strip() if last_name else ""

    if not first or not domain:
        return [f"contact@{domain}", f"hello@{domain}", f"info@{domain}"]

    patterns = []

    if first and last:
        patterns = [
            f"{first}@{domain}",
            f"{first}.{last}@{domain}",
            f"{first}{last}@{domain}",
            f"{first[0]}{last}@{domain}",
            f"{first}_{last}@{domain}",
            f"{last}@{domain}",
            f"{first[0]}.{last}@{domain}",
        ]
    else:
        patterns = [
            f"{first}@{domain}",
            f"contact@{domain}",
            f"hello@{domain}",
            f"info@{domain}",
        ]

    # Always add generic fallbacks
    patterns += [f"contact@{domain}", f"hello@{domain}", f"info@{domain}"]

    # Deduplicate while preserving order
    seen = set()
    unique = []
    for p in patterns:
        if p not in seen:
            seen.add(p)
            unique.append(p)

    return unique


# ---------------------------------------------------------------------------
# SMTP verification
# ---------------------------------------------------------------------------

SMTP_CACHE = {}  # domain -> (mx_server, is_catchall)


def check_catchall(mx_server, domain):
    """Test if domain accepts any email (catch-all). Returns True if catch-all."""
    fake_email = f"definitelynotreal12345@{domain}"
    result = smtp_verify_single(mx_server, fake_email)
    return result == "valid"  # if fake email is "valid", it's a catch-all


def smtp_verify_single(mx_server, email):
    """Check a single email via SMTP. Returns 'valid', 'invalid', or 'unknown'."""
    if not mx_server:
        return "unknown"

    for attempt in range(MAX_RETRIES):
        try:
            with smtplib.SMTP(timeout=SMTP_TIMEOUT) as smtp:
                smtp.connect(mx_server, 25)
                smtp.ehlo("nexuspoint.io")
                smtp.mail(SMTP_FROM)
                code, _ = smtp.rcpt(email)
                smtp.quit()

                if code == 250:
                    return "valid"
                elif code in (550, 551, 552, 553, 554):
                    return "invalid"
                else:
                    return "unknown"

        except smtplib.SMTPConnectError:
            # Try port 587 on retry
            try:
                with smtplib.SMTP(timeout=SMTP_TIMEOUT) as smtp:
                    smtp.connect(mx_server, 587)
                    smtp.ehlo("nexuspoint.io")
                    smtp.mail(SMTP_FROM)
                    code, _ = smtp.rcpt(email)
                    smtp.quit()
                    if code == 250:
                        return "valid"
                    return "invalid"
            except Exception:
                return "unknown"
        except (socket.timeout, socket.gaierror, ConnectionRefusedError):
            return "unknown"
        except smtplib.SMTPException:
            if attempt < MAX_RETRIES - 1:
                time.sleep(2)
                continue
            return "unknown"

    return "unknown"


def verify_email(email, domain):
    """Full verification: MX lookup + catch-all check + SMTP verify."""
    if domain not in SMTP_CACHE:
        mx = get_mx_server(domain)
        if not mx:
            SMTP_CACHE[domain] = (None, False)
        else:
            is_catchall = check_catchall(mx, domain)
            SMTP_CACHE[domain] = (mx, is_catchall)

    mx_server, is_catchall = SMTP_CACHE[domain]

    if not mx_server:
        return "unknown"

    if is_catchall:
        return "unverified"  # can't verify, but domain exists — still worth sending

    result = smtp_verify_single(mx_server, email)
    return result


# ---------------------------------------------------------------------------
# Process leads
# ---------------------------------------------------------------------------

def find_email_for_lead(lead_row, raw_headers):
    """Find and verify an email for one lead row. Returns (email, status)."""
    def get(col_name):
        idx = col_index(TAB_RAW, col_name)
        return lead_row[idx] if idx >= 0 and len(lead_row) > idx else ""

    company = get("Company")
    linkedin_url = get("LinkedIn URL")
    company_website = get("Company Website")
    first_name = get("First Name")
    last_name = get("Last Name")

    # Use actual website domain first (most accurate), fall back to LinkedIn slug guess
    domain = None
    if company_website:
        match = re.search(r'https?://(?:www\.)?([^/?&#\s]+)', company_website)
        if match:
            domain = match.group(1).lower()
    if not domain:
        domain = extract_domain(linkedin_url)
    if not domain:
        return None, "no_domain"

    patterns = generate_patterns(first_name, last_name, domain)

    for email in patterns:
        print(f"    Trying {email}...", end=" ", flush=True)
        status = verify_email(email, domain)
        print(status, flush=True)

        if status == "valid":
            return email, "Y"
        elif status == "unverified":
            # Catch-all domain — use first pattern (most likely format)
            first_pattern = patterns[0]
            return first_pattern, "Unverified"
        # "invalid" or "unknown" — try next pattern

        time.sleep(0.5)  # rate limit

    return None, "not_found"


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="Find and verify emails for CRM leads")
    parser.add_argument("--limit", type=int, default=50, help="Max leads to process (default 50)")
    parser.add_argument("--test", action="store_true", help="Dry run — print results without saving")
    args = parser.parse_args()

    print("Cold Outreach — Email Finder")
    print("-" * 40)

    sheet_id = get_or_create_sheet()
    print(f"CRM: https://docs.google.com/spreadsheets/d/{sheet_id}\n")

    # Read unprocessed leads from Raw Leads
    status_col = col_index(TAB_RAW, "Status")
    all_raw = read_all_rows(sheet_id, TAB_RAW)
    unprocessed = [
        (i + 2, row) for i, row in enumerate(all_raw)
        if len(row) > status_col and row[status_col] == "Unprocessed"
    ]

    if not unprocessed:
        print("No unprocessed leads found. Run scrape_leads.py first.")
        sys.exit(0)

    batch = unprocessed[:args.limit]
    print(f"Processing {len(batch)} leads (of {len(unprocessed)} unprocessed)...\n")

    # Read existing enriched leads to avoid duplicates
    existing_enriched = read_all_rows(sheet_id, TAB_ENRICHED)
    company_col_e = col_index(TAB_ENRICHED, "Company")
    enriched_companies = {
        row[company_col_e].lower().strip()
        for row in existing_enriched
        if len(row) > company_col_e and row[company_col_e]
    }

    today = date.today().isoformat()
    enriched_rows = []
    no_email_count = 0
    found_count = 0

    for raw_row_num, raw_row in batch:
        def get_raw(col_name):
            idx = col_index(TAB_RAW, col_name)
            return raw_row[idx] if idx >= 0 and len(raw_row) > idx else ""

        company = get_raw("Company")
        if company.lower().strip() in enriched_companies:
            # Already enriched — just update status in Raw
            if not args.test:
                status_col_letter = col_letter(status_col)
                update_cell(sheet_id, TAB_RAW, raw_row_num, status_col_letter, "Already Enriched")
            continue

        print(f"[{company}]", flush=True)

        email, verified = find_email_for_lead(raw_row, RAW_HEADERS)

        if email and verified != "not_found" and verified != "no_domain":
            status = "Ready"
            found_count += 1
            print(f"  -> {email} ({verified})\n")
        else:
            status = "No Email Found"
            email = ""
            verified = "N"
            no_email_count += 1
            print(f"  -> No email found\n")

        # Build Enriched Leads row
        # ENRICHED_HEADERS: First Name, Last Name, Title, Company, Email, Verified,
        #                   LinkedIn URL, Pain Signal, Enrolled,
        #                   Email 1 Date, Email 2 Date, Email 3 Date, Email 4 Date,
        #                   Status, Reply Date
        enriched_row = [
            "",                         # First Name (from profile scraper if available)
            "",                         # Last Name
            get_raw("Job Title Posted"), # Title (using job posted as proxy)
            company,
            email,
            verified,
            get_raw("LinkedIn URL"),
            get_raw("Pain Signal"),
            "",                         # Enrolled
            "", "", "", "",             # Email 1-4 Dates
            status,
            ""                          # Reply Date
        ]

        enriched_rows.append(enriched_row)
        enriched_companies.add(company.lower().strip())

        # Update Raw Leads status
        if not args.test:
            status_col_letter = col_letter(status_col)
            new_raw_status = "Enriched" if email else "No Email Found"
            update_cell(sheet_id, TAB_RAW, raw_row_num, status_col_letter, new_raw_status)

    # Write all enriched rows at once
    if enriched_rows and not args.test:
        append_rows(sheet_id, TAB_ENRICHED, enriched_rows)
    elif enriched_rows and args.test:
        print("DRY RUN — would have written:")
        for row in enriched_rows:
            print(f"  {row[3]} | {row[4]} | verified={row[5]}")

    print("-" * 40)
    print(f"Done.")
    print(f"  Emails found:    {found_count}")
    print(f"  No email found:  {no_email_count}")
    print(f"  CRM: https://docs.google.com/spreadsheets/d/{sheet_id}")

    print(json.dumps({
        "status": "ok",
        "found": found_count,
        "not_found": no_email_count,
        "sheet_id": sheet_id
    }))


if __name__ == "__main__":
    main()
