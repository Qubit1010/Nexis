"""LinkedIn deep profile enrichment via Proxycurl API.

Only called for HOT tier leads (cost: ~$0.01/call).
Extracts full work history, recent posts, follower count, and activity level.

Proxycurl docs: https://nubela.co/proxycurl/docs
"""

import os
import sys
import requests
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from utils.rate_limit import retry, sleep_between

PROXYCURL_BASE = "https://nubela.co/proxycurl/api/v2"


@retry(max_attempts=2, base_delay=3.0, exceptions=(requests.RequestException,))
def fetch_linkedin_profile(linkedin_url: str) -> dict:
    """Fetch a LinkedIn profile via Proxycurl.

    Returns:
        Full profile dict or {} on failure
    """
    api_key = os.environ.get("PROXYCURL_API_KEY", "").strip()
    if not api_key:
        return {}  # Proxycurl disabled — skip silently

    if not linkedin_url or "linkedin.com/in/" not in linkedin_url:
        return {}

    try:
        resp = requests.get(
            f"{PROXYCURL_BASE}/linkedin",
            params={
                "url": linkedin_url,
                "use_cache": "if-present",
                "fallback_to_cache": "on-error",
                "extra": "include",
                "personal_contact_number": "exclude",
                "personal_email": "exclude",
                "inferred_salary": "include",
                "skills": "include",
                "github_profile_id": "exclude",
                "facebook_profile_id": "exclude",
                "twitter_profile_id": "include",
            },
            headers={"Authorization": f"Bearer {api_key}"},
            timeout=20,
        )
        if resp.status_code == 404:
            print(f"  Proxycurl: profile not found ({linkedin_url})", flush=True)
            return {}
        if resp.status_code == 402:
            print("  Proxycurl: credits exhausted.", flush=True)
            return {}
        resp.raise_for_status()
        return resp.json()
    except requests.RequestException as exc:
        print(f"  Proxycurl failed: {exc}", flush=True)
        return {}


def extract_recent_posts(profile: dict) -> list[dict]:
    """Extract the most recent 3 LinkedIn posts from a Proxycurl profile."""
    activities = profile.get("activities") or []
    posts = []
    for activity in activities[:5]:
        if activity.get("type") == "post" or activity.get("type") == "article":
            posts.append({
                "text": (activity.get("text") or activity.get("title") or "")[:500],
                "date": activity.get("createdAt") or activity.get("date") or "",
                "likes": activity.get("numLikes") or 0,
                "comments": activity.get("numComments") or 0,
            })
    return posts[:3]


def enrich_linkedin(lead: dict) -> dict:
    """Fetch deep LinkedIn profile data for a lead.

    Args:
        lead: Lead dict from DB

    Returns:
        Enrichment data dict (to be merged into enrichment record)
    """
    linkedin_url = (lead.get("linkedin_url") or "").strip()
    if not linkedin_url:
        return {}

    print(f"  Proxycurl: {linkedin_url}", flush=True)

    profile = fetch_linkedin_profile(linkedin_url)
    if not profile:
        return {}

    recent_posts = extract_recent_posts(profile)

    # Extract relevant summary data
    result = {
        "proxycurl_data": profile,
        "recent_posts": recent_posts,
        "enrichment_cost": 0.01,  # ~$0.01 per Proxycurl call
    }

    # Update lead fields if we got better data
    updates = {}
    if profile.get("full_name") and not lead.get("full_name"):
        updates["full_name"] = profile["full_name"]
    if profile.get("headline") and not lead.get("title"):
        updates["title"] = profile["headline"][:200]
    if profile.get("city") or profile.get("state") or profile.get("country_full_name"):
        location_parts = filter(None, [
            profile.get("city"), profile.get("state"), profile.get("country_full_name")
        ])
        updates["location"] = ", ".join(location_parts)

    result["lead_updates"] = updates

    sleep_between(1.0, 2.0)
    return result
