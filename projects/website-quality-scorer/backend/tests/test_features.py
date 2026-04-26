"""Smoke tests for feature extraction."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from features.extractor import FEATURE_NAMES, extract_all


def _crawl_fixture(html: str = "", url: str = "https://example.com") -> dict:
    return {"url": url, "html": html, "markdown": "", "metadata": {}}


def _pagespeed_fixture() -> dict:
    return {
        "mobile": {"score": 82, "lcp_seconds": 2.1, "cls": 0.05, "tbt_seconds": 0.3},
        "desktop": {"score": 95, "lcp_seconds": 1.2, "cls": 0.02, "tbt_seconds": 0.1},
    }


def test_extract_all_returns_full_schema():
    """Even with empty inputs, all feature keys must be present."""
    features = extract_all(_crawl_fixture(), {"mobile": {}, "desktop": {}})
    assert set(features.keys()) == set(FEATURE_NAMES)
    assert len(features) == 41  # 10 + 10 + 11 + 10


def test_extract_with_real_html():
    html = """
    <html>
      <head>
        <title>Acme</title>
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <meta name="description" content="Acme builds AI tools for SaaS teams. Trusted by 500+ companies.">
      </head>
      <body>
        <header>
          <nav><a href="/">Home</a><a href="/pricing">Pricing</a></nav>
        </header>
        <section class="hero">
          <h1>Build faster with Acme</h1>
          <p>We help SaaS teams automate their workflow in minutes.</p>
          <button class="cta">Get Started Free</button>
        </section>
        <section class="testimonials">
          <h2>What our customers say</h2>
          <p>Trusted by 500+ companies.</p>
        </section>
        <footer>
          <a href="/privacy">Privacy Policy</a>
          <a href="https://twitter.com/acme">Twitter</a>
          <p>contact@acme.com</p>
        </footer>
      </body>
    </html>
    """
    features = extract_all(_crawl_fixture(html), _pagespeed_fixture())

    assert features["ux_cta_total"] >= 1
    assert features["ux_viewport_meta"] == 1
    assert features["ux_has_hero_section"] == 1
    assert features["content_h1_count"] == 1
    assert features["content_h1_unique"] == 1
    assert features["content_value_prop_detected"] == 1
    assert features["tech_pagespeed_mobile"] == 82
    assert features["tech_https"] == 1
    assert features["trust_testimonials"] == 1
    assert features["trust_email_visible"] == 1
    assert features["trust_privacy_link"] == 1
    assert features["trust_social_link_count"] >= 1


def test_handles_empty_html_gracefully():
    """Crawl failures shouldn't crash the pipeline."""
    features = extract_all(_crawl_fixture(""), {"mobile": {}, "desktop": {}})
    assert features["ux_cta_total"] == 0
    assert features["content_word_count"] == 0
    assert features["tech_pagespeed_mobile"] is None
