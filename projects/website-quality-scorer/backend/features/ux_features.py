"""UX & layout feature extractors (10 features)."""

from __future__ import annotations

import re
from typing import Optional

from bs4 import BeautifulSoup

CTA_KEYWORDS = re.compile(
    r"\b(get started|sign up|signup|try free|book|buy now|order|"
    r"learn more|contact us|request demo|schedule|subscribe|"
    r"download|register|join|start free|get a quote)\b",
    re.IGNORECASE,
)


def _count_ctas(soup: BeautifulSoup) -> tuple[int, int]:
    """Return (total_ctas, ctas_above_fold_estimate).

    Above-fold heuristic: count CTAs in the first 30% of body content (by tag order).
    """
    candidates = soup.find_all(["a", "button"])
    cta_count = 0
    above_fold = 0
    fold_cutoff = max(1, len(candidates) * 30 // 100)

    for idx, tag in enumerate(candidates):
        text = (tag.get_text() or "").strip()
        classes = " ".join(tag.get("class") or []).lower()
        if not text:
            continue
        is_cta = bool(CTA_KEYWORDS.search(text)) or any(
            kw in classes for kw in ("btn", "button", "cta")
        )
        if is_cta:
            cta_count += 1
            if idx < fold_cutoff:
                above_fold += 1
    return cta_count, above_fold


def _has_hero(soup: BeautifulSoup) -> int:
    selectors = [
        {"class_": re.compile(r"hero", re.IGNORECASE)},
        {"id": re.compile(r"hero", re.IGNORECASE)},
        {"class_": re.compile(r"banner|jumbotron", re.IGNORECASE)},
    ]
    for sel in selectors:
        if soup.find("section", **sel) or soup.find("div", **sel):
            return 1
    return 0


def _viewport_meta(soup: BeautifulSoup) -> int:
    tag = soup.find("meta", attrs={"name": "viewport"})
    return 1 if tag else 0


def _count_breakpoints(html: str) -> int:
    """Count distinct media-query min/max-width breakpoints in inline CSS."""
    matches = re.findall(r"@media[^{]*\(\s*(?:min|max)-width\s*:\s*(\d+)", html, re.IGNORECASE)
    return len(set(matches))


def _nav_link_count(soup: BeautifulSoup) -> int:
    nav = soup.find("nav") or soup.find("header")
    if not nav:
        return 0
    return len(nav.find_all("a"))


def _form_field_count(soup: BeautifulSoup) -> int:
    fields = soup.find_all(["input", "textarea", "select"])
    return sum(
        1 for f in fields if f.get("type") not in ("hidden", "submit", "button")
    )


def _image_text_ratio(soup: BeautifulSoup) -> float:
    images = len(soup.find_all("img"))
    text_len = max(1, len(soup.get_text()))
    return round(images / (text_len / 1000), 3)  # images per 1k chars


def _whitespace_ratio_estimate(html: str) -> float:
    """Crude estimate: ratio of whitespace chars to total chars in raw HTML."""
    if not html:
        return 0.0
    ws = sum(1 for c in html if c.isspace())
    return round(ws / len(html), 3)


def extract(crawl_data: dict) -> dict:
    html = crawl_data.get("html") or ""
    soup = BeautifulSoup(html, "html.parser") if html else BeautifulSoup("", "html.parser")

    cta_total, cta_above_fold = _count_ctas(soup)

    return {
        "ux_cta_total": cta_total,
        "ux_cta_above_fold": cta_above_fold,
        "ux_nav_link_count": _nav_link_count(soup),
        "ux_form_field_count": _form_field_count(soup),
        "ux_image_text_ratio": _image_text_ratio(soup),
        "ux_whitespace_ratio": _whitespace_ratio_estimate(html),
        "ux_viewport_meta": _viewport_meta(soup),
        "ux_responsive_breakpoints": _count_breakpoints(html),
        "ux_has_hero_section": _has_hero(soup),
        "ux_total_links": len(soup.find_all("a")),
    }
