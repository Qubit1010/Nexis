"""Product Hunt scraper — finds SaaS founders who recently launched.

Recent PH launches = founders with:
  - A public product to talk about (easy personalization hook)
  - Recent funding signal (PH launch often coincides with funding)
  - High likelihood of needing web/tech help to scale

Uses Product Hunt's public GraphQL API (no auth required for basic queries).
"""

import os
import sys
import requests
from datetime import date, datetime, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from config import DISCOVERY

PH_GRAPHQL = "https://api.producthunt.com/v2/api/graphql"

# GraphQL query for recent posts
POSTS_QUERY = """
query RecentPosts($after: String, $postedAfter: DateTime) {
  posts(order: NEWEST, after: $after, postedAfter: $postedAfter) {
    edges {
      node {
        id
        name
        tagline
        url
        website
        votesCount
        createdAt
        topics {
          edges {
            node {
              name
            }
          }
        }
        makers {
          id
          name
          username
          websiteUrl
          twitterUsername
        }
      }
    }
    pageInfo {
      hasNextPage
      endCursor
    }
  }
}
"""


def get_ph_token() -> str | None:
    """Get Product Hunt API token from env (optional)."""
    return os.environ.get("PRODUCT_HUNT_API_TOKEN", "").strip() or None


def fetch_ph_posts(days_back: int = 60, categories: list = None) -> list[dict]:
    """Fetch recent Product Hunt launches.

    Args:
        days_back: How many days back to search
        categories: List of topic names to filter by (e.g. ["SaaS", "AI"])

    Returns:
        List of post dicts with maker information
    """
    cutoff = datetime.utcnow() - timedelta(days=days_back)
    posted_after = cutoff.strftime("%Y-%m-%dT%H:%M:%SZ")

    headers = {"Content-Type": "application/json"}
    token = get_ph_token()
    if token:
        headers["Authorization"] = f"Bearer {token}"

    if categories is None:
        categories = DISCOVERY.get("product_hunt_categories", [])

    categories_lower = {c.lower() for c in categories}

    if not token:
        print("  Product Hunt: No API token found — requests will likely fail.", flush=True)
        print("  Get a token at: https://www.producthunt.com/v2/oauth/applications", flush=True)
        print("  Then add PRODUCT_HUNT_API_TOKEN=<token> to projects/lead-gen/.env", flush=True)
        return []

    all_posts = []
    cursor = None
    max_pages = 5  # cap to avoid rate limit issues

    for page in range(max_pages):
        variables = {"postedAfter": posted_after}
        if cursor:
            variables["after"] = cursor

        try:
            resp = requests.post(
                PH_GRAPHQL,
                json={"query": POSTS_QUERY, "variables": variables},
                headers=headers,
                timeout=20,
            )
            resp.raise_for_status()
        except requests.RequestException as exc:
            print(f"  Product Hunt API error: {exc}", flush=True)
            break

        data = resp.json()
        if "errors" in data:
            print(f"  Product Hunt GraphQL errors: {data['errors']}", flush=True)
            break

        posts_data = data.get("data", {}).get("posts", {})
        edges = posts_data.get("edges", [])

        for edge in edges:
            post = edge.get("node", {})

            # Filter by category if specified
            if categories_lower:
                post_topics = {
                    t["node"]["name"].lower()
                    for t in post.get("topics", {}).get("edges", [])
                }
                if not post_topics.intersection(categories_lower):
                    continue

            all_posts.append(post)

        page_info = posts_data.get("pageInfo", {})
        if not page_info.get("hasNextPage"):
            break
        cursor = page_info.get("endCursor")

    print(f"  Fetched {len(all_posts)} Product Hunt launches.", flush=True)
    return all_posts


def posts_to_leads(posts: list[dict]) -> list[dict]:
    """Convert PH post data to lead dicts.

    Each post maker becomes a separate lead.
    All PH makers get funding_signal=True (PH launch = public signal).
    """
    leads = []
    today = date.today().isoformat()
    seen_makers = set()  # dedup by maker ID

    for post in posts:
        company = post.get("name", "").strip()
        company_website = (post.get("website") or post.get("url") or "").strip()
        tagline = post.get("tagline", "")
        votes = post.get("votesCount", 0)
        launched_at = post.get("createdAt", "")[:10]  # ISO date

        for maker in post.get("makers", []):
            maker_id = maker.get("id") or maker.get("username")
            if maker_id and maker_id in seen_makers:
                continue
            if maker_id:
                seen_makers.add(maker_id)

            full_name = (maker.get("name") or "").strip()
            if not full_name:
                continue

            name_parts = full_name.split()
            first_name = name_parts[0] if name_parts else ""
            last_name = " ".join(name_parts[1:]) if len(name_parts) > 1 else ""

            # Maker website (often their personal site or company site)
            maker_website = (maker.get("websiteUrl") or company_website or "").strip()

            twitter = (maker.get("twitterUsername") or "").strip()

            # Use tagline as the "pain signal" context — it describes what they built
            pain_signal = f"Launched '{company}' on Product Hunt: {tagline}" if tagline else f"Launched '{company}' on Product Hunt."

            leads.append({
                "source": "product_hunt",
                "first_name": first_name,
                "last_name": last_name,
                "full_name": full_name,
                "title": "Founder",  # PH makers are typically founders
                "company": company,
                "company_size": "",
                "industry": "SaaS",  # PH leans SaaS/tech
                "company_website": maker_website,
                "linkedin_url": "",  # found during enrichment
                "company_linkedin": "",
                "instagram_url": f"https://twitter.com/{twitter}" if twitter else "",
                "instagram_handle": twitter,
                "email": "",
                "email_verified": "",
                "location": "",
                "pain_signal": pain_signal,
                "pain_keywords": "",
                "recent_activity": f"Launched on Product Hunt ({launched_at}) with {votes} upvotes: {tagline}",
                "funding_signal": True,  # PH launch is a funding/growth signal
                "date_discovered": today,
            })

    return leads


def run(dry_run: bool = False) -> list[dict]:
    """Fetch Product Hunt launches and return as lead dicts."""
    days_back = DISCOVERY.get("product_hunt_days_back", 60)
    categories = DISCOVERY.get("product_hunt_categories", [])

    print(f"\nProduct Hunt Discovery (last {days_back} days, categories: {categories})...", flush=True)

    if dry_run:
        print("  [DRY RUN] Would call Product Hunt GraphQL API")
        return []

    posts = fetch_ph_posts(days_back=days_back, categories=categories)
    leads = posts_to_leads(posts)

    print(f"Product Hunt total: {len(leads)} maker leads.", flush=True)
    return leads
