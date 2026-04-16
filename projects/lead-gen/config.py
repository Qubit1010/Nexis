"""NexusPoint Lead Generation — Configuration & ICP Definition."""

from pathlib import Path

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

PROJECT_DIR = Path(__file__).resolve().parent
DB_PATH = PROJECT_DIR / "data" / "leads.db"
DB_PATH.parent.mkdir(exist_ok=True)

# ---------------------------------------------------------------------------
# Apify actor IDs
# ---------------------------------------------------------------------------

APIFY_ACTORS = {
    "linkedin_jobs":     "hKByXkMQaC5Qt9UMN",    # LinkedIn Jobs Scraper by curious_coder
    "linkedin_profile":  "2SyF0bVxmgGr8IVCZ",    # LinkedIn Profile Scraper by Apify
    "google_search":     "nFJndFXA5zjCTuudP",     # Google Search Scraper by Apify
    "linkedin_profiles": "harvestapi~linkedin-profile-search",  # HarvestAPI LinkedIn Profile Search
}

# ---------------------------------------------------------------------------
# ICP — Ideal Customer Profile
# ---------------------------------------------------------------------------

ICP = {
    "industries": [
        "SaaS", "Software", "E-commerce", "Marketing Agency", "Digital Agency",
        "Marketing & Advertising", "Advertising Services", "Internet",
        "Real Estate Tech", "Healthcare Tech", "EdTech", "Fintech",
        "Professional Services", "Consulting", "Technology", "Startup",
        "Retail Tech", "Logistics Tech", "Insurance Tech",
    ],
    # Company size strings that appear in LinkedIn / Apollo data
    "target_sizes": ["1-10", "11-50", "51-200", "2-10"],
    "sweet_spot_sizes": ["11-50", "1-10", "2-10"],

    "decision_maker_titles_tier1": [
        "founder", "co-founder", "cofounder", "owner", "proprietor",
    ],
    "decision_maker_titles_tier2": [
        "ceo", "chief executive", "cto", "chief technology", "coo", "chief operating",
    ],
    "decision_maker_titles_tier3": [
        "head of product", "head of operations", "director of operations",
        "vp operations", "director of engineering", "head of engineering",
        "vp of product", "marketing director", "director of marketing",
    ],
    "decision_maker_titles_tier4": [
        "manager", "lead", "senior manager",
    ],

    # Job posting keywords → company is advertising automation bottleneck
    "pain_keywords": [
        "data entry", "manual", "admin", "reporting analyst", "spreadsheet",
        "copy-paste", "copy paste", "repetitive", "administrative", "tracking",
        "data management", "operations admin", "excel", "maintain records",
        "update records", "time-consuming", "manual process",
    ],

    # Website tech stack signals → company has tech debt
    "tech_debt_signals": [
        "wix", "squarespace", "weebly", "godaddy website builder",
        "jimdo", "strikingly", "yola",
    ],

    # Target geographies (primary)
    "locations_primary": [
        "United States", "United Kingdom", "Australia", "Canada",
        "US", "UK", "AU", "CA",
    ],

    # Disqualifiers — auto-reject if matched
    "disqualify_sizes": ["1001-5000", "5001-10000", "10001+", "201-500"],
    "disqualify_industries": ["Government", "NGO", "Non-profit", "Military", "Education"],
    "disqualify_titles": [
        "intern", "assistant", "coordinator", "student", "junior",
        "trainee", "entry level",
    ],
    "generic_email_prefixes": [
        "info", "contact", "hello", "admin", "support", "sales",
        "team", "general", "enquiries", "enquiry",
    ],
}

# ---------------------------------------------------------------------------
# Scoring weights (must sum to 100)
# ---------------------------------------------------------------------------

SCORING = {
    # Layer 1: Contact Quality (max 20)
    "email_verified": 8,
    "linkedin_present": 6,
    "phone_present": 3,
    "social_present": 3,
    "generic_email_penalty": -5,

    # Layer 2: Company Quality (max 20)
    "has_website": 5,
    "size_sweet_spot": 5,
    "company_age": 4,           # founded 2+ years ago
    "revenue_signal": 3,
    "has_reviews": 3,
    "no_website_penalty": -10,

    # Layer 3: Intent & Pain Signal (max 25)
    "tech_debt_signal": 8,      # Wix/Squarespace site
    "job_posting_pain": 8,      # active ops/admin/dev job
    "funding_signal": 6,        # recent funding news
    "product_hunt_launch": 5,   # launched on PH in last 60 days
    "linkedin_pain_post": 5,    # posted about tech/automation need
    "pagespeed_low": 4,         # mobile score < 60
    "ssl_issues": 3,            # no SSL or broken links

    # Layer 4: Decision Maker Access (max 20)
    "title_founder": 20,
    "title_csuite": 16,
    "title_head": 12,
    "title_manager": 6,

    # Layer 5: Reachability (max 15)
    "linkedin_active": 5,       # posted in last 30 days
    "professional_email": 4,    # not Yahoo/Hotmail/Gmail
    "second_degree": 3,         # mutual LinkedIn connection
    "twitter_active": 3,
}

