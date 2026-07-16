"""Secondary resolution pass for businesses WebSearch couldn't resolve (the SKILL.md primary
method). Fetches the business's own website directly and regexes Instagram/LinkedIn/Facebook
hrefs out of the raw HTML — the footer/header nav is where most sites link their own social
profiles. Tries the homepage first, then a few common contact/about paths if the homepage has
nothing (some sites only put social links on a dedicated contact page).

If LinkedIn is still missing after that, tries a set of team/leadership page paths (`TEAM_PATHS`)
specifically, since that's where a founder's personal `/in/` LinkedIn is actually linked (headshot
+ name + icon) — the footer/contact page usually only carries the company page, if anything.
Uses BeautifulSoup (not raw regex) for this pass so it can pull the name/title text near each
LinkedIn href into a `linkedin_candidates` list. These are NEVER auto-accepted: a bare href on a
team page doesn't say which team member it belongs to, so the caller must confirm the `context`
text plausibly reads as founder/CEO/owner (same confidence bar as the WebSearch founder query)
before writing it — `likely_founder` is a hint, not a verdict.

This was the original primary-method candidate (see references/how-it-works.md) before WebSearch
proved more reliable overall — kept here as a cheap, free, zero-ambiguity secondary pass for the
businesses WebSearch missed, since these are the business's own published links, not a search
guess. Works for maybe 1 in 3-4 of WebSearch's misses (many of those sites also block direct
fetches, or genuinely don't link their socials in-page) but every hit here is free.

Usage:
  python scrape_socials.py '<json array of business dicts with a "website" field>'
Prints a JSON object keyed by row number with whichever instagram/linkedin/facebook URLs were
found, plus `linkedin_candidates` (list of {url, context, likely_founder}) when a team page had
person links but nothing was confident enough to auto-fill — feed confirmed values straight into
write_resolved.py / write_result_main.py.
"""

import json
import re
import sys
from urllib.parse import urljoin, urlparse

import requests
import url_filters  # shared social-URL classifier (single source of truth with resolve.py)
from bs4 import BeautifulSoup

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
}

CONTACT_PATHS = ["/contact/", "/contact-us/", "/about/", "/about-us/"]

# Checked only when LinkedIn is still missing after CONTACT_PATHS -- team/leadership pages are
# where a founder's personal LinkedIn actually lives (headshot + name + LinkedIn icon), but they're
# a less universal URL shape than /about/ so they're tried second, not merged into CONTACT_PATHS.
TEAM_PATHS = [
    "/team/", "/our-team/", "/meet-the-team/", "/about/team/", "/about-us/team/",
    "/people/", "/leadership/",
]

FOUNDER_TITLE_RE = re.compile(r"founder|co-founder|owner|principal|ceo|president", re.I)


def _extract(html):
    """First valid profile per platform, using the shared classifier (company pages rejected here —
    this legacy pass feeds the per-channel Instant sheets, which still want a person; resolve.py opts
    into company pages for the new Main-sheet company-LinkedIn column)."""
    found = {}
    for m in url_filters.SOCIAL_RE.finditer(html):
        hit = url_filters.social_profile(m.group(0))
        if hit:
            platform, url = hit
            found.setdefault(platform, url)
    return found


def _team_linkedin_candidates(html):
    """Finds person LinkedIn links (/in/) on a team/leadership page plus the nearby name/title
    text, so the caller can confirm it's actually the founder/CEO/owner before trusting it --
    same confidence bar as the WebSearch founder query in how-it-works.md. Never auto-accepted:
    a raw href tells you nothing about which team member it belongs to."""
    soup = BeautifulSoup(html, "lxml")
    hits, seen = [], set()
    for a in soup.find_all("a", href=True):
        href = url_filters.clean(a["href"])
        if not url_filters.is_person_linkedin(href) or href in seen:
            continue
        seen.add(href)
        context, node = "", a
        for _ in range(4):
            node = node.parent
            if node is None:
                break
            text = node.get_text(" ", strip=True)
            if len(text) >= 10:
                context = text
                break
        hits.append({
            "url": href,
            "context": context[:200],
            "likely_founder": bool(FOUNDER_TITLE_RE.search(context)),
        })
    return hits


def fetch(url, timeout=6):
    try:
        r = requests.get(url, headers=HEADERS, timeout=timeout)
        if r.status_code == 200:
            return r.text
    except requests.RequestException:
        pass
    return None


def resolve_one(website):
    if not website:
        return {}
    html = fetch(website)
    found = _extract(html) if html else {}
    if len(found) >= 2:  # homepage already found enough, don't spend extra requests
        return found
    parsed = urlparse(website if "://" in website else f"https://{website}")
    base = f"{parsed.scheme}://{parsed.netloc}"
    for path in CONTACT_PATHS:
        html = fetch(urljoin(base, path))
        if html:
            found.update({k: v for k, v in _extract(html).items() if k not in found})
        if len(found) >= 3:
            break

    if "linkedin" not in found:
        for path in TEAM_PATHS:
            html = fetch(urljoin(base, path))
            if not html:
                continue
            candidates = _team_linkedin_candidates(html)
            if candidates:
                found["linkedin_candidates"] = candidates
                break

    return found


def main():
    businesses = json.loads(sys.argv[1])
    results = {}
    for b in businesses:
        row = b["row"]
        found = resolve_one(b.get("website", ""))
        results[str(row)] = found
        print(f"row {row} ({b['company']}): {found or 'nothing found'}", file=sys.stderr)
    print(json.dumps(results, indent=2))


if __name__ == "__main__":
    main()
