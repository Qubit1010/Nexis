"""Technical performance feature extractors (10 features)."""

from __future__ import annotations

from urllib.parse import urlparse

from bs4 import BeautifulSoup


def _has_https(url: str) -> int:
    return 1 if urlparse(url).scheme == "https" else 0


def _has_schema_markup(soup: BeautifulSoup) -> int:
    """Detect JSON-LD, microdata, or RDFa structured data."""
    if soup.find("script", type="application/ld+json"):
        return 1
    if soup.find(attrs={"itemscope": True}) or soup.find(attrs={"itemtype": True}):
        return 1
    if soup.find(attrs={"vocab": True}) or soup.find(attrs={"typeof": True}):
        return 1
    return 0


def _alt_text_coverage(soup: BeautifulSoup) -> float:
    images = soup.find_all("img")
    if not images:
        return 1.0  # no images = no missing alts
    with_alt = sum(1 for img in images if (img.get("alt") or "").strip())
    return round(with_alt / len(images), 3)


def _external_resource_count(soup: BeautifulSoup) -> tuple[int, int]:
    css = len(soup.find_all("link", rel=lambda r: r and "stylesheet" in r))
    js = len(soup.find_all("script", src=True))
    return css, js


def _page_size_kb(html: str) -> float:
    return round(len(html.encode("utf-8")) / 1024, 1)


def extract(crawl_data: dict, pagespeed_data: dict) -> dict:
    html = crawl_data.get("html") or ""
    url = crawl_data.get("url") or ""
    soup = BeautifulSoup(html, "html.parser") if html else BeautifulSoup("", "html.parser")

    mobile = pagespeed_data.get("mobile") or {}
    desktop = pagespeed_data.get("desktop") or {}

    css_count, js_count = _external_resource_count(soup)

    return {
        "tech_pagespeed_mobile": mobile.get("score"),
        "tech_pagespeed_desktop": desktop.get("score"),
        "tech_lcp_seconds": mobile.get("lcp_seconds"),
        "tech_cls": mobile.get("cls"),
        "tech_tbt_seconds": mobile.get("tbt_seconds"),
        "tech_https": _has_https(url),
        "tech_schema_markup": _has_schema_markup(soup),
        "tech_alt_text_coverage": _alt_text_coverage(soup),
        "tech_external_css_count": css_count,
        "tech_external_js_count": js_count,
        "tech_page_size_kb": _page_size_kb(html),
    }
