"""Email finding and verification.

Strategy:
  1. Hunter.io API (free tier: 25/month) — try for HOT leads first
  2. SMTP pattern guessing + MX verification — free, unlimited, fallback

Ported from cold-outreach/scripts/find_emails.py with Hunter.io added.
"""

import os
import re
import sys
import smtplib
import socket
import time
from pathlib import Path

import requests

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from database import get_config, set_config
from utils.rate_limit import sleep_between

# SMTP constants
SMTP_TIMEOUT = 10
SMTP_FROM = "verify@nexuspoint.io"
MAX_RETRIES = 2

try:
    import dns.resolver
    HAS_DNS = True
except ImportError:
    HAS_DNS = False


# ---------------------------------------------------------------------------
# Domain extraction
# ---------------------------------------------------------------------------

def extract_domain_from_website(url: str) -> str | None:
    """Extract email domain from a website URL."""
    if not url:
        return None
    match = re.search(r'https?://(?:www\.)?([^/?&#\s]+)', url)
    if match:
        domain = match.group(1).lower()
        # Skip social media / link aggregators
        skip = ["linkedin.com", "twitter.com", "instagram.com", "facebook.com",
                "linktr.ee", "linktree.com", "bit.ly"]
        if any(s in domain for s in skip):
            return None
        return domain
    return None


def extract_domain_from_linkedin(linkedin_url: str) -> str | None:
    """Guess email domain from LinkedIn company URL slug."""
    if not linkedin_url:
        return None
    match = re.search(r'linkedin\.com/company/([^/?&\s]+)', linkedin_url, re.IGNORECASE)
    if not match:
        return None
    slug = match.group(1).rstrip("/").lower()
    # Normalize: strip common legal suffixes
    slug = re.sub(r'[-_](inc|llc|ltd|corp|co|company|technologies|tech|solutions|group|labs|io|ai)$', '', slug)
    domain = slug.replace("-", "") + ".com"
    return domain


# ---------------------------------------------------------------------------
# Email pattern generation
# ---------------------------------------------------------------------------

def generate_patterns(first: str, last: str, domain: str) -> list[str]:
    """Generate candidate email patterns in priority order."""
    first = first.lower().strip() if first else ""
    last = last.lower().strip() if last else ""

    if not first or not domain:
        return [f"contact@{domain}", f"info@{domain}", f"hello@{domain}"]

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
        patterns = [f"{first}@{domain}", f"contact@{domain}", f"hello@{domain}"]

    # Always add generic fallbacks
    patterns += [f"contact@{domain}", f"hello@{domain}", f"info@{domain}"]

    # Deduplicate preserving order
    seen = set()
    unique = []
    for p in patterns:
        if p not in seen:
            seen.add(p)
            unique.append(p)
    return unique


# ---------------------------------------------------------------------------
# MX lookup + SMTP verification (from cold-outreach find_emails.py)
# ---------------------------------------------------------------------------

_mx_cache: dict = {}  # domain -> (mx_server, is_catchall)


def get_mx_server(domain: str) -> str | None:
    if not HAS_DNS:
        return domain
    try:
        records = dns.resolver.resolve(domain, "MX")
        sorted_records = sorted(records, key=lambda r: r.preference)
        return str(sorted_records[0].exchange).rstrip(".")
    except Exception:
        return None


def check_catchall(mx_server: str, domain: str) -> bool:
    fake = f"definitelynotreal99999@{domain}"
    return smtp_verify_single(mx_server, fake) == "valid"


def smtp_verify_single(mx_server: str, email: str) -> str:
    """Returns 'valid', 'invalid', or 'unknown'."""
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
                return "unknown"
        except smtplib.SMTPConnectError:
            try:
                with smtplib.SMTP(timeout=SMTP_TIMEOUT) as smtp:
                    smtp.connect(mx_server, 587)
                    smtp.ehlo("nexuspoint.io")
                    smtp.mail(SMTP_FROM)
                    code, _ = smtp.rcpt(email)
                    smtp.quit()
                    return "valid" if code == 250 else "invalid"
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