# Tier thresholds
# NOTE: Pre-enrichment scores top out ~40 (founder + linkedin + website, no intent signals).
# WARM is intentionally low so that qualified founders pass through to enrichment.
# After website_intel enrichment, rescore — intent signals push good leads to STRONG/HOT.
TIER_HOT = 80       # → all 3 platforms + Proxycurl
TIER_STRONG = 60    # → cold email + LinkedIn
TIER_WARM = 35      # → cold email only (passes to enrichment)
# < 35 → rejected

# ---------------------------------------------------------------------------
# Discovery configuration
# ---------------------------------------------------------------------------

DISCOVERY = {
    "linkedin_jobs_queries": [
        "operations admin",
        "data entry specialist",
        "reporting analyst",
        "operations coordinator",
        "manual reporting",
    ],
    "linkedin_jobs_limit": 50,

    "linkedin_profiles_queries": [
        # (title, industry) pairs
        ("Founder", "SaaS"),
        ("CEO", "E-commerce"),
        ("Founder", "Marketing Agency"),
        ("CTO", "Fintech"),
        ("CEO", "EdTech"),
        ("Founder", "Software"),
        ("COO", "SaaS"),
        ("CEO", "Digital Agency"),
    ],
    "linkedin_profiles_limit": 15,  # per query

    # Primary founder discovery (replaces broken harvestapi actor)
    "google_search_queries": [
        # US founders — SaaS / software
        'site:linkedin.com/in "Founder" "SaaS" "United States"',
        'site:linkedin.com/in "CEO" "SaaS" "United States"',
        'site:linkedin.com/in "Founder" "Software" "United States"',
        # UK / AU founders
        'site:linkedin.com/in "Founder" "SaaS" "United Kingdom"',
        'site:linkedin.com/in "Founder" "E-commerce" "Australia"',
        # E-commerce / agencies
        'site:linkedin.com/in "CEO" "E-commerce" "United States"',
        'site:linkedin.com/in "Founder" "Marketing Agency" "United States"',
        'site:linkedin.com/in "CEO" "Digital Agency" "United Kingdom"',
        # Fintech / EdTech / AI
        'site:linkedin.com/in "Founder" "Fintech" "United States"',
        'site:linkedin.com/in "CEO" "EdTech" "United States"',
        'site:linkedin.com/in "Founder" "AI" "United States"',
        'site:linkedin.com/in "CTO" "Startup" "United States"',
    ],
    "google_search_limit": 10,  # per query

    "product_hunt_days_back": 60,
    "product_hunt_categories": ["SaaS", "AI", "Developer Tools", "Productivity", "Marketing"],

    # ---------------------------------------------------------------------------
    # Playwright-based scrapers (browser automation — no API keys needed)
    # ---------------------------------------------------------------------------

    # playwright_google.py: HackerNews Algolia API (Show HN posts → founder company sites)
    # These are topic queries for the HN Algolia search API — NOT search engine site: queries.
    # Show HN posters are almost always founders with real company URLs attached.
    "playwright_queries": [
        "SaaS startup",
        "e-commerce automation",
        "we built small business",
        "marketing tool agency",
        "AI tool founder",
        "web app startup",
        "productivity SaaS",
        "CRM tool small business",
        "invoicing tool freelancer",
        "analytics dashboard startup",
        "email marketing tool",
        "customer support automation",
    ],
    "playwright_limit_per_query": 15,  # HN hits per query (API param hitsPerPage)

    # builtwith_scraper.py: platforms to scrape + domains per platform
    # Set via env: BUILTWITH_PLATFORMS=wix,squarespace,wordpress
    #              BUILTWITH_MAX_DOMAINS=30
    "builtwith_platforms": ["wix", "squarespace", "wordpress"],
    "builtwith_max_domains": 30,  # domains to check per platform

    # ---------------------------------------------------------------------------
    # Manual Google Sheet import (primary lead source)
    # ---------------------------------------------------------------------------
    # Set input_sheet_id to your Google Sheet ID, then run:
    #   python main.py import --source sheets
    # Or pass it inline: python main.py import --source sheets --sheet-id <ID>
    "input_sheet_id":  "",           # Google Sheet ID
    "input_sheet_tab": "Sheet1",     # Tab name within the sheet
    "include_column":  "Include",    # Column header that marks rows to keep
    "include_value":   "yes",        # Value (case-insensitive) meaning "keep this lead"
}

