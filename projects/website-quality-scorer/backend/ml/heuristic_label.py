"""Heuristic baseline scorer for cold-start synthetic labels.

Used by `train.py` to bootstrap an initial XGBoost model before real labeled
data exists. Once 100+ real labels are collected, retrain on real data only.

Weights:
    PageSpeed × 0.40   (technical performance)
    Readability × 0.20 (Flesch reading ease)
    CTA presence × 0.20
    Trust signals × 0.20
"""

from __future__ import annotations


def _safe(value, default=0.0):
    if value is None:
        return default
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _normalize(value: float, lo: float, hi: float) -> float:
    if hi == lo:
        return 0.5
    return max(0.0, min(1.0, (value - lo) / (hi - lo)))


def heuristic_score(features: dict) -> float:
    """Return composite score 0-100 from a feature dict."""

    # Technical (40%)
    pagespeed = _safe(features.get("tech_pagespeed_mobile"), 50)
    https = _safe(features.get("tech_https"))
    schema = _safe(features.get("tech_schema_markup"))
    alt_cov = _safe(features.get("tech_alt_text_coverage"), 0.5)
    technical = (pagespeed / 100) * 0.7 + https * 0.1 + schema * 0.1 + alt_cov * 0.1

    # Content (20%)
    flesch = _safe(features.get("content_flesch_reading_ease"), 50)
    flesch_norm = _normalize(flesch, 30, 80)
    heading = _safe(features.get("content_heading_hierarchy_score"), 0.5)
    word_count = _safe(features.get("content_word_count"))
    word_norm = _normalize(word_count, 100, 1500)
    h1_unique = _safe(features.get("content_h1_unique"))
    value_prop = _safe(features.get("content_value_prop_detected"))
    content = flesch_norm * 0.3 + heading * 0.25 + word_norm * 0.2 + h1_unique * 0.1 + value_prop * 0.15

    # UX / Conversion (20%)
    cta_total = _safe(features.get("ux_cta_total"))
    cta_norm = _normalize(cta_total, 0, 8)
    cta_above = _safe(features.get("ux_cta_above_fold"))
    cta_above_norm = _normalize(cta_above, 0, 3)
    viewport = _safe(features.get("ux_viewport_meta"))
    hero = _safe(features.get("ux_has_hero_section"))
    ux = cta_norm * 0.3 + cta_above_norm * 0.3 + viewport * 0.2 + hero * 0.2

    # Trust (20%)
    testimonials = _safe(features.get("trust_testimonials"))
    logos = _safe(features.get("trust_client_logos"))
    phone = _safe(features.get("trust_phone_visible"))
    email = _safe(features.get("trust_email_visible"))
    privacy = _safe(features.get("trust_privacy_link"))
    social_count = _safe(features.get("trust_social_link_count"))
    social_norm = _normalize(social_count, 0, 5)
    pricing = _safe(features.get("trust_has_pricing"))
    trust = (
        testimonials * 0.2 + logos * 0.15 + phone * 0.1 + email * 0.1
        + privacy * 0.1 + social_norm * 0.15 + pricing * 0.2
    )

    composite = (
        technical * 0.40
        + content * 0.20
        + ux * 0.20
        + trust * 0.20
    )

    return round(composite * 100, 2)


def heuristic_score_detailed(features: dict) -> dict:
    """Return per-dimension scores (0-25) and composite (0-100)."""
    # Reuse heuristic_score internals to get per-dimension 0-1 values
    pagespeed = _safe(features.get("tech_pagespeed_mobile"), 50)
    https = _safe(features.get("tech_https"))
    schema = _safe(features.get("tech_schema_markup"))
    alt_cov = _safe(features.get("tech_alt_text_coverage"), 0.5)
    technical = (pagespeed / 100) * 0.7 + https * 0.1 + schema * 0.1 + alt_cov * 0.1

    flesch = _safe(features.get("content_flesch_reading_ease"), 50)
    flesch_norm = _normalize(flesch, 30, 80)
    heading = _safe(features.get("content_heading_hierarchy_score"), 0.5)
    word_count = _safe(features.get("content_word_count"))
    word_norm = _normalize(word_count, 100, 1500)
    h1_unique = _safe(features.get("content_h1_unique"))
    value_prop = _safe(features.get("content_value_prop_detected"))
    content = flesch_norm * 0.3 + heading * 0.25 + word_norm * 0.2 + h1_unique * 0.1 + value_prop * 0.15

    cta_total = _safe(features.get("ux_cta_total"))
    cta_norm = _normalize(cta_total, 0, 8)
    cta_above = _safe(features.get("ux_cta_above_fold"))
    cta_above_norm = _normalize(cta_above, 0, 3)
    viewport = _safe(features.get("ux_viewport_meta"))
    hero = _safe(features.get("ux_has_hero_section"))
    ux = cta_norm * 0.3 + cta_above_norm * 0.3 + viewport * 0.2 + hero * 0.2

    testimonials = _safe(features.get("trust_testimonials"))
    logos = _safe(features.get("trust_client_logos"))
    phone = _safe(features.get("trust_phone_visible"))
    email = _safe(features.get("trust_email_visible"))
    privacy = _safe(features.get("trust_privacy_link"))
    social_count = _safe(features.get("trust_social_link_count"))
    social_norm = _normalize(social_count, 0, 5)
    pricing = _safe(features.get("trust_has_pricing"))
    trust = (
        testimonials * 0.2 + logos * 0.15 + phone * 0.1 + email * 0.1
        + privacy * 0.1 + social_norm * 0.15 + pricing * 0.2
    )

    composite = technical * 0.40 + content * 0.20 + ux * 0.20 + trust * 0.20
    return {
        "technical": round(technical * 25, 2),
        "content": round(content * 25, 2),
        "ux": round(ux * 25, 2),
        "trust": round(trust * 25, 2),
        "total": round(composite * 100, 2),
    }
