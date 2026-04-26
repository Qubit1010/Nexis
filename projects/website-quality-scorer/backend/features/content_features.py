"""Content & readability feature extractors (10 features)."""

from __future__ import annotations

import re
from typing import Optional

from bs4 import BeautifulSoup

try:
    import textstat  # type: ignore
except ImportError:  # pragma: no cover
    textstat = None


VALUE_PROP_PATTERNS = re.compile(
    r"\b(we help|we build|all-in-one|the only|"
    r"#1|leading|trusted by|automate your|grow your|"
    r"increase your|save \d+|in minutes|in seconds)\b",
    re.IGNORECASE,
)


def _visible_text(soup: BeautifulSoup) -> str:
    for tag in soup(["script", "style", "noscript"]):
        tag.decompose()
    return soup.get_text(separator=" ", strip=True)


def _flesch_reading_ease(text: str) -> Optional[float]:
    if not text or textstat is None:
        return None
    try:
        return float(textstat.flesch_reading_ease(text))
    except Exception:
        return None


def _flesch_kincaid_grade(text: str) -> Optional[float]:
    if not text or textstat is None:
        return None
    try:
        return float(textstat.flesch_kincaid_grade(text))
    except Exception:
        return None


def _heading_hierarchy_score(soup: BeautifulSoup) -> float:
    """Score 0-1 based on heading structure quality.

    Penalties: missing H1, multiple H1s, H3 before H2, etc.
    """
    headings = [(int(t.name[1]), t.get_text(strip=True)) for t in soup.find_all(re.compile(r"^h[1-6]$"))]
    if not headings:
        return 0.0
    h1_count = sum(1 for level, _ in headings if level == 1)
    score = 1.0
    if h1_count == 0:
        score -= 0.5
    if h1_count > 1:
        score -= 0.2
    # Penalize jumps (e.g., H1 → H3 with no H2)
    prev = 0
    for level, _ in headings:
        if prev and level > prev + 1:
            score -= 0.05
        prev = level
    return max(0.0, round(score, 3))


def _paragraph_length_variance(soup: BeautifulSoup) -> float:
    paragraphs = [len(p.get_text(strip=True)) for p in soup.find_all("p")]
    if len(paragraphs) < 2:
        return 0.0
    mean = sum(paragraphs) / len(paragraphs)
    variance = sum((x - mean) ** 2 for x in paragraphs) / len(paragraphs)
    return round(variance**0.5, 2)


def _avg_sentence_length(text: str) -> float:
    if not text:
        return 0.0
    sentences = re.split(r"[.!?]+", text)
    sentences = [s.strip() for s in sentences if s.strip()]
    if not sentences:
        return 0.0
    word_counts = [len(s.split()) for s in sentences]
    return round(sum(word_counts) / len(word_counts), 2)


def _value_prop_present(text: str) -> int:
    return 1 if VALUE_PROP_PATTERNS.search(text) else 0


def extract(crawl_data: dict) -> dict:
    html = crawl_data.get("html") or ""
    metadata = crawl_data.get("metadata") or {}
    soup = BeautifulSoup(html, "html.parser") if html else BeautifulSoup("", "html.parser")
    text = _visible_text(soup)
    word_count = len(text.split())

    h1_tags = soup.find_all("h1")
    h1_count = len(h1_tags)

    return {
        "content_word_count": word_count,
        "content_flesch_reading_ease": _flesch_reading_ease(text),
        "content_flesch_kincaid_grade": _flesch_kincaid_grade(text),
        "content_avg_sentence_length": _avg_sentence_length(text),
        "content_heading_hierarchy_score": _heading_hierarchy_score(soup),
        "content_h1_count": h1_count,
        "content_h1_unique": 1 if h1_count == 1 else 0,
        "content_paragraph_length_std": _paragraph_length_variance(soup),
        "content_value_prop_detected": _value_prop_present(text),
        "content_meta_description_length": len((metadata.get("description") or "").strip()),
    }