# ---------------------------------------------------------------------------
# Enrichment configuration
# ---------------------------------------------------------------------------

ENRICHMENT = {
    "hunter_monthly_limit": 25,     # free tier
    "proxycurl_tiers": ["HOT"],     # only call Proxycurl for HOT leads (cost control)
    "pagespeed_threshold": 60,      # scores below this = slow site signal
    "instagram_discovery_tiers": ["HOT", "STRONG"],  # find Instagram for HOT + STRONG leads
}

# ---------------------------------------------------------------------------
# Personalization
# ---------------------------------------------------------------------------

PERSONALIZATION = {
    "model": "gpt-4o-mini",
    "tiers": ["HOT", "STRONG"],  # WARM gets template-based hooks only
    "max_tokens": 1500,
}

# ---------------------------------------------------------------------------
# Export mappings to existing CRM Google Sheets
# ---------------------------------------------------------------------------

CRM_SHEET_NAMES = {
    "cold_email": "NexusPoint Cold Outreach CRM",
    "linkedin": "NexusPoint LinkedIn Outreach CRM",
    "instagram": "NexusPoint Instagram Outreach CRM",
}

CRM_TABS = {
    "cold_email": "Enriched Leads",
    "linkedin": "Leads",
    "instagram": "Leads",
}

# Exact column orders expected by each CRM (must match exactly)
CRM_COLUMNS = {
    "cold_email": [
        "First Name", "Last Name", "Title", "Company", "Email", "Verified",
        "LinkedIn URL", "Pain Signal", "Enrolled",
        "Email 1 Date", "Email 2 Date", "Email 3 Date", "Email 4 Date",
        "Status", "Reply Date", "Source",
    ],
    "linkedin": [
        "Name", "First Name", "Company", "Role", "LinkedIn URL",
        "Location", "Recent Post", "Connection Message", "Status", "Date Added",
    ],
    "instagram": [
        "Name", "Username", "Company", "Role", "Instagram URL",
        "Followers", "Bio", "Touch 1 Message", "Status", "Date Added",
    ],
}

# Which tiers export to which platforms
EXPORT_TIERS = {
    "cold_email": ["HOT", "STRONG", "WARM"],
    "linkedin": ["HOT", "STRONG"],
    "instagram": ["HOT", "STRONG"],  # plus requires instagram_url
}

# ---------------------------------------------------------------------------
# NexusPoint context (used in personalization prompts)
# ---------------------------------------------------------------------------

NEXUSPOINT_CONTEXT = """
NexusPoint is a digital agency based in Pakistan, serving clients in the US, UK, Australia, and Canada.

Services:
- Custom web development (React, Next.js, Node.js, Framer, Webflow, WordPress)
- AI automation & workflows (LangChain, LangGraph, n8n, Make, custom Python)
- Custom SaaS / web apps (full-stack MERN with AI integration)
- CMS builds (Shopify, Webflow, WordPress)

Strategic positioning: "We don't just build websites — we build the systems that let your team focus on growth."

Best results for: founder/CEO at 5-50 person company that is scaling fast and needs tech to handle the operational load.

Track record: Fast delivery, technical depth, strong communication.
Differentiator: AI automation + web development as a combined offer, not two separate things.
""".strip()

# ---------------------------------------------------------------------------
# Email sequence templates (used in transformers)
# ---------------------------------------------------------------------------

EMAIL_SEQUENCE_TEMPLATES = {
    "email_1": {
        "subject_template": "quick question about {company}'s {pain_area}",
        "body_template": """Hi {first_name},

{hook}

{pain_point}

I've helped {industry} companies in similar situations — happy to share what worked.

Would it be worth a 15-min call to see if this is relevant for you?

{signature}""",
    },
    "email_2": {
        "subject_template": "something I noticed about {company}",
        "body_template": """Hi {first_name},

{value_insight}

Not pitching anything — just sharing what's been useful for {industry} founders at your stage.

{signature}""",
    },
    "email_3": {
        "subject_template": "re: {company}",
        "body_template": """Hi {first_name},

Still happy to do a quick audit — 5-minute Loom showing exactly what I'd change and why.

No strings attached. If it's not useful, you haven't lost anything.

Worth a look?

{signature}""",
    },
    "email_4": {
        "subject_template": "closing the loop",
        "body_template": """Hi {first_name},

Should I close your file, or is the timing just off right now?

Either way is fine — just want to make sure I'm not missing something.

{signature}""",
    },
}

EMAIL_SIGNATURE = "Aleem | NexusPoint\nnexuspointai.com"
