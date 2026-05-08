"""Trust & conversion feature extractors (10 features)."""

from __future__ import annotations

import re

from bs4 import BeautifulSoup

TESTIMONIAL_PATTERNS = re.compile(
    r"\b(testimonials?|reviews?|what our (customers|clients) say|"
    r"trusted by|case studies?|success stories)\b",
    re.IGNORECASE,
)

CLIENT_LOGO_PATTERNS = re.compile(
    r"\b(our clients?|featured in|as seen in|partners?|"
    r"trusted partners|brands?)\b",
    re.IGNORECASE,
)

PRICING_PATTERNS = re.compile(r"\b(pricing|plans?|packages?|cost|fees?)\b", re.IGNORECASE)

PHONE_PATTERN = re.compile(
    r"(\+?\d{1,3}[\s\-]?)?\(?\d{3}\)?[\s\-]?\d{3}[\s\-]?\d{4}"
)
EMAIL_PATTERN = re.compile(r"[\w\.\-]+@[\w\.\-]+\.\w+")
ADDRESS_PATTERN = re.compile(
    r"\b\d+\s+[A-Z][a-z]+\s+(Street|St|Avenue|Ave|Road|Rd|Lane|Ln|Drive|Dr|Boulevard|Blvd)\b"
)
SOCIAL_DOMAINS = re.compile(
    r"(facebook|twitter|x\.com|linkedin|instagram|youtube|tiktok)\.com",
    re.IGNORECASE,
)


def _has_testimonials(soup: BeautifulSoup, text: str) -> int:
    if TESTIMONIAL_PATTERNS.search(text):
        return 1
    if soup.find(attrs={"class": re.compile(r"testimonial|review", re.IGNORECASE)}):
        return 1
    return 0


def _has_client_logos(soup: BeautifulSoup, text: str) -> int:
    if CLIENT_LOGO_PATTERNS.search(text):
        return 1
    if soup.find(attrs={"class": re.compile(r"client|partner|logo-cloud", re.IGNORECASE)}):
        return 1
    return 0


def _social_proof_count(text: str) -> int:
    """Detect numbers next to credibility words (e.g., '500+ customers')."""
    pattern = re.compile(
        r"\b\d{2,}[+,]?\s*(customers?|users?|clients?|companies|reviews?)\b",
        re.IGNORECASE,
    )
    return len(pattern.findall(text))


def _has_video(soup: BeautifulSoup) -> int:
    if soup.find("video") or soup.find("iframe", src=re.compile(r"youtube|vimeo|wistia", re.IGNORECASE)):
        return 1
    return 0


def _has_privacy_link(soup: BeautifulSoup, text: str) -> int:
    for a in soup.find_all("a"):
        href = (a.get("href") or "").lower()
        anchor = (a.get_text() or "").lower()
        if "privacy" in href or "privacy" in anchor:
            return 1
    return 0


def _social_link_count(soup: BeautifulSoup) -> int:
    count = 0
    for a in soup.find_all("a"):
        href = a.get("href") or ""
        if SOCIAL_DOMAINS.search(href):
            count += 1
    return count


def extract(crawl_data: dict) -> dict:
    html = crawl_data.get("html") or ""
    soup = BeautifulSoup(html, "html.parser") if html else BeautifulSoup("", "html.parser")
    text = soup.get_text(" ", strip=True) if html else ""

    return {
        "trust_testimonials": _has_testimonials(soup, text),
        "trust_client_logos": _has_client_logos(soup, text),
        "trust_social_proof_count": _social_proof_count(text),
        "trust_phone_visible": 1 if PHONE_PATTERN.search(text) else 0,
        "trust_email_visible": 1 if EMAIL_PATTERN.search(text) else 0,
        "trust_address_visible": 1 if ADDRESS_PATTERN.search(text) else 0,
        "trust_privacy_link": _has_privacy_link(soup, text),
        "trust_social_link_count": _social_link_count(soup),
        "trust_has_video": _has_video(soup),
        "trust_has_pricing": 1 if PRICING_PATTERNS.search(text) else 0,
    }