def verify_via_smtp(email: str, domain: str) -> tuple[str, str]:
    """Full verification: MX lookup + catch-all check + SMTP verify.

    Returns:
        (email: str, verified: str) where verified is "Y", "Unverified", or "N"
    """
    if domain not in _mx_cache:
        mx = get_mx_server(domain)
        if not mx:
            _mx_cache[domain] = (None, False)
        else:
            is_catchall = check_catchall(mx, domain)
            _mx_cache[domain] = (mx, is_catchall)

    mx_server, is_catchall = _mx_cache[domain]
    if not mx_server:
        return email, "N"
    if is_catchall:
        return email, "Unverified"

    result = smtp_verify_single(mx_server, email)
    if result == "valid":
        return email, "Y"
    elif result == "invalid":
        return "", "N"
    return email, "Unverified"


# ---------------------------------------------------------------------------
# Hunter.io API
# ---------------------------------------------------------------------------

HUNTER_BASE = "https://api.hunter.io/v2"


def get_hunter_usage() -> int:
    """Return number of Hunter.io calls made this month."""
    from datetime import date
    key = f"hunter_calls_{date.today().strftime('%Y%m')}"
    return int(get_config(key, 0))


def increment_hunter_usage():
    from datetime import date
    key = f"hunter_calls_{date.today().strftime('%Y%m')}"
    current = int(get_config(key, 0))
    set_config(key, current + 1)


def find_via_hunter(first: str, last: str, domain: str) -> tuple[str, str]:
    """Use Hunter.io to find verified email.

    Returns:
        (email, verified) or ("", "")
    """
    from config import ENRICHMENT as ENRICH_CFG

    monthly_limit = ENRICH_CFG.get("hunter_monthly_limit", 25)
    api_key = os.environ.get("HUNTER_API_KEY", "").strip()

    if not api_key:
        return "", ""

    if get_hunter_usage() >= monthly_limit:
        print(f"  Hunter.io: monthly limit ({monthly_limit}) reached. Using SMTP fallback.", flush=True)
        return "", ""

    try:
        resp = requests.get(
            f"{HUNTER_BASE}/email-finder",
            params={
                "domain": domain,
                "first_name": first,
                "last_name": last,
                "api_key": api_key,
            },
            timeout=15,
        )
        if resp.status_code == 429:
            print("  Hunter.io: rate limited.", flush=True)
            return "", ""
        resp.raise_for_status()
        data = resp.json().get("data", {})
        email = (data.get("email") or "").strip()
        confidence = data.get("score", 0)
        increment_hunter_usage()

        if email and confidence >= 70:
            return email, "Y"
        elif email:
            return email, "Unverified"
    except requests.RequestException as exc:
        print(f"  Hunter.io failed: {exc}", flush=True)

    return "", ""


# ---------------------------------------------------------------------------
# Main enrichment function
# ---------------------------------------------------------------------------

def find_email(lead: dict, use_hunter: bool = True) -> dict:
    """Find and verify email for a lead.

    Args:
        lead: Lead dict from DB
        use_hunter: Whether to try Hunter.io first (before SMTP)

    Returns:
        Dict with "email" and "email_verified" keys
    """
    first = (lead.get("first_name") or "").strip()
    last = (lead.get("last_name") or "").strip()
    company_website = (lead.get("company_website") or "").strip()
    linkedin_url = (lead.get("linkedin_url") or "").strip()
    company_linkedin = (lead.get("company_linkedin") or "").strip()

    # Get domain
    domain = extract_domain_from_website(company_website)
    if not domain:
        domain = extract_domain_from_linkedin(company_linkedin or linkedin_url)
    if not domain:
        return {"email": "", "email_verified": ""}

    print(f"  Email finder: {first} {last} @ {domain}", flush=True)

    # 1. Hunter.io (for HOT tier leads — preserve free credits)
    if use_hunter:
        email, verified = find_via_hunter(first, last, domain)
        if email:
            print(f"  Hunter.io found: {email} ({verified})", flush=True)
            return {"email": email, "email_verified": verified}

    # 2. SMTP pattern guessing
    patterns = generate_patterns(first, last, domain)
    for pattern in patterns:
        print(f"    Trying {pattern}...", end=" ", flush=True)
        email, verified = verify_via_smtp(pattern, domain)
        print(verified, flush=True)

        if verified == "Y":
            return {"email": email, "email_verified": "Y"}
        elif verified == "Unverified":
            # Catch-all domain — return first (most likely) pattern
            return {"email": patterns[0], "email_verified": "Unverified"}

        sleep_between(0.3, 0.8)

    return {"email": "", "email_verified": "N"}
