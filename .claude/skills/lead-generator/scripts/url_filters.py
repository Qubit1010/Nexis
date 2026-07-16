"""Shared social-URL classification for both resolution passes, so they never drift on what counts
as a real profile vs junk:

- resolve.py    filters the research skill's result URLs (discrete full URLs).
- scrape_socials.py regexes hrefs out of a page's HTML.

`social_profile(url)` is the one gate: give it any URL, get back (platform, clean_url) if it's a real
Instagram/LinkedIn/Facebook PROFILE, else None. Rejects post/reel/share/tracking shapes, review/
directory sites that merely mention a business, and (unless allow_company) LinkedIn company pages.
"""
from __future__ import annotations

import re
from urllib.parse import urlparse

# Matches an instagram/linkedin/facebook URL anywhere it appears (page HTML or a result URL).
SOCIAL_RE = re.compile(
    r"https?://(?:www\.|[a-z]{2}-[a-z]{2}\.)?(instagram|facebook|linkedin)\.com/[A-Za-z0-9_./?=&%-]+",
    re.I,
)

# Non-profile URL shapes (posts/reels/share/etc.) — learned empirically over the live batches.
# photos/videos/popular added 2026-07-17: the plural "photos"/"videos" (Facebook's actual path shape for
# a photo/video post -- the singular "photo" alone never matches real URLs) and "/popular/" (a search-
# aggregator listing path, not a real instagram.com profile) all slipped through a founder-social
# re-verify pass as if they were profiles -- one even landed a video of an UNRELATED person's story on a
# company's Facebook page as a "personal profile" match.
_BAD_PATH = re.compile(
    r"/(p|reel|reels|explore|tv|posts|pulse|photo|photos|video|videos|popular|sharer|share|hashtag)(/|$|\?)",
    re.I)
_BAD_PATH_FB = re.compile(r"facebook\.com/(tr/?$|2008/fbml|profile\.php|plugins/|sharer)", re.I)
_BAD_PATH_LI = re.compile(
    r"linkedin\.com/(feed|showcase|posts|pulse|jobs)/|linkedin\.com/authwall|"
    r"linkedin\.com/pub/dir/",  # pub/dir = a people-DIRECTORY search page, not a real profile;
                                # jobs/ = a job posting page, not a person
    re.I)

# Review/directory sites: showing up here means "no confident match", not a match.
_DIRECTORY = re.compile(
    r"\b(yelp|clutch|bbb|designrush|trustpilot|glassdoor|indeed|crunchbase|goodfirms|sortlist|"
    r"manta|yellowpages|mapquest|tripadvisor|g2|capterra|expertise|upcity)\.", re.I)


def clean(url: str) -> str:
    return (url or "").split("?")[0].rstrip("/")


def is_directory(url: str) -> bool:
    return bool(_DIRECTORY.search(url or ""))


def is_person_linkedin(url: str) -> bool:
    """A personal LinkedIn profile (/in/<slug>) — the only shape usable as a founder identity."""
    return "linkedin.com/in/" in (url or "").lower()


def social_profile(url: str, *, allow_company: bool = False):
    """Return (platform, clean_url) if url is a real IG/LI/FB profile, else None.

    allow_company: keep a linkedin.com/company/ page (wanted for the COMPANY LinkedIn column, which
    now exists separately from the founder's personal /in/ column). Default False preserves
    scrape_socials.py's original person-only behavior for the legacy per-channel flow.
    """
    m = SOCIAL_RE.match(url or "")
    if not m:
        return None
    platform = m.group(1).lower()
    cu = clean(url)
    if _BAD_PATH.search(cu):
        return None
    if platform == "facebook" and _BAD_PATH_FB.search(cu):
        return None
    if platform == "linkedin" and _BAD_PATH_LI.search(cu):
        return None
    if not urlparse(cu).path.strip("/"):  # bare domain, no profile slug
        return None
    if platform == "linkedin" and "/company/" in cu.lower() and not allow_company:
        return None
    return platform, cu


if __name__ == "__main__":
    # real profiles pass
    assert social_profile("https://www.instagram.com/nexuspoint/") == ("instagram", "https://www.instagram.com/nexuspoint")
    assert social_profile("https://linkedin.com/in/aleem-ul-hassan") == ("linkedin", "https://linkedin.com/in/aleem-ul-hassan")
    # junk shapes rejected
    assert social_profile("https://instagram.com/p/abc123/") is None
    assert social_profile("https://facebook.com/tr") is None
    assert social_profile("https://www.linkedin.com/feed/update/xyz") is None
    # a people-DIRECTORY search page, not a real profile (live-caught: a founder-name social search
    # surfaced this instead of the person's actual /in/ profile for 3 rows in the 2026-07-17 backfill)
    assert social_profile("https://www.linkedin.com/pub/dir/David/Morneau") is None
    # plural photos/videos + popular: real shapes that slipped past the singular-only regex
    assert social_profile("https://www.facebook.com/acme/photos/some-post-123") is None
    assert social_profile("https://www.facebook.com/acme/videos/some-clip-456") is None
    assert social_profile("https://www.instagram.com/popular/some-listing") is None
    assert social_profile("https://www.linkedin.com/jobs/view/some-role-3607041216") is None  # job posting
    assert social_profile("https://instagram.com/") is None                      # bare domain
    # company page: rejected by default, kept when allowed
    assert social_profile("https://linkedin.com/company/acme") is None
    assert social_profile("https://linkedin.com/company/acme", allow_company=True) == ("linkedin", "https://linkedin.com/company/acme")
    # directory + person helpers
    assert is_directory("https://www.clutch.co/profile/acme")
    assert not is_directory("https://acme.com")
    assert is_person_linkedin("https://linkedin.com/in/jane") and not is_person_linkedin("https://linkedin.com/company/acme")
    print("url_filters self-check OK")
