"""Secondary resolution pass for businesses WebSearch couldn't resolve (the SKILL.md primary
method). Fetches the business's own website directly and regexes Instagram/LinkedIn/Facebook
hrefs out of the raw HTML — the footer/header nav is where most sites link their own social
profiles. Tries the homepage first, then a few common contact/about paths if the homepage has
nothing (some sites only put social links on a dedicated contact page).

This was the original primary-method candidate (see references/how-it-works.md) before WebSearch
proved more reliable overall — kept here as a cheap, free, zero-ambiguity secondary pass for the
businesses WebSearch missed, since these are the business's own published links, not a search
guess. No confidence scoring needed for the same reason. Works for maybe 1 in 3-4 of WebSearch's
misses (many of those sites also block direct fetches, or genuinely don't link their socials
in-page) but every hit here is free.

Usage:
  python scrape_socials.py '<json array of business dicts with a "website" field>'
Prints a JSON object keyed by row number with whichever instagram/linkedin/facebook URLs were
found — feed that straight into write_resolved.py.
"""

import json
import re
import sys
from urllib.parse import urljoin, urlparse

import requests

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
}

SOCIAL_RE = re.compile(
    r"https?://(?:www\.|[a-z]{2}-[a-z]{2}\.)?(instagram|facebook|linkedin)\.com/[A-Za-z0-9_./?=&%-]+",
    re.I,
)

# Non-profile URL shapes to reject, same rule as the WebSearch pass.
_BAD_PATH = re.compile(r"/(p|reel|explore|tv|posts|pulse|photo|sharer|share)(/|$|\?)", re.I)

CONTACT_PATHS = ["/contact/", "/contact-us/", "/about/", "/about-us/"]


def _clean(url):
    return url.split("?")[0].rstrip("/")


def _extract(html):
    found = {}
    for m in SOCIAL_RE.finditer(html):
        url = _clean(m.group(0))
        platform = m.group(1).lower()
        if _BAD_PATH.search(url):
            continue
        # Skip share/widget links (og:image style CDN links, sharer.php already caught above).
        path = urlparse(url).path
        if not path or path == "/":
            continue
        found.setdefault(platform, url)
    return found


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
